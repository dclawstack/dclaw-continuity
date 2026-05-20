from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.crisis import (
    CrisisActivateRequest,
    CrisisActivationRead,
    CrisisStatusUpdate,
)
from app.services import crisis_service

router = APIRouter()


@router.get("/", response_model=list[CrisisActivationRead])
async def list_activations(
    only_open: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await crisis_service.list_activations(db, only_open=only_open)


@router.post(
    "/activate",
    response_model=CrisisActivationRead,
    status_code=status.HTTP_201_CREATED,
)
async def activate(
    payload: CrisisActivateRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    try:
        return await crisis_service.activate(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{activation_id}", response_model=CrisisActivationRead)
async def get_activation(
    activation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    a = await crisis_service.get_activation(db, activation_id)
    if a is None:
        raise HTTPException(status_code=404, detail="activation not found")
    return a


@router.post("/{activation_id}/status", response_model=CrisisActivationRead)
async def update_status(
    activation_id: uuid.UUID,
    payload: CrisisStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    a = await crisis_service.get_activation(db, activation_id)
    if a is None:
        raise HTTPException(status_code=404, detail="activation not found")
    return await crisis_service.update_status(db, a, payload)
