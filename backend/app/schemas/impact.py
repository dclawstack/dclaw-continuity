from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ImpactAssessmentBase(BaseModel):
    scenario: str = Field(min_length=1, max_length=255)
    description: str = ""
    revenue_impact_usd: int = 0
    operational_impact_score: int = Field(default=0, ge=0, le=10)
    reputation_impact_score: int = Field(default=0, ge=0, le=10)
    details: dict[str, Any] = Field(default_factory=dict)


class ImpactAssessmentCreate(ImpactAssessmentBase):
    function_id: uuid.UUID


class ImpactAssessmentRead(ImpactAssessmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    function_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ImpactModelRequest(BaseModel):
    function_id: uuid.UUID
    scenario: str = Field(min_length=1, max_length=255)
    additional_context: str = ""
