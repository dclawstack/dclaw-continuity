import pytest


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/work-area/",
        "/api/v1/it-dr/",
        "/api/v1/supply-chain/",
        "/api/v1/regulatory/",
    ],
)
@pytest.mark.asyncio
async def test_p2_stubs_return_501(authed_client, path):
    resp = await authed_client.get(path)
    assert resp.status_code == 501
    assert "not yet implemented" in resp.json()["detail"]
