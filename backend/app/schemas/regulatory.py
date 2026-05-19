from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.regulatory import ReportStatus


class RegulatoryReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    framework: str
    period: str
    title: str
    status: ReportStatus
    content: dict[str, Any]
    validation: dict[str, Any]
    submission_reference: str
    notes: str
    created_at: datetime
    updated_at: datetime


class RegulatoryReportGenerateRequest(BaseModel):
    framework: str = Field(min_length=1, max_length=64)
    period: str = Field(min_length=1, max_length=64)
    additional_context: str = ""


class RegulatoryReportSubmitRequest(BaseModel):
    submission_reference: str = Field(min_length=1, max_length=255)


class RegulatoryReportUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[ReportStatus] = None
    notes: Optional[str] = None
