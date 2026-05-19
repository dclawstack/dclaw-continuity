from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CopilotSuggestion(BaseModel):
    action: str
    label: str
    payload: dict[str, Any] = Field(default_factory=dict)


class CopilotChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: Optional[uuid.UUID] = None
    context: dict[str, Any] = Field(default_factory=dict)


class CopilotChatResponse(BaseModel):
    conversation_id: uuid.UUID
    reply: str
    suggestions: list[CopilotSuggestion] = Field(default_factory=list)


class CopilotMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    suggestions: list[Any]
    created_at: datetime
