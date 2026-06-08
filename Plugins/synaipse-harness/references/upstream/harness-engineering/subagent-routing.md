# Subagent Routing For Harness Engineering

## Purpose
Define the Harness Engineering stage-to-subagent routing contract so stages use consistent helper roles, only call roles that are actually available, and continue safely when delegated coverage is unavailable.

## Source Of Truth
Use [routing-map.json](routing-map.json) as the machine-readable source of truth for stage policies and mapped roles.

Use `~/.codex/agents/manifest.json` as the runtime availability source for subagent roles. The manifest may be either:

- a top-level array of role records, for example `[{"role":"worker"}]`
- an object with an `agents` array, for example `{"agents":[{"role":"worker"}]}`

Do not invent or prefer `he-*` role aliases. Stage names use the `he-*` prefix; subagent role names must be the exact canonical role names from `routing-map.json` and must resolve in the runtime manifest before they are launched.

## Inventory Policy
`subagent_inventory_policy` in `routing-map.json` classifies installed Codex agents:

- `he_relevant_roles` must be mapped to at least one Harness Engineering stage whenever they exist in the manifest.
- `global_non_he_roles` are intentionally kept outside the Harness Engineering lifecycle because they belong to separate plugin, CI, design, security, or operator workflows.
- `retired_roles` must not remain in the runtime manifest. If one is needed again, reintroduce it through `[[codex-agent-creator]]` with a concrete stage mapping or explicit global-owner rationale.

## Resolution Contract
1. Select exactly one Harness Engineering stage.
2. Load the selected stage from `subagent_stage_map` in `routing-map.json`.
3. Preserve the full mapped role set for the stage; do not silently drop missing roles.
4. Read manifest role names from the top-level array or `.agents[]`.
5. Split mapped roles into `available` and `missing` against the manifest.
6. Auto-spawn only available roles and only when the stage policy allows it.
7. If auto-spawn is unavailable, unsafe, or any mapped role is missing, continue inline and emit fallback guidance.
8. When a missing role represents coding, testing, correctness, reliability,
   security, adversarial, or agent-native coverage, emit coverage parity
   evidence before handoff. Inline continuation must name the replacement
   checklist, evidence inspected, unresolved risk, and whether the gap blocks
   `he-work`, closure, or external mutation.

## Auto-Launch Policies
- `always`: launch baseline roles by default when they are available and spawning is safe.
- `conditional`: launch only when the user explicitly requested delegation (`delegation`, `subagents`, `swarm`, `external-delegate`) or when stage risk signals justify specialist lanes.
- `manual-only`: do not auto-spawn; provide explicit role advice when delegation would help.

## Fallback Contract
When auto-spawn is unavailable or one or more mapped roles are missing:

1. Continue the stage in the main thread without blocking.
2. Emit one concise note listing unavailable or missing roles.
3. Keep the planned role list visible so coverage gaps are traceable.
4. Add a `coverage_parity` block for each missing high-risk role with:
   `lens`, `inline_checks_completed`, `evidence`, `unresolved_risk`, and
   `blocks_handoff`.
5. Route missing role creation or installation to `[[codex-agent-creator]]`.

Fallback message template:

```text
Subagent assist unavailable in this run. I will continue inline.
Mapped roles: <comma-separated mapped roles>.
Available roles: <comma-separated available roles or none>.
Missing/unavailable roles: <comma-separated missing roles or none>.
Coverage parity: <lens -> inline checks/evidence/unresolved risk/blocks_handoff>.
If delegated coverage is required, provision missing roles with [[codex-agent-creator]] and rerun this stage with delegation enabled.
```

## Output Requirement For Stage Skills
Every Harness Engineering stage output should include, in prose or structured fields:

- selected stage name
- subagent policy (`always`, `conditional`, or `manual-only`)
- roles used automatically
- roles recommended for manual launch
- roles missing from the manifest
- `coverage_parity` for missing high-risk roles, including whether the missing
  lens blocks handoff, closure, or mutation
