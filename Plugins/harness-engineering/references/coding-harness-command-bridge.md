# Coding Harness Command Bridge

Use this when HE is operating inside a `coding-harness` managed repo.

## Detection

Treat the repo as managed when repo-local evidence such as `harness.contract.json`, `.harness/`, Harness docs, Project Brain, north-star evidence, or Harness-managed Linear state is present.

When uncertain, inspect first and record `coding_harness.mode: unknown`.

## Lifecycle State

Preserve this block in structured output or handoff notes:

```yaml
coding_harness:
  mode: coding-harness-managed|generic-he|unknown
  linear_state: S0_TRIAGE|S1_READY|S2_IN_PROGRESS|S3_IN_REVIEW|S4_DONE|S5_FAIL|unknown|not_applicable
  blocked_overlay: true|false|unknown|not_applicable
  transition_event: scoped|start|progress_tick|pr_opened|handoff_ready|merged|blocked|unblocked|fail|not_applicable
  transition_command: "<harness linear ... command, Linear action, or blocked reason>"
  project_brain_status: updated|not_applicable|blocked|not_checked
  north_star_evidence_status: pass|blocked|not_applicable|not_checked
  harness_commands_run: []
  harness_commands_blocked: []
```

In managed repos, `project_brain_status: not_applicable` is valid only when `.harness/` and Project Brain surfaces are truly absent.

## Stage Gates

| Stage | Required coding-harness behavior |
| --- | --- |
| `he-brainstorm` | Resolve/create Linear before durable handoff; write brainstorm docs under `.harness/brainstorm/**.md` or folded ideation docs under `.harness/ideate/**.md`; run `harness brainstorm-gate --json` when present; if blocked, return a ready-to-create Linear payload. |
| `he-spec` | Resolve/create Linear before tracked specs; write specs under `.harness/specs/**.md`; include Linear Work Item Contract and acceptance traceability; run or block any repo spec/Linear gate. |
| `he-plan` | Write plans under `.harness/plan/**.md`; run or block `harness plan-gate --require-plan-id --require-traceability --json`; preserve acceptance IDs, plan IDs, Linear keys, and future PR evidence. |
| `he-work` | Inspect branch, dirty state, and Harness artifacts; run/block `blast-radius`, `policy-gate`, `preflight-gate`, and `validation-plan`. |
| `he-code-review` | Review `Linear -> spec/source IDs -> plan -> PR -> validation`; run/block docs, review, CodeRabbit, learnings, context, and north-star gates. |
| `he-compound` | Map earliest incomplete HE stage plus Harness lifecycle state; refresh Project Brain when `.harness/knowledge/**`, `.harness/decisions/**`, or `.harness/review-log.md` changed. |

Record exact pass/fail/blocked outcomes. If north-star evidence is unavailable, cap readiness. Never collapse Linear, Project Brain, spec, plan, PR, and validation into one chat summary.

## Blocker Handling

Approval, network, missing-file, permission, lint, timeout, test, and git-state blockers are expected operational states. Classify them explicitly:

```yaml
harness_blocker:
  type: approval_required|network|missing_file|permission|lint_failure|timeout|test_failure|git_state|tool_unavailable
  exact_command_or_path: "<command, path, or tool>"
  recovery_step: "<smallest next action>"
```

Do not hide a blocked Harness gate by falling back to generic prose. A blocked gate is valid evidence when the exact command/path and recovery step are preserved.
