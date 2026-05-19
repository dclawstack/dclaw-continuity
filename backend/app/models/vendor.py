"""Vendor + VendorAssessment: continuity readiness of external suppliers."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    pass


class Vendor(Base, TimestampMixin):
    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    contact: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    services_provided: Mapped[str] = mapped_column(Text, default="", nullable=False)
    tier: Mapped[str] = mapped_column(String(32), default="tier-2", nullable=False)

    # Latest readiness score (0-100); 0 = unknown.
    readiness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    assessments: Mapped[list["VendorAssessment"]] = relationship(
        back_populates="vendor", cascade="all, delete-orphan"
    )


class VendorAssessment(Base, TimestampMixin):
    __tablename__ = "vendor_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    readiness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    vendor: Mapped["Vendor"] = relationship(back_populates="assessments")
