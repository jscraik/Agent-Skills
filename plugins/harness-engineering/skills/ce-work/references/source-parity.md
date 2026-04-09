# CE Work Prompt Parity Map

## Table of Contents
- [Purpose](#purpose)
- [Source prompts and donor patterns](#source-prompts-and-donor-patterns)
- [Parity mapping](#parity-mapping)
- [Intentional modernizations](#intentional-modernizations)
- [No-loss checklist](#no-loss-checklist)

## Purpose
This document records how the prompt sources for the execution stage were migrated into `ce-work` so the conversion stays auditable.

## Source prompts and donor patterns
- canonical source prompt:
  - `/Users/jamiecraik/dev/configs/codex/prompts/workflow-work.md`
- donor prompts explicitly preserved:
  - `https://github.com/EveryInc/compound-engineering-plugin/tree/0ae91dcc298721e5b2c4ab6d1fc6f76a13b6f67c/plugins/compound-engineering/skills/ce-work`
  - `https://github.com/EveryInc/compound-engineering-plugin/tree/0ae91dcc298721e5b2c4ab6d1fc6f76a13b6f67c/plugins/compound-engineering/skills/ce-work-beta`
- packaging target:
  - `/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-work/`

## Parity mapping
| Prompt behavior | Preserved in skill | Notes |
|---|---|---|
| execute plan, todo, or spec systematically | `SKILL.md` overall structure | Preserved directly |
| prefer plans over raw specs and escalate risky specs to planning first | `Workflow -> Phase 0` | Preserved directly |
| read linked artifacts such as `origin`, parent spec, or related plan | `Workflow -> Phase 0` | Preserved directly |
| restate the contract before coding | `Workflow -> Phase 1` | Preserved directly |
| branch/worktree safety checks before execution | `Workflow -> Phase 1`, `references/execution-modes.md` | Preserved directly |
| derive tasks from implementation units, files, tests, and verification | `Workflow -> Phase 1` | Preserved directly |
| choose inline, serial, parallel, or swarm strategy | `Workflow -> Phase 2`, `references/execution-modes.md` | Preserved directly |
| honor `Execution note`, test-first, and characterization-first posture | `Workflow -> Phase 3` | Preserved directly |
| keep plan checkboxes and task state aligned with real progress | `Workflow -> Phase 3`, `Validation` | Preserved directly |
| system-wide test check around callbacks, persistence, parity, and error handling | `Workflow -> Phase 3` | Preserved directly |
| stop when implementation reveals design drift and update artifacts first | `Workflow -> Phase 4` | Preserved directly |
| run deep validation before finishing | `Workflow -> Phase 5` | Preserved directly |
| UI execution requires prototype gate and shipped-surface validation | `Workflow -> Phase 5`, `references/ui-execution.md` | Preserved directly |
| final shipping package includes summary, tests, and post-deploy validation notes | `Workflow -> Phase 6`, `references/handoff-and-shipping.md` | Preserved directly |
| beta external delegation mode | `Execution modes`, `references/execution-modes.md` | Preserved directly as an optional task-level modifier |
| beta environment guard and delegate fallback rules | `references/execution-modes.md` | Preserved directly |
| default full-review tier with inline-review exception | `Workflow -> Phase 6`, `references/handoff-and-shipping.md` | Preserved as repo-compatible handoff guidance |
| tiny bare-prompt execution compatibility | `Working agreement`, `Required inputs`, `Workflow -> Phase 0` | Preserved as a guarded compatibility path |
| optional swarm mode for explicit agent-team requests | `Workflow -> Phase 2`, `references/execution-modes.md` | Preserved directly |

## Intentional modernizations
- `workflow-work.md` was treated as the canonical source and the older `ce:work` / `ce:work-beta` prompts were folded in as donor behavior rather than separate competing skills.
- Legacy harness-specific commit and PR footer templates were replaced with portable shipping guidance so the skill does not hardcode stale vendor attribution or badge syntax.
- The execution workflow now states the lane choice explicitly as `plan-led | todo-led | small-spec-direct`, which makes raw-spec execution safer and easier to audit.
- UI execution behavior was moved into `references/ui-execution.md` so the main skill keeps the 2026 delivery rules without becoming excessively long.
- External delegation was preserved, but framed as a guarded optional modifier that falls back cleanly instead of being assumed available everywhere.
- Donor bare-prompt execution was preserved only as a tiny, low-risk compatibility path; this repo still keeps artifact-led execution as the default.
- Parallel execution is preserved as an execution strategy, but the skill avoids assuming that every platform or turn permits subagent spawning.
- `contract.yaml` and `evals.yaml` were added to improve routing reliability and validation coverage.
- non-route-critical standards and philosophy guidance were relocated to `references/style-and-operating-guidance.md` so `SKILL.md` stays execution-focused without losing context
- deterministic execution and verification role mapping is now explicit in `references/sub-agent-map.md`
- missing supporting references were restored for operational completeness: `references/mcp-integration.md` and `references/ce-anti-patterns.md`

## No-loss checklist
- plan, todo, and direct-spec execution paths are still present
- risky raw-spec execution is still blocked in favor of planning first
- linked artifacts are still read before implementation
- contract restatement is still required before coding
- execution-posture signals are still honored
- plan/task synchronization is still central
- system-wide validation is still required
- contract-drift updates are still required before continuing
- UI prototype and screenshot discipline is still present
- external delegate mode is still available
- final handoff still includes operational validation notes
