import pytest


@pytest.mark.asyncio
async def test_requires_auth(client):
    resp = await client.get("/api/v1/functions/")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_list_get_delete(authed_client):
    create = await authed_client.post(
        "/api/v1/functions/",
        json={
            "name": "Payments",
            "description": "Card processing",
            "owner": "Finance",
            "criticality": "critical",
            "rto_minutes": 60,
            "rpo_minutes": 15,
        },
    )
    assert create.status_code == 201, create.text
    fn = create.json()
    assert fn["name"] == "Payments"
    assert fn["criticality"] == "critical"

    listing = await authed_client.get("/api/v1/functions/")
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    got = await authed_client.get(f"/api/v1/functions/{fn['id']}")
    assert got.status_code == 200

    deleted = await authed_client.delete(f"/api/v1/functions/{fn['id']}")
    assert deleted.status_code == 204
    after = await authed_client.get(f"/api/v1/functions/{fn['id']}")
    assert after.status_code == 404
