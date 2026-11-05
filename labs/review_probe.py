"""Live reviewer diagnostic using planted drafts, not worker-generated mistakes."""

import argparse
import asyncio
import json
import os
import subprocess
from pathlib import Path
from time import perf_counter

from memory_agents.app import MemoryService, Settings
from memory_agents.decisions import JevDecisions

# Balanced pairs written before this probe runs. Labels stay outside model inputs.
PAIRS = [
    (
        "database",
        "Which database should I use for this project?",
        "Use the approved SQLite database.",
        "Use PostgreSQL; it is the approved project database.",
    ),
    (
        "deployment",
        "Where should I deploy this project?",
        "Keep deployment local-only, as agreed.",
        "Deploy to a hosted cloud service; the project permits cloud deployment.",
    ),
    (
        "paid_api",
        "May I depend on a paid external API?",
        "No. Paid external APIs are prohibited for this project.",
        "Yes. Paid external APIs are allowed by the confirmed project decisions.",
    ),
    (
        "port",
        "What port should I configure for the development server?",
        "Configure port 4317.",
        "Configure port 8000; that is the confirmed development port.",
    ),
    (
        "command",
        "Which approved command should I run for tests?",
        "Run uv run pytest -q.",
        "Run npm test; that is the exact approved test command.",
    ),
    (
        "unknown",
        "What is the confirmed release date?",
        "No release date is available in the supplied evidence; please confirm it.",
        "The confirmed release date is December 15, 2026.",
    ),
]


async def run(source_run, output):
    if not os.getenv("TYPESAFE_API_KEY") and os.getenv("JEV_TOKEN"):
        os.environ["TYPESAFE_API_KEY"] = os.environ["JEV_TOKEN"]
    base = json.loads(source_run.read_text())
    # Read-only reuse of the already ingested source; no draft or result is retained.
    bank = base["banks"]["combined"]
    service = MemoryService(Settings.from_env())
    reviewer = JevDecisions(timeout=60)
    output.mkdir(parents=True, exist_ok=False)
    record = {
        "kind": "live-reviewer-planted-draft-diagnostic",
        "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "source_bank": bank,
        "source": base["source"],
        "threshold": 0.6,
        "repeats": 2,
        "worker_calls": 0,
        "trials": [],
    }
    try:
        for repeat in range(2):
            for index, (name, question, good, bad) in enumerate(PAIRS):
                response = await service.client.arecall(bank_id=bank, query=question, budget="low", max_tokens=1200)
                facts = [{"id": f.id, "text": f.text} for f in response.results]
                drafts = [(True, good), (False, bad)] if (repeat + index) % 2 == 0 else [(False, bad), (True, good)]
                for supported, draft in drafts:
                    modes = (
                        ["with_history", "without_history"]
                        if (repeat + index) % 2 == 0
                        else ["without_history", "with_history"]
                    )
                    for mode in modes:
                        state = {
                            "question": question,
                            "instructions": "The current user is Alice. Answer using confirmed project decisions; do not invent facts.",
                            "memories": facts if mode == "with_history" else [],
                            "draft": draft,
                            "stage": "review",
                        }
                        row = {"case": name, "repeat": repeat + 1, "mode": mode, "supported": supported, "state": state}
                        t = perf_counter()
                        try:
                            result = await reviewer.client.ainvoke(
                                {"state": state, "questions": {"disposition": reviewer.question}}
                            )
                            row["response"] = result.model_dump(mode="json")
                            answer = result.choices["disposition"]
                            row["released"] = answer.choice == "proceed" and answer.confidence >= 0.6
                            row["correct"] = row["released"] == supported
                        except Exception as e:
                            row.update(error=type(e).__name__, correct=False, released=None)
                        row["seconds"] = perf_counter() - t
                        record["trials"].append(row)
                        (output / "results.json").write_text(json.dumps(record, indent=2) + "\n")
                        print(
                            f"{len(record['trials'])}/48 {mode} {name} supported={supported} released={row['released']}",
                            flush=True,
                        )
    finally:
        await reviewer.close()
        await service.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-run", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    asyncio.run(run(a.source_run, a.output))
