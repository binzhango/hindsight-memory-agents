from unittest.mock import AsyncMock
import json

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from hindsight_client_api.exceptions import NotFoundException

from memory_agents.app import MemoryAgent, MemoryFact, MemoryService, Scope, Settings


@pytest.mark.asyncio
async def test_new_user_has_empty_memory_but_unrelated_404_is_an_error():
    service = MemoryService(Settings())
    scope = Scope("new-user", "demo")
    error = NotFoundException(status=404)
    error.body = json.dumps({"detail": f"Bank '{scope.bank_id}' not found"})
    service.client.arecall = AsyncMock(side_effect=error)
    try:
        assert await service.recall(scope, "Any preferences?") == []
        error.body = '{"detail": "Not Found"}'
        with pytest.raises(NotFoundException):
            await service.recall(scope, "Any preferences?")
    finally:
        await service.close()


def test_scope_is_stable_and_unambiguous():
    assert Scope("alice", "project").bank_id == Scope("alice", "project").bank_id
    assert Scope("a-b", "c").bank_id != Scope("a", "b-c").bank_id
    assert Scope("alice", "project").bank_id != Scope("bob", "project").bank_id
    assert Scope("alice", "project").bank_id != Scope("alice", "other").bank_id
    with pytest.raises(ValueError):
        Scope("", "project")


@pytest.mark.asyncio
async def test_agents_share_scope_but_keep_instructions_and_recall_each_question():
    memory = AsyncMock()
    memory.recall.return_value = [MemoryFact(id="fact-1", text="Use Python and SQLite.")]
    prompts = []
    model = RunnableLambda(lambda messages: prompts.append(messages) or AIMessage(content="Use SQLite."))
    scope = Scope("alice", "demo")
    for role in ["Plan the project.", "Implement the project."]:
        agent = MemoryAgent(model, memory, role)
        answer = await agent.ask(scope, role)
        assert answer.memories[0].id == "fact-1"
        assert answer.bank_id == scope.bank_id
    assert memory.recall.await_count == 2
    assert prompts[0][0].content.startswith("Plan")
    assert prompts[1][0].content.startswith("Implement")
    assert "Python and SQLite" in prompts[1][1].content
    # Answer generation must not implicitly store model-generated claims.
    memory.remember.assert_not_called()


@pytest.mark.asyncio
async def test_baseline_skips_recall():
    memory = AsyncMock()
    agent = MemoryAgent(RunnableLambda(lambda _: AIMessage(content="No preferences known.")), memory, "Help")
    answer = await agent.ask(Scope("alice", "demo"), "Choose a database", use_memory=False)
    assert answer.memories == []
    memory.recall.assert_not_called()


@pytest.mark.asyncio
async def test_memory_failure_is_visible_and_prevents_inference():
    memory = AsyncMock()
    memory.recall.side_effect = RuntimeError("offline")
    model_call = AsyncMock()
    agent = MemoryAgent(RunnableLambda(model_call), memory, "Help")
    with pytest.raises(RuntimeError, match="offline"):
        await agent.ask(Scope("alice", "demo"), "Question")
    model_call.assert_not_called()


@pytest.mark.asyncio
async def test_explicit_remember_uses_source_identity_and_waits_for_ingestion():
    service = MemoryService(Settings())
    service.client.aretain = AsyncMock()
    scope = Scope("alice", "demo")
    try:
        doc = await service.remember(scope, "Use SQLite", "coder", "preferences")
        assert doc == "preferences"
        kwargs = service.client.aretain.call_args.kwargs
        assert kwargs["bank_id"] == scope.bank_id
        assert kwargs["retain_async"] is False
        assert kwargs["metadata"]["source_agent"] == "coder"
        assert kwargs["update_mode"] == "replace"
        with pytest.raises(ValueError):
            await service.remember(scope, " ", "coder")
    finally:
        await service.close()
