from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.copilot import (
    CopilotChatRequest,
    CopilotChatResponse,
    CopilotMessageRead,
)
from app.services import copilot_service

router = APIRouter()


@router.post("/chat", response_model=CopilotChatResponse)
async def chat(
    payload: CopilotChatRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    return await copilot_service.chat(db, user.sub, payload)


@router.get("/conversations/{conversation_id}", response_model=list[CopilotMessageRead])
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await copilot_service.get_conversation(db, conversation_id)
