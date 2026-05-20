from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business_function import BusinessFunction
from app.models.work_area import WorkAreaPlan, WorkAreaSite
from app.schemas.work_area import (
    WorkAreaPlanRequest,
    WorkAreaSiteCreate,
    WorkAreaSiteUpdate,
)
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import COPILOT_SYSTEM_PROMPT, WORK_AREA_PLAN_PROMPT


async def list_sites(db: AsyncSession) -> list[WorkAreaSite]:
    result = await db.execute(select(WorkAreaSite).order_by(WorkAreaSite.name))
    return list(result.scalars().all())


async def get_site(db: AsyncSession, site_id: uuid.UUID) -> Optional[WorkAreaSite]:
    return (
        await db.execute(select(WorkAreaSite).where(WorkAreaSite.id == site_id))
    ).scalar_one_or_none()


async def create_site(db: AsyncSession, payload: WorkAreaSiteCreate) -> WorkAreaSite:
    site = WorkAreaSite(**payload.model_dump())
    db.add(site)
    await db.commit()
    await db.refresh(site)
    return site


async def update_site(
    db: AsyncSession, site: WorkAreaSite, payload: WorkAreaSiteUpdate
) -> WorkAreaSite:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(site, k, v)
    await db.commit()
    await db.refresh(site)
    return site


async def delete_site(db: AsyncSession, site: WorkAreaSite) -> None:
    await db.delete(site)
    await db.commit()


async def list_plans(
    db: AsyncSession, function_id: Optional[uuid.UUID] = None
) -> list[WorkAreaPlan]:
    stmt = select(WorkAreaPlan).order_by(WorkAreaPlan.created_at.desc())
    if function_id is not None:
        stmt = stmt.where(WorkAreaPlan.function_id == function_id)
    return list((await db.execute(stmt)).scalars().all())


async def get_plan(db: AsyncSession, plan_id: uuid.UUID) -> Optional[WorkAreaPlan]:
    return (
        await db.execute(select(WorkAreaPlan).where(WorkAreaPlan.id == plan_id))
    ).scalar_one_or_none()


async def recommend_plan(
    db: AsyncSession,
    function: BusinessFunction,
    request: WorkAreaPlanRequest,
    llm: Optional[LLMClient] = None,
) -> WorkAreaPlan:
    """AI-recommends how to fill the function's headcount from available sites."""

    llm = llm or get_llm_client()
    sites = await list_sites(db)
    site_summary = [
        {
            "id": str(s.id),
            "name": s.name,
            "kind": s.kind.value,
            "location": s.location,
            "capacity_seats": s.capacity_seats,
            "has_remote_access": s.has_remote_access,
        }
        for s in sites
    ]

    prompt = WORK_AREA_PLAN_PROMPT.format(
        function_name=function.name,
        criticality=function.criticality.value,
        headcount=request.headcount_required,
        sites=site_summary or "(no sites registered)",
        additional_context=request.additional_context or "(none)",
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    plan = WorkAreaPlan(
        function_id=function.id,
        headcount_required=request.headcount_required,
        summary=str(result.get("summary") or ""),
        details=result,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    await rag_service.index_work_area_plan(db, plan)
    return plan
