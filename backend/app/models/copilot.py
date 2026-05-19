"""CopilotMessage: chat history with the AI Continuity Copilot."""

from __future__ import annotations

import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class CopilotMessage(Base, TimestampMixin):
    __tablename__ = "copilot_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False, index=True
    )
    user_sub: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    role: Mapped[str] = mapped_column(String(32), nullable=False)  # user|assistant|system
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Suggested next-actions returned alongside the assistant message.
    suggestions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
