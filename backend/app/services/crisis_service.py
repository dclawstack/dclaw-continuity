from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bcp import BCP, BCPStatus
from app.models.crisis import ActivationStatus, CrisisActivation
from app.schemas.crisis import CrisisActivateRequest, CrisisStatusUpdate


async def list_activations(
    db: AsyncSession, *, only_open: bool = False
) -> list[CrisisActivation]:
    stmt = select(CrisisActivation).order_by(CrisisActivation.activated_at.desc())
    if only_open:
        stmt = stmt.where(CrisisActivation.status != ActivationStatus.CLOSED)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_activation(
    db: AsyncSession, activation_id: uuid.UUID
) -> Optional[CrisisActivation]:
    result = await db.execute(
        select(CrisisActivation).where(CrisisActivation.id == activation_id)
    )
    return result.scalar_one_or_none()


async def activate(
    db: AsyncSession, payload: CrisisActivateRequest
) -> CrisisActivation:
    """Resolve a BCP and create a new activation record.

    Prefers an explicit bcp_id; if only function_id is given, picks the most
    recently-approved BCP, else the most recent draft.
    """

    bcp = await _resolve_bcp(db, payload)
    if bcp is None:
        raise ValueError(
            "no BCP available — provide bcp_id or function_id with an existing BCP"
        )

    now = datetime.now(timezone.utc)
    activation = CrisisActivation(
        bcp_id=bcp.id,
        external_crisis_id=payload.external_crisis_id,
        source=payload.source,
        title=payload.title,
        description=payload.description,
        status=ActivationStatus.ACTIVATED,
        activated_at=now,
        timeline=[
            {
                "at": now.isoformat(),
                "status": ActivationStatus.ACTIVATED.value,
                "note": f"activated from source={payload.source}",
            }
        ],
    )
    db.add(activation)
    await db.commit()
    await db.refresh(activation)
    return activation


async def update_status(
    db: AsyncSession,
    activation: CrisisActivation,
    update: CrisisStatusUpdate,
) -> CrisisActivation:
    now = datetime.now(timezone.utc)
    activation.status = update.status
    activation.timeline = activation.timeline + [
        {
            "at": now.isoformat(),
            "status": update.status.value,
            "note": update.note,
        }
    ]
    if update.status == ActivationStatus.CLOSED:
        activation.closed_at = now
    await db.commit()
    await db.refresh(activation)
    return activation


async def _resolve_bcp(
    db: AsyncSession, payload: CrisisActivateRequest
) -> Optional[BCP]:
    if payload.bcp_id is not None:
        result = await db.execute(select(BCP).where(BCP.id == payload.bcp_id))
        return result.scalar_one_or_none()

    if payload.function_id is None:
        return None

    # Prefer approved, else most recent.
    approved = (
        await db.execute(
            select(BCP)
            .where(BCP.function_id == payload.function_id)
            .where(BCP.status == BCPStatus.APPROVED)
            .order_by(BCP.updated_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if approved is not None:
        return approved

    return (
        await db.execute(
            select(BCP)
            .where(BCP.function_id == payload.function_id)
            .order_by(BCP.updated_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
