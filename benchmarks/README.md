# Local benchmark runs

Use [the final comparison](2026-11-05-local/REPORT.md). Every directory also contains raw `results.json` with per-request answers, evidence, timing and token counts.

## Result and interpretation

All 36 final requests completed without API errors; every model response finished with `stop`.

| Mode | Stored facts correct | Unknown/scope checks | Median answer latency |
|---|---:|---:|---:|
| No memory | 0/8 | 4/4 | 6.80 s |
| Hindsight | 8/8 | 4/4 | 16.32 s |
| Source supplied directly | 8/8 | 4/4 | 15.72 s |

Hindsight made past project facts available across fresh requests. The memory-free model consistently returned null instead of guessing. Supplying the original source directly achieved the same answer accuracy in this small test. This demonstrates the value of persistence/retrieval when an app no longer has the facts in its current prompt; it does not demonstrate an accuracy advantage over supplying complete context.

The single source took 62.93 seconds to ingest. Median Hindsight recall was 0.08 seconds. Most answer time was spent in Muse Glimmer: mean completion tokens were 93.3 without memory, 248.2 with Hindsight, and 190.0 with supplied context. These completion counts include model reasoning. The slowest Hindsight response took 38.35 seconds. The small median difference between Hindsight and supplied context is not evidence of a statistically reliable speed difference.

For the stored-fact questions alone, median answer times were 6.84, 17.90, and 15.72 seconds respectively. The all-question table includes the faster unknown-user cases. Two repeats of six synthetic cases are a learning experiment, not a production evaluation. There were no distractor documents, changing facts, concurrent users, or business-tool tasks.

Practical lessons: pass relevant authenticated identity into agent instructions, allow enough output budget for Muse Glimmer's reasoning, retain selected verified information, and inspect retrieved evidence. The two discarded pilots explain how these settings were discovered. Eight sample/benchmark unit tests and explicit Ruff checks passed; the repository lint hook ran but does not cover the example package.

## Environment

- Date: November 5, 2026. Timestamps inside result files are UTC.
- Hardware: Apple M4 Max, 64 GiB RAM; macOS arm64.
- Local model: Muse Glimmer 30B UD, Q6_K_XL, API identifier `muse-glimmer-30b`, 16,384-token loaded context.
- Model endpoint: LM Studio at `localhost:1234/v1`.
- Hindsight: dedicated Docker service at `localhost:8889`, with the image digest and configuration in `../compose.yaml`.
- Python 3.12.9, langchain-openai 1.7.4, langchain-core 1.7.6, openai 3.46.0, hindsight-client 1.2.0 (editable from this fork).
- Workspace HEAD: `919885bb9a350ba0cf2650af4405ccba4897222e`; the sample and benchmark are local additions.
- Embedding/reranking use the container defaults. Retain extraction and agent answers use the local model. Observation consolidation is disabled in the sample.
- Server prompt caches remain enabled; no concurrent benchmark requests are made. These are single-machine warm-service measurements, not a throughput or cold-start study.

## Pilot runs retained for transparency

1. `2026-11-05-pilot-256-tokens`: stopped after six completed trials. Three responses were empty and exhausted the 256-token output budget. A diagnostic response confirmed that reasoning tokens consume completion-token budget. The final run uses 1,024 tokens for every mode.
2. `2026-11-05-pilot-implicit-identity`: stopped after four completed trials. The question referred to “my project,” while evidence named Alice without identifying the current speaker. Hindsight and directly supplied context both produced abstentions. The final protocol identifies Alice or Bob explicitly in every mode and declares evidence scoped to the current project.

The pilot results are excluded from the final score and latency table. They document protocol changes made during this exploratory benchmark. The final cases reuse the same source/questions, so this is not a held-out evaluation.

Each run has a separate synthetic bank. Data remains in the dedicated demo service for inspection. No existing personal memory bank is part of this benchmark.
