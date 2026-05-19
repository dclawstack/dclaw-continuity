from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bcp import BCP, BCPStatus
from app.models.business_function import BusinessFunction
from app.models.dependency import Dependency
from app.schemas.bcp import BCPCreate, BCPUpdate
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import (
    BCP_GAP_ANALYSIS_PROMPT,
    BCP_GENERATION_PROMPT,
    COPILOT_SYSTEM_PROMPT,
)


async def list_bcps(
    db: AsyncSession, function_id: Optional[uuid.UUID] = None
) -> list[BCP]:
    stmt = select(BCP).order_by(BCP.created_at.desc())
    if function_id is not None:
        stmt = stmt.where(BCP.function_id == function_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_bcp(db: AsyncSession, bcp_id: uuid.UUID) -> Optional[BCP]:
    result = await db.execute(select(BCP).where(BCP.id == bcp_id))
    return result.scalar_one_or_none()


async def create_bcp(db: AsyncSession, payload: BCPCreate) -> BCP:
    bcp = BCP(**payload.model_dump())
    db.add(bcp)
    await db.commit()
    await db.refresh(bcp)
    return bcp


async def update_bcp(db: AsyncSession, bcp: BCP, payload: BCPUpdate) -> BCP:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(bcp, k, v)
    await db.commit()
    await db.refresh(bcp)
    return bcp


async def delete_bcp(db: AsyncSession, bcp: BCP) -> None:
    await db.delete(bcp)
    await db.commit()


async def generate_bcp_for_function(
    db: AsyncSession,
    function: BusinessFunction,
    additional_context: str = "",
    llm: Optional[LLMClient] = None,
) -> BCP:
    """Ask the AI to draft a BCP and persist it as DRAFT."""

    llm = llm or get_llm_client()

    deps_result = await db.execute(
        select(Dependency).where(Dependency.function_id == function.id)
    )
    deps = [f"{d.name} ({d.type.value})" for d in deps_result.scalars()]

    prompt = BCP_GENERATION_PROMPT.format(
        name=function.name,
        description=function.description or "(no description)",
        owner=function.owner or "(unassigned)",
        criticality=function.criticality.value,
        rto_minutes=function.rto_minutes,
        rpo_minutes=function.rpo_minutes,
        dependencies=", ".join(deps) or "none recorded",
        additional_context=additional_context or "(none)",
    )

    plan = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    bcp = BCP(
        function_id=function.id,
        title=plan.get("title") or f"BCP — {function.name}",
        summary=plan.get("summary", ""),
        status=BCPStatus.DRAFT,
        content=plan,
        gaps=[],
    )
    db.add(bcp)
    await db.commit()
    await db.refresh(bcp)
    await rag_service.index_bcp(db, bcp)
    return bcp


async def run_gap_analysis(
    db: AsyncSession, bcp: BCP, llm: Optional[LLMClient] = None
) -> BCP:
    llm = llm or get_llm_client()

    fn_result = await db.execute(
        select(BusinessFunction).where(BusinessFunction.id == bcp.function_id)
    )
    function = fn_result.scalar_one()

    prompt = BCP_GAP_ANALYSIS_PROMPT.format(
        bcp_json=bcp.content,
        criticality=function.criticality.value,
        rto_minutes=function.rto_minutes,
        rpo_minutes=function.rpo_minutes,
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )
    bcp.gaps = result.get("gaps", [])
    await db.commit()
    await db.refresh(bcp)
    return bcp
