# Subagent Routing For Harness Engineering

## Purpose
Define one canonical stage-to-subagent map for the `harness-engineering` plugin so CE stages pick consistent helper roles and always provide a fallback when automatic subagent spawning is unavailable.

## Agent Source Of Truth
Use `~/.codex/agents/manifest.json` as the runtime source of available roles.
Support both observed manifest shapes:
- top-level array of role records (for example `[{"role":"worker",...}]`)
- object wrapper with an `agents` array (for example `{"agents":[{"role":"worker",...}]}`)

Resolution contract:
1. Read `role` entries from either the top-level array or `.agents[]`.
2. Keep only mapped roles that exist in the manifest.
3. Auto-spawn available roles based on the stage policy below.
4. If auto-spawn is unavailable or a role is missing, continue inline and emit manual launch guidance.

## Auto-Launch Policies
- `always`: launch baseline roles by default.
- `conditional`: launch only when the user explicitly requested delegation (`delegation`, `subagents`, `swarm`, `external-delegate`) or when risk signals justify specialist lanes.
- `manual-only`: never auto-spawn; provide explicit role advice.

## Stage Map
| Stage | Policy | Baseline roles | Conditional roles (by signal) |
|---|---|---|---|
| `he-router` | `manual-only` | `none` | `repo-research-analyst`, `learnings-researcher` when stage intent is ambiguous |
| `he-compound` | `conditional` | `repo-research-analyst`, `learnings-researcher` | `session-historian` for deep resume/recovery; `spec-flow-analyzer` for artifact trust ambiguity |
| `he-ideate` | `conditional` | `repo-research-analyst`, `learnings-researcher` | `issue-intelligence-analyst` for issue/theme-heavy ideation |
| `he-brainstorm` | `conditional` | `repo-research-analyst`, `learnings-researcher` | `best-practices-researcher` when external constraints materially shape requirements |
| `he-spec` | `conditional` | `repo-research-analyst`, `learnings-researcher` | `best-practices-researcher`, `framework-docs-researcher` for standards/framework-sensitive contracts |
| `he-deepen-spec` | `conditional` | `repo-research-analyst`, `learnings-researcher`, `spec-flow-analyzer` | `coherence-reviewer`, `scope-guardian-reviewer`, `product-lens-reviewer`, `design-lens-reviewer`, `security-lens-reviewer`, `reliability-reviewer`, `architecture-strategist`, `api-contract-reviewer`, `data-integrity-guardian`, `deployment-verification-agent` |
| `he-plan` | `conditional` | `repo-research-analyst`, `learnings-researcher` | `best-practices-researcher`, `framework-docs-researcher`, `spec-flow-analyzer` |
| `he-deepen-plan` | `conditional` | `repo-research-analyst`, `learnings-researcher` | `feasibility-reviewer`, `coherence-reviewer`, `scope-guardian-reviewer`, `product-lens-reviewer`, `design-lens-reviewer`, `security-lens-reviewer`, `reliability-reviewer`, `architecture-strategist`, `api-contract-reviewer`, `data-integrity-guardian`, `deployment-verification-agent` |
| `he-work` | `conditional` | `worker` (isolated slices only) | `correctness-reviewer`, `testing-reviewer`, `security-reviewer`, `performance-reviewer`, `data-integrity-guardian`, `reliability-reviewer`, `api-contract-reviewer`, `deployment-verification-agent`, `design-implementation-reviewer`, `julik-frontend-races-reviewer` |
| `he-tdd` | `always` | `testing-reviewer`, `correctness-reviewer` | `security-reviewer`, `data-integrity-guardian`, `performance-reviewer`, `architecture-strategist`, `code-simplicity-reviewer` |
| `he-review` | `always` | `agent-native-reviewer`, `learnings-researcher`, `code-simplicity-reviewer` | `kieran-rails-reviewer`, `kieran-typescript-reviewer`, `kieran-python-reviewer`, `julik-frontend-races-reviewer`, `design-implementation-reviewer`, `architecture-strategist`, `api-contract-reviewer`, `security-reviewer`, `performance-reviewer`, `data-integrity-guardian`, `schema-drift-detector`, `reliability-reviewer`, `deployment-verification-agent` |
| `he-technical-review` | `always` | `correctness-reviewer`, `testing-reviewer`, `code-simplicity-reviewer` | `kieran-rails-reviewer`, `kieran-typescript-reviewer`, `kieran-python-reviewer`, `security-reviewer`, `performance-reviewer`, `data-integrity-guardian`, `schema-drift-detector`, `reliability-reviewer`, `deployment-verification-agent`, `api-contract-reviewer`, `architecture-strategist`, `maintainability-reviewer`, `julik-frontend-races-reviewer`, `spec-flow-analyzer`, `feasibility-reviewer` |
| `he-reliability-review` | `always` | `reliability-reviewer`, `learnings-researcher` | `api-contract-reviewer`, `security-reviewer`, `performance-reviewer`, `data-integrity-guardian`, `data-migration-expert`, `deployment-verification-agent`, `architecture-strategist`, `adversarial-reviewer` |
| `he-compound-refresh` | `conditional` | `repo-research-analyst`, `learnings-researcher` | `worker` for one-at-a-time replacement drafting after explicit delegation approval |

## Fallback Contract
When auto-spawn is unavailable or one or more required roles are missing:
1. Continue the stage in the main thread without blocking.
2. Emit one concise note listing missing or unavailable roles.
3. Provide manual launch guidance using this template:

```text
Subagent assist unavailable in this run. If you want delegated coverage, launch these roles from ~/.codex/agents/manifest.json: <comma-separated roles>.
Then rerun this stage with delegation enabled.
```

## Output Requirement For Stage Skills
Every CE stage output should include:
- selected stage name
- subagent policy (`always`, `conditional`, or `manual-only`)
- roles used automatically (if any)
- roles recommended for manual launch when fallback path is taken
