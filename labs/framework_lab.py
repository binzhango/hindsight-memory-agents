"""Exercise real framework adapters with a simulated memory service; no inference."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from hindsight_client import Hindsight
from hindsight_client_api.models.recall_response import RecallResponse
from hindsight_client_api.models.recall_result import RecallResult
from hindsight_langgraph import create_hindsight_tools, create_recall_node, create_retain_node
from hindsight_pydantic_ai import create_hindsight_tools as pydantic_tools
from hindsight_pydantic_ai import memory_instructions
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel


async def main() -> None:
    client = MagicMock(spec=Hindsight)
    client.arecall = AsyncMock(return_value=RecallResponse(results=[RecallResult(id="m1", text="Alice prefers tea.")]))
    client.aretain = AsyncMock()
    client.areflect = AsyncMock()
    tools = create_hindsight_tools(client=client, include_reflect=False)
    recall_tool = next(t for t in tools if t.name == "hindsight_recall")
    for user in ("alice", "bob"):
        await recall_tool.ainvoke({"query": "drink preference"}, config={"configurable": {"user_id": user}})
        assert client.arecall.call_args.kwargs["bank_id"] == user
    print("PASS: LangChain tools resolve each request's bank")

    async def answer(state: MessagesState) -> dict[str, list[AIMessage]]:
        return {"messages": [AIMessage(content="Acknowledged.")]}

    builder = StateGraph(MessagesState)
    builder.add_node("recall", create_recall_node(client=client, bank_id="alice"))
    builder.add_node("answer", answer)
    builder.add_node("retain", create_retain_node(client=client, bank_id="alice"))
    builder.add_edge(START, "recall")
    builder.add_edge("recall", "answer")
    builder.add_edge("answer", "retain")
    builder.add_edge("retain", END)
    graph = builder.compile()
    first = await graph.ainvoke({"messages": [HumanMessage(content="What should I drink?")]})
    assert any(isinstance(m, SystemMessage) and "tea" in str(m.content) for m in first["messages"])
    client.arecall.return_value = RecallResponse(results=[])
    second = await graph.ainvoke(first)
    assert not any(m.id == "hindsight_memory_context" for m in second["messages"])
    client.aretain.assert_awaited()
    print("PASS: compiled LangGraph injects, retains, and clears stale context")

    client.arecall.return_value = RecallResponse(results=[RecallResult(id="m1", text="Alice prefers tea.")])
    agent = Agent(
        TestModel(call_tools=["hindsight_recall"]),
        tools=pydantic_tools(client=client, bank_id="alice", include_retain=False, include_reflect=False),
        instructions=[memory_instructions(client=client, bank_id="alice")],
    )
    result = await agent.run("What should I drink?")
    assert client.arecall.call_args.kwargs["bank_id"] == "alice"
    assert "tea" in str(result.all_messages())
    print("PASS: real Pydantic AI agent executes memory instructions and recall tool")
    client.arecall.side_effect = RuntimeError("simulated outage")
    instructions = memory_instructions(client=client, bank_id="alice")
    assert await instructions(None) == ""
    print("PASS: Pydantic AI instructions degrade to empty context on outage")
    print("These checks prove adapter wiring, not extraction or answer quality.")


if __name__ == "__main__":
    asyncio.run(main())
