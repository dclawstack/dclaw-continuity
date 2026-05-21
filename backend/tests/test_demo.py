"""Verify the public /api/v1/demo seed + clear lifecycle."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_seed_returns_creds_and_populates_workspace(client):
    resp = await client.post("/api/v1/demo/seed")
    assert resp.status_code == 201, resp.text
    body = resp.json()

    assert body["email"].startswith("demo-") and body["email"].endswith("@demo.dclaw.app")
    assert len(body["password"]) >= 8
    assert body["access_token"].count(".") == 2  # looks like a JWT
    assert body["expires_in"] > 0

    # Using the returned token, the demo user can hit protected routes.
    auth = {"Authorization": f"Bearer {body['access_token']}"}
    me = await client.get("/api/v1/auth/me", headers=auth)
    assert me.status_code == 200
    assert me.json()["email"] == body["email"]

    fns = await client.get("/api/v1/functions/", headers=auth)
    assert fns.status_code == 200
    names = [f["name"] for f in fns.json()]
    assert any("Payments" in n for n in names)
    assert any("Checkout" in n for n in names)
    assert any("Support" in n for n in names)

    bcps = await client.get("/api/v1/bcps/", headers=auth)
    assert bcps.status_code == 200 and len(bcps.json()) >= 1

    vendors = await client.get("/api/v1/vendors/", headers=auth)
    assert vendors.status_code == 200 and len(vendors.json()) >= 1


@pytest.mark.asyncio
async def test_clear_wipes_user_and_their_data(client):
    seeded = (await client.post("/api/v1/demo/seed")).json()
    user_id = seeded["user_id"]
    token = seeded["access_token"]

    # Sanity: data exists pre-clear.
    auth = {"Authorization": f"Bearer {token}"}
    pre = await client.get("/api/v1/functions/", headers=auth)
    assert len(pre.json()) >= 3

    # Clear is no-auth on purpose — only requires the user_id, which the
    # landing tab holds in localStorage.
    cleared = await client.post(
        "/api/v1/demo/clear", json={"user_id": user_id}
    )
    assert cleared.status_code == 204

    # User no longer exists → their token doesn't authenticate them.
    me = await client.get("/api/v1/auth/me", headers=auth)
    assert me.status_code == 401


@pytest.mark.asyncio
async def test_clear_is_idempotent(client):
    seeded = (await client.post("/api/v1/demo/seed")).json()
    user_id = seeded["user_id"]

    first = await client.post("/api/v1/demo/clear", json={"user_id": user_id})
    second = await client.post("/api/v1/demo/clear", json={"user_id": user_id})
    assert first.status_code == 204
    assert second.status_code == 204  # 2nd call is a no-op


@pytest.mark.asyncio
async def test_clear_refuses_non_demo_user(client):
    # Sign up a normal user.
    real = (
        await client.post(
            "/api/v1/auth/signup",
            json={"email": "real@example.com", "password": "real-pw-123"},
        )
    ).json()
    # Try to clear them via the demo endpoint — should be a silent no-op
    # (clear_demo checks is_demo before deleting). User still exists.
    resp = await client.post(
        "/api/v1/demo/clear", json={"user_id": real["user"]["id"]}
    )
    assert resp.status_code == 204
    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {real['access_token']}"},
    )
    assert me.status_code == 200  # not deleted
