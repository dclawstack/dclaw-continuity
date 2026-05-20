import pytest


@pytest.mark.asyncio
async def test_signup_login_me_flow(client):
    # signup
    signup = await client.post(
        "/api/v1/auth/signup",
        json={"email": "alice@example.com", "password": "s3cret-pw-123"},
    )
    assert signup.status_code == 201, signup.text
    body = signup.json()
    assert "access_token" in body
    assert body["user"]["email"] == "alice@example.com"
    token = body["access_token"]

    # login with same creds
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "s3cret-pw-123"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["email"] == "alice@example.com"

    # /me with the signup token
    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_duplicate_email_rejected(client):
    payload = {"email": "dupe@example.com", "password": "s3cret-pw-123"}
    first = await client.post("/api/v1/auth/signup", json=payload)
    assert first.status_code == 201
    second = await client.post("/api/v1/auth/signup", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_wrong_password_rejected(client):
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "bob@example.com", "password": "s3cret-pw-123"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "bob@example.com", "password": "wrong-pw"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_real_jwt(client):
    signup = await client.post(
        "/api/v1/auth/signup",
        json={"email": "carol@example.com", "password": "s3cret-pw-123"},
    )
    token = signup.json()["access_token"]

    resp = await client.get("/api/v1/functions/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_protected_route_rejects_bad_token(client):
    resp = await client.get(
        "/api/v1/functions/",
        headers={"Authorization": "Bearer this-is-not-a-jwt"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_dev_mode_token_still_works(authed_client):
    """authed_client uses DEV_AUTH_TOKEN — should still be accepted while
    AUTH_DEV_MODE is on."""

    resp = await authed_client.get("/api/v1/functions/")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_short_password_rejected(client):
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "dave@example.com", "password": "short"},
    )
    assert resp.status_code == 422
