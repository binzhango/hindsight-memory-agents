> **Aborted identity-ambiguous pilot — excluded from final comparison.** Facts name Alice, but the prompt asks about “my project” without telling the model who is speaking. Both Hindsight and supplied-context answers abstained despite evidence. The final protocol explicitly identifies Alice (or Bob) in every mode. Partial raw results remain here; they are not combined with the final scores.

# Local memory benchmark

Run: `20261105T122522Z-98ebb2f0`; model: `muse-glimmer-30b`; started UTC: 2026-11-05T12:25:22.151747+00:00.
Retain (one source document): **54.67 s**, excluded from answer latency.

| Mode | Known facts correct | Unknown/scope checks correct | All correct | Median total | Median recall | Median model | Mean input tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| no_memory | 0/1 | 0/0 | 0/1 | 7.12 s | 0.00 s | 7.11 s | 128.0 |
| hindsight | 0/2 | 0/0 | 0/2 | 36.26 s | 0.08 s | 36.18 s | 202.5 |
| provided_context | 0/1 | 0/0 | 0/1 | 37.04 s | 0.00 s | 37.04 s | 182.0 |

## Method

Six cases × three modes × 2 repeats. All calls are sequential, with rotated mode order. Each request starts with fresh messages; no chat history or answer is retained. The same model, system instructions, questions, temperature 0 and 1024-token output cap apply to all modes. One model call and one recall warm up the services before measured trials. Server prompt caches are not disabled; these are warm-service timings on one Mac, not throughput measurements.

`no_memory` uses empty evidence. `hindsight` recalls the stored source via the real server. `provided_context` supplies the original source directly, without Hindsight, only for its owner. This third mode controls for having the facts already available in a prompt.

Scoring requires valid JSON with only an `answer` key and exact expected value (case-insensitive, surrounding whitespace ignored; numeric port accepted). Unknown and other-user cases require JSON null. Failures count as incorrect and are saved. No LLM judge is used. Inspect the raw answers and retrieved facts in results.json.

This is a small synthetic cross-session factual-memory test, not a standard benchmark or a measure of general reasoning, coding, production authorization, large-memory retrieval, or long-term updates. Repeats are not independent tasks. A memory-free model cannot know arbitrary historical facts; the comparison shows context availability, not improved model intelligence. Recall/model/total columns are separate medians and need not add up. A short prompt containing all facts can be sufficient when it fits your application.

## Per-trial answers

### database / no_memory / repeat 1

Correct: False; total: 7.12 s; error: none.

```text
{"answer": null}
```

### database / hindsight / repeat 1

Correct: False; total: 34.20 s; error: none.

```text
{"answer": null}
```

### database / provided_context / repeat 1

Correct: False; total: 37.04 s; error: none.

```text
{"answer": null}
```

### codename / hindsight / repeat 1

Correct: False; total: 38.32 s; error: none.

```text
{"answer": null}
```
