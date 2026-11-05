# Exercise hints and solutions

Attempt the chapter exercise before reading this page.

| Exercise | Hint | Solution / verification |
|---|---|---|
| Memory survives process exit | Reuse identity, not Python objects | Run SDK retain and recall separately against the same persistent service. Inspect evidence after restarting the service. |
| Two users | Keep app identity authoritative | Use two banks, two separate conversation states, and the same source ID. Inspect both recall results. |
| LangGraph prompt placement | `output_key` changes the node's output | Add `memory_context: str | None` to your graph state; set `output_key="memory_context"`; construct your model prompt using that field. Inspect the exact model input. |
| Stale graph context | Empty list is an update, not necessarily deletion | Compare current recall node with commit `7ba944aa4^`; the fix emits `RemoveMessage` for the reserved memory-message ID. The offline lab checks current behavior, not an execution of the old revision. |
| Pydantic request scope | Factory closures capture arguments | Construct tools/instructions using the current authenticated user's bank and current query before creating/running the request's agent. Assert SDK arguments for Alice and Bob. |
| Pydantic shared-agent extension | Read typed dependencies at call time | Define a dependency dataclass with `client`, `bank_id`, and `query`. Implement your own async tool/instructions function using `ctx.deps`; do not expect built-in `takes_ctx=False` tools to read it. |
| Avoid transcript replay | Write the delta | Keep a cursor/source ID in your application and retain only newly accepted content. Record retained character count per turn. |
| Memory outage | Test each surface separately | Tools/nodes raise; instructions helpers fall back. Decide whether your app should answer without memory or stop, then test that policy. |
| Compare memory strategies | Keep all other inputs fixed | Record answer rubric, retrieved IDs/text, call counts, elapsed time and model usage for no-memory, hooks, and tools runs. |

Source: [reviewed Hindsight integrations](https://github.com/vectorize-io/hindsight/tree/ee3bd049ebe3b96b7d1120328429102100c1e28e/hindsight-integrations).
