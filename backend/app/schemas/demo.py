from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr


class DemoSeedResponse(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    password: str
    access_token: str
    expires_in: int


class DemoClearRequest(BaseModel):
    user_id: uuid.UUID
