from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business_function import BusinessFunction
from app.schemas.function import FunctionCreate, FunctionUpdate


async def list_functions(db: AsyncSession) -> list[BusinessFunction]:
    result = await db.execute(select(BusinessFunction).order_by(BusinessFunction.created_at.desc()))
    return list(result.scalars().all())


async def get_function(db: AsyncSession, function_id: uuid.UUID) -> Optional[BusinessFunction]:
    result = await db.execute(
        select(BusinessFunction).where(BusinessFunction.id == function_id)
    )
    return result.scalar_one_or_none()


async def create_function(db: AsyncSession, payload: FunctionCreate) -> BusinessFunction:
    fn = BusinessFunction(**payload.model_dump())
    db.add(fn)
    await db.commit()
    await db.refresh(fn)
    return fn


async def update_function(
    db: AsyncSession, fn: BusinessFunction, payload: FunctionUpdate
) -> BusinessFunction:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(fn, k, v)
    await db.commit()
    await db.refresh(fn)
    return fn


async def delete_function(db: AsyncSession, fn: BusinessFunction) -> None:
    await db.delete(fn)
    await db.commit()
