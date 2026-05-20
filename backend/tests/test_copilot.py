import pytest


@pytest.mark.asyncio
async def test_chat_persists_conversation(authed_client, fake_llm):
    fake_llm.text_response = (
        "Sure! You should create a BCP for the Payments function.\n"
        "<suggest>"
        '{"suggestions":[{"action":"generate_bcp","label":"Generate Payments BCP",'
        '"payload":{}}]}'
        "</suggest>"
    )

    resp = await authed_client.post(
        "/api/v1/copilot/chat",
        json={"message": "How do I get started?"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "create a BCP" in body["reply"]
    assert len(body["suggestions"]) == 1
    assert body["suggestions"][0]["action"] == "generate_bcp"

    convo_id = body["conversation_id"]
    history = await authed_client.get(f"/api/v1/copilot/conversations/{convo_id}")
    assert history.status_code == 200
    rows = history.json()
    assert len(rows) == 2
    assert rows[0]["role"] == "user"
    assert rows[1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_chat_without_suggestions(authed_client, fake_llm):
    fake_llm.text_response = "Just a plain reply."
    resp = await authed_client.post("/api/v1/copilot/chat", json={"message": "hi"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "Just a plain reply."
    assert body["suggestions"] == []
