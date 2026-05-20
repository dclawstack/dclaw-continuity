from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseGenerateRequest,
    ExerciseRead,
    ExerciseRunObservation,
    ExerciseUpdate,
)
from app.services import bcp_service, exercise_service

router = APIRouter()


@router.get("/", response_model=list[ExerciseRead])
async def list_exercises(
    bcp_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await exercise_service.list_exercises(db, bcp_id=bcp_id)


@router.post("/", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    payload: ExerciseCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await exercise_service.create_exercise(db, payload)


@router.get("/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(
    exercise_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    ex = await exercise_service.get_exercise(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    return ex


@router.patch("/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(
    exercise_id: uuid.UUID,
    payload: ExerciseUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    ex = await exercise_service.get_exercise(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    return await exercise_service.update_exercise(db, ex, payload)


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(
    exercise_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    ex = await exercise_service.get_exercise(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    await exercise_service.delete_exercise(db, ex)


@router.post("/generate", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
async def generate_exercise(
    payload: ExerciseGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    bcp = await bcp_service.get_bcp(db, payload.bcp_id)
    if bcp is None:
        raise HTTPException(status_code=404, detail="bcp not found")
    return await exercise_service.generate_exercise_from_bcp(db, bcp, focus=payload.focus)


@router.post("/{exercise_id}/start", response_model=ExerciseRead)
async def start_exercise(
    exercise_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    ex = await exercise_service.get_exercise(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    return await exercise_service.start_exercise(db, ex)


@router.post("/{exercise_id}/evaluate", response_model=ExerciseRead)
async def evaluate_exercise(
    exercise_id: uuid.UUID,
    payload: ExerciseRunObservation,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    ex = await exercise_service.get_exercise(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    return await exercise_service.evaluate_exercise(db, ex, payload)
