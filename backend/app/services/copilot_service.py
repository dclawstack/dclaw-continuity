from __future__ import annotations

import json
import re
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bcp import BCP
from app.models.business_function import BusinessFunction
from app.models.copilot import CopilotMessage
from app.models.impact_assessment import ImpactAssessment
from app.models.recovery_strategy import RecoveryStrategy
from app.schemas.copilot import (
    CopilotChatRequest,
    CopilotChatResponse,
    CopilotSuggestion,
)
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import COPILOT_SYSTEM_PROMPT

_SUGGEST_HINT = """After your answer, on a new line, emit a JSON object with the
key "suggestions" — an array (0-3 items) of {action, label, payload}. Use
actions from: create_function, generate_bcp, model_impact, recommend_recovery,
gap_analysis. Wrap the JSON between <suggest> and </suggest> tags."""


_RAG_HINT = """If the retrieved evidence below is relevant, cite it inline like
"(per BCP: <title>)" or "(per Exercise eval: <title>)". If nothing in the
evidence applies, answer from general continuity knowledge and don't fabricate
citations."""


async def chat(
    db: AsyncSession,
    user_sub: str,
    request: CopilotChatRequest,
    llm: LLMClient | None = None,
) -> CopilotChatResponse:
    llm = llm or get_llm_client()

    conversation_id = request.conversation_id or uuid.uuid4()
    context_snapshot = await _build_context_snapshot(db)
    history = await _load_history(db, conversation_id, limit=10)
    retrieved = await rag_service.search(db, request.message)

    messages: list[ChatMessage] = [
        ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
        ChatMessage(
            role="system",
            content=f"Current workspace snapshot:\n{json.dumps(context_snapshot, indent=2)}",
        ),
    ]
    if retrieved:
        messages.append(
            ChatMessage(
                role="system",
                content=_format_retrieved(retrieved),
            )
        )
        messages.append(ChatMessage(role="system", content=_RAG_HINT))
    messages.append(ChatMessage(role="system", content=_SUGGEST_HINT))
    messages.extend(history)
    messages.append(ChatMessage(role="user", content=request.message))

    raw = await llm.chat(messages)
    reply, suggestions = _split_reply_and_suggestions(raw)

    db.add_all(
        [
            CopilotMessage(
                conversation_id=conversation_id,
                user_sub=user_sub,
                role="user",
                content=request.message,
                suggestions=[],
            ),
            CopilotMessage(
                conversation_id=conversation_id,
                user_sub=user_sub,
                role="assistant",
                content=reply,
                suggestions=[s.model_dump() for s in suggestions],
            ),
        ]
    )
    await db.commit()

    return CopilotChatResponse(
        conversation_id=conversation_id,
        reply=reply,
        suggestions=suggestions,
    )


async def get_conversation(db: AsyncSession, conversation_id: uuid.UUID) -> list[CopilotMessage]:
    result = await db.execute(
        select(CopilotMessage)
        .where(CopilotMessage.conversation_id == conversation_id)
        .order_by(CopilotMessage.created_at)
    )
    return list(result.scalars().all())


async def _load_history(
    db: AsyncSession, conversation_id: uuid.UUID, *, limit: int
) -> list[ChatMessage]:
    result = await db.execute(
        select(CopilotMessage)
        .where(CopilotMessage.conversation_id == conversation_id)
        .order_by(CopilotMessage.created_at.desc())
        .limit(limit)
    )
    rows = list(result.scalars().all())[::-1]
    return [ChatMessage(role=r.role, content=r.content) for r in rows]


async def _build_context_snapshot(db: AsyncSession) -> dict:
    fn_count = (await db.execute(select(func.count(BusinessFunction.id)))).scalar() or 0
    bcp_count = (await db.execute(select(func.count(BCP.id)))).scalar() or 0
    ia_count = (await db.execute(select(func.count(ImpactAssessment.id)))).scalar() or 0
    rs_count = (await db.execute(select(func.count(RecoveryStrategy.id)))).scalar() or 0

    fn_sample = (await db.execute(select(BusinessFunction).limit(5))).scalars().all()

    return {
        "counts": {
            "business_functions": fn_count,
            "bcps": bcp_count,
            "impact_assessments": ia_count,
            "recovery_strategies": rs_count,
        },
        "sample_functions": [
            {
                "id": str(f.id),
                "name": f.name,
                "criticality": f.criticality.value,
                "rto_minutes": f.rto_minutes,
                "rpo_minutes": f.rpo_minutes,
            }
            for f in fn_sample
        ],
    }


def _format_retrieved(hits: list) -> str:
    lines = ["Retrieved evidence (most similar first):"]
    for h in hits:
        lines.append(f"- [{h.source_type}] {h.title}\n  {h.text[:600]}")
    return "\n".join(lines)


_SUGGEST_RE = re.compile(r"<suggest>(.*?)</suggest>", re.DOTALL)


def _split_reply_and_suggestions(raw: str) -> tuple[str, list[CopilotSuggestion]]:
    match = _SUGGEST_RE.search(raw)
    if not match:
        return raw.strip(), []
    reply = (raw[: match.start()] + raw[match.end() :]).strip()
    body = match.group(1).strip()
    try:
        parsed = json.loads(body)
        items = parsed.get("suggestions", []) if isinstance(parsed, dict) else parsed
        suggestions = []
        for s in items:
            if not isinstance(s, dict) or not s.get("action"):
                continue
            # Small models often emit `payload` as a string (e.g. an id) even
            # when told it's an object. Coerce to {} so the whole reply isn't
            # lost to a single bad suggestion.
            payload = s.get("payload", {})
            if not isinstance(payload, dict):
                payload = {}
            suggestions.append(
                CopilotSuggestion(
                    action=s.get("action", ""),
                    label=s.get("label", ""),
                    payload=payload,
                )
            )
        return reply, suggestions
    except (json.JSONDecodeError, AttributeError):
        return reply, []
