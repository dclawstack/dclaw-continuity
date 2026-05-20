"""BCP attachment upload/download/delete against an in-memory fake S3."""

from __future__ import annotations

import pytest
import pytest_asyncio

from app.core import storage as storage_module


class FakeObjectStorage:
    """In-memory stand-in for S3 — same surface as ObjectStorage."""

    def __init__(self) -> None:
        self.objects: dict[str, tuple[bytes, str]] = {}

    async def put_object(self, key: str, data: bytes, content_type: str) -> None:
        self.objects[key] = (data, content_type)

    async def delete_object(self, key: str) -> None:
        self.objects.pop(key, None)

    async def presigned_get_url(self, key: str, expires_in: int | None = None) -> str:
        if key not in self.objects:
            raise FileNotFoundError(key)
        return f"http://fake-s3.test/{key}?signature=fake"


@pytest_asyncio.fixture
async def fake_storage(monkeypatch):
    fake = FakeObjectStorage()
    monkeypatch.setattr(storage_module, "get_storage", lambda: fake)
    # The routes import get_storage via attachment_service.get_storage
    # so patch the bound name there too.
    from app.services import attachment_service

    monkeypatch.setattr(attachment_service, "get_storage", lambda: fake)
    yield fake


async def _create_function_and_bcp(client):
    fn = (
        await client.post(
            "/api/v1/functions/",
            json={"name": "Trading", "criticality": "critical"},
        )
    ).json()
    bcp = (
        await client.post(
            "/api/v1/bcps/",
            json={"function_id": fn["id"], "title": "Trading BCP"},
        )
    ).json()
    return bcp


@pytest.mark.asyncio
async def test_upload_list_url_delete_roundtrip(authed_client, fake_storage):
    bcp = await _create_function_and_bcp(authed_client)

    # Upload
    resp = await authed_client.post(
        f"/api/v1/bcps/{bcp['id']}/attachments",
        files={"file": ("incident.pdf", b"fake-pdf-bytes", "application/pdf")},
    )
    assert resp.status_code == 201, resp.text
    att = resp.json()
    assert att["filename"] == "incident.pdf"
    assert att["content_type"] == "application/pdf"
    assert att["size"] == len(b"fake-pdf-bytes")
    assert att["uploaded_by"] == "dev-user"

    # Object actually exists in fake storage
    assert att["key"] in fake_storage.objects
    assert fake_storage.objects[att["key"]][0] == b"fake-pdf-bytes"

    # List
    listing = await authed_client.get(f"/api/v1/bcps/{bcp['id']}/attachments")
    assert listing.status_code == 200
    rows = listing.json()
    assert len(rows) == 1
    assert rows[0]["id"] == att["id"]

    # Presigned URL
    url_resp = await authed_client.get(f"/api/v1/bcps/{bcp['id']}/attachments/{att['id']}/url")
    assert url_resp.status_code == 200
    payload = url_resp.json()
    assert payload["url"].startswith("http")
    assert payload["expires_in"] > 0

    # Delete
    deleted = await authed_client.delete(f"/api/v1/bcps/{bcp['id']}/attachments/{att['id']}")
    assert deleted.status_code == 204
    after = await authed_client.get(f"/api/v1/bcps/{bcp['id']}/attachments")
    assert after.json() == []
    assert att["key"] not in fake_storage.objects


@pytest.mark.asyncio
async def test_upload_too_large_rejected(authed_client, fake_storage, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "s3_max_upload_bytes", 16)
    bcp = await _create_function_and_bcp(authed_client)

    resp = await authed_client.post(
        f"/api/v1/bcps/{bcp['id']}/attachments",
        files={"file": ("big.bin", b"X" * 32, "application/octet-stream")},
    )
    assert resp.status_code == 413


@pytest.mark.asyncio
async def test_missing_attachment_returns_404(authed_client, fake_storage):
    bcp = await _create_function_and_bcp(authed_client)
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await authed_client.get(f"/api/v1/bcps/{bcp['id']}/attachments/{fake_id}/url")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_returns_503_when_storage_disabled(authed_client, monkeypatch):
    """Routes should fail loudly (503) — not silently — when S3 is missing."""
    from app.services import attachment_service

    monkeypatch.setattr(attachment_service, "get_storage", lambda: None)

    bcp = await _create_function_and_bcp(authed_client)
    resp = await authed_client.post(
        f"/api/v1/bcps/{bcp['id']}/attachments",
        files={"file": ("a.txt", b"hi", "text/plain")},
    )
    assert resp.status_code == 503
