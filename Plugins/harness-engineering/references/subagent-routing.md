# Generic Desktop Collaborator Routing For Harness Engineering

## Purpose

Route Harness Engineering work by task capability rather than a fictional
named-role selection mechanism. Codex Desktop can spawn generic collaborators,
but its reserved collaboration schema does not accept `agent_type`.

## Source Of Truth

Use [routing-map.json](routing-map.json) as the machine-readable source of truth.
Route by task capability, authority, evidence requirements, and stop condition.
`desktop_collaboration_contract` declares this runtime boundary, and a
stage's baseline and conditional capabilities describe the work packet for a
generic collaborator.

Do not use `~/.codex/agents/manifest.json` as a runtime availability source.
`task_name` is a label, not a selected role.

## Resolution Contract

1. Select exactly one Harness Engineering stage.
2. Load its capabilities from `subagent_stage_map`.
3. Build a capability packet containing task capability, authority, evidence
   requirements, and stop condition.
4. Spawn a generic collaborator only when the stage policy permits it and the
   work can be bounded by that packet. Do not pass `agent_type`.
5. If a capability cannot be covered by a collaborator, continue inline only
   when the packet's evidence requirements can still be met; otherwise record
   a coverage gap.

## Auto-Launch Policies

- `always`: launch baseline capability packets when spawning is safe.
- `conditional`: launch only when the user explicitly requests delegation or
  risk signals justify a bounded supporting lane.
- `manual-only`: do not auto-spawn; state the capability packet that would
  make delegation useful.

## Fallback Contract

When generic collaboration is unavailable, unsafe, or incomplete:

1. Continue the stage inline without silently claiming equivalent coverage.
2. Name the capabilities covered and capabilities not covered.
3. Add a `coverage_parity` block for each uncovered high-risk capability with
   `lens`, `inline_checks_completed`, `evidence`, `unresolved_risk`, and
   `blocks_handoff`.
4. Do not create or install a named role as a workaround. Revisit only when
   Desktop exposes a supported selection field.

## Output Requirement For Stage Skills

Every stage closeout includes the selected stage, subagent policy,
`capabilities_covered`, `capabilities_not_covered`, and coverage parity for
each uncovered high-risk capability.
