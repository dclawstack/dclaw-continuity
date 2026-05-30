from __future__ import annotations

import asyncio
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
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
    # CPU-only ollama can take >60s to respond; the Next.js dev proxy drops
    # idle connections at ~30s. Drip whitespace into the response while the
    # work is in flight so the proxy keeps the socket open. JSON.parse on
    # the client tolerates leading whitespace.
    async def gen():
        task = asyncio.create_task(copilot_service.chat(db, user.sub, payload))
        while True:
            try:
                result = await asyncio.wait_for(asyncio.shield(task), timeout=10)
                break
            except TimeoutError:
                yield b" "
        yield result.model_dump_json().encode()

    return StreamingResponse(gen(), media_type="application/json")


@router.get("/conversations/{conversation_id}", response_model=list[CopilotMessageRead])
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await copilot_service.get_conversation(db, conversation_id)
