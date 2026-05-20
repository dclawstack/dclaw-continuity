from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.it_dr import SystemTier


class ITSystemBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    owner: str = ""
    tier: SystemTier = SystemTier.TIER_2
    rto_minutes: int = 0
    rpo_minutes: int = 0
    backup_strategy: str = ""


class ITSystemCreate(ITSystemBase):
    pass


class ITSystemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    owner: str | None = None
    tier: SystemTier | None = None
    rto_minutes: int | None = None
    rpo_minutes: int | None = None
    backup_strategy: str | None = None


class ITSystemRead(ITSystemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ITDRPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    system_id: uuid.UUID
    title: str
    summary: str
    procedure: dict[str, Any]
    test_plan: list[Any]
    last_tested_at: datetime | None
    last_test_passed: bool | None
    created_at: datetime
    updated_at: datetime


class ITDRGenerateRequest(BaseModel):
    system_id: uuid.UUID
    additional_context: str = ""


class ITDRTestRecord(BaseModel):
    passed: bool
    notes: str = ""
