import pytest


async def _create_function(client, name="Payments"):
    resp = await client.post(
        "/api/v1/functions/",
        json={"name": name, "criticality": "critical", "rto_minutes": 60},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_bcp_crud(authed_client):
    fn = await _create_function(authed_client)
    resp = await authed_client.post(
        "/api/v1/bcps/",
        json={
            "function_id": fn["id"],
            "title": "Payments BCP",
            "summary": "Plan to keep card processing up",
            "status": "draft",
            "content": {"objectives": ["restore within 60m"]},
        },
    )
    assert resp.status_code == 201, resp.text
    bcp = resp.json()
    assert bcp["title"] == "Payments BCP"

    listing = await authed_client.get("/api/v1/bcps/", params={"function_id": fn["id"]})
    assert listing.status_code == 200
    assert len(listing.json()) == 1


@pytest.mark.asyncio
async def test_bcp_generate_uses_llm(authed_client, fake_llm):
    fake_llm.json_response = {
        "title": "Generated BCP",
        "summary": "AI-drafted plan",
        "objectives": ["restore quickly"],
        "procedures": [{"step": 1, "action": "activate", "owner": "ops", "duration_minutes": 5}],
    }
    fn = await _create_function(authed_client, name="Logistics")
    resp = await authed_client.post(
        "/api/v1/bcps/generate",
        json={"function_id": fn["id"], "additional_context": "warehouse closure"},
    )
    assert resp.status_code == 201, resp.text
    bcp = resp.json()
    assert bcp["title"] == "Generated BCP"
    assert bcp["status"] == "draft"
    assert bcp["content"]["procedures"][0]["action"] == "activate"
    assert len(fake_llm.calls) == 1


@pytest.mark.asyncio
async def test_bcp_gap_analysis(authed_client, fake_llm):
    fake_llm.json_response = {
        "title": "BCP",
        "summary": "",
        "procedures": [],
    }
    fn = await _create_function(authed_client, name="Support")
    gen = await authed_client.post("/api/v1/bcps/generate", json={"function_id": fn["id"]})
    bcp_id = gen.json()["id"]

    fake_llm.json_response = {
        "gaps": [
            {
                "severity": "high",
                "area": "communication",
                "issue": "no external comms plan",
                "recommendation": "draft external statement",
            }
        ]
    }
    resp = await authed_client.post(f"/api/v1/bcps/{bcp_id}/gap-analysis")
    assert resp.status_code == 200, resp.text
    bcp = resp.json()
    assert len(bcp["gaps"]) == 1
    assert bcp["gaps"][0]["severity"] == "high"
