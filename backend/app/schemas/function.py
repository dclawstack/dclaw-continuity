from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.business_function import Criticality


class FunctionBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    owner: str = ""
    criticality: Criticality = Criticality.MEDIUM
    rto_minutes: int = 0
    rpo_minutes: int = 0


class FunctionCreate(FunctionBase):
    pass


class FunctionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    owner: Optional[str] = None
    criticality: Optional[Criticality] = None
    rto_minutes: Optional[int] = None
    rpo_minutes: Optional[int] = None


class FunctionRead(FunctionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
