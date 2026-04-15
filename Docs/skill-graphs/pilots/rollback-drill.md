# Rollback Drill Report

- Generated at: `2026-02-25T11:47:29Z`

| Case | Rollout | Kill | Rollback | Exit | Status | Stop reason | Blocker |
|---|---|:---:|:---:|---:|---|---|---|
| baseline_active | active | ❌ | ❌ | 0 | passed | pass | none |
| kill_switch | active | ✅ | ❌ | 4 | aborted | aborted | kill_switch_activated |
| rollback_required | active | ❌ | ✅ | 5 | failed | dependency_missing | run_rollback_required |
| rollout_off | off | ❌ | ❌ | 5 | failed | policy_failed | run_rollforward_blocked |

Expected blockers:
- `kill_switch` -> `kill_switch_activated`
- `rollback_required` -> `run_rollback_required`
- `rollout_off` -> `run_rollforward_blocked`
