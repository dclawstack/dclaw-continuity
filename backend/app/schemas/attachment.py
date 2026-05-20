from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class AttachmentRead(BaseModel):
    id: uuid.UUID
    key: str
    filename: str
    content_type: str
    size: int
    uploaded_at: datetime
    uploaded_by: str


class AttachmentUrl(BaseModel):
    url: str
    expires_in: int
