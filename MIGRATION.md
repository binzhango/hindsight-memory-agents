# Standalone extraction

Extracted November 5, 2026 from the locally authored `examples/lmstudio-memory-agents` and `docs/learning-guide/labs` in the Hindsight learning checkout. Original workspace HEAD: `919885bb9a350ba0cf2650af4405ccba4897222e`; upstream code base: `ee3bd049ebe3b96b7d1120328429102100c1e28e`.

The original sample and benchmark were local additions. Runtime code, tests, and measured result JSON were preserved. Packaging now installs Hindsight dependencies from the public upstream revision rather than a relative editable path. Documentation and lab paths were adapted for this repository. The lockfile was regenerated for a standalone environment; this does not retroactively change the recorded benchmark environment. See benchmarks/README.md for the original versions and hardware.

Only source, tests, synthetic results, documentation, lock/config templates, and license material were extracted. The local `.env`, virtual environments, caches, database volume, and model files were not copied. The Compose identity and persistent-volume name were preserved for users migrating the original local service.

## Standalone validation

A fresh Python 3.12 environment installed successfully with `uv sync --frozen --extra labs`. All eight sample/benchmark tests passed. Ruff lint and formatting checks passed for all ten Python source/test/lab files. The framework lab passed all four checks using the real installed adapters with simulated memory. The CLI help command loaded successfully. Original benchmark JSON files were compared byte-for-byte against the source checkout. No new live inference benchmark was performed during extraction.
