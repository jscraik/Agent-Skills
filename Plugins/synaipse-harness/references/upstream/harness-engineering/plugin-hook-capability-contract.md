# Plugin Hook Capability Contract

Bundled plugin hooks are optional runtime guardrails. They are not the Harness
Engineering lifecycle, not a replacement for `.harness` artifacts, and not a
hidden authority for Linear closure.

Use this contract when a Harness Engineering stage proposes, plans, reviews, or
depends on plugin-declared hooks such as `.codex-plugin/plugin.json` `hooks`,
`hooks/hooks.json`, `SessionStart`, `PreToolUse`, or `Stop` behavior.

## Load When

- A spec or plan proposes plugin hooks, runtime guardrails, startup context, or
  lifecycle enforcement inside a plugin.
- A code review touches plugin manifests, hook declarations, hook commands, or
  scripts invoked from hooks.
- An eval or closure recommendation depends on hook behavior.
- A compound/state reconstruction uses startup context, tool blocking, or stop
  handoff evidence that may have been produced by plugin hooks.

## Capability Status

- `plugin_hooks` is feature-gated runtime behavior. Treat it as optional unless
  the active Codex config proves plugins, hooks, `plugin_hooks`, and the target
  plugin are enabled.
- HE must preserve a fallback skill, validator, or eval path while
  `plugin_hooks` can be disabled or unavailable.
- Plugin hooks may make guardrails more portable, but they must not be the only
  correctness path for closure, routing, or artifact generation.
- Plugin hook declarations should prefer the default `hooks/hooks.json`
  convention unless a custom manifest path or inline config has a concrete
  reason.
- Hook commands must use plugin-scoped placeholders such as `${PLUGIN_ROOT}` and
  `${PLUGIN_DATA}` when referencing plugin-owned files. Hardcoded machine paths
  are portability defects unless explicitly justified.

## Required Check

Record this check when plugin hooks are relevant:

```yaml
plugin_hook_capability_check:
  verified_runtime_failure: "<repeated failure or none>"
  proposed_hook_event: "SessionStart | PreToolUse | Stop | Other | none"
  feature_gate_status: "enabled | disabled | unknown | not_applicable"
  fallback_path: "<skill, validator, eval, or manual route>"
  portability_check: "pass | fail | partial | not_applicable"
  side_effect_class: "read_only | artifact_write | repo_edit | external_update | destructive | completion_gate"
  lifecycle_authority: "limited | invalid | not_applicable"
  outcome: "proceed | warn | block | defer | not_applicable"
```

## Safe HE Hook Candidates

- `SessionStart` context primer: may surface concise HE orientation, active
  stage hints, or validator reminders. It must not create or mutate `.harness`
  artifacts.
- `PreToolUse` closure guard: may warn or block risky completion commands when
  required eval proof is missing. It must provide a visible fallback path.
- `Stop` handoff guard: may remind the agent to record status, blockers, and
  next route. It must not silently mark work complete or mutate Linear.

## Forbidden Hook Behavior

- Hidden lifecycle execution that skips HE skills, specs, plans, eval reports,
  or `.harness` proof artifacts.
- Automatic Linear mutation, issue closure, status changes, or milestone updates.
- Hook-only enforcement for safety or completion claims while `plugin_hooks` is
  default-off or unproven in the active session.
- Hardcoded absolute paths to plugin-owned scripts when `${PLUGIN_ROOT}` or
  `${PLUGIN_DATA}` would work.
- Destructive commands, network mutation, credential access, or repo edits unless
  separately approved by the relevant security and workflow contracts.

## Decision Rules

1. Do not recommend bundled hooks unless a repeated or high-cost runtime failure
   shows that lifecycle-timed enforcement is the smallest effective mechanism.
2. If a validator, eval, or skill instruction can prevent the failure with lower
   runtime risk, prefer that path.
3. If hook enforcement is proposed, specify the fallback path that still works
   when `plugin_hooks` is disabled.
4. If closure depends on plugin hooks, require hook behavior proof and fallback
   proof. Skill-only validation is insufficient.
5. Treat plugin hook output as runtime evidence. It can inform `.harness`
   artifacts, but it cannot replace them.
6. If hook state affects startup/context, record it in source artifact trace or
   runtime evidence rather than treating it as durable cognition.
