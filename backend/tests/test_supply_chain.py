import pytest


@pytest.mark.asyncio
async def test_supplier_crud_and_assess(authed_client, fake_llm):
    create = await authed_client.post(
        "/api/v1/supply-chain/",
        json={
            "name": "Chipmaker Co",
            "category": "semiconductors",
            "region": "Taiwan",
            "criticality": "critical",
        },
    )
    assert create.status_code == 201, create.text
    s = create.json()
    assert s["region"] == "Taiwan"

    fake_llm.json_response = {
        "disruption_probability": 62,
        "risk_drivers": ["geopolitical tension", "single-region production"],
        "suggested_alternatives": [
            {"name": "Backup Fab Korea", "rationale": "second-source already qualified"}
        ],
        "summary": "Concentrated supplier; high disruption probability",
        "monitoring_indicators": ["semi industry shipping delays"],
    }
    resp = await authed_client.post(
        "/api/v1/supply-chain/assess",
        json={"supplier_id": s["id"], "additional_context": "single-source for chips"},
    )
    assert resp.status_code == 201, resp.text
    a = resp.json()
    assert a["disruption_probability"] == 62
    assert len(a["suggested_alternatives"]) == 1

    s2 = (await authed_client.get(f"/api/v1/supply-chain/{s['id']}")).json()
    assert s2["disruption_probability"] == 62


@pytest.mark.asyncio
async def test_assess_clamps_probability(authed_client, fake_llm):
    s = (await authed_client.post("/api/v1/supply-chain/", json={"name": "Vendor Z"})).json()
    fake_llm.json_response = {"disruption_probability": 500}
    a = (
        await authed_client.post("/api/v1/supply-chain/assess", json={"supplier_id": s["id"]})
    ).json()
    assert a["disruption_probability"] == 100
