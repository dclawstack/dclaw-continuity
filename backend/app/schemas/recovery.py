from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.recovery_strategy import StrategyKind


class RecoveryStrategyBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    kind: StrategyKind
    description: str = ""
    estimated_cost_usd: int = 0
    rto_minutes: int = 0
    rpo_minutes: int = 0
    is_recommended: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class RecoveryStrategyCreate(RecoveryStrategyBase):
    function_id: uuid.UUID


class RecoveryStrategyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    kind: StrategyKind | None = None
    description: str | None = None
    estimated_cost_usd: int | None = None
    rto_minutes: int | None = None
    rpo_minutes: int | None = None
    is_recommended: bool | None = None
    details: dict[str, Any] | None = None


class RecoveryStrategyRead(RecoveryStrategyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    function_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RecoveryRecommendRequest(BaseModel):
    function_id: uuid.UUID
    budget_usd: int | None = None
    additional_context: str = ""
