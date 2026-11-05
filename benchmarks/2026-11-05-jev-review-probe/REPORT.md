# Live reviewer diagnostic: history makes review more selective

48 live Jev calls: six draft pairs, two evidence conditions, two repeats. No worker inference. The drafts are deliberately authored, balanced examples; these are not naturally occurring worker mistakes. Added as a diagnostic after early end-to-end observations; not held out.

| Observed behavior | No recalled history | With recalled history |
|---|---:|---:|
| Supported factual drafts released | 0/10 | 10/10 |
| Unsupported drafts withheld | 12/12 | 12/12 |
| Supported clarification drafts unnecessarily withheld | 2/2 | 2/2 |
| Service errors | 0/24 | 0/24 |

The same question, draft, rubric and 0.60 threshold are used in both evidence conditions. With-history uses real Hindsight recall from the completed benchmark's synthetic bank; no drafts/results are retained. Order is rotated. Raw states and provider responses are preserved.

The benefit is selectivity: evidence lets the reviewer release supported facts instead of withholding everything. Both conditions withhold the unsupported drafts. Both conditions also withhold the two supported clarification drafts. With history, Jev selects proceed at confidence 0.25 and 0.30; without history, it selects clarify at 0.58 and 0.50. All four fall below the 0.60 threshold and are routed to review. This is an additional limitation of the gate.

The raw `release_matches_supported_label` field records literal draft-release agreement only. Do not interpret it as overall task accuracy. These controlled results do not overturn the end-to-end regression or establish general review quality. Repeats are not independent cases.
