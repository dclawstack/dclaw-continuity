from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class SupplierBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = ""
    region: str = ""
    criticality: str = "medium"
    description: str = ""
    alternatives: list[str] = Field(default_factory=list)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    category: Optional[str] = None
    region: Optional[str] = None
    criticality: Optional[str] = None
    description: Optional[str] = None
    alternatives: Optional[list[str]] = None


class SupplierRead(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    disruption_probability: int
    created_at: datetime
    updated_at: datetime


class SupplyChainAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    supplier_id: uuid.UUID
    disruption_probability: int
    risk_drivers: list[Any]
    suggested_alternatives: list[Any]
    summary: str
    details: dict[str, Any]
    created_at: datetime


class SupplyChainAssessRequest(BaseModel):
    supplier_id: uuid.UUID
    additional_context: str = ""
