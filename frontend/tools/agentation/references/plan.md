# Agentation skill update plan

## Objective
Realign the `agentation` skill with the current public Agentation surface:
- React 18+ root install and dev-only mount.
- MCP setup via `add-mcp`, `init`, `doctor`, and the default server on `localhost:4747`.
- `endpoint` and `webhookUrl` as the primary integration props.
- Current hands-free workflows: watch mode, critique mode, and self-driving.

## Task graph

- **T1 (depends_on: [])** — Replace outdated env-script automation assumptions with docs-backed workflow guidance.
- **T2 (depends_on: [T1])** — Align webhook guidance to `webhookUrl`, current event types, and real `submit` verification.
- **T3 (depends_on: [T1])** — Align MCP guidance to `add-mcp`, `init`, `doctor`, current tool names, and `endpoint` debugging.
- **T4 (depends_on: [T2, T3])** — Update watch-mode state and readiness checker terminology (`self_driving` vs legacy `autopilot`).
- **T5 (depends_on: [T2, T3, T4])** — Refresh contract, evals, and metadata to match the current public site plus the original upstream skill compatibility route.
- **T6 (depends_on: [T5])** — Run focused skill validation plus broader docs validation and fix the first failing gate.

## Acceptance criteria

- Skill description routes to current Agentation integration and workflow tasks.
- Workflow distinguishes UI mount, `endpoint`, MCP, and `webhookUrl`.
- Current MCP commands and tool names are documented accurately.
- Critique and self-driving are described as workflow modes, not undocumented env toggles.
- Validation passes for the revised skill package.
