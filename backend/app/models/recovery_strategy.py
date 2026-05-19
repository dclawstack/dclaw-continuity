"""RecoveryStrategy: AI-recommended approach to restore a function after disruption."""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.business_function import BusinessFunction


class StrategyKind(str, enum.Enum):
    HOT_SITE = "hot_site"
    WARM_SITE = "warm_site"
    COLD_SITE = "cold_site"
    REMOTE_WORK = "remote_work"
    THIRD_PARTY = "third_party"
    MANUAL_WORKAROUND = "manual_workaround"
    REDUNDANCY = "redundancy"
    OTHER = "other"


class RecoveryStrategy(Base, TimestampMixin):
    __tablename__ = "recovery_strategies"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    function_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("business_functions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[StrategyKind] = mapped_column(
        Enum(
            StrategyKind,
            name="strategy_kind",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    estimated_cost_usd: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rto_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rpo_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_recommended: Mapped[bool] = mapped_column(default=False, nullable=False)

    details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    function: Mapped["BusinessFunction"] = relationship(
        back_populates="recovery_strategies"
    )
