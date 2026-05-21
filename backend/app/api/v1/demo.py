"""Public demo lifecycle — no auth, on purpose. Anyone can spin up a sandbox
account and tear it down again."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.demo import DemoClearRequest, DemoSeedResponse
from app.services import demo_service

router = APIRouter()


@router.post(
    "/seed",
    response_model=DemoSeedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def seed(db: AsyncSession = Depends(get_db)):
    """Create a brand-new demo user with pre-populated continuity content."""
    return await demo_service.seed_demo(db)


@router.post("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear(
    payload: DemoClearRequest,
    db: AsyncSession = Depends(get_db),
):
    """Tear down a previously-seeded demo. Idempotent — clearing twice is fine."""
    await demo_service.clear_demo(db, payload.user_id)
