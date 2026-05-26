# Adversarial Review — PR #215

## Findings (severity-ranked)

### 1. High — Runtime-proof can pass even when the user handle resolves outside workspace runtime
- Classification: introduced by current patch
- Evidence:
  - Trigger: user runtime root link is healthy (`~/.agents/skills -> <workspace>/.agents/skills`), but an individual user handle path resolves to an unexpected external location.
  - Execution path:
    - [Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:1240](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:1240) defines `handle_points_to_workspace`.
    - [Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:1245](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:1245) returns `runtime_link.points_to_workspace_runtime` when `_path_is_under(handle_path, expected_runtime)` is false.
    - [Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:1268](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:1268) uses this result for `agents_user_runtime_ready`.
  - Failure outcome:
    - A poisoned or stale per-handle path can be treated as runtime-ready solely because the root symlink is healthy, producing a false pass in command-handle proof and masking handle-level drift.
- Remediation suggestion:
  - Keep the rooted-source compatibility intent, but require handle-level containment/target validation (for example, verify the handle resolves under expected runtime or matches workspace handle target) before granting runtime-ready.

### 2. Medium — Doctor blocks editable roots based on static classification while claiming manifest override support
- Classification: introduced by current patch
- Evidence:
  - Trigger: owner repo intentionally declares a non-default root as canonical in `skills-sdk.json` per new project-manifest contract.
  - Execution path:
    - [Infrastructure/scripts/lib/ask/commands/skills_impl.py:2515](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2515) hard-codes `.codex/skills` as `client_runtime_config`.
    - [Infrastructure/scripts/lib/ask/commands/skills_impl.py:3467](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:3467) fails `projection_ownership` when source classification is runtime/config.
    - [Infrastructure/scripts/lib/ask/commands/skills_impl.py:3477](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:3477) tells users to declare root in owner manifest.
    - New manifest schema exists ([Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:1](/Users/jamiecraik/dev/agent-skills/Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:1)) and is wired in config ([Infrastructure/config/skills-sdk.json:98](/Users/jamiecraik/dev/agent-skills/Infrastructure/config/skills-sdk.json:98)), but this doctor path does not read/resolve that manifest (no manifest consumption in this check path).
  - Failure outcome:
    - Legitimate owner-declared source roots can still be blocked by doctor despite guidance saying declaration unblocks editability, causing policy/implementation divergence and repeated false blockers.
- Remediation suggestion:
  - Resolve `skills-sdk.json` in doctor ownership checks and gate failure on effective manifest classification rather than static path heuristics alone.

## Open Questions
- Should runtime-proof treat a healthy root symlink as sufficient evidence, or must every handle path also prove containment under expected runtime?
- Is `skills-sdk.project.v1` intended to be normative for doctor decisions now, or only advisory metadata until a later integration step?

## No-finding coverage notes
- Checked schema wire-up consistency for new check key `projection_ownership` across contracts/tests; no immediate schema-key drift found.
- Checked removal of top-level `next_command_decision` from doctor schema; no immediate break detected in current touched tests.
- Checked added runtime-observation partial-status mutation ([runtime_adapters.py:683](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:683)); behavior appears consistent with intended downgrade semantics.

WROTE: artifacts/reviews/adversarial-reviewer-pr215.md
