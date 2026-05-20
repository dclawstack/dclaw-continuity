from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.work_area import SiteKind


class WorkAreaSiteBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    kind: SiteKind
    location: str = ""
    capacity_seats: int = 0
    has_remote_access: bool = False
    notes: str = ""


class WorkAreaSiteCreate(WorkAreaSiteBase):
    pass


class WorkAreaSiteUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    kind: SiteKind | None = None
    location: str | None = None
    capacity_seats: int | None = None
    has_remote_access: bool | None = None
    notes: str | None = None


class WorkAreaSiteRead(WorkAreaSiteBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class WorkAreaPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    function_id: uuid.UUID
    headcount_required: int
    summary: str
    details: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class WorkAreaPlanRequest(BaseModel):
    function_id: uuid.UUID
    headcount_required: int = Field(default=0, ge=0)
    additional_context: str = ""
