# Local memory benchmark

Run: `20261105T122856Z-3c05c2e3`; model: `muse-glimmer-30b`; started UTC: 2026-11-05T12:28:56.514581+00:00.
Retain (one source document): **62.93 s**, excluded from answer latency.

| Mode | Known facts correct | Unknown/scope checks correct | All correct | Median total | Median recall | Median model | Mean input tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| no_memory | 0/8 | 4/4 | 4/12 | 6.80 s | 0.00 s | 6.80 s | 144.3 |
| hindsight | 8/8 | 4/4 | 12/12 | 16.32 s | 0.08 s | 16.24 s | 205.2 |
| provided_context | 8/8 | 4/4 | 12/12 | 15.72 s | 0.00 s | 15.72 s | 189.3 |

## Method

Six cases × three modes × 2 repeats. All calls are sequential, with rotated mode order. Each request starts with fresh messages; no chat history or answer is retained. The same model, system instructions, questions, temperature 0 and 1024-token output cap apply to all modes. The current user is identified as Alice (or Bob in the other-user case) in every mode, and supplied evidence is explicitly scoped to the current project. One model call and one recall warm up the services before measured trials. Server prompt caches are not disabled; these are warm-service timings on one Mac, not throughput measurements.

`no_memory` uses empty evidence. `hindsight` recalls the stored source via the real server. `provided_context` supplies the original source directly, without Hindsight, only for its owner. This third mode controls for having the facts already available in a prompt.

Scoring requires valid JSON with only an `answer` key and exact expected value (case-insensitive, surrounding whitespace ignored; numeric port accepted). Unknown and other-user cases require JSON null. Failures count as incorrect and are saved. No LLM judge is used. Inspect the raw answers and retrieved facts in results.json.

This is a small synthetic cross-session factual-memory test, not a standard benchmark or a measure of general reasoning, coding, production authorization, large-memory retrieval, or long-term updates. Repeats are not independent tasks. A memory-free model cannot know arbitrary historical facts; the comparison shows context availability, not improved model intelligence. Recall/model/total columns are separate medians and need not add up. A short prompt containing all facts can be sufficient when it fits your application.

## Per-trial answers

### database / no_memory / repeat 1

Correct: False; total: 6.87 s; error: none.

```text
{"answer": null}
```

### database / hindsight / repeat 1

Correct: True; total: 15.40 s; error: none.

```text
{"answer": "SQLite"}
```

### database / provided_context / repeat 1

Correct: True; total: 13.67 s; error: none.

```text
{"answer": "SQLite"}
```

### codename / hindsight / repeat 1

Correct: True; total: 19.30 s; error: none.

```text
{"answer": "maple-731"}
```

### codename / provided_context / repeat 1

Correct: True; total: 10.29 s; error: none.

```text
{"answer": "maple-731"}
```

### codename / no_memory / repeat 1

Correct: False; total: 6.41 s; error: none.

```text
{"answer": null}
```

### port / provided_context / repeat 1

Correct: True; total: 17.44 s; error: none.

```text
{"answer": "4317"}
```

### port / no_memory / repeat 1

Correct: False; total: 8.84 s; error: none.

```text
{"answer": null}
```

### port / hindsight / repeat 1

Correct: True; total: 16.05 s; error: none.

```text
{"answer": "4317"}
```

### test_command / no_memory / repeat 1

Correct: False; total: 6.79 s; error: none.

```text
{"answer": null}
```

### test_command / hindsight / repeat 1

Correct: True; total: 37.72 s; error: none.

```text
{"answer": "uv run pytest -q"}
```

### test_command / provided_context / repeat 1

Correct: True; total: 17.86 s; error: none.

```text
{"answer": "uv run pytest -q"}
```

### unknown / hindsight / repeat 1

Correct: True; total: 16.08 s; error: none.

```text
{"answer": null}
```

### unknown / provided_context / repeat 1

Correct: True; total: 19.21 s; error: none.

```text
{"answer": null}
```

### unknown / no_memory / repeat 1

Correct: True; total: 6.93 s; error: none.

```text
{"answer": null}
```

### other_user / provided_context / repeat 1

Correct: True; total: 7.45 s; error: none.

```text
{"answer": null}
```

### other_user / no_memory / repeat 1

Correct: True; total: 6.63 s; error: none.

```text
{"answer": null}
```

### other_user / hindsight / repeat 1

Correct: True; total: 6.67 s; error: none.

```text
{"answer": null}
```

### database / hindsight / repeat 2

Correct: True; total: 16.51 s; error: none.

```text
{"answer": "SQLite"}
```

### database / provided_context / repeat 2

Correct: True; total: 13.99 s; error: none.

```text
{"answer": "SQLite"}
```

### database / no_memory / repeat 2

Correct: False; total: 6.81 s; error: none.

```text
{"answer": null}
```

### codename / provided_context / repeat 2

Correct: True; total: 11.32 s; error: none.

```text
{"answer": "maple-731"}
```

### codename / no_memory / repeat 2

Correct: False; total: 6.63 s; error: none.

```text
{"answer": null}
```

### codename / hindsight / repeat 2

Correct: True; total: 19.44 s; error: none.

```text
{"answer": "maple-731"}
```

### port / no_memory / repeat 2

Correct: False; total: 9.16 s; error: none.

```text
{"answer": null}
```

### port / hindsight / repeat 2

Correct: True; total: 16.22 s; error: none.

```text
{"answer": "4317"}
```

### port / provided_context / repeat 2

Correct: True; total: 17.82 s; error: none.

```text
{"answer": "4317"}
```

### test_command / hindsight / repeat 2

Correct: True; total: 38.35 s; error: none.

```text
{"answer": "uv run pytest -q"}
```

### test_command / provided_context / repeat 2

Correct: True; total: 19.39 s; error: none.

```text
{"answer": "uv run pytest -q"}
```

### test_command / no_memory / repeat 2

Correct: False; total: 7.55 s; error: none.

```text
{"answer": null}
```

### unknown / provided_context / repeat 2

Correct: True; total: 20.85 s; error: none.

```text
{"answer": null}
```

### unknown / no_memory / repeat 2

Correct: True; total: 6.65 s; error: none.

```text
{"answer": null}
```

### unknown / hindsight / repeat 2

Correct: True; total: 16.43 s; error: none.

```text
{"answer": null}
```

### other_user / no_memory / repeat 2

Correct: True; total: 6.65 s; error: none.

```text
{"answer": null}
```

### other_user / hindsight / repeat 2

Correct: True; total: 6.62 s; error: none.

```text
{"answer": null}
```

### other_user / provided_context / repeat 2

Correct: True; total: 6.56 s; error: none.

```text
{"answer": null}
```
