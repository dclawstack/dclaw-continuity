"""ImpactAssessment: AI-modeled impact of a disruption scenario on a function."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.business_function import BusinessFunction


class ImpactAssessment(Base, TimestampMixin):
    __tablename__ = "impact_assessments"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    function_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("business_functions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    scenario: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # Quantitative impact (USD where applicable).
    revenue_impact_usd: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    operational_impact_score: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # 0-10
    reputation_impact_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-10

    # AI breakdown: {"timeline": {...}, "stakeholders": [...], "narrative": "..."}
    details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    function: Mapped[BusinessFunction] = relationship(back_populates="impact_assessments")
