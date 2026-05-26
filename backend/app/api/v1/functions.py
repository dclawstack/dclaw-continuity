from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.function import FunctionCreate, FunctionRead, FunctionUpdate
from app.services import function_service

router = APIRouter()


@router.get("", response_model=list[FunctionRead])
async def list_functions(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await function_service.list_functions(db)


@router.post("", response_model=FunctionRead, status_code=status.HTTP_201_CREATED)
async def create_function(
    payload: FunctionCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await function_service.create_function(db, payload)


@router.get("/{function_id}", response_model=FunctionRead)
async def get_function(
    function_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    fn = await function_service.get_function(db, function_id)
    if fn is None:
        raise HTTPException(status_code=404, detail="function not found")
    return fn


@router.patch("/{function_id}", response_model=FunctionRead)
async def update_function(
    function_id: uuid.UUID,
    payload: FunctionUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    fn = await function_service.get_function(db, function_id)
    if fn is None:
        raise HTTPException(status_code=404, detail="function not found")
    return await function_service.update_function(db, fn, payload)


@router.delete("/{function_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_function(
    function_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    fn = await function_service.get_function(db, function_id)
    if fn is None:
        raise HTTPException(status_code=404, detail="function not found")
    await function_service.delete_function(db, fn)
