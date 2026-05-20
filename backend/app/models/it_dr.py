"""ITSystem + ITDRPlan: technical disaster recovery for specific systems."""

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
    pass


class SystemTier(enum.StrEnum):
    TIER_0 = "tier-0"
    TIER_1 = "tier-1"
    TIER_2 = "tier-2"
    TIER_3 = "tier-3"


class ITSystem(Base, TimestampMixin):
    __tablename__ = "it_systems"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    owner: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    tier: Mapped[SystemTier] = mapped_column(
        Enum(
            SystemTier,
            name="system_tier",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=SystemTier.TIER_2,
        nullable=False,
    )
    rto_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rpo_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    backup_strategy: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    plans: Mapped[list[ITDRPlan]] = relationship(
        back_populates="system", cascade="all, delete-orphan"
    )


class ITDRPlan(Base, TimestampMixin):
    __tablename__ = "it_dr_plans"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    system_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("it_systems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # Generated DR procedure body (steps, prerequisites, failback, validation)
    procedure: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    # AI-suggested automated tests + cadence: [{"name":..., "schedule":..., "validates":...}]
    test_plan: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_test_passed: Mapped[bool | None] = mapped_column(nullable=True)

    system: Mapped[ITSystem] = relationship(back_populates="plans")
