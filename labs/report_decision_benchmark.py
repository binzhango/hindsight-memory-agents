"""Recompute a Markdown report from saved live benchmark trials."""

import argparse
import json
from pathlib import Path

from memory_agents.decision_benchmark import MODES, summarize


def report(record):
    rows = record["trials"]
    stats = summarize(rows)
    lines = [
        "# Live Hindsight + Jev benchmark",
        "",
        f"Worker: {record['worker_model']}. Runner: `{record['revision']}`.",
        f"Completed trials: {len(rows)} / {len(record['cases']) * 4 * record['repeats']}.",
        "Exploratory synthetic cases; repeat runs are not independent tasks.",
        "",
        "| Mode | Successful outcomes | Accepted non-success | Withheld | Errors | Median total | Median recall | Median worker | Median Jev |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for mode in MODES:
        if mode not in stats:
            continue
        s = stats[mode]
        lines.append(
            f"| {mode} | {s['correct']}/{s['n']} | {s['accepted_wrong']} | {s['withheld']} | {s['errors']} | "
            f"{s['median_total_seconds']:.2f}s | {s['median_recall_seconds']:.2f}s | "
            f"{s['median_worker_seconds']:.2f}s | {s['median_jev_seconds']:.2f}s |"
        )
    lines += ["", "## Paired combined versus memory-only", ""]
    index = {(r["case"], r["repeat"], r["mode"]): r for r in rows}
    pairs = [
        (r, index[(r["case"], r["repeat"], "combined")])
        for r in rows
        if r["mode"] == "memory" and (r["case"], r["repeat"], "combined") in index
    ]
    wins = sum(not a["correct"] and b["correct"] for a, b in pairs)
    losses = sum(a["correct"] and not b["correct"] for a, b in pairs)
    ties = len(pairs) - wins - losses
    lines += [
        f"Matched pairs: {len(pairs)}. Combined improves {wins}, regresses {losses}, ties {ties}.",
        "These are descriptive paired counts, not a significance claim.",
        "",
        "## Per-case success counts",
        "",
        "| Case | Baseline | Memory | Jev | Combined |",
        "|---|---:|---:|---:|---:|",
    ]
    for case in record["cases"]:
        cells = []
        for mode in MODES:
            trials = [r for r in rows if r["case"] == case["id"] and r["mode"] == mode]
            cells.append(f"{sum(r['correct'] for r in trials)}/{len(trials)}")
        lines.append("| " + case["id"] + " | " + " | ".join(cells) + " |")
    lines += ["", "## Review-stage audit", ""]
    for mode in ("jev", "combined"):
        if mode not in stats:
            continue
        s = stats[mode]
        lines.append(
            f"- {mode}: {s['reviewed_drafts']} reviewed drafts; {s['good_drafts_withheld']} correct drafts withheld; "
            f"{s['bad_drafts_withheld']} incorrect drafts withheld. Provider errors remain separately counted."
        )
    lines += [
        "",
        "## Scope and limitations",
        "",
        "Six stored-fact questions plus unknown-release and other-scope cases. Unknown/scope succeeds with JSON null or clarification; "
        "generic review is not success. Accepted known answers require exact JSON values. Errors stay in denominators.",
        "Memory-free arms cannot know arbitrary project history. Compare combined against memory-only to judge added Jev value. "
        "No prompt or threshold tuning from these results. No held-out or general reasoning claim.",
        "Accepted non-success includes abstentions (JSON null on known-fact cases), not just incorrect factual claims.",
        "Separate stage medians do not sum to the total median. Ingestion is excluded from answer time. "
        "The server caches are warm and not controlled. Read PROTOCOL.md and raw results.json for details.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("results", type=Path)
    args = p.parse_args()
    target = args.results.with_name("REPORT.md")
    target.write_text(report(json.loads(args.results.read_text())))
    print(target)
