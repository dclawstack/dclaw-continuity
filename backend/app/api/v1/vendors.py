from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.vendor import (
    VendorAssessmentRead,
    VendorAssessRequest,
    VendorCreate,
    VendorRead,
    VendorUpdate,
)
from app.services import vendor_service

router = APIRouter()


@router.get("/", response_model=list[VendorRead])
async def list_vendors(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await vendor_service.list_vendors(db)


@router.post("/", response_model=VendorRead, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    payload: VendorCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await vendor_service.create_vendor(db, payload)


@router.get("/{vendor_id}", response_model=VendorRead)
async def get_vendor(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    v = await vendor_service.get_vendor(db, vendor_id)
    if v is None:
        raise HTTPException(status_code=404, detail="vendor not found")
    return v


@router.patch("/{vendor_id}", response_model=VendorRead)
async def update_vendor(
    vendor_id: uuid.UUID,
    payload: VendorUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    v = await vendor_service.get_vendor(db, vendor_id)
    if v is None:
        raise HTTPException(status_code=404, detail="vendor not found")
    return await vendor_service.update_vendor(db, v, payload)


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    v = await vendor_service.get_vendor(db, vendor_id)
    if v is None:
        raise HTTPException(status_code=404, detail="vendor not found")
    await vendor_service.delete_vendor(db, v)


@router.get("/{vendor_id}/assessments", response_model=list[VendorAssessmentRead])
async def list_vendor_assessments(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await vendor_service.list_assessments(db, vendor_id=vendor_id)


@router.post(
    "/assess",
    response_model=VendorAssessmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def assess(
    payload: VendorAssessRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    v = await vendor_service.get_vendor(db, payload.vendor_id)
    if v is None:
        raise HTTPException(status_code=404, detail="vendor not found")
    return await vendor_service.assess_vendor(db, v, payload)
