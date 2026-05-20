import pytest


async def _create_fn(client, name="Payments", criticality="critical"):
    r = await client.post(
        "/api/v1/functions/",
        json={"name": name, "criticality": criticality},
    )
    return r.json()


@pytest.mark.asyncio
async def test_bcp_creation_indexes_chunk(authed_client, fake_llm):
    fake_llm.json_response = {
        "title": "Payments BCP",
        "summary": "Plan for card processing outage",
        "objectives": ["restore within 60m"],
        "procedures": [{"step": 1, "action": "activate", "owner": "ops", "duration_minutes": 5}],
    }
    fn = await _create_fn(authed_client)
    gen = await authed_client.post("/api/v1/bcps/generate", json={"function_id": fn["id"]})
    assert gen.status_code == 201

    # Knowledge-chunks row should exist now
    from sqlalchemy import select

    from app.models.knowledge_chunk import KnowledgeChunk
    from tests.conftest import test_engine

    async with test_engine.connect() as conn:
        result = await conn.execute(
            select(KnowledgeChunk).where(KnowledgeChunk.source_type == "bcp")
        )
        rows = result.fetchall()
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_copilot_uses_rag_results(authed_client, fake_llm):
    """Verify retrieved evidence is injected into the LLM call."""

    fake_llm.json_response = {
        "title": "BCP for Logistics",
        "summary": "warehouse outage plan",
        "objectives": [],
        "procedures": [],
    }
    fn = await _create_fn(authed_client, name="Logistics", criticality="high")
    await authed_client.post("/api/v1/bcps/generate", json={"function_id": fn["id"]})

    fake_llm.text_response = "Based on the existing plan, you should rehearse it."
    resp = await authed_client.post(
        "/api/v1/copilot/chat",
        json={"message": "What plans cover Logistics?"},
    )
    assert resp.status_code == 200

    # Inspect the last fake_llm call: it should include a "Retrieved evidence"
    # system message because RAG returned at least one hit.
    assert fake_llm.calls, "fake_llm was never called"
    last = fake_llm.calls[-1]
    sysmsgs = [
        m.content if hasattr(m, "content") else m["content"]
        for m in last["messages"]
        if (getattr(m, "role", None) or m.get("role")) == "system"
    ]
    assert any("Retrieved evidence" in s for s in sysmsgs)


@pytest.mark.asyncio
async def test_chat_works_when_no_chunks_indexed(authed_client, fake_llm):
    """RAG returns 0 hits → Copilot still answers."""

    fake_llm.text_response = "Sure, here's general guidance."
    resp = await authed_client.post("/api/v1/copilot/chat", json={"message": "give me an overview"})
    assert resp.status_code == 200
    assert "general guidance" in resp.json()["reply"]
