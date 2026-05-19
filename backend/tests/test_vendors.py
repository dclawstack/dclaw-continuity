import pytest


@pytest.mark.asyncio
async def test_create_and_assess_vendor(authed_client, fake_llm):
    create = await authed_client.post(
        "/api/v1/vendors/",
        json={
            "name": "Acquirer Co",
            "services_provided": "card settlement",
            "tier": "tier-1",
        },
    )
    assert create.status_code == 201, create.text
    v = create.json()

    fake_llm.json_response = {
        "readiness_score": 72,
        "risk_level": "medium",
        "summary": "Has DR but no recent test",
        "strengths": ["redundant DCs"],
        "weaknesses": ["last test 18m ago"],
        "monitoring_indicators": ["uptime SLA breaches"],
    }
    resp = await authed_client.post(
        "/api/v1/vendors/assess",
        json={"vendor_id": v["id"], "additional_context": "PCI vendor"},
    )
    assert resp.status_code == 201, resp.text
    a = resp.json()
    assert a["readiness_score"] == 72
    assert a["risk_level"] == "medium"

    # Vendor's readiness score should be updated
    v2 = (await authed_client.get(f"/api/v1/vendors/{v['id']}")).json()
    assert v2["readiness_score"] == 72


@pytest.mark.asyncio
async def test_assess_score_clamped(authed_client, fake_llm):
    v = (
        await authed_client.post(
            "/api/v1/vendors/", json={"name": "Vendor X"}
        )
    ).json()
    fake_llm.json_response = {"readiness_score": -100, "risk_level": "high"}
    a = (
        await authed_client.post(
            "/api/v1/vendors/assess", json={"vendor_id": v["id"]}
        )
    ).json()
    assert a["readiness_score"] == 0
