> **Aborted pilot — excluded from final comparison.** Only six of 36 planned trials completed. Three answers were empty and consumed the entire 256-token output budget. A diagnostic call confirmed that Muse Glimmer uses completion tokens for reasoning. The final run uses 1,024 tokens for all modes. These partial observations are retained for transparency.

# Local memory benchmark

Run: `20261105T122216Z-84a2b36c`; model: `muse-glimmer-30b`; started UTC: 2026-11-05T12:22:16.042258+00:00.
Retain (one source document): **62.99 s**, excluded from answer latency.

| Mode | Known facts correct | Unknown/scope checks correct | All correct | Median total | Median recall | Median model | Mean input tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| no_memory | 0/2 | 0/0 | 0/2 | 6.96 s | 0.00 s | 6.96 s | 127.5 |
| hindsight | 1/2 | 0/0 | 1/2 | 13.89 s | 0.09 s | 13.80 s | 328.5 |
| provided_context | 0/2 | 0/0 | 0/2 | 15.73 s | 0.00 s | 15.73 s | 181.5 |

## Method

Six cases × three modes × 2 repeats. All calls are sequential, with rotated mode order. Each request starts with fresh messages; no chat history or answer is retained. The same model, system instructions, questions, temperature 0 and 256-token output cap apply to all modes. One model call and one recall warm up the services before measured trials. Server prompt caches are not disabled; these are warm-service timings on one Mac, not throughput measurements.

`no_memory` uses empty evidence. `hindsight` recalls the stored source via the real server. `provided_context` supplies the original source directly, without Hindsight, only for its owner. This third mode controls for having the facts already available in a prompt.

Scoring requires valid JSON with only an `answer` key and exact expected value (case-insensitive, surrounding whitespace ignored; numeric port accepted). Unknown and other-user cases require JSON null. Failures count as incorrect and are saved. No LLM judge is used. Inspect the raw answers and retrieved facts in results.json.

This is a small synthetic cross-session factual-memory test, not a standard benchmark or a measure of general reasoning, coding, production authorization, large-memory retrieval, or long-term updates. Repeats are not independent tasks. A memory-free model cannot know arbitrary historical facts; the comparison shows context availability, not improved model intelligence. Recall/model/total columns are separate medians and need not add up. A short prompt containing all facts can be sufficient when it fits your application.

## Per-trial answers

### database / no_memory / repeat 1

Correct: False; total: 6.53 s; error: none.

```text
{"answer": null}
```

### database / hindsight / repeat 1

Correct: True; total: 11.11 s; error: none.

```text
{"answer": "SQLite"}
```

### database / provided_context / repeat 1

Correct: False; total: 15.30 s; error: none.

```text

```

### codename / hindsight / repeat 1

Correct: False; total: 16.68 s; error: none.

```text

```

### codename / provided_context / repeat 1

Correct: False; total: 16.17 s; error: none.

```text

```

### codename / no_memory / repeat 1

Correct: False; total: 7.39 s; error: none.

```text
{"answer": null}
```
