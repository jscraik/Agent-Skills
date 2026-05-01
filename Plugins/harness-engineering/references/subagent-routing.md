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
Compatibility note: `he-compound` and `he-compound-refresh` are legacy Harness Engineering stage aliases retained for routing continuity.

| Stage | Policy | Baseline roles | Conditional roles (by signal) |
|---|---|---|---|
| `he-router` | `manual-only` | `none` | `he-repo-research-analyst`, `he-learnings-researcher` when stage intent is ambiguous |
| `he-compound` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-session-historian` for deep resume/recovery; `he-spec-flow-analyzer` for artifact trust ambiguity |
| `he-ideate` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-issue-intelligence-analyst` for issue/theme-heavy ideation |
| `he-brainstorm` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-best-practices-researcher` when external constraints materially shape requirements |
| `he-spec` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-best-practices-researcher`, `he-framework-docs-researcher` for standards/framework-sensitive contracts |
| `he-deepen-spec` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher`, `he-spec-flow-analyzer` | `he-coherence-reviewer`, `he-scope-guardian-reviewer`, `he-product-lens-reviewer`, `he-design-lens-reviewer`, `he-security-lens-reviewer`, `he-reliability-reviewer`, `he-architecture-strategist`, `he-api-contract-reviewer`, `he-data-integrity-guardian`, `he-deployment-verification-agent` |
| `he-plan` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-best-practices-researcher`, `he-framework-docs-researcher`, `he-spec-flow-analyzer` |
| `he-deepen-plan` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-feasibility-reviewer`, `he-coherence-reviewer`, `he-scope-guardian-reviewer`, `he-product-lens-reviewer`, `he-design-lens-reviewer`, `he-security-lens-reviewer`, `he-reliability-reviewer`, `he-architecture-strategist`, `he-api-contract-reviewer`, `he-data-integrity-guardian`, `he-deployment-verification-agent` |
| `he-improve` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `he-best-practices-researcher`, `he-framework-docs-researcher`, `worker`, `he-testing-reviewer`, `he-correctness-reviewer`, `he-performance-reviewer` |
| `he-refine` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `worker`, `he-testing-reviewer`, `he-correctness-reviewer`, `he-design-implementation-reviewer`, `he-julik-frontend-races-reviewer` |
| `he-work` | `conditional` | `worker` (isolated slices only) | `he-correctness-reviewer`, `he-testing-reviewer`, `he-security-reviewer`, `he-performance-reviewer`, `he-data-integrity-guardian`, `he-reliability-reviewer`, `he-api-contract-reviewer`, `he-deployment-verification-agent`, `he-design-implementation-reviewer`, `he-julik-frontend-races-reviewer` |
| `he-fix-bugs` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `worker`, `he-testing-reviewer`, `he-correctness-reviewer`, `he-reliability-reviewer`, `he-performance-reviewer`, `he-security-reviewer` |
| `he-prune-branches` | `manual-only` | `none` | `he-repo-research-analyst` when repo/worktree topology is ambiguous and delegation is explicitly requested |
| `he-tdd` | `always` | `he-testing-reviewer`, `he-correctness-reviewer` | `he-security-reviewer`, `he-data-integrity-guardian`, `he-performance-reviewer`, `he-architecture-strategist`, `he-code-simplicity-reviewer` |
| `he-code-review` | `always` | `he-agent-native-reviewer`, `he-learnings-researcher`, `he-code-simplicity-reviewer` | `he-kieran-rails-reviewer`, `he-kieran-typescript-reviewer`, `he-kieran-python-reviewer`, `he-julik-frontend-races-reviewer`, `he-design-implementation-reviewer`, `he-architecture-strategist`, `he-api-contract-reviewer`, `he-security-reviewer`, `he-performance-reviewer`, `he-data-integrity-guardian`, `he-schema-drift-detector`, `he-reliability-reviewer`, `he-deployment-verification-agent` |
| `he-technical-review` | `always` | `he-correctness-reviewer`, `he-testing-reviewer`, `he-code-simplicity-reviewer` | `he-kieran-rails-reviewer`, `he-kieran-typescript-reviewer`, `he-kieran-python-reviewer`, `he-security-reviewer`, `he-performance-reviewer`, `he-data-integrity-guardian`, `he-schema-drift-detector`, `he-reliability-reviewer`, `he-deployment-verification-agent`, `he-api-contract-reviewer`, `he-architecture-strategist`, `he-maintainability-reviewer`, `he-julik-frontend-races-reviewer`, `he-spec-flow-analyzer`, `he-feasibility-reviewer`, `he-adversarial-reviewer` |
| `he-reliability-review` | `always` | `he-reliability-reviewer`, `he-learnings-researcher` | `he-api-contract-reviewer`, `he-security-reviewer`, `he-performance-reviewer`, `he-data-integrity-guardian`, `he-data-migration-expert`, `he-deployment-verification-agent`, `he-architecture-strategist`, `he-adversarial-reviewer` |
| `he-compound-refresh` | `conditional` | `he-repo-research-analyst`, `he-learnings-researcher` | `worker` for one-at-a-time replacement drafting after explicit delegation approval |

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
