from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.business_function import BusinessFunction
from app.models.communication import CommunicationPlan, CommunicationTemplate
from app.schemas.communication import (
    CommunicationDraftRequest,
    CommunicationPlanCreate,
    CommunicationPlanUpdate,
)
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import COMMUNICATION_PLAN_PROMPT, COPILOT_SYSTEM_PROMPT


async def list_plans(
    db: AsyncSession, function_id: Optional[uuid.UUID] = None
) -> list[CommunicationPlan]:
    stmt = (
        select(CommunicationPlan)
        .options(selectinload(CommunicationPlan.templates))
        .order_by(CommunicationPlan.created_at.desc())
    )
    if function_id is not None:
        stmt = stmt.where(CommunicationPlan.function_id == function_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_plan(
    db: AsyncSession, plan_id: uuid.UUID
) -> Optional[CommunicationPlan]:
    result = await db.execute(
        select(CommunicationPlan)
        .options(selectinload(CommunicationPlan.templates))
        .where(CommunicationPlan.id == plan_id)
    )
    return result.scalar_one_or_none()


async def create_plan(
    db: AsyncSession, payload: CommunicationPlanCreate
) -> CommunicationPlan:
    plan = CommunicationPlan(**payload.model_dump())
    db.add(plan)
    await db.commit()
    # Reload with templates relationship populated.
    return await get_plan(db, plan.id)  # type: ignore[return-value]


async def update_plan(
    db: AsyncSession, plan: CommunicationPlan, payload: CommunicationPlanUpdate
) -> CommunicationPlan:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(plan, k, v)
    await db.commit()
    full = await get_plan(db, plan.id)
    if full is not None:
        await rag_service.index_communication_plan(db, full)
    return full  # type: ignore[return-value]


async def delete_plan(db: AsyncSession, plan: CommunicationPlan) -> None:
    await db.delete(plan)
    await db.commit()


async def draft_plan(
    db: AsyncSession,
    function: BusinessFunction,
    request: CommunicationDraftRequest,
    llm: Optional[LLMClient] = None,
) -> CommunicationPlan:
    """AI-drafts a multi-channel communication plan for a scenario + audience."""

    llm = llm or get_llm_client()

    prompt = COMMUNICATION_PLAN_PROMPT.format(
        function_name=function.name,
        criticality=function.criticality.value,
        scenario=request.scenario,
        audience=request.audience,
        additional_context=request.additional_context or "(none)",
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    plan = CommunicationPlan(
        function_id=function.id,
        audience=result.get("audience") or request.audience,
        scenario=request.scenario,
        tone=str(result.get("tone") or "formal"),
        channels=list(result.get("channels", [])),
        escalation_path=list(result.get("escalation_path", [])),
        notes="",
    )
    db.add(plan)
    await db.flush()

    for tpl in result.get("templates", []):
        if not isinstance(tpl, dict) or not tpl.get("body"):
            continue
        db.add(
            CommunicationTemplate(
                plan_id=plan.id,
                channel=str(tpl.get("channel") or "email"),
                trigger=str(tpl.get("trigger") or ""),
                subject=str(tpl.get("subject") or ""),
                body=str(tpl.get("body") or ""),
            )
        )

    await db.commit()
    full = await get_plan(db, plan.id)
    if full is not None:
        await rag_service.index_communication_plan(db, full)
    return full  # type: ignore[return-value]
