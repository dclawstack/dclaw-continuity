"""BusinessFunction: a critical business capability that needs continuity planning."""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.bcp import BCP
    from app.models.dependency import Dependency
    from app.models.impact_assessment import ImpactAssessment
    from app.models.recovery_strategy import RecoveryStrategy


class Criticality(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BusinessFunction(Base, TimestampMixin):
    __tablename__ = "business_functions"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    owner: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    criticality: Mapped[Criticality] = mapped_column(
        Enum(
            Criticality,
            name="criticality",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=Criticality.MEDIUM,
        nullable=False,
    )

    # Recovery objectives (minutes). 0 = unset.
    rto_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rpo_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    bcps: Mapped[list["BCP"]] = relationship(
        back_populates="function", cascade="all, delete-orphan"
    )
    dependencies: Mapped[list["Dependency"]] = relationship(
        back_populates="function",
        cascade="all, delete-orphan",
        foreign_keys="Dependency.function_id",
    )
    impact_assessments: Mapped[list["ImpactAssessment"]] = relationship(
        back_populates="function", cascade="all, delete-orphan"
    )
    recovery_strategies: Mapped[list["RecoveryStrategy"]] = relationship(
        back_populates="function", cascade="all, delete-orphan"
    )
