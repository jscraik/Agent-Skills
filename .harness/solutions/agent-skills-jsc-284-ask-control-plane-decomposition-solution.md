---
schema_version: 1
artifact_id: agent-skills-jsc-284-he-compound-solution
artifact_type: he-compound-solution
canonical_slug: agent-skills-jsc-284
title: Agent Skills JSC-284 Ask Control Plane Decomposition Solution
harness_stage: he-compound
status: complete
traceability_required: true
origin: .harness/evals/agent-skills-jsc-284-eval.md
linear_issue: JSC-284
linear_milestone: Command surface and ask reliability
asset_family: ask control plane service extraction
owner: Agent Skills Team
source_artifact: .harness/evals/agent-skills-jsc-284-eval.md
freshness_reviewed_on: 2026-05-08
review_after_days: 90
project_brain_status: not_applicable
---

# Agent Skills JSC-284 Ask Control Plane Decomposition Solution

## Problem

`Infrastructure/scripts/lib/ask/commands/skills.py` had accumulated plugin
cache behavior, plugin source helper behavior, command adaptation, projection
coordination, proof-adjacent state, and runtime-budget concerns behind one
public command surface. The risk was not length alone. The real risk was that
future agents had to read too much mixed-context code to change a small cache
behavior safely.

The slice also exposed a governance trap: local implementation proof and Linear
closure are separate gates. Treating those as the same gate would either block
valid local work or mutate Linear from stale state.

## Resolution

Use a staged Harness Engineering path:

1. Preserve the public `./bin/ask` command contract first.
2. Extract plugin cache behavior into `ask.services.plugin_cache`.
3. Extract shared plugin source/materialization helpers into
   `ask.services.plugin_sources` so the service layer does not import from
   `ask.commands.*`.
4. Keep catalog/projection, proof enforcement, routing, and tool-resolution
   extractions out of the slice.
5. Repair adjacent parity blockers only when they directly block the slice:
   projection/catalog parity, local plugin picker expected surface, home plugin
   mirror pruning, and curated `agents-sdk` runtime-budget collision baseline.
6. Record local closure proof in `.harness/evals/**`.
7. Keep Linear issue closure blocked until live Linear state can be refreshed;
   after refresh, post closure proof and close children before the parent.

This preserves source/projection trust, reduces command-module coupling, and
keeps tracker mutation honest.

## Evidence

- `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`
  records `plan_ask_005_complete_linear_resolved`.
- `.harness/evals/agent-skills-jsc-284-eval.md` validates the HE eval-report
  closure gate and records Linear completion.
- `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`
  records detailed validation traces, changed-file classification, rollback
  status, and Linear traceability.
- `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md`
  defines proof levels and lifecycle states without implementing enforcement.
- `./bin/ask skills sync --scope workspace --projection rooted --dry-run --json`
  passed with trace `ae7aa5a8-0578-4f32-9fb9-6de30ea455a7`, preserving
  `plugin_cache_writes`, logs, command surface `95`, and mutation counts
  `219` writes, `6` deletes, `1` symlink.
- `./bin/ask repo doctor --json --robot` passed with trace
  `5954fd8e-642d-4fc6-8d9b-b723cff7269e`; `blocking: false`.
- `python3 -m pytest Infrastructure/tests/test_local_plugin_picker_surface.py -q`
  passed with `9 passed`.
- `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q`
  passed with `25 passed in 3.77s`.
- `python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py .harness/evals/agent-skills-jsc-284-eval.md`
  passed.
- `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/agent-skills-jsc-284-eval.md`
  passed.
- Linear live issue fetches verified `JSC-284`, `JSC-285`, `JSC-286`, and
  `JSC-287` as `Done`; closure proof comment
  `a54b9452-af8c-4498-bbba-ed61f92bd773` was posted to `JSC-284`.

## Maintenance Notes

- Do not let `ask.services.*` import from `ask.commands.*`; that recreates the
  command-to-command coupling the slice removed.
- Keep plugin cache dry-run fields and log strings stable unless a separate ADR
  changes the public command contract.
- Do not fold repo-surface diagnostic debt into this slice; repo doctor reports
  it as non-blocking diagnostic debt.
- Do not close future Linear tracker sets from stale local proof. Refresh live
  tracker state first, post closure proof, close children before the parent, and
  update local harness artifacts so they do not preserve obsolete blockers.
- If future decomposition slices touch catalog/projection, proof enforcement,
  routing, or tool resolution, select a fresh HE slice and eval artifact rather
  than widening this solved pattern.

## Project Brain Status

```yaml
project_brain_status: not_applicable
project_brain_evidence:
  source: ".harness/solutions/agent-skills-jsc-284-ask-control-plane-decomposition-solution.md"
  target: null
  reason: "No .harness/knowledge/** Project Brain target exists in this repo at capture time."
```
