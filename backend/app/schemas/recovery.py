from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

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
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    kind: Optional[StrategyKind] = None
    description: Optional[str] = None
    estimated_cost_usd: Optional[int] = None
    rto_minutes: Optional[int] = None
    rpo_minutes: Optional[int] = None
    is_recommended: Optional[bool] = None
    details: Optional[dict[str, Any]] = None


class RecoveryStrategyRead(RecoveryStrategyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    function_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RecoveryRecommendRequest(BaseModel):
    function_id: uuid.UUID
    budget_usd: Optional[int] = None
    additional_context: str = ""
