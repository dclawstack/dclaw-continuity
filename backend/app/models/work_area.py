"""WorkAreaSite + WorkAreaPlan: alternate work locations for disrupted functions."""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.business_function import BusinessFunction


class SiteKind(enum.StrEnum):
    ALTERNATE_OFFICE = "alternate_office"
    REMOTE = "remote"
    HOT_SITE = "hot_site"
    WARM_SITE = "warm_site"
    COLD_SITE = "cold_site"
    COWORKING = "coworking"
    OTHER = "other"


class WorkAreaSite(Base, TimestampMixin):
    __tablename__ = "work_area_sites"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    kind: Mapped[SiteKind] = mapped_column(
        Enum(
            SiteKind,
            name="site_kind",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    location: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    capacity_seats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    has_remote_access: Mapped[bool] = mapped_column(default=False, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)


class WorkAreaPlan(Base, TimestampMixin):
    """AI-recommended assignment of functions to sites."""

    __tablename__ = "work_area_plans"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    function_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("business_functions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    headcount_required: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    # AI plan body: {"assignments": [{"site_id": "...", "seats": N, "rationale": "..."}],
    #                "test_plan": "...", "shortfall_seats": N}
    details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    function: Mapped[BusinessFunction] = relationship()
