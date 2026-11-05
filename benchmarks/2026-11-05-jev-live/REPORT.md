# Live Hindsight + Jev benchmark

Worker: muse-glimmer-30b. Runner: `b38a7af3790b2c3e0c062fe56ba9fea8629dee50`.
Completed trials: 64 / 64.
Exploratory synthetic cases; repeat runs are not independent tasks.

| Mode | Successful outcomes | Accepted non-success | Withheld | Errors | Median total | Median recall | Median worker | Median Jev |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 4/16 | 12 | 0 | 0 | 8.79s | 0.00s | 8.79s | 0.00s |
| memory | 16/16 | 0 | 0 | 0 | 15.46s | 0.10s | 15.35s | 0.00s |
| jev | 4/16 | 0 | 16 | 0 | 0.26s | 0.00s | 0.00s | 0.26s |
| combined | 14/16 | 0 | 6 | 0 | 13.65s | 0.10s | 13.12s | 0.37s |

## Paired combined versus memory-only

Matched pairs: 16. Combined improves 0, regresses 2, ties 14.
These are descriptive paired counts, not a significance claim.

## Per-case success counts

| Case | Baseline | Memory | Jev | Combined |
|---|---:|---:|---:|---:|
| database | 0/2 | 2/2 | 0/2 | 2/2 |
| deployment | 0/2 | 2/2 | 0/2 | 2/2 |
| paid_api | 0/2 | 2/2 | 0/2 | 2/2 |
| port | 0/2 | 2/2 | 0/2 | 2/2 |
| command | 0/2 | 2/2 | 0/2 | 0/2 |
| distractor | 0/2 | 2/2 | 0/2 | 2/2 |
| unknown | 2/2 | 2/2 | 2/2 | 2/2 |
| other_scope | 2/2 | 2/2 | 2/2 | 2/2 |

## Review-stage audit

- jev: 0 reviewed drafts; 0 correct drafts withheld; 0 incorrect drafts withheld. Provider errors remain separately counted.
- combined: 10 reviewed drafts; 0 correct drafts withheld; 0 incorrect drafts withheld. Provider errors remain separately counted.

## Scope and limitations

Six stored-fact questions plus unknown-release and other-scope cases. Unknown/scope succeeds with JSON null or clarification; generic review is not success. Accepted known answers require exact JSON values. Errors stay in denominators.
Memory-free arms cannot know arbitrary project history. Compare combined against memory-only to judge added Jev value. No prompt or threshold tuning from these results. No held-out or general reasoning claim.
Accepted non-success includes abstentions (JSON null on known-fact cases), not just incorrect factual claims.
Separate stage medians do not sum to the total median. Ingestion is excluded from answer time. The server caches are warm and not controlled. Read PROTOCOL.md and raw results.json for details.
