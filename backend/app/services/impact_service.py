from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business_function import BusinessFunction
from app.models.impact_assessment import ImpactAssessment
from app.schemas.impact import ImpactAssessmentCreate, ImpactModelRequest
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import COPILOT_SYSTEM_PROMPT, IMPACT_MODELING_PROMPT


async def list_impact_assessments(
    db: AsyncSession, function_id: Optional[uuid.UUID] = None
) -> list[ImpactAssessment]:
    stmt = select(ImpactAssessment).order_by(ImpactAssessment.created_at.desc())
    if function_id is not None:
        stmt = stmt.where(ImpactAssessment.function_id == function_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_impact_assessment(
    db: AsyncSession, impact_id: uuid.UUID
) -> Optional[ImpactAssessment]:
    result = await db.execute(
        select(ImpactAssessment).where(ImpactAssessment.id == impact_id)
    )
    return result.scalar_one_or_none()


async def create_impact_assessment(
    db: AsyncSession, payload: ImpactAssessmentCreate
) -> ImpactAssessment:
    ia = ImpactAssessment(**payload.model_dump())
    db.add(ia)
    await db.commit()
    await db.refresh(ia)
    return ia


async def model_impact_scenario(
    db: AsyncSession,
    function: BusinessFunction,
    request: ImpactModelRequest,
    llm: Optional[LLMClient] = None,
) -> ImpactAssessment:
    llm = llm or get_llm_client()

    prompt = IMPACT_MODELING_PROMPT.format(
        name=function.name,
        description=function.description or "(no description)",
        criticality=function.criticality.value,
        scenario=request.scenario,
        additional_context=request.additional_context or "(none)",
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    ia = ImpactAssessment(
        function_id=function.id,
        scenario=request.scenario,
        description=result.get("narrative", ""),
        revenue_impact_usd=int(result.get("revenue_impact_usd") or 0),
        operational_impact_score=_clamp(int(result.get("operational_impact_score") or 0)),
        reputation_impact_score=_clamp(int(result.get("reputation_impact_score") or 0)),
        details=result,
    )
    db.add(ia)
    await db.commit()
    await db.refresh(ia)
    await rag_service.index_impact(db, ia)
    return ia


def _clamp(n: int, lo: int = 0, hi: int = 10) -> int:
    return max(lo, min(hi, n))
