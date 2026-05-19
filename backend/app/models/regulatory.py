"""RegulatoryReport: AI-generated continuity compliance reports."""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    pass


class ReportStatus(str, enum.Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    SUBMITTED = "submitted"
    REJECTED = "rejected"


class RegulatoryReport(Base, TimestampMixin):
    __tablename__ = "regulatory_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=new_uuid
    )

    framework: Mapped[str] = mapped_column(String(64), nullable=False)
    period: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(
            ReportStatus,
            name="report_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ReportStatus.DRAFT,
        nullable=False,
    )

    # AI-generated content sections: {"executive_summary": "...", "sections": [...], "metrics": {...}}
    content: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Validation results: {"complete": bool, "issues": [...], "score": int}
    validation: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    submission_reference: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
