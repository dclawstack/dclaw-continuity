import pytest


@pytest.mark.asyncio
async def test_site_crud(authed_client):
    create = await authed_client.post(
        "/api/v1/work-area/sites/",
        json={
            "name": "Backup Office London",
            "kind": "alternate_office",
            "location": "London, UK",
            "capacity_seats": 50,
            "has_remote_access": True,
        },
    )
    assert create.status_code == 201, create.text
    site = create.json()
    assert site["kind"] == "alternate_office"

    listing = await authed_client.get("/api/v1/work-area/sites/")
    assert len(listing.json()) == 1

    patched = await authed_client.patch(
        f"/api/v1/work-area/sites/{site['id']}",
        json={"capacity_seats": 75},
    )
    assert patched.json()["capacity_seats"] == 75


@pytest.mark.asyncio
async def test_recommend_plan_uses_llm(authed_client, fake_llm):
    fn = (
        await authed_client.post(
            "/api/v1/functions/",
            json={"name": "Customer Support", "criticality": "high"},
        )
    ).json()
    await authed_client.post(
        "/api/v1/work-area/sites/",
        json={
            "name": "Site A",
            "kind": "remote",
            "capacity_seats": 100,
            "has_remote_access": True,
        },
    )

    fake_llm.json_response = {
        "summary": "100% remote coverage available",
        "assignments": [
            {
                "site_name": "Site A",
                "seats": 30,
                "rationale": "remote ready",
            }
        ],
        "shortfall_seats": 0,
        "test_plan": "Quarterly remote-access drill",
    }
    resp = await authed_client.post(
        "/api/v1/work-area/plans/recommend",
        json={"function_id": fn["id"], "headcount_required": 30},
    )
    assert resp.status_code == 201, resp.text
    plan = resp.json()
    assert plan["summary"].startswith("100%")
    assert plan["headcount_required"] == 30
    assert plan["details"]["shortfall_seats"] == 0
