"""CommunicationPlan + CommunicationTemplate: stakeholder-specific crisis comms."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.business_function import BusinessFunction


class CommunicationPlan(Base, TimestampMixin):
    __tablename__ = "communication_plans"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    function_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("business_functions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    audience: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario: Mapped[str] = mapped_column(String(255), nullable=False)
    tone: Mapped[str] = mapped_column(String(64), default="formal", nullable=False)
    channels: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    escalation_path: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    templates: Mapped[list[CommunicationTemplate]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )
    function: Mapped[BusinessFunction] = relationship()


class CommunicationTemplate(Base, TimestampMixin):
    __tablename__ = "communication_templates"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    plan_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("communication_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    channel: Mapped[str] = mapped_column(String(64), nullable=False)
    trigger: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    subject: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    plan: Mapped[CommunicationPlan] = relationship(back_populates="templates")
