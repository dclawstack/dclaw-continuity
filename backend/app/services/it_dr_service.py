from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.it_dr import ITDRPlan, ITSystem
from app.schemas.it_dr import (
    ITDRTestRecord,
    ITSystemCreate,
    ITSystemUpdate,
)
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import COPILOT_SYSTEM_PROMPT, IT_DR_PLAN_PROMPT

# ── Systems ─────────────────────────────────────────────────────────────────


async def list_systems(db: AsyncSession) -> list[ITSystem]:
    return list((await db.execute(select(ITSystem).order_by(ITSystem.name))).scalars().all())


async def get_system(db: AsyncSession, system_id: uuid.UUID) -> ITSystem | None:
    return (await db.execute(select(ITSystem).where(ITSystem.id == system_id))).scalar_one_or_none()


async def create_system(db: AsyncSession, payload: ITSystemCreate) -> ITSystem:
    sys = ITSystem(**payload.model_dump())
    db.add(sys)
    await db.commit()
    await db.refresh(sys)
    return sys


async def update_system(db: AsyncSession, sys: ITSystem, payload: ITSystemUpdate) -> ITSystem:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(sys, k, v)
    await db.commit()
    await db.refresh(sys)
    return sys


async def delete_system(db: AsyncSession, sys: ITSystem) -> None:
    await db.delete(sys)
    await db.commit()


# ── DR Plans ────────────────────────────────────────────────────────────────


async def list_plans(db: AsyncSession, system_id: uuid.UUID | None = None) -> list[ITDRPlan]:
    stmt = select(ITDRPlan).order_by(ITDRPlan.created_at.desc())
    if system_id is not None:
        stmt = stmt.where(ITDRPlan.system_id == system_id)
    return list((await db.execute(stmt)).scalars().all())


async def get_plan(db: AsyncSession, plan_id: uuid.UUID) -> ITDRPlan | None:
    return (await db.execute(select(ITDRPlan).where(ITDRPlan.id == plan_id))).scalar_one_or_none()


async def generate_plan(
    db: AsyncSession,
    system: ITSystem,
    additional_context: str = "",
    llm: LLMClient | None = None,
) -> ITDRPlan:
    """AI-generates a DR plan (procedure + automated test plan) for the system."""

    llm = llm or get_llm_client()

    prompt = IT_DR_PLAN_PROMPT.format(
        name=system.name,
        description=system.description or "(no description)",
        owner=system.owner or "(unassigned)",
        tier=system.tier.value,
        rto_minutes=system.rto_minutes,
        rpo_minutes=system.rpo_minutes,
        backup_strategy=system.backup_strategy or "(none recorded)",
        additional_context=additional_context or "(none)",
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    plan = ITDRPlan(
        system_id=system.id,
        title=str(result.get("title") or f"DR plan — {system.name}"),
        summary=str(result.get("summary") or ""),
        procedure=result,
        test_plan=list(result.get("test_plan", [])),
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    await rag_service.index_it_dr_plan(db, plan)
    return plan


async def record_test(db: AsyncSession, plan: ITDRPlan, record: ITDRTestRecord) -> ITDRPlan:
    plan.last_tested_at = datetime.now(UTC)
    plan.last_test_passed = record.passed
    await db.commit()
    await db.refresh(plan)
    return plan
