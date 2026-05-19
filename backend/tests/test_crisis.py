import pytest


async def _create_bcp(client):
    fn = (
        await client.post(
            "/api/v1/functions/",
            json={"name": "Trading", "criticality": "critical"},
        )
    ).json()
    return (
        await client.post(
            "/api/v1/bcps/",
            json={"function_id": fn["id"], "title": "Trading BCP"},
        )
    ).json()


@pytest.mark.asyncio
async def test_activate_then_advance_status(authed_client):
    bcp = await _create_bcp(authed_client)
    resp = await authed_client.post(
        "/api/v1/crisis/activate",
        json={
            "bcp_id": bcp["id"],
            "title": "East region offline",
            "description": "Primary DC down",
            "external_crisis_id": "INC-001",
            "source": "dclaw-crisis",
        },
    )
    assert resp.status_code == 201, resp.text
    a = resp.json()
    assert a["status"] == "activated"
    assert len(a["timeline"]) == 1
    aid = a["id"]

    r2 = await authed_client.post(
        f"/api/v1/crisis/{aid}/status",
        json={"status": "recovering", "note": "failover started"},
    )
    body = r2.json()
    assert body["status"] == "recovering"
    assert len(body["timeline"]) == 2

    r3 = await authed_client.post(
        f"/api/v1/crisis/{aid}/status",
        json={"status": "closed", "note": "all clear"},
    )
    assert r3.json()["status"] == "closed"
    assert r3.json()["closed_at"] is not None


@pytest.mark.asyncio
async def test_activate_resolves_by_function_id(authed_client):
    fn = (
        await authed_client.post(
            "/api/v1/functions/",
            json={"name": "Ops", "criticality": "high"},
        )
    ).json()
    await authed_client.post(
        "/api/v1/bcps/",
        json={"function_id": fn["id"], "title": "Ops BCP latest"},
    )
    resp = await authed_client.post(
        "/api/v1/crisis/activate",
        json={"function_id": fn["id"], "title": "Generic crisis"},
    )
    assert resp.status_code == 201, resp.text


@pytest.mark.asyncio
async def test_activate_without_resolvable_bcp_returns_400(authed_client):
    resp = await authed_client.post(
        "/api/v1/crisis/activate",
        json={"title": "no target"},
    )
    assert resp.status_code == 400
