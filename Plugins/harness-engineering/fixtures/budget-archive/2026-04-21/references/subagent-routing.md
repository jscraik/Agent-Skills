# Subagent Routing For Harness Engineering

## Purpose
Define one canonical stage-to-subagent map for the `harness-engineering` plugin so Harness Engineering stages pick consistent helper roles and always provide a fallback when automatic subagent spawning is unavailable.

## Agent Source Of Truth
Use `~/.codex/agents/manifest.json` as the runtime source of available roles.
Support both observed manifest shapes:
- top-level array of role records (for example `[{"role":"worker",...}]`)
- object wrapper with an `agents` array (for example `{"agents":[{"role":"worker",...}]}`)

Resolution contract:
1. Read `role` entries from either the top-level array or `.agents[]`.
2. Preserve the full mapped role set for the selected stage (do not silently drop missing roles).
3. Prefer `he-*` roles in stage maps where parity aliases exist; keep canonical role names only where no `he-*` alias exists.
4. Split mapped roles into `available` and `missing` against the manifest.
5. Auto-spawn available roles based on the stage policy below.
6. If auto-spawn is unavailable or any mapped role is missing, continue inline and emit manual launch guidance.

## Auto-Launch Policies
- `always`: launch baseline roles by default.
- `conditional`: launch only when the user explicitly requested delegation (`delegation`, `subagents`, `swarm`, `external-delegate`) or when risk signals justify specialist lanes.
- `manual-only`: never auto-spawn; provide explicit role advice.

## Stage Map
Compatibility note: folded stage names are preserved as nested context but route through parent stages. See [folded skill context](./folded-skill-context.md).

| Stage | Policy | Baseline roles | Conditional roles (by signal) |
|---|---|---|---|
| `he-router` | `manual-only` | `none` | `he-repo-research-analyst`, `he-learnings-researcher` when stage intent is ambiguous |
| `he-compound` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-session-historian` for deep resume/recovery; `he-spec-flow-analyzer` for artifact trust ambiguity |
| `he-brainstorm` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-best-practices-researcher` when external constraints materially shape requirements |
| `he-spec` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-best-practices-researcher`, `he-framework-docs-researcher` for standards/framework-sensitive contracts |
| `he-plan` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-best-practices-researcher`, `he-framework-docs-researcher`, `he-spec-flow-analyzer` |
| `he-improve` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-best-practices-researcher`, `he-framework-docs-researcher`, `worker`, `he-testing-reviewer`, `he-correctness-reviewer`, `he-performance-reviewer` |
| `he-work` | `conditional` | `worker` (isolated slices only) | `he-correctness-reviewer`, `he-testing-reviewer`, `he-security-reviewer`, `he-performance-reviewer`, `he-data-integrity-guardian`, `he-reliability-reviewer`, `he-api-contract-reviewer`, `he-deployment-verification-agent`, `he-design-implementation-reviewer`, `he-julik-frontend-races-reviewer` |
| `he-fix-bugs` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `worker`, `he-testing-reviewer`, `he-correctness-reviewer`, `he-reliability-reviewer`, `he-performance-reviewer`, `he-security-reviewer` |
| `he-code-review` | `always` | `he-agent-native-reviewer`, `he-learnings-researcher`, `he-code-simplicity-reviewer` | `he-kieran-rails-reviewer`, `he-kieran-typescript-reviewer`, `he-kieran-python-reviewer`, `he-julik-frontend-races-reviewer`, `he-design-implementation-reviewer`, `he-architecture-strategist`, `he-api-contract-reviewer`, `he-security-reviewer`, `he-performance-reviewer`, `he-data-integrity-guardian`, `he-schema-drift-detector`, `he-reliability-reviewer`, `he-deployment-verification-agent` |

Folded modes inherit the parent stage policy and add their preserved specialist context:

| Folded mode | Parent stage |
|---|---|
| `he-ideate` | `he-brainstorm` |
| `he-deepen-spec` | `he-spec` |
| `he-deepen-plan` | `he-plan` |
| `he-refine` | `he-improve` |
| `he-tdd` | `he-work` |
| `he-technical-review` | `he-code-review` |
| `he-reliability-review` | `he-code-review` |
| `he-compound-refresh` | `he-compound` |
| `he-prune-branches` | `he-router` with `agent-ops` branch-hygiene handoff |

## Fallback Contract
When auto-spawn is unavailable or one or more required roles are missing:
1. Continue the stage in the main thread without blocking.
2. Emit one concise note listing missing or unavailable roles.
3. Provide manual launch guidance using this template:

```text
Subagent assist unavailable in this run. If you want delegated coverage, launch these roles from ~/.codex/agents/manifest.json: <comma-separated roles>.
Then rerun this stage with delegation enabled.
If required roles are missing, create or install them with [[codex-agent-creator]] before rerunning delegation.
```

## Output Requirement For Stage Skills
Every Harness Engineering stage output should include:
- selected stage name
- subagent policy (`always`, `conditional`, or `manual-only`)
- roles used automatically (if any)
- roles recommended for manual launch when fallback path is taken
