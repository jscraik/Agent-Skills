# Context7 Decision Guidance (Trimmed From SKILL.md)

Use this reference when deeper strategic guidance is needed without expanding `SKILL.md`.

## Philosophy and tradeoffs
- Prioritize current-source evidence over memory when behavior may have drifted.
- Prefer narrow, implementation-shaped retrieval queries over broad documentation pulls.
- If ambiguity remains after retrieval, ask for minimal clarification rather than filling gaps with assumptions.

## Execution path policy
- Default path: CLI-first using `op run --env-file ~/.codex/.env -- ctx7 ...`.
- Docs retrieval backup path: MCP (`resolve_library_id` + `query_docs`) when CLI is unavailable.
- Final backup path: API helper (`python3 Infrastructure/scripts/context7.py`) when CLI and MCP cannot run.
- Skill install/generate/setup flows remain CLI-only; do not simulate those via MCP.

## Quota and failure handling
- If Context7 quota is exceeded, state that explicitly instead of silently switching sources.
- Recommend auth remediation: `ctx7 login` (or API key path) before retry.
- If API backup is used after quota or CLI/MCP failure, label that path in `source_basis`.
- If no retrieval path is available, ask for minimal clarification or report a concrete blocker.

## Caveats
- Do not treat weak fuzzy library matches as authoritative.
- Do not skip validation steps when output will drive implementation decisions.
- Do not replace engineering judgment with a rigid checklist; adapt to repo constraints and risk.

## Adaptation heuristics
- Small tasks: one focused retrieval query with explicit assumptions.
- Medium tasks: compare two likely library matches and explain why one was selected.
- Large tasks: produce version-scoped guidance plus a short risk list for migration gaps.

## Decision prompts
- Why is this the right library match?
- What version constraints are inferred vs confirmed?
- Which part of the final answer is direct documentation vs interpretation?
- Did we stay within attempt caps (`library` <= 3, `docs` <= 3)?
- Which execution path was used (`cli_primary`, `mcp_backup`, or `api_backup`)?
