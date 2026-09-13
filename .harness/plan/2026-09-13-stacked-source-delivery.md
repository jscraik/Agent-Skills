---
schema_version: 1
plan_id: stacked-source-delivery-20260913
status: in_progress
owner: agent-skills
---

# Stacked source delivery

Consumer: Jamie and the reviewers of the September source-maintenance stack.
Scope: the 70 dirty entries inventoried on `codex/telos-runtime-owner`.
The original checkout is preserved. Delivery starts from current `main`
at `f1f2f212f56b9155b1a80d0cde78305490439204`; it does not replay the older
Telos commits already superseded by merged PR #505.

## Final ownership boundary

Skills SDK owns creation, repair, evaluation, judging, review, and handoff
tooling. Skills Foundry retains skill packages. Agent-Skills retires after
both destinations work independently. This stack preserves transitional
corrections; it does not establish permanent ownership or prove migration.

## Stack and checklist

- [x] Layer 1: shared guidance and PM validation; signed `10aa689a6`, pushed
  as `codex/stack-guidance-foundations`, PR #510 targets `main`.
- [x] Layer 2: factory routes and evaluator fixes; signed `e5f380726`, pushed
  as `codex/stack-skill-evaluation`, intended base is layer 1.
- [ ] Open layer 2 PR: execution approval rejects the body-file command for
  lacking a template flag, although its body preserves the template and
  GitHub CLI rejects combining that flag with a body file.
- [x] Layer 3 source commit: `f1f40365d` on
  `codex/stack-skill-package-guidance`, intended base is layer 2.
- [ ] Publish layer 3: its first push failed on missing worktree projection;
  workspace sync and the strict agents-md audit now pass. The generated index
  refresh accompanies this correction; PR creation remains a separate gate.
- [ ] Hosted checks and independent reviews: not completed by local proof.

## Local evidence boundary

Layer 1 focused tests passed: 19 tests and 32 subtests. Normal commit hooks
passed. The overdue Aidevcon review date was carried forward from the reviewed
local correction; the strict catalog check then reported 98 healthy assets.

Layer 2 focused tests passed: 46 tests and 161 subtests. The commit hook exposed
oversized evaluator functions. Helper extraction fixed that gate; tests,
Ruff, modularity, and normal commit hooks passed afterward. Forty pre/post
discovery comparisons returned identical results. Both factory package
verifications and the route, archive-link, and system-overlay checks passed.

All six layer 3 source audits passed, initially using source-only mode for
agents-md. The pre-push diagnostic then required its worktree projection.
`./bin/ask skills sync --scope workspace --projection flat --json --robot`
passed and materialized that projection without changing home links;
the strict agents-md audit passed afterward without source-only mode.
Package verification passed for agents-md, alignment-checkpoint,
pr-green-sweep, and simplify. Both frontend packages remain blocked for
package admission by rubric, provenance, and writing-shape gaps; their
source audits do not waive those requirements.

Plugin Eval used the existing primary-checkout wrapper against the delivery
files because this clean worktree has no Plugin Eval cache. Scores were
agents-md A/100, alignment-checkpoint A/100, frontend-design A/95,
pr-green-sweep C/77, simplify A/95, and frontend-ui-design A/95.
The pr-green-sweep failure is its deferred-context budget; it is not a
passing quality-target result. No release or runtime-readiness claim follows.
The earlier reconciliation plan retains historical proof tied to its named
checkout; that proof is not relabeled as fresh testing of this stack.

## Preserved local-only records

The eight raw runtime-proof JSON files for Telos and alignment-checkpoint
and the two untracked historical audit reports under `artifacts/reviews/`
remain in the original checkout. They contain local session identifiers or
machine paths and are not published as fresh review or runtime evidence.
This summary accounts for them without copying private provenance.

The full repository validation and the layer 3 commit hooks passed with zero
required failures and zero warnings. That source result does not waive the
separate package-admission or Plugin Eval failures recorded above.

Compatibility manifests, the root index, and the runtime-separation summary are regenerated
from the delivery tree rather than copied over newer main-branch state.
No home runtime links, installations, releases, merges, or cleanup are selected.
