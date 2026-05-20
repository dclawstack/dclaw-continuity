from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.recovery import (
    RecoveryRecommendRequest,
    RecoveryStrategyCreate,
    RecoveryStrategyRead,
    RecoveryStrategyUpdate,
)
from app.services import function_service, recovery_service

router = APIRouter()


@router.get("/", response_model=list[RecoveryStrategyRead])
async def list_strategies(
    function_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await recovery_service.list_strategies(db, function_id=function_id)


@router.post("/", response_model=RecoveryStrategyRead, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    payload: RecoveryStrategyCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await recovery_service.create_strategy(db, payload)


@router.get("/{strategy_id}", response_model=RecoveryStrategyRead)
async def get_strategy(
    strategy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    strat = await recovery_service.get_strategy(db, strategy_id)
    if strat is None:
        raise HTTPException(status_code=404, detail="recovery strategy not found")
    return strat


@router.patch("/{strategy_id}", response_model=RecoveryStrategyRead)
async def update_strategy(
    strategy_id: uuid.UUID,
    payload: RecoveryStrategyUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    strat = await recovery_service.get_strategy(db, strategy_id)
    if strat is None:
        raise HTTPException(status_code=404, detail="recovery strategy not found")
    return await recovery_service.update_strategy(db, strat, payload)


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    strat = await recovery_service.get_strategy(db, strategy_id)
    if strat is None:
        raise HTTPException(status_code=404, detail="recovery strategy not found")
    await recovery_service.delete_strategy(db, strat)


@router.post(
    "/recommend",
    response_model=list[RecoveryStrategyRead],
    status_code=status.HTTP_201_CREATED,
)
async def recommend(
    payload: RecoveryRecommendRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    fn = await function_service.get_function(db, payload.function_id)
    if fn is None:
        raise HTTPException(status_code=404, detail="function not found")
    return await recovery_service.recommend_strategies(db, fn, payload)
