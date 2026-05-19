from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.bcp import (
    BCPCreate,
    BCPGenerateRequest,
    BCPRead,
    BCPUpdate,
)
from app.services import bcp_service, function_service

router = APIRouter()


@router.get("/", response_model=list[BCPRead])
async def list_bcps(
    function_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await bcp_service.list_bcps(db, function_id=function_id)


@router.post("/", response_model=BCPRead, status_code=status.HTTP_201_CREATED)
async def create_bcp(
    payload: BCPCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await bcp_service.create_bcp(db, payload)


@router.get("/{bcp_id}", response_model=BCPRead)
async def get_bcp(
    bcp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    bcp = await bcp_service.get_bcp(db, bcp_id)
    if bcp is None:
        raise HTTPException(status_code=404, detail="bcp not found")
    return bcp


@router.patch("/{bcp_id}", response_model=BCPRead)
async def update_bcp(
    bcp_id: uuid.UUID,
    payload: BCPUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    bcp = await bcp_service.get_bcp(db, bcp_id)
    if bcp is None:
        raise HTTPException(status_code=404, detail="bcp not found")
    return await bcp_service.update_bcp(db, bcp, payload)


@router.delete("/{bcp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bcp(
    bcp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    bcp = await bcp_service.get_bcp(db, bcp_id)
    if bcp is None:
        raise HTTPException(status_code=404, detail="bcp not found")
    await bcp_service.delete_bcp(db, bcp)


@router.post("/generate", response_model=BCPRead, status_code=status.HTTP_201_CREATED)
async def generate_bcp(
    payload: BCPGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    fn = await function_service.get_function(db, payload.function_id)
    if fn is None:
        raise HTTPException(status_code=404, detail="function not found")
    return await bcp_service.generate_bcp_for_function(
        db, fn, additional_context=payload.additional_context
    )


@router.post("/{bcp_id}/gap-analysis", response_model=BCPRead)
async def gap_analysis(
    bcp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    bcp = await bcp_service.get_bcp(db, bcp_id)
    if bcp is None:
        raise HTTPException(status_code=404, detail="bcp not found")
    return await bcp_service.run_gap_analysis(db, bcp)
