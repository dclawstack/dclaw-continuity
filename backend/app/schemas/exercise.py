from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.exercise import ExerciseStatus


class ExerciseBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    scenario: str = Field(min_length=1)
    objectives: list[str] = Field(default_factory=list)
    status: ExerciseStatus = ExerciseStatus.PLANNED


class ExerciseCreate(ExerciseBase):
    bcp_id: uuid.UUID


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    scenario: Optional[str] = None
    objectives: Optional[list[str]] = None
    status: Optional[ExerciseStatus] = None


class ExerciseRead(ExerciseBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    bcp_id: uuid.UUID
    score: int
    evaluation: dict[str, Any]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class ExerciseGenerateRequest(BaseModel):
    bcp_id: uuid.UUID
    focus: str = ""


class ExerciseRunObservation(BaseModel):
    """Operator notes captured while running the exercise."""

    observations: str
    issues_encountered: list[str] = Field(default_factory=list)
