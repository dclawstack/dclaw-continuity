"""CrisisActivation: a BCP activation triggered by (or recorded against) a crisis event.

The DClaw Crisis app POSTs to /api/v1/crisis/activate when a real crisis is
declared. This module records the activation and links to the BCP that was
auto-activated, plus tracks recovery status updates.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.bcp import BCP


class ActivationStatus(str, enum.Enum):
    ACTIVATED = "activated"
    RECOVERING = "recovering"
    STABILIZED = "stabilized"
    CLOSED = "closed"


class CrisisActivation(Base, TimestampMixin):
    __tablename__ = "crisis_activations"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    bcp_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("bcps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # External identifier from the source app (e.g. DClaw Crisis incident ID).
    external_crisis_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    source: Mapped[str] = mapped_column(String(64), default="manual", nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    status: Mapped[ActivationStatus] = mapped_column(
        Enum(
            ActivationStatus,
            name="activation_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ActivationStatus.ACTIVATED,
        nullable=False,
    )

    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Append-only log of status updates: [{"at": iso, "status": str, "note": str}]
    timeline: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    bcp: Mapped["BCP"] = relationship()
