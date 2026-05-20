"""BCP: a business continuity plan for a single business function."""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.business_function import BusinessFunction


class BCPStatus(enum.StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    RETIRED = "retired"


class BCP(Base, TimestampMixin):
    __tablename__ = "bcps"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    function_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("business_functions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[BCPStatus] = mapped_column(
        Enum(
            BCPStatus,
            name="bcp_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=BCPStatus.DRAFT,
        nullable=False,
    )

    # AI-generated plan body. Schema (rough):
    #   {"objectives": [...], "activation_triggers": [...], "roles": [...],
    #    "procedures": [{"step":..., "action":..., "owner":...}],
    #    "communication_plan": "...", "recovery_targets": {"rto":..., "rpo":...}}
    content: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Gaps identified during gap-analysis runs.
    gaps: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # File attachments uploaded by the user. Each entry is:
    #   {"id": uuid, "key": "bcps/<bcp>/<id>", "filename": str,
    #    "content_type": str, "size": int, "uploaded_at": iso, "uploaded_by": sub}
    attachments: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    function: Mapped[BusinessFunction] = relationship(back_populates="bcps")
