"""Exercise: a BCP test/drill against a generated scenario."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.bcp import BCP


class ExerciseStatus(enum.StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Exercise(Base, TimestampMixin):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    bcp_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("bcps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario: Mapped[str] = mapped_column(Text, nullable=False)
    objectives: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[ExerciseStatus] = mapped_column(
        Enum(
            ExerciseStatus,
            name="exercise_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ExerciseStatus.PLANNED,
        nullable=False,
    )

    # Evaluation (populated when status moves to COMPLETED)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    evaluation: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    bcp: Mapped[BCP] = relationship()
