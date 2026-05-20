"""Dependency: directional link between functions / systems / vendors."""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.business_function import BusinessFunction


class DependencyType(enum.StrEnum):
    SYSTEM = "system"
    PROCESS = "process"
    PEOPLE = "people"
    VENDOR = "vendor"
    FACILITY = "facility"
    DATA = "data"


class Dependency(Base, TimestampMixin):
    __tablename__ = "dependencies"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=new_uuid)
    function_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("business_functions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Optional link to another function if this dep is internal.
    depends_on_function_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("business_functions.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[DependencyType] = mapped_column(
        Enum(
            DependencyType,
            name="dependency_type",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    criticality: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)

    function: Mapped[BusinessFunction] = relationship(
        back_populates="dependencies", foreign_keys=[function_id]
    )
