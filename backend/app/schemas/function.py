from __future__ import annotations

import uuid
from datetime import datetime

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
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    owner: str | None = None
    criticality: Criticality | None = None
    rto_minutes: int | None = None
    rpo_minutes: int | None = None


class FunctionRead(FunctionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
