from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.dependency import DependencyType


class DependencyBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: DependencyType
    description: str = ""
    criticality: str = "medium"
    depends_on_function_id: uuid.UUID | None = None


class DependencyCreate(DependencyBase):
    function_id: uuid.UUID


class DependencyRead(DependencyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    function_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
