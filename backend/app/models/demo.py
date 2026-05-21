"""DemoSeed: tracks every entity created by a demo seed so 'clear' can wipe
exactly what was seeded without touching real workspaces.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.user import User


class DemoSeed(Base, TimestampMixin):
    __tablename__ = "demo_seeds"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    # IDs we created during seeding. Keys: functions, vendors.
    # Everything else (bcps, impact, recovery, exercises, comms, work-area,
    # vendor_assessments, etc.) cascades from these via existing FK
    # ondelete=CASCADE constraints.
    created_ids: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    user: Mapped[User] = relationship()
