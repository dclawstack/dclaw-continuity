from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.work_area import (
    WorkAreaPlanRead,
    WorkAreaPlanRequest,
    WorkAreaSiteCreate,
    WorkAreaSiteRead,
    WorkAreaSiteUpdate,
)
from app.services import function_service, work_area_service

router = APIRouter()


@router.get("/sites/", response_model=list[WorkAreaSiteRead])
async def list_sites(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await work_area_service.list_sites(db)


@router.post(
    "/sites/", response_model=WorkAreaSiteRead, status_code=status.HTTP_201_CREATED
)
async def create_site(
    payload: WorkAreaSiteCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await work_area_service.create_site(db, payload)


@router.patch("/sites/{site_id}", response_model=WorkAreaSiteRead)
async def update_site(
    site_id: uuid.UUID,
    payload: WorkAreaSiteUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    site = await work_area_service.get_site(db, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="site not found")
    return await work_area_service.update_site(db, site, payload)


@router.delete("/sites/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    site = await work_area_service.get_site(db, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="site not found")
    await work_area_service.delete_site(db, site)


@router.get("/plans/", response_model=list[WorkAreaPlanRead])
async def list_plans(
    function_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await work_area_service.list_plans(db, function_id=function_id)


@router.post(
    "/plans/recommend",
    response_model=WorkAreaPlanRead,
    status_code=status.HTTP_201_CREATED,
)
async def recommend_plan(
    payload: WorkAreaPlanRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    fn = await function_service.get_function(db, payload.function_id)
    if fn is None:
        raise HTTPException(status_code=404, detail="function not found")
    return await work_area_service.recommend_plan(db, fn, payload)
