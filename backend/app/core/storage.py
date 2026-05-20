"""S3-compatible object storage (MinIO locally, AWS S3 in prod).

Routes that need storage call `get_storage()` and check for `None`. If
S3 is unavailable, they should return 503 — *not* swallow the failure
silently, because attachments are user-visible data.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aioboto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


class StorageUnavailable(RuntimeError):
    pass


class ObjectStorage:
    """Thin async wrapper around aioboto3. One short-lived client per call —
    aioboto3 sessions aren't thread-safe and cheap to reopen."""

    def __init__(self) -> None:
        self.endpoint_url = settings.s3_endpoint_url
        self.region = settings.s3_region
        self.access_key = settings.s3_access_key_id
        self.secret_key = settings.s3_secret_access_key
        self.bucket = settings.s3_bucket
        self.force_path_style = settings.s3_force_path_style
        self._session = aioboto3.Session()

    @asynccontextmanager
    async def _client(self) -> AsyncIterator:
        config = Config(
            signature_version="s3v4",
            s3={"addressing_style": "path" if self.force_path_style else "auto"},
        )
        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url or None,
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=config,
        ) as client:
            yield client

    async def ensure_bucket(self) -> None:
        async with self._client() as client:
            try:
                await client.head_bucket(Bucket=self.bucket)
            except ClientError as exc:
                code = exc.response.get("Error", {}).get("Code", "")
                if code in {"404", "NoSuchBucket", "NotFound"}:
                    await client.create_bucket(Bucket=self.bucket)
                else:
                    raise StorageUnavailable(f"head_bucket: {exc}") from exc
            except BotoCoreError as exc:
                raise StorageUnavailable(f"head_bucket: {exc}") from exc

    async def put_object(self, key: str, data: bytes, content_type: str) -> None:
        async with self._client() as client:
            try:
                await client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=data,
                    ContentType=content_type,
                )
            except (BotoCoreError, ClientError) as exc:
                raise StorageUnavailable(f"put_object: {exc}") from exc

    async def delete_object(self, key: str) -> None:
        async with self._client() as client:
            try:
                await client.delete_object(Bucket=self.bucket, Key=key)
            except (BotoCoreError, ClientError) as exc:
                raise StorageUnavailable(f"delete_object: {exc}") from exc

    async def presigned_get_url(self, key: str, expires_in: int | None = None) -> str:
        ttl = expires_in or settings.s3_presigned_url_ttl_seconds
        async with self._client() as client:
            try:
                return await client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": key},
                    ExpiresIn=ttl,
                )
            except (BotoCoreError, ClientError) as exc:
                raise StorageUnavailable(f"presigned_get_url: {exc}") from exc


_singleton: ObjectStorage | None = None


def get_storage() -> ObjectStorage | None:
    """Return the shared storage client, or None if disabled.

    Storage is considered disabled when both `s3_endpoint_url` and
    `s3_access_key_id` are empty — i.e. nothing meaningful to point at.
    Otherwise we always return a client and let aioboto3 / the endpoint
    handle credential resolution (this lets tests use moto, which only
    intercepts the AWS-default endpoint and so needs an empty endpoint_url).
    """
    global _singleton
    if not settings.s3_endpoint_url and not settings.s3_access_key_id:
        return None
    if _singleton is None:
        _singleton = ObjectStorage()
    return _singleton
