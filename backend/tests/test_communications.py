import pytest


@pytest.mark.asyncio
async def test_draft_communication_plan(authed_client, fake_llm):
    fn = (
        await authed_client.post(
            "/api/v1/functions/",
            json={"name": "Checkout", "criticality": "critical"},
        )
    ).json()

    fake_llm.json_response = {
        "audience": "Customers",
        "channels": ["email", "status_page"],
        "tone": "reassuring",
        "templates": [
            {
                "channel": "email",
                "trigger": "T+0 — at incident declaration",
                "subject": "Checkout temporarily unavailable",
                "body": "Hi {{name}}, we're aware of an issue and working on it.",
            },
            {
                "channel": "status_page",
                "trigger": "T+15m",
                "subject": "",
                "body": "Investigating checkout issues. Updates every 30m.",
            },
        ],
        "escalation_path": ["L1", "L2", "VP"],
    }

    resp = await authed_client.post(
        "/api/v1/communications/draft",
        json={
            "function_id": fn["id"],
            "audience": "Customers",
            "scenario": "Checkout outage",
        },
    )
    assert resp.status_code == 201, resp.text
    p = resp.json()
    assert p["audience"] == "Customers"
    assert "email" in p["channels"]
    assert len(p["templates"]) == 2
    assert p["templates"][0]["channel"] == "email"
    assert p["escalation_path"] == ["L1", "L2", "VP"]
