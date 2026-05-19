from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.it_dr import (
    ITDRGenerateRequest,
    ITDRPlanRead,
    ITDRTestRecord,
    ITSystemCreate,
    ITSystemRead,
    ITSystemUpdate,
)
from app.services import it_dr_service

router = APIRouter()


# ── Systems ─────────────────────────────────────────────────────────────────


@router.get("/systems/", response_model=list[ITSystemRead])
async def list_systems(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await it_dr_service.list_systems(db)


@router.post(
    "/systems/", response_model=ITSystemRead, status_code=status.HTTP_201_CREATED
)
async def create_system(
    payload: ITSystemCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await it_dr_service.create_system(db, payload)


@router.get("/systems/{system_id}", response_model=ITSystemRead)
async def get_system(
    system_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    sys = await it_dr_service.get_system(db, system_id)
    if sys is None:
        raise HTTPException(status_code=404, detail="system not found")
    return sys


@router.patch("/systems/{system_id}", response_model=ITSystemRead)
async def update_system(
    system_id: uuid.UUID,
    payload: ITSystemUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    sys = await it_dr_service.get_system(db, system_id)
    if sys is None:
        raise HTTPException(status_code=404, detail="system not found")
    return await it_dr_service.update_system(db, sys, payload)


@router.delete("/systems/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system(
    system_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    sys = await it_dr_service.get_system(db, system_id)
    if sys is None:
        raise HTTPException(status_code=404, detail="system not found")
    await it_dr_service.delete_system(db, sys)


# ── DR Plans ────────────────────────────────────────────────────────────────


@router.get("/plans/", response_model=list[ITDRPlanRead])
async def list_plans(
    system_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await it_dr_service.list_plans(db, system_id=system_id)


@router.post(
    "/plans/generate",
    response_model=ITDRPlanRead,
    status_code=status.HTTP_201_CREATED,
)
async def generate_plan(
    payload: ITDRGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    sys = await it_dr_service.get_system(db, payload.system_id)
    if sys is None:
        raise HTTPException(status_code=404, detail="system not found")
    return await it_dr_service.generate_plan(
        db, sys, additional_context=payload.additional_context
    )


@router.post("/plans/{plan_id}/test-record", response_model=ITDRPlanRead)
async def record_test(
    plan_id: uuid.UUID,
    payload: ITDRTestRecord,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    plan = await it_dr_service.get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="plan not found")
    return await it_dr_service.record_test(db, plan, payload)
