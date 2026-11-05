"""Two-process live memory experiment. Requires an explicitly configured service."""

import argparse
import asyncio
import os
import time

from hindsight_client import Hindsight


async def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["retain", "recall", "reflect"])
    parser.add_argument("--bank", required=True, help="Use a disposable learning bank")
    parser.add_argument("--text", required=True, help="Content to retain or query to ask")
    parser.add_argument("--document", default="learning-preference")
    args = parser.parse_args()
    url = os.environ.get("HINDSIGHT_URL")
    if not url:
        parser.error("Set HINDSIGHT_URL explicitly, e.g. http://localhost:8888")
    client = Hindsight(base_url=url, api_key=os.environ.get("HINDSIGHT_API_KEY"), timeout=120)
    started = time.perf_counter()
    try:
        if args.operation == "retain":
            result = await client.aretain(
                bank_id=args.bank,
                content=args.text,
                document_id=args.document,
                update_mode="replace",
                tags=["learning"],
                retain_async=False,
            )
        elif args.operation == "recall":
            result = await client.arecall(bank_id=args.bank, query=args.text, budget="low", max_tokens=1024)
        else:
            result = await client.areflect(bank_id=args.bank, query=args.text, budget="low")
        print(result.to_json())
        print(f"Elapsed: {time.perf_counter() - started:.3f}s")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(run())
