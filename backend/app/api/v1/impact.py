from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.impact import (
    ImpactAssessmentCreate,
    ImpactAssessmentRead,
    ImpactModelRequest,
)
from app.services import function_service, impact_service

router = APIRouter()


@router.get("", response_model=list[ImpactAssessmentRead])
async def list_impact(
    function_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await impact_service.list_impact_assessments(db, function_id=function_id)


@router.post("", response_model=ImpactAssessmentRead, status_code=status.HTTP_201_CREATED)
async def create_impact(
    payload: ImpactAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await impact_service.create_impact_assessment(db, payload)


@router.get("/{impact_id}", response_model=ImpactAssessmentRead)
async def get_impact(
    impact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    ia = await impact_service.get_impact_assessment(db, impact_id)
    if ia is None:
        raise HTTPException(status_code=404, detail="impact assessment not found")
    return ia


@router.post(
    "/model",
    response_model=ImpactAssessmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def model_impact(
    payload: ImpactModelRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    fn = await function_service.get_function(db, payload.function_id)
    if fn is None:
        raise HTTPException(status_code=404, detail="function not found")
    return await impact_service.model_impact_scenario(db, fn, payload)
