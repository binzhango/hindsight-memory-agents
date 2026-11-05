"""CLI for cross-agent, cross-process memory experiments."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from pydantic import BaseModel

from .app import MemoryAgent, MemoryService, Scope, Settings

ROLES = {
    "planner": "You are a project planner. Give a short actionable plan consistent with the user's constraints.",
    "coder": "You are a coding assistant. Recommend concrete implementation choices consistent with project constraints.",
}


class ModelEntry(BaseModel):
    id: str


class ModelList(BaseModel):
    data: list[ModelEntry]


async def doctor(settings: Settings) -> bool:
    ok = True
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        for name, url, key in [
            ("LM Studio", settings.lm_url + "/models", settings.lm_key),
            ("Hindsight", settings.memory_url + "/health", settings.memory_key),
        ]:
            try:
                async with session.get(url, headers={"Authorization": f"Bearer {key}"} if key else {}) as response:
                    response.raise_for_status()
                    data = await response.json()
                if name == "LM Studio":
                    ids = [m.id for m in ModelList.model_validate(data).data]
                    print("LM Studio models:", ", ".join(ids))
                    if settings.model not in ids:
                        print(
                            f"Configured model {settings.model!r} was not advertised; set LM_STUDIO_MODEL to its exact ID."
                        )
                        ok = False
                else:
                    print("Hindsight:", json.dumps(data))
            except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
                print(f"{name} unavailable: {type(exc).__name__}. Check {url} and authentication.")
                ok = False
    print("Hindsight's server-side model configuration is independent and is not verified by this health check.")
    return ok


async def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    for name in ("remember", "ask", "recall"):
        command = sub.add_parser(name)
        command.add_argument("text")
        command.add_argument("--user", required=True)
        command.add_argument("--project", default="demo")
        command.add_argument("--agent", choices=list(ROLES), default="planner")
        if name == "remember":
            command.add_argument("--document-id", help="Reuse to replace this source document")
        if name == "ask":
            command.add_argument("--no-memory", action="store_true", help="Baseline without recall")
    args = parser.parse_args()
    load_dotenv(args.env_file, override=False)
    settings = Settings.from_env()
    if args.command == "doctor":
        return 0 if await doctor(settings) else 1
    scope = Scope(args.user, args.project)
    memory = MemoryService(settings)
    try:
        if args.command == "remember":
            document = await memory.remember(scope, args.text, args.agent, args.document_id)
            print(f"Retain completed: bank={scope.bank_id} document={document}")
            print(
                "Use recall to inspect extracted facts; successful submission does not imply a particular fact count."
            )
        elif args.command == "recall":
            facts = await memory.recall(scope, args.text)
            print(json.dumps([f.model_dump() for f in facts], indent=2))
        else:
            agent = MemoryAgent(settings.chat_model(), memory, ROLES[args.agent])
            answer = await agent.ask(scope, args.text, use_memory=not args.no_memory)
            print(answer.model_dump_json(indent=2))
        return 0
    finally:
        await memory.close()


def main() -> None:
    try:
        code = asyncio.run(run())
    except KeyboardInterrupt:
        code = 130
    except Exception as exc:
        # Avoid dumping provider payloads or credentials into normal CLI output.
        print(f"Request failed ({type(exc).__name__}). Run doctor; inspect the relevant service logs.", file=sys.stderr)
        code = 1
    raise SystemExit(code)


if __name__ == "__main__":
    main()
