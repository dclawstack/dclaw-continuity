from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CommunicationTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plan_id: uuid.UUID
    channel: str
    trigger: str
    subject: str
    body: str
    created_at: datetime


class CommunicationPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    function_id: uuid.UUID
    audience: str
    scenario: str
    tone: str
    channels: list[str]
    escalation_path: list[str]
    notes: str
    templates: list[CommunicationTemplateRead]
    created_at: datetime
    updated_at: datetime


class CommunicationDraftRequest(BaseModel):
    function_id: uuid.UUID
    audience: str = Field(min_length=1, max_length=255)
    scenario: str = Field(min_length=1, max_length=255)
    additional_context: str = ""


class CommunicationPlanCreate(BaseModel):
    function_id: uuid.UUID
    audience: str = Field(min_length=1, max_length=255)
    scenario: str = Field(min_length=1, max_length=255)
    tone: str = "formal"
    channels: list[str] = Field(default_factory=list)
    escalation_path: list[str] = Field(default_factory=list)
    notes: str = ""


class CommunicationPlanUpdate(BaseModel):
    audience: Optional[str] = None
    scenario: Optional[str] = None
    tone: Optional[str] = None
    channels: Optional[list[str]] = None
    escalation_path: Optional[list[str]] = None
    notes: Optional[str] = None
