import pytest


async def _create_function(client):
    resp = await client.post(
        "/api/v1/functions/",
        json={"name": "Customer Support", "criticality": "high", "rto_minutes": 240},
    )
    return resp.json()


@pytest.mark.asyncio
async def test_recommend_persists_three_strategies(authed_client, fake_llm):
    fake_llm.json_response = {
        "strategies": [
            {
                "title": "Hot site",
                "kind": "hot_site",
                "description": "fully mirrored",
                "estimated_cost_usd": 500000,
                "rto_minutes": 5,
                "rpo_minutes": 1,
                "is_recommended": False,
                "rationale": "expensive",
            },
            {
                "title": "Remote work",
                "kind": "remote_work",
                "description": "agents WFH",
                "estimated_cost_usd": 20000,
                "rto_minutes": 60,
                "rpo_minutes": 0,
                "is_recommended": True,
                "rationale": "best balance",
            },
            {
                "title": "Manual workaround",
                "kind": "manual_workaround",
                "description": "phone tree",
                "estimated_cost_usd": 5000,
                "rto_minutes": 240,
                "rpo_minutes": 0,
                "is_recommended": False,
                "rationale": "fallback",
            },
        ]
    }
    fn = await _create_function(authed_client)
    resp = await authed_client.post(
        "/api/v1/recovery/recommend",
        json={"function_id": fn["id"], "budget_usd": 100000},
    )
    assert resp.status_code == 201, resp.text
    strats = resp.json()
    assert len(strats) == 3
    recommended = [s for s in strats if s["is_recommended"]]
    assert len(recommended) == 1
    assert recommended[0]["kind"] == "remote_work"
