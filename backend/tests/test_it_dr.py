import pytest


@pytest.mark.asyncio
async def test_system_crud_and_generate_plan(authed_client, fake_llm):
    sys_resp = await authed_client.post(
        "/api/v1/it-dr/systems/",
        json={
            "name": "Orders DB",
            "owner": "Platform",
            "tier": "tier-1",
            "rto_minutes": 15,
            "rpo_minutes": 5,
            "backup_strategy": "WAL streaming + 5m snapshots",
        },
    )
    assert sys_resp.status_code == 201, sys_resp.text
    sys = sys_resp.json()
    assert sys["tier"] == "tier-1"

    fake_llm.json_response = {
        "title": "Orders DB DR Plan",
        "summary": "Failover to standby cluster",
        "prerequisites": ["streaming replica healthy"],
        "procedure": [
            {
                "step": 1,
                "action": "promote standby",
                "owner": "DBA",
                "duration_minutes": 5,
            }
        ],
        "validation": ["read/write smoke test"],
        "failback": ["resync once primary is restored"],
        "test_plan": [
            {
                "name": "monthly failover",
                "schedule": "first Sunday 02:00 UTC",
                "validates": "automatic promotion",
                "automation_hint": "use pg_ctl promote in a kube CronJob",
            }
        ],
    }
    gen = await authed_client.post(
        "/api/v1/it-dr/plans/generate",
        json={"system_id": sys["id"]},
    )
    assert gen.status_code == 201, gen.text
    plan = gen.json()
    assert plan["title"] == "Orders DB DR Plan"
    assert len(plan["test_plan"]) == 1
    assert plan["last_tested_at"] is None


@pytest.mark.asyncio
async def test_record_test(authed_client, fake_llm):
    sys = (await authed_client.post("/api/v1/it-dr/systems/", json={"name": "Cache"})).json()
    fake_llm.json_response = {"title": "Plan", "test_plan": []}
    plan = (
        await authed_client.post("/api/v1/it-dr/plans/generate", json={"system_id": sys["id"]})
    ).json()
    r = await authed_client.post(
        f"/api/v1/it-dr/plans/{plan['id']}/test-record",
        json={"passed": True, "notes": "clean run"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["last_test_passed"] is True
    assert body["last_tested_at"] is not None
