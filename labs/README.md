# SDK and framework labs

Run from this standalone repository root:

```sh
uv sync --frozen --extra labs
uv run --extra labs python labs/framework_lab.py
```

The framework lab invokes real LangChain tools, a compiled LangGraph, and a Pydantic AI test-model agent against a simulated SDK client. Four PASS lines confirm routing, stale-context removal, Pydantic AI wiring, and its instructions-helper fallback. The mock returns the same evidence for different banks, so it tests routing rather than backend isolation.

For live SDK calls, first start the services described in the root README. The SDK lab reads exported environment variables (not `.env` automatically):

```sh
export HINDSIGHT_URL=http://localhost:8889
uv run python labs/sdk_lab.py retain --bank learning-alice --text 'Alice prefers tea.'
uv run python labs/sdk_lab.py recall --bank learning-alice --text 'What does Alice drink?'
uv run python labs/sdk_lab.py reflect --bank learning-alice --text 'Suggest a drink for Alice using what you know.'
```

Set `HINDSIGHT_API_KEY` in the shell if required. Each command starts a new process and prints response JSON and elapsed time. Reuse `--document` to replace a source, or choose a new document ID for an independent source. These calls create synthetic data and do not delete it afterward. Reflect is outside the historical LangChain benchmark.

See [exercise hints](solutions/README.md). Framework dependencies and the client are pinned to the same reviewed upstream revision in `pyproject.toml`; `uv.lock` fixes the transitive environment.
