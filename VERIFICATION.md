# Observed verification

Verified on this Mac on 2026-11-05, using the actual local model and memory server.

## Runtime

- LM Studio model identifier: `muse-glimmer-30b` (installed Muse Glimmer 30B UD Q6_K_XL).
- Loaded context length: 16,384; one-hour idle TTL.
- LM Studio API: `http://localhost:1234/v1`.
- Dedicated sample Hindsight API: `http://localhost:8889`; control plane: `http://localhost:9998`.
- Docker image pinned by digest in `compose.yaml`; separate persistent volume.
- Agent inference and Hindsight extraction both use LM Studio. Observations/consolidation are disabled for this experiment.

## Checks and results

1. `uv sync` installed the locked environment with the fork's editable Python client.
2. `doctor` returned success: model ID advertised and sample database healthy.
3. A real `ask --no-memory` returned a text answer from Muse Glimmer with `memories: []`.
4. The planner's explicit `remember` ingested the synthetic fact: “For this project Alice requires Python, SQLite, and no paid external APIs.” Extraction took approximately 90 seconds on this run.
5. A separate `recall` process returned an extracted fact with a server-assigned ID:

   ```text
   Alice requires Python, SQLite, and no paid external APIs for this project | Involving: Alice
   ```

6. A fresh coder process recalled that fact and recommended Python, SQLite through the built-in `sqlite3` module, and no paid external API dependencies. Its response included the retrieved fact and its ID. No previous chat history was supplied to the coder.
7. Recall for `sample-bob` in the same project returned `[]`, while Alice's fact remained in Alice's bank. A first-time bank initially returned a server 404; the wrapper now recognizes that specific missing-bank response as empty memory. Unrelated 404s remain errors.
8. Six automated tests passed, covering scope boundaries, cross-role recall, baseline behavior, visible failures, first-time users, and explicit retention.
9. Ruff lint and formatting checks passed for the sample. The repository lint hook also ran; it reported no changed packages in its scope, so the sample was checked explicitly.

The example data is synthetic and remains in the dedicated demo volume so you can inspect it. These checks demonstrate the integration and one memory-use case; they do not measure general model quality, throughput, tool-calling capability, or production tenant authorization. The existing-agent adapter in the README is a recipe and was not executed against your separate applications.
