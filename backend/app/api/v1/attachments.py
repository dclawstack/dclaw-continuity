from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.core.storage import StorageUnavailable
from app.schemas.attachment import AttachmentRead, AttachmentUrl
from app.services import attachment_service, bcp_service

router = APIRouter()


@router.get("/{bcp_id}/attachments", response_model=list[AttachmentRead])
async def list_attachments(
    bcp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    bcp = await bcp_service.get_bcp(db, bcp_id)
    if bcp is None:
        raise HTTPException(status_code=404, detail="bcp not found")
    return bcp.attachments or []


@router.post(
    "/{bcp_id}/attachments",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    bcp_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    bcp = await bcp_service.get_bcp(db, bcp_id)
    if bcp is None:
        raise HTTPException(status_code=404, detail="bcp not found")

    data = await file.read()
    try:
        record = await attachment_service.upload_attachment(
            db,
            bcp,
            filename=file.filename or "untitled",
            content_type=file.content_type or "application/octet-stream",
            data=data,
            uploaded_by=current.sub,
        )
    except StorageUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc))
    return record


@router.get(
    "/{bcp_id}/attachments/{attachment_id}/url",
    response_model=AttachmentUrl,
)
async def get_attachment_url(
    bcp_id: uuid.UUID,
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    bcp = await bcp_service.get_bcp(db, bcp_id)
    if bcp is None:
        raise HTTPException(status_code=404, detail="bcp not found")
    try:
        url, ttl = await attachment_service.presigned_url(bcp, attachment_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="attachment not found")
    except StorageUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )
    return AttachmentUrl(url=url, expires_in=ttl)


@router.delete(
    "/{bcp_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_attachment(
    bcp_id: uuid.UUID,
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    bcp = await bcp_service.get_bcp(db, bcp_id)
    if bcp is None:
        raise HTTPException(status_code=404, detail="bcp not found")
    try:
        removed = await attachment_service.delete_attachment(
            db, bcp, attachment_id
        )
    except StorageUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )
    if not removed:
        raise HTTPException(status_code=404, detail="attachment not found")
