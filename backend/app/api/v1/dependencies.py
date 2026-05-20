from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.dependency import DependencyCreate, DependencyRead
from app.services import dependency_service

router = APIRouter()


@router.get("/", response_model=list[DependencyRead])
async def list_deps(
    function_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await dependency_service.list_dependencies(db, function_id=function_id)


@router.post("/", response_model=DependencyRead, status_code=status.HTTP_201_CREATED)
async def create_dep(
    payload: DependencyCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await dependency_service.create_dependency(db, payload)


@router.delete("/{dep_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dep(
    dep_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    dep = await dependency_service.get_dependency(db, dep_id)
    if dep is None:
        raise HTTPException(status_code=404, detail="dependency not found")
    await dependency_service.delete_dependency(db, dep)
