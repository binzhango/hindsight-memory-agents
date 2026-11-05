"""Small local, paired memory benchmark; run with python -m memory_agents.benchmark."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from time import perf_counter
from typing import Literal
from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, ConfigDict

from .app import MemoryAgent, MemoryFact, MemoryService, Scope, Settings

SOURCE = (
    "For Alice's benchmark project, the selected database is SQLite. "
    "The internal project codename is maple-731. The local development server port is 4317. "
    "The exact test command is uv run pytest -q."
)
INSTRUCTIONS = (
    'Answer the question using available evidence. Return only JSON with one key: {"answer": value}. '
    "Use a string for a known value, or JSON null if it is unknown. Do not guess. "
    "Return only the requested value without explanations or citations."
)
Mode = Literal["no_memory", "hindsight", "provided_context"]
MODES: list[Mode] = ["no_memory", "hindsight", "provided_context"]


class Case(BaseModel):
    name: str
    question: str
    expected: str | None
    other_user: bool = False


CASES = [
    Case(name="database", question="Which database did we select for my project?", expected="SQLite"),
    Case(name="codename", question="What is my project's internal codename?", expected="maple-731"),
    Case(
        name="port", question="Which port is my project's local development server configured to use?", expected="4317"
    ),
    Case(name="test_command", question="What is the exact test command for my project?", expected="uv run pytest -q"),
    Case(name="unknown", question="What is my project's agreed release date?", expected=None),
    Case(name="other_user", question="Which database did we select for my project?", expected=None, other_user=True),
]


class ResponseValue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: str | int | None


class Trial(BaseModel):
    case: str
    repeat: int
    mode: Mode
    expected: str | None
    answer: str = ""
    correct: bool = False
    total_seconds: float = 0
    recall_seconds: float = 0
    model_seconds: float = 0
    input_tokens: int | None = None
    output_tokens: int | None = None
    finish_reason: str | None = None
    memories: list[MemoryFact] = []
    error: str | None = None


class BenchmarkRun(BaseModel):
    started_utc: str
    run_id: str
    model: str
    source: str = SOURCE
    temperature: float = 0
    max_output_tokens: int = 1024
    repeats: int
    bank_id: str
    retain_seconds: float = 0
    trials: list[Trial] = []


def score(text: str, expected: str | None) -> bool:
    """Strict JSON scoring: never grant credit for merely mentioning the expected text."""
    try:
        answer = ResponseValue.model_validate_json(text).answer
    except ValueError:
        return False
    if expected is None:
        return answer is None
    return answer is not None and str(answer).strip().casefold() == expected.casefold()


class TrialMemory:
    def __init__(self, service: MemoryService, trial: Trial, owner: Scope) -> None:
        self.service = service
        self.trial = trial
        self.owner = owner

    async def recall(self, scope: Scope, query: str) -> list[MemoryFact]:
        if self.trial.mode == "provided_context":
            return [MemoryFact(id="source-document", text=SOURCE)] if scope == self.owner else []
        start = perf_counter()
        try:
            return await self.service.recall(scope, query)
        finally:
            self.trial.recall_seconds = perf_counter() - start


def report(run: BenchmarkRun) -> str:
    lines = [
        "# Local memory benchmark",
        "",
        f"Run: `{run.run_id}`; model: `{run.model}`; started UTC: {run.started_utc}.",
        f"Retain (one source document): **{run.retain_seconds:.2f} s**, excluded from answer latency.",
        "",
        "| Mode | Known facts correct | Unknown/scope checks correct | All correct | Median total | Median recall | Median model | Mean input tokens |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for mode in MODES:
        rows = [t for t in run.trials if t.mode == mode]
        if not rows:
            continue
        known = [t for t in rows if t.expected is not None]
        unknown = [t for t in rows if t.expected is None]
        tokens = [t.input_tokens for t in rows if t.input_tokens is not None]
        token_text = f"{sum(tokens) / len(tokens):.1f}" if tokens else "unavailable"
        lines.append(
            f"| {mode} | {sum(t.correct for t in known)}/{len(known)} "
            f"| {sum(t.correct for t in unknown)}/{len(unknown)} "
            f"| {sum(t.correct for t in rows)}/{len(rows)} "
            f"| {median(t.total_seconds for t in rows):.2f} s "
            f"| {median(t.recall_seconds for t in rows):.2f} s "
            f"| {median(t.model_seconds for t in rows):.2f} s | {token_text} |"
        )
    lines.extend(
        [
            "",
            "## Method",
            "",
            f"Six cases × three modes × {run.repeats} repeats. All calls are sequential, with rotated mode order. "
            "Each request starts with fresh messages; no chat history or answer is retained. "
            "The same model, system instructions, questions, temperature 0 and 1024-token output cap apply to all modes. "
            "The current user is identified as Alice (or Bob in the other-user case) in every mode, "
            "and supplied evidence is explicitly scoped to the current project. "
            "One model call and one recall warm up the services before measured trials. "
            "Server prompt caches are not disabled; these are warm-service timings on one Mac, not throughput measurements.",
            "",
            "`no_memory` uses empty evidence. `hindsight` recalls the stored source via the real server. "
            "`provided_context` supplies the original source directly, without Hindsight, only for its owner. "
            "This third mode controls for having the facts already available in a prompt.",
            "",
            "Scoring requires valid JSON with only an `answer` key and exact expected value "
            "(case-insensitive, surrounding whitespace ignored; numeric port accepted). "
            "Unknown and other-user cases require JSON null. Failures count as incorrect and are saved. "
            "No LLM judge is used. Inspect the raw answers and retrieved facts in results.json.",
            "",
            "This is a small synthetic cross-session factual-memory test, not a standard benchmark or a measure of "
            "general reasoning, coding, production authorization, large-memory retrieval, or long-term updates. "
            "Repeats are not independent tasks. A memory-free model cannot know arbitrary historical facts; "
            "the comparison shows context availability, not improved model intelligence. "
            "Recall/model/total columns are separate medians and need not add up. "
            "A short prompt containing all facts can be sufficient when it fits your application.",
            "",
            "## Per-trial answers",
            "",
        ]
    )
    for trial in run.trials:
        lines.extend(
            [
                f"### {trial.case} / {trial.mode} / repeat {trial.repeat}",
                "",
                f"Correct: {trial.correct}; total: {trial.total_seconds:.2f} s; error: {trial.error or 'none'}.",
                "",
                "```text",
                trial.answer,
                "```",
                "",
            ]
        )
    return "\n".join(lines)


async def run_benchmark(output: Path, repeats: int) -> None:
    output.mkdir(parents=True, exist_ok=False)
    settings = Settings.from_env().model_copy(update={"timeout": 300})
    service = MemoryService(settings)
    model = settings.chat_model().bind(temperature=0, max_tokens=1024)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    owner = Scope("benchmark-alice", run_id)
    other = Scope("benchmark-bob", run_id)
    run = BenchmarkRun(
        started_utc=datetime.now(timezone.utc).isoformat(),
        run_id=run_id,
        model=settings.model,
        repeats=repeats,
        bank_id=owner.bank_id,
    )

    def save() -> None:
        (output / "results.json").write_text(run.model_dump_json(indent=2) + "\n")
        (output / "REPORT.md").write_text(report(run))

    try:
        print(f"Retaining synthetic source in {owner.bank_id} ...", flush=True)
        start = perf_counter()
        await service.remember(owner, SOURCE, "benchmark", "benchmark-source")
        run.retain_seconds = perf_counter() - start
        save()
        print(f"Retain completed in {run.retain_seconds:.2f}s. Warming services ...", flush=True)
        await service.recall(owner, "What are my project settings?")
        await model.ainvoke([HumanMessage(content='Return only {"ready": true}.')])
        for repeat in range(repeats):
            for index, case in enumerate(CASES):
                offset = (index + repeat) % len(MODES)
                for mode in MODES[offset:] + MODES[:offset]:
                    trial = Trial(case=case.name, repeat=repeat + 1, mode=mode, expected=case.expected)

                    async def invoke(messages: list[BaseMessage]) -> BaseMessage:
                        start = perf_counter()
                        try:
                            reply = await model.ainvoke(messages)
                            trial.finish_reason = reply.response_metadata.get("finish_reason")
                            usage = getattr(reply, "usage_metadata", None)
                            if usage:
                                trial.input_tokens = usage.get("input_tokens")
                                trial.output_tokens = usage.get("output_tokens")
                            return reply
                        finally:
                            trial.model_seconds = perf_counter() - start

                    # Scope IDs route retrieval but are not otherwise sent to the model.
                    # State the same caller identity in every arm so 'my project' is unambiguous.
                    identity = "Bob" if case.other_user else "Alice"
                    instructions = (
                        INSTRUCTIONS + f" The current user is {identity}. "
                        "All supplied memory evidence belongs to the current project."
                    )
                    agent = MemoryAgent(RunnableLambda(invoke), TrialMemory(service, trial, owner), instructions)
                    start = perf_counter()
                    try:
                        answer = await agent.ask(
                            other if case.other_user else owner, case.question, mode != "no_memory"
                        )
                        trial.answer = answer.text
                        trial.memories = answer.memories
                        trial.correct = score(answer.text, case.expected)
                    except Exception as exc:
                        trial.error = type(exc).__name__
                    trial.total_seconds = perf_counter() - start
                    run.trials.append(trial)
                    save()
                    print(
                        f"{len(run.trials)}/{len(CASES) * len(MODES) * repeats} {mode} {case.name}: "
                        f"correct={trial.correct} total={trial.total_seconds:.2f}s error={trial.error}",
                        flush=True,
                    )
    finally:
        await service.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory for raw results and report")
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    load_dotenv(override=False)
    asyncio.run(run_benchmark(args.output, args.repeats))


if __name__ == "__main__":
    main()
