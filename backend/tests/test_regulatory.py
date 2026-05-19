import pytest


@pytest.mark.asyncio
async def test_generate_and_submit_complete_report(authed_client, fake_llm):
    fake_llm.json_response = {
        "title": "SOX 2026Q1",
        "executive_summary": "All critical BCPs are in force and exercises met targets",
        "metrics": {
            "bcps_in_force": 12,
            "exercises_completed": 8,
            "vendor_coverage_pct": 90,
            "avg_exercise_score": 78,
        },
        "sections": [
            {"title": "Governance", "body": "Board reviews quarterly..."},
            {"title": "Testing", "body": "8 of 12 BCPs were exercised in period"},
        ],
        "attestation": "I attest as the BCM Officer that the above is accurate.",
    }
    resp = await authed_client.post(
        "/api/v1/regulatory/generate",
        json={"framework": "SOX", "period": "2026-Q1"},
    )
    assert resp.status_code == 201, resp.text
    r = resp.json()
    assert r["framework"] == "SOX"
    assert r["status"] == "validated"
    assert r["validation"]["complete"] is True
    assert r["validation"]["issues"] == []

    submit = await authed_client.post(
        f"/api/v1/regulatory/{r['id']}/submit",
        json={"submission_reference": "SOX-2026Q1-001"},
    )
    body = submit.json()
    assert body["status"] == "submitted"
    assert body["submission_reference"] == "SOX-2026Q1-001"


@pytest.mark.asyncio
async def test_validation_flags_missing_sections(authed_client, fake_llm):
    fake_llm.json_response = {
        "title": "Incomplete",
        "executive_summary": "ok",
        # missing sections + metrics
    }
    resp = await authed_client.post(
        "/api/v1/regulatory/generate",
        json={"framework": "PCI", "period": "2026-Q1"},
    )
    r = resp.json()
    assert r["status"] == "draft"
    assert r["validation"]["complete"] is False
    assert "missing sections" in r["validation"]["issues"]


@pytest.mark.asyncio
async def test_cannot_submit_incomplete_report(authed_client, fake_llm):
    fake_llm.json_response = {"title": "x", "executive_summary": "y"}
    r = (
        await authed_client.post(
            "/api/v1/regulatory/generate",
            json={"framework": "ISO22301", "period": "2026"},
        )
    ).json()
    submit = await authed_client.post(
        f"/api/v1/regulatory/{r['id']}/submit",
        json={"submission_reference": "X"},
    )
    assert submit.json()["status"] == "rejected"
    assert submit.json()["submission_reference"] == ""
