from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business_function import BusinessFunction
from app.models.recovery_strategy import RecoveryStrategy, StrategyKind
from app.schemas.recovery import RecoveryRecommendRequest, RecoveryStrategyCreate, RecoveryStrategyUpdate
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import COPILOT_SYSTEM_PROMPT, RECOVERY_RECOMMENDATION_PROMPT


async def list_strategies(
    db: AsyncSession, function_id: Optional[uuid.UUID] = None
) -> list[RecoveryStrategy]:
    stmt = select(RecoveryStrategy).order_by(RecoveryStrategy.created_at.desc())
    if function_id is not None:
        stmt = stmt.where(RecoveryStrategy.function_id == function_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_strategy(
    db: AsyncSession, strategy_id: uuid.UUID
) -> Optional[RecoveryStrategy]:
    result = await db.execute(
        select(RecoveryStrategy).where(RecoveryStrategy.id == strategy_id)
    )
    return result.scalar_one_or_none()


async def create_strategy(
    db: AsyncSession, payload: RecoveryStrategyCreate
) -> RecoveryStrategy:
    strat = RecoveryStrategy(**payload.model_dump())
    db.add(strat)
    await db.commit()
    await db.refresh(strat)
    return strat


async def update_strategy(
    db: AsyncSession, strat: RecoveryStrategy, payload: RecoveryStrategyUpdate
) -> RecoveryStrategy:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(strat, k, v)
    await db.commit()
    await db.refresh(strat)
    return strat


async def delete_strategy(db: AsyncSession, strat: RecoveryStrategy) -> None:
    await db.delete(strat)
    await db.commit()


async def recommend_strategies(
    db: AsyncSession,
    function: BusinessFunction,
    request: RecoveryRecommendRequest,
    llm: Optional[LLMClient] = None,
) -> list[RecoveryStrategy]:
    """Generate 3 AI-recommended strategies and persist them."""

    llm = llm or get_llm_client()

    prompt = RECOVERY_RECOMMENDATION_PROMPT.format(
        name=function.name,
        description=function.description or "(no description)",
        criticality=function.criticality.value,
        rto_minutes=function.rto_minutes,
        rpo_minutes=function.rpo_minutes,
        budget_usd=request.budget_usd or 0,
        additional_context=request.additional_context or "(none)",
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    strategies: list[RecoveryStrategy] = []
    for entry in result.get("strategies", []):
        try:
            kind = StrategyKind(entry.get("kind", "other"))
        except ValueError:
            kind = StrategyKind.OTHER
        strat = RecoveryStrategy(
            function_id=function.id,
            title=entry.get("title", "Recovery strategy"),
            kind=kind,
            description=entry.get("description", ""),
            estimated_cost_usd=int(entry.get("estimated_cost_usd") or 0),
            rto_minutes=int(entry.get("rto_minutes") or 0),
            rpo_minutes=int(entry.get("rpo_minutes") or 0),
            is_recommended=bool(entry.get("is_recommended", False)),
            details={"rationale": entry.get("rationale", "")},
        )
        db.add(strat)
        strategies.append(strat)
    await db.commit()
    for s in strategies:
        await db.refresh(s)
        await rag_service.index_recovery_strategy(db, s)
    return strategies
