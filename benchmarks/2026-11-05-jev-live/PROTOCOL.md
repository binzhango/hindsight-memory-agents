# Live Hindsight + Jev exploratory benchmark

## Frozen run protocol

Runner revision: `b38a7af` (committed before running). Eight cases × four modes × two repeats = 64 trials. Six cases require stored facts; one asks for an unknown release date; one asks from another user's scope. The distractor case quotes an unapproved database suggestion. Full source, questions, expected labels and instructions are in results.json.

- Worker: Muse Glimmer (`muse-glimmer-30b`), temperature 0, 1024 output tokens, fresh messages on every trial.
- Memory: live Hindsight with the repository's existing retrieval settings. Memory-only and combined each receive the same synthetic source in separate new banks. Other-user queries select a distinct empty bank. Scope routing is not an authorization penetration test.
- Jev: live TypeSafe classifier, default requested model `jev-latest`, confidence threshold 0.60. Actual response model, request ID, usage, probabilities and confidence are recorded per call. The reviewer receives the same selected evidence as the worker; only review adds the draft.
- Every model input excludes case IDs, expected answers, and scoring labels. Expected facts intentionally occur in the retained source.
- Execution: sequential, rotated mode order per case/repeat. Recall and worker warm-up precede trials. Services and caches remain warm; these are not throughput or cold-start timings.
- Source ingestion is measured separately and excluded from per-answer times. Partial results save after every completed trial.

## Scoring

Known facts require disposition `answered` and valid JSON with only `answer`, matching the expected string (case-insensitive, surrounding whitespace ignored; numeric ports allowed). A correct rejected draft does not count as a completed task. Unknown/scope cases accept JSON null or a `clarify` disposition. A generic `review` result is never automatically correct. Errors and malformed output count as failures.

Report successful outcomes with full denominators; accepted non-successes (including null on known-fact questions); withheld answers; service errors; review-stage good drafts withheld and bad drafts caught. Preserve preflight stops separately in the raw traces. A wrong draft withheld is caught before release but does not complete a known-fact task.

Total, recall, worker, and Jev medians are reported separately and need not add up. Token usage is available in raw worker and decision records; monetary costs are not estimated.

## Interpretation

This is a small synthetic, exploratory comparison, not held-out validation. Cases were written for this integration; repeat runs are not independent new scenarios. Memory-free arms lack arbitrary historical facts by design. Their scores measure missing-context behavior, not intelligence. The decisive added-value comparison is combined versus memory-only.

No prompt, case, threshold or scoring change is made in response to this run's results. A ceiling result or regression must be reported as such. The deterministic decision lab is separate and is not part of live accuracy scores.
