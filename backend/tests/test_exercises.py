import pytest


async def _create_bcp(client):
    fn = (
        await client.post(
            "/api/v1/functions/",
            json={"name": "Payments", "criticality": "critical"},
        )
    ).json()
    bcp = (
        await client.post(
            "/api/v1/bcps/",
            json={"function_id": fn["id"], "title": "Payments BCP"},
        )
    ).json()
    return bcp


@pytest.mark.asyncio
async def test_exercise_generate_start_evaluate(authed_client, fake_llm):
    bcp = await _create_bcp(authed_client)

    fake_llm.json_response = {
        "name": "Datacenter Outage Drill",
        "scenario": "At 0930 the primary east region fails…",
        "objectives": ["failover under 30m", "comms in <10m"],
    }
    gen = await authed_client.post(
        "/api/v1/exercises/generate",
        json={"bcp_id": bcp["id"], "focus": "datacenter outage"},
    )
    assert gen.status_code == 201, gen.text
    ex = gen.json()
    assert ex["status"] == "planned"
    assert len(ex["objectives"]) == 2

    started = await authed_client.post(f"/api/v1/exercises/{ex['id']}/start")
    assert started.json()["status"] == "running"
    assert started.json()["started_at"] is not None

    fake_llm.json_response = {
        "score": 82,
        "strengths": ["fast comms"],
        "weaknesses": ["DB restore slow"],
        "missed_objectives": [],
        "recommendations": ["test backups monthly"],
    }
    evaluated = await authed_client.post(
        f"/api/v1/exercises/{ex['id']}/evaluate",
        json={"observations": "team responded in 12m", "issues_encountered": []},
    )
    assert evaluated.status_code == 200, evaluated.text
    result = evaluated.json()
    assert result["status"] == "completed"
    assert result["score"] == 82
    assert result["completed_at"] is not None


@pytest.mark.asyncio
async def test_exercise_score_clamped(authed_client, fake_llm):
    bcp = await _create_bcp(authed_client)
    fake_llm.json_response = {"name": "X", "scenario": "y", "objectives": []}
    ex = (
        await authed_client.post(
            "/api/v1/exercises/generate", json={"bcp_id": bcp["id"]}
        )
    ).json()
    await authed_client.post(f"/api/v1/exercises/{ex['id']}/start")
    fake_llm.json_response = {"score": 9999}
    r = await authed_client.post(
        f"/api/v1/exercises/{ex['id']}/evaluate",
        json={"observations": "ok"},
    )
    assert r.json()["score"] == 100
