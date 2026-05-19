from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.bcp import BCPStatus


class BCPBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    summary: str = ""
    status: BCPStatus = BCPStatus.DRAFT
    content: dict[str, Any] = Field(default_factory=dict)
    gaps: list[Any] = Field(default_factory=list)


class BCPCreate(BCPBase):
    function_id: uuid.UUID


class BCPUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    summary: Optional[str] = None
    status: Optional[BCPStatus] = None
    content: Optional[dict[str, Any]] = None
    gaps: Optional[list[Any]] = None


class BCPRead(BCPBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    function_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class BCPGenerateRequest(BaseModel):
    """Ask the AI Copilot to draft a BCP for a function."""

    function_id: uuid.UUID
    additional_context: str = ""


class BCPGapAnalysisRequest(BaseModel):
    bcp_id: uuid.UUID
