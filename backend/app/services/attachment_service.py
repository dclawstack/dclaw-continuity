"""Attach files to BCPs, backed by S3-compatible object storage."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.storage import ObjectStorage, StorageUnavailable, get_storage
from app.models.bcp import BCP


async def upload_attachment(
    db: AsyncSession,
    bcp: BCP,
    *,
    filename: str,
    content_type: str,
    data: bytes,
    uploaded_by: str,
    storage: Optional[ObjectStorage] = None,
) -> dict:
    storage = storage or get_storage()
    if storage is None:
        raise StorageUnavailable("object storage is not configured")

    if len(data) > settings.s3_max_upload_bytes:
        raise ValueError(
            f"file too large: {len(data)} bytes > "
            f"{settings.s3_max_upload_bytes} byte limit"
        )

    attachment_id = uuid.uuid4()
    key = f"bcps/{bcp.id}/{attachment_id}"
    await storage.put_object(key, data, content_type or "application/octet-stream")

    record = {
        "id": str(attachment_id),
        "key": key,
        "filename": filename,
        "content_type": content_type or "application/octet-stream",
        "size": len(data),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "uploaded_by": uploaded_by,
    }
    bcp.attachments = (bcp.attachments or []) + [record]
    await db.commit()
    await db.refresh(bcp)
    return record


async def delete_attachment(
    db: AsyncSession,
    bcp: BCP,
    attachment_id: str,
    *,
    storage: Optional[ObjectStorage] = None,
) -> bool:
    storage = storage or get_storage()
    if storage is None:
        raise StorageUnavailable("object storage is not configured")

    keep: list = []
    target: Optional[dict] = None
    for att in bcp.attachments or []:
        if att.get("id") == attachment_id:
            target = att
        else:
            keep.append(att)
    if target is None:
        return False

    await storage.delete_object(target["key"])
    bcp.attachments = keep
    await db.commit()
    await db.refresh(bcp)
    return True


async def presigned_url(
    bcp: BCP,
    attachment_id: str,
    *,
    storage: Optional[ObjectStorage] = None,
) -> tuple[str, int]:
    storage = storage or get_storage()
    if storage is None:
        raise StorageUnavailable("object storage is not configured")

    for att in bcp.attachments or []:
        if att.get("id") == attachment_id:
            url = await storage.presigned_get_url(att["key"])
            return url, settings.s3_presigned_url_ttl_seconds
    raise FileNotFoundError(attachment_id)
