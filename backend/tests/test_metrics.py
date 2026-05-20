"""Verify Prometheus instrumentation is wired correctly."""

import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint_is_open(client):
    """/metrics must be reachable WITHOUT auth — Prometheus scrapers don't
    carry our app's bearer token."""
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    body = resp.text
    # Standard Prometheus exposition format starts with `# HELP`/`# TYPE`
    assert "# HELP" in body
    assert "# TYPE" in body


@pytest.mark.asyncio
async def test_metrics_record_protected_requests(authed_client):
    """A request to a real route should bump the http_requests counter."""
    # Trigger an instrumented request first
    await authed_client.get("/api/v1/functions/")
    resp = await authed_client.get("/metrics")
    body = resp.text
    # The instrumentator emits `http_requests_total` by default.
    assert "http_requests_total" in body


@pytest.mark.asyncio
async def test_metrics_skip_health_and_self(authed_client):
    """Excluded handlers shouldn't appear as separate series."""
    await authed_client.get("/health/")
    await authed_client.get("/metrics")
    resp = await authed_client.get("/metrics")
    body = resp.text
    # The default counter name is http_requests_total — make sure neither
    # /health nor /metrics shows up in any series labels.
    for line in body.splitlines():
        if line.startswith("http_requests_total"):
            assert "/health" not in line
            assert "/metrics" not in line
