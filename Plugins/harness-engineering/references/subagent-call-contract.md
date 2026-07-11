# Generic Desktop Collaborator Call Contract

Harness Engineering stages must use the same Desktop-safe path before calling
or recommending a collaborator.

## Required Flow

1. Load the selected stage and `desktop_collaboration_contract` from
   `Plugins/harness-engineering/references/routing-map.json`.
2. Use the capability packet declared by `routing-map.json`. Build it with task capability, authority, evidence
   requirements, and stop condition.
3. Spawn only a generic Desktop collaborator, with the packet in its message.
   Do not pass `agent_type`.
4. If spawning is unavailable or unsafe, continue inline and identify the
   capabilities covered and capabilities not covered.
5. Do not create or install named roles as a workaround.

## Trigger Rules

- `always`: call baseline capability packets when spawning is safe.
- `conditional`: call only when user-requested delegation or risk signals
  justify a bounded supporting lane.
- `manual-only`: do not call helpers automatically; report the capability
  packet that would make delegation useful.

## Traceability Fields

Each stage closeout includes `subagent_policy`, `capabilities_covered`,
`capabilities_not_covered`, and `git_staging_status` when the stage wrote
artifacts.
