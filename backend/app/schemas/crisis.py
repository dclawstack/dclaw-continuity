from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.crisis import ActivationStatus


class CrisisActivationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    bcp_id: uuid.UUID
    external_crisis_id: Optional[str]
    source: str
    title: str
    description: str
    status: ActivationStatus
    activated_at: datetime
    closed_at: Optional[datetime]
    timeline: list[Any]
    created_at: datetime
    updated_at: datetime


class CrisisActivateRequest(BaseModel):
    """Payload from the upstream Crisis app (or manual activation)."""

    bcp_id: Optional[uuid.UUID] = None
    function_id: Optional[uuid.UUID] = None
    external_crisis_id: Optional[str] = None
    source: str = "manual"
    title: str = Field(min_length=1, max_length=255)
    description: str = ""


class CrisisStatusUpdate(BaseModel):
    status: ActivationStatus
    note: str = ""
