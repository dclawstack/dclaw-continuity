from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.communication import (
    CommunicationDraftRequest,
    CommunicationPlanCreate,
    CommunicationPlanRead,
    CommunicationPlanUpdate,
)
from app.services import communication_service, function_service

router = APIRouter()


@router.get("/", response_model=list[CommunicationPlanRead])
async def list_plans(
    function_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await communication_service.list_plans(db, function_id=function_id)


@router.post(
    "/", response_model=CommunicationPlanRead, status_code=status.HTTP_201_CREATED
)
async def create_plan(
    payload: CommunicationPlanCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await communication_service.create_plan(db, payload)


@router.get("/{plan_id}", response_model=CommunicationPlanRead)
async def get_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    p = await communication_service.get_plan(db, plan_id)
    if p is None:
        raise HTTPException(status_code=404, detail="plan not found")
    return p


@router.patch("/{plan_id}", response_model=CommunicationPlanRead)
async def update_plan(
    plan_id: uuid.UUID,
    payload: CommunicationPlanUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    p = await communication_service.get_plan(db, plan_id)
    if p is None:
        raise HTTPException(status_code=404, detail="plan not found")
    return await communication_service.update_plan(db, p, payload)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    p = await communication_service.get_plan(db, plan_id)
    if p is None:
        raise HTTPException(status_code=404, detail="plan not found")
    await communication_service.delete_plan(db, p)


@router.post(
    "/draft",
    response_model=CommunicationPlanRead,
    status_code=status.HTTP_201_CREATED,
)
async def draft(
    payload: CommunicationDraftRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    fn = await function_service.get_function(db, payload.function_id)
    if fn is None:
        raise HTTPException(status_code=404, detail="function not found")
    return await communication_service.draft_plan(db, fn, payload)
