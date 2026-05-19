"""Supplier + SupplyChainAssessment: AI mapping of upstream disruption risk."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    pass


class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    region: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    criticality: Mapped[str] = mapped_column(
        String(32), default="medium", nullable=False
    )
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    # JSON list of alternative supplier names (free-form for now).
    alternatives: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # Latest disruption-probability percentage (0-100); 0 = unassessed.
    disruption_probability: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    assessments: Mapped[list["SupplyChainAssessment"]] = relationship(
        back_populates="supplier", cascade="all, delete-orphan"
    )


class SupplyChainAssessment(Base, TimestampMixin):
    __tablename__ = "supply_chain_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    disruption_probability: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    risk_drivers: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    suggested_alternatives: Mapped[list] = mapped_column(
        JSONB, default=list, nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    supplier: Mapped["Supplier"] = relationship(back_populates="assessments")
