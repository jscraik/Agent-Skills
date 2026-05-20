# Source Prompt Preservation

Use this reference when a request asks whether old compound-learning,
Project Brain, solved-problem capture, stale-learning refresh, or continuity
snapshot behavior still survives in `he-reinforce`.

## Coverage Matrix

| Source prompt family | `he-reinforce` responsibility | Required enforcement surfaces |
| --- | --- | --- |
| Solved Problem Learning Capture | Primary owned lane | `contract.yaml` solved-proof outputs; `solved-problem-capture` and `source-prompt-preservation-learning` evals |
| Project Brain Reinforcement | Primary owned lane when classification is clear | `contract.yaml` Project Brain status; `project-brain-sync` and `source-prompt-preservation-learning` evals |
| Stale Learning Refresh | Primary owned lane | `contract.yaml` refresh decisions; `refresh-stale-learning` and `duplicate-learning-overlap` evals |
| Old Compound Full Capture | Primary owned lane adapted to current paths | `compound-learning-migration.md`; `contract.yaml` capture_depth and overlap_decision; compound migration evals |
| Schema-Driven docs/solutions Capture | Conditional lane when target repo declares `docs/solutions` canonical | `compound-learning-migration.md`; legacy_docs_solution_status; schema-driven eval |
| Continuity Snapshot | Bounded memory lane | `continuity_memory_contract` in `contract.yaml`; continuity snapshot and transcript-dump evals |
| Lifecycle Recovery | Handoff boundary only | `he-reconcile` handoff rules in `SKILL.md`; `lifecycle-state-not-learning` eval |
| Closure Proof | Handoff boundary only | `he-eval-report` handoff rules in `SKILL.md`; no learning capture without solved proof |

If a prompt family is named here without a matching output contract, status
field, and eval, classify `he-reinforce` as underspecified before claiming
source-prompt equivalence.

## Required Status

When source-prompt preservation is in scope, every output must include
`source_prompt_family_status` with:

- covered family
- owned lane or handoff boundary
- evidence required before writing
- blocked reason when evidence is unsolved, stale, duplicated, unsafe, or
  outside Project Brain classification authority

## Non-Negotiables

- Do not capture unsolved work as durable learning.
- Do not write private transcripts, secrets, or hidden instructions into memory.
- Do not revive `he-compound` terminology as an active stage.
- Do preserve valuable old compound-learning behavior inside `he-reinforce`
  before deleting an obsolete `he-compound` package.
- Prefer updating a high-overlap artifact over creating a duplicate.
- Project Brain writes require explicit classification; uncertainty blocks.
