from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.supply_chain import (
    SupplierCreate,
    SupplierRead,
    SupplierUpdate,
    SupplyChainAssessRequest,
    SupplyChainAssessmentRead,
)
from app.services import supply_chain_service

router = APIRouter()


@router.get("/", response_model=list[SupplierRead])
async def list_suppliers(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await supply_chain_service.list_suppliers(db)


@router.post("/", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    payload: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await supply_chain_service.create_supplier(db, payload)


@router.get("/{supplier_id}", response_model=SupplierRead)
async def get_supplier(
    supplier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    s = await supply_chain_service.get_supplier(db, supplier_id)
    if s is None:
        raise HTTPException(status_code=404, detail="supplier not found")
    return s


@router.patch("/{supplier_id}", response_model=SupplierRead)
async def update_supplier(
    supplier_id: uuid.UUID,
    payload: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    s = await supply_chain_service.get_supplier(db, supplier_id)
    if s is None:
        raise HTTPException(status_code=404, detail="supplier not found")
    return await supply_chain_service.update_supplier(db, s, payload)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    s = await supply_chain_service.get_supplier(db, supplier_id)
    if s is None:
        raise HTTPException(status_code=404, detail="supplier not found")
    await supply_chain_service.delete_supplier(db, s)


@router.get(
    "/{supplier_id}/assessments",
    response_model=list[SupplyChainAssessmentRead],
)
async def list_supplier_assessments(
    supplier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await supply_chain_service.list_assessments(db, supplier_id=supplier_id)


@router.post(
    "/assess",
    response_model=SupplyChainAssessmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def assess(
    payload: SupplyChainAssessRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    s = await supply_chain_service.get_supplier(db, payload.supplier_id)
    if s is None:
        raise HTTPException(status_code=404, detail="supplier not found")
    return await supply_chain_service.assess_supplier(db, s, payload)
