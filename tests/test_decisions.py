from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from memory_agents.app import MemoryAgent, MemoryFact, Scope
from memory_agents.decisions import Decision


def decision(stage="preflight", choice="proceed", confidence=0.9):
    return Decision(stage=stage, choice=choice, confidence=confidence, elapsed_ms=1)


@pytest.mark.asyncio
async def test_shared_snapshot_and_review():
    memory = AsyncMock()
    memory.recall.return_value = [MemoryFact(id="f1", text="Use SQLite")]
    provider = AsyncMock()
    provider.assess.side_effect = [decision(), decision("review")]
    prompts = []
    worker = RunnableLambda(lambda messages: prompts.append(messages) or AIMessage(content="Use SQLite"))
    result = await MemoryAgent(worker, memory, "Help", provider).ask(Scope("a", "p"), "Database?")
    assert result.disposition == "answered"
    assert len(result.decisions) == 2
    assert memory.recall.await_count == 1
    states = [call.args[0] for call in provider.assess.await_args_list]
    assert states[0]["memories"] == states[1]["memories"] == [{"id": "f1", "text": "Use SQLite"}]
    assert "draft" not in states[0]
    assert states[1]["draft"] == "Use SQLite"
    assert "Use SQLite" in prompts[0][1].content
    memory.remember.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "choice,confidence,expected", [("clarify", 0.9, "clarify"), ("proceed", 0.59, "review"), ("review", 0.9, "review")]
)
async def test_preflight_can_stop_worker(choice, confidence, expected):
    memory, provider, worker = AsyncMock(), AsyncMock(), AsyncMock()
    memory.recall.return_value = []
    provider.assess.return_value = decision(choice=choice, confidence=confidence)
    result = await MemoryAgent(worker, memory, "Help", provider).ask(Scope("a", "p"), "Question")
    assert result.disposition == expected
    worker.ainvoke.assert_not_called()


@pytest.mark.asyncio
async def test_rejected_draft_is_separate_from_answer_and_no_memory_skips_recall():
    memory, provider, worker = AsyncMock(), AsyncMock(), AsyncMock()
    provider.assess.side_effect = [decision(), decision("review", "review")]
    worker.ainvoke.return_value = AIMessage(content="Use a paid service")
    result = await MemoryAgent(worker, memory, "Help", provider).ask(Scope("a", "p"), "Question", False)
    assert result.disposition == "review"
    assert result.draft == "Use a paid service"
    assert result.text != result.draft
    assert provider.assess.call_args.args[0]["memories"] == []
    memory.recall.assert_not_called()


@pytest.mark.asyncio
async def test_provider_failure_does_not_approve():
    memory, provider, worker = AsyncMock(), AsyncMock(), AsyncMock()
    memory.recall.return_value = []
    provider.assess.side_effect = TimeoutError()
    with pytest.raises(TimeoutError):
        await MemoryAgent(worker, memory, "Help", provider).ask(Scope("a", "p"), "Question")
    worker.ainvoke.assert_not_called()


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError):
        decision(confidence=float("nan"))
    with pytest.raises(ValueError):
        MemoryAgent(AsyncMock(), AsyncMock(), "Help", confidence_threshold=float("nan"))


@pytest.mark.asyncio
async def test_installed_sdk_adapter_contract(monkeypatch):
    sdk = pytest.importorskip("langchain_typesafe")
    from langchain_typesafe.types import ClassifierResponse
    from memory_agents.decisions import JevDecisions

    monkeypatch.setenv("TYPESAFE_API_KEY", "test-only")
    response = ClassifierResponse.model_validate(
        {
            "model": "fixture",
            "request_id": "request-1",
            "answers": {
                "disposition": {
                    "type": "choice",
                    "choice": "proceed",
                    "confidence": 0.9,
                    "probabilities": {"proceed": 0.95, "clarify": 0.03, "review": 0.02},
                }
            },
        }
    )
    invoke = AsyncMock(return_value=response)
    monkeypatch.setattr(sdk.TypeSafeClassifier, "ainvoke", invoke)
    adapter = JevDecisions()
    try:
        result = await adapter.assess({"question": "Database?", "memories": []}, "preflight")
        assert result.choice == "proceed"
        assert result.request_id == "request-1"
        sent = invoke.call_args.args[0]
        assert sent["state"]["stage"] == "preflight"
        assert set(sent["questions"]["disposition"].criteria) == {"proceed", "clarify", "review"}
    finally:
        await adapter.close()
