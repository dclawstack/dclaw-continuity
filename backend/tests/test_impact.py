import pytest


async def _create_function(client):
    resp = await client.post(
        "/api/v1/functions/",
        json={"name": "Order Intake", "criticality": "high"},
    )
    return resp.json()


@pytest.mark.asyncio
async def test_impact_model_uses_llm(authed_client, fake_llm):
    fake_llm.json_response = {
        "revenue_impact_usd": 250000,
        "operational_impact_score": 8,
        "reputation_impact_score": 7,
        "narrative": "All orders blocked",
        "timeline": {
            "first_hour": "queue grows",
            "first_day": "SLAs breached",
            "first_week": "customer churn",
        },
        "stakeholders": [],
    }
    fn = await _create_function(authed_client)
    resp = await authed_client.post(
        "/api/v1/impact/model",
        json={
            "function_id": fn["id"],
            "scenario": "Datacenter outage",
            "additional_context": "8-hour outage",
        },
    )
    assert resp.status_code == 201, resp.text
    ia = resp.json()
    assert ia["revenue_impact_usd"] == 250000
    assert ia["operational_impact_score"] == 8
    assert ia["scenario"] == "Datacenter outage"


@pytest.mark.asyncio
async def test_impact_clamps_scores(authed_client, fake_llm):
    fake_llm.json_response = {
        "revenue_impact_usd": 0,
        "operational_impact_score": 99,
        "reputation_impact_score": -3,
        "narrative": "",
    }
    fn = await _create_function(authed_client)
    resp = await authed_client.post(
        "/api/v1/impact/model",
        json={"function_id": fn["id"], "scenario": "edge"},
    )
    ia = resp.json()
    assert ia["operational_impact_score"] == 10
    assert ia["reputation_impact_score"] == 0
