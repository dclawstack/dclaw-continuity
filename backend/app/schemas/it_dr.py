from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

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
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    owner: Optional[str] = None
    tier: Optional[SystemTier] = None
    rto_minutes: Optional[int] = None
    rpo_minutes: Optional[int] = None
    backup_strategy: Optional[str] = None


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
    last_tested_at: Optional[datetime]
    last_test_passed: Optional[bool]
    created_at: datetime
    updated_at: datetime


class ITDRGenerateRequest(BaseModel):
    system_id: uuid.UUID
    additional_context: str = ""


class ITDRTestRecord(BaseModel):
    passed: bool
    notes: str = ""
