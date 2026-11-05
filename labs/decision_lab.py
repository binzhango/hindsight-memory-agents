"""Run the real wrapper with scripted providers; measure routing, not model quality."""

import argparse
import asyncio
import json
from pathlib import Path

from langchain_core.messages import AIMessage
from memory_agents.app import MemoryAgent, MemoryFact, Scope
from memory_agents.decisions import Decision


async def run_case(name, script, *, use_memory=True, use_jev=True):
    events = []

    class Memory:
        async def recall(self, scope, query):
            events.append({"event": "recall", "bank_id": scope.bank_id, "query": query})
            return [MemoryFact(id="fixture-constraint", text="Use Python and SQLite. No paid external APIs.")]

    class Worker:
        async def ainvoke(self, messages):
            events.append({"event": "worker", "messages": [{"role": m.type, "content": m.content} for m in messages]})
            return AIMessage(
                content="Use a paid hosted database." if name == "rejected_draft" else "Use Python and SQLite."
            )

    class Reviewer:
        async def assess(self, state, stage):
            events.append({"event": stage, "state": state})
            item = script[0 if stage == "preflight" else 1]
            if item == "timeout":
                raise TimeoutError("Scripted provider timeout")
            return Decision(
                stage=stage, choice=item[0], confidence=item[1], elapsed_ms=0, request_id="scripted-" + stage
            )

    result = {"case": name, "source": "scripted-providers-real-wrapper", "events": events}
    try:
        answer = await MemoryAgent(
            Worker(), Memory(), "Respect the confirmed project constraints.", Reviewer() if use_jev else None
        ).ask(Scope("synthetic-alice", "decision-lab"), "Suggest an implementation stack.", use_memory)
        result["output"] = answer.model_dump()
        result["outcome"] = answer.disposition
    except TimeoutError:
        result["outcome"] = "error"
        result["error"] = "TimeoutError"
    result["recall_calls"] = sum(e["event"] == "recall" for e in events)
    result["worker_calls"] = sum(e["event"] == "worker" for e in events)
    result["decision_calls"] = sum(e["event"] in {"preflight", "review"} for e in events)
    return result


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    proceed = ("proceed", 0.9)
    definitions = [
        ("accepted", [proceed, proceed], {}, ("answered", 1, 1, 2)),
        ("rejected_draft", [proceed, ("review", 0.9)], {}, ("review", 1, 1, 2)),
        ("missing_context", [("clarify", 0.9)], {}, ("clarify", 1, 0, 1)),
        ("low_confidence", [("proceed", 0.59)], {}, ("review", 1, 0, 1)),
        ("threshold_boundary", [("proceed", 0.6), proceed], {}, ("answered", 1, 1, 2)),
        ("preflight_timeout", ["timeout"], {}, ("error", 1, 0, 1)),
        ("review_timeout", [proceed, "timeout"], {}, ("error", 1, 1, 2)),
        ("memory_only", [], {"use_jev": False}, ("answered", 1, 1, 0)),
        ("jev_without_memory", [proceed, proceed], {"use_memory": False}, ("answered", 0, 1, 2)),
    ]
    results = []
    for name, script, options, expected in definitions:
        result = await run_case(name, script, **options)
        actual = (result["outcome"], result["recall_calls"], result["worker_calls"], result["decision_calls"])
        if actual != expected:
            raise AssertionError((name, actual, expected))
        if name == "rejected_draft":
            assert result["output"]["draft"] == "Use a paid hosted database."
            assert result["output"]["text"] != result["output"]["draft"]
        results.append(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"kind": "deterministic-control-flow-lab", "live_model_calls": 0, "cases": results}, indent=2) + "\n"
    )
    print(f"Verified {len(results)} scripted control-flow cases; zero live model calls. Saved {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
