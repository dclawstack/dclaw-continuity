from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class VendorBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    contact: str = ""
    services_provided: str = ""
    tier: str = "tier-2"


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    contact: Optional[str] = None
    services_provided: Optional[str] = None
    tier: Optional[str] = None


class VendorRead(VendorBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    readiness_score: int
    created_at: datetime
    updated_at: datetime


class VendorAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    readiness_score: int
    risk_level: str
    summary: str
    details: dict[str, Any]
    created_at: datetime


class VendorAssessRequest(BaseModel):
    vendor_id: uuid.UUID
    additional_context: str = ""
