from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dependency import Dependency
from app.schemas.dependency import DependencyCreate


async def list_dependencies(
    db: AsyncSession, function_id: Optional[uuid.UUID] = None
) -> list[Dependency]:
    stmt = select(Dependency).order_by(Dependency.created_at.desc())
    if function_id is not None:
        stmt = stmt.where(Dependency.function_id == function_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_dependency(db: AsyncSession, dep_id: uuid.UUID) -> Optional[Dependency]:
    result = await db.execute(select(Dependency).where(Dependency.id == dep_id))
    return result.scalar_one_or_none()


async def create_dependency(db: AsyncSession, payload: DependencyCreate) -> Dependency:
    dep = Dependency(**payload.model_dump())
    db.add(dep)
    await db.commit()
    await db.refresh(dep)
    return dep


async def delete_dependency(db: AsyncSession, dep: Dependency) -> None:
    await db.delete(dep)
    await db.commit()
