# Agent Testing Gates

## Table of Contents

- [Validation order](#validation-order)
- [Failure policy](#failure-policy)

## Validation order

1. Run the smallest relevant behavior or contract check for the changed surface.
2. When authorized source or projection changes require regeneration, run
   `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh --workspace`.
   This command mutates generated projections and indexes; it is not a
   prerequisite for read-only review or unrelated documentation changes.
   Home runtime synchronization requires its separately selected authority.
3. For documentation changes, run
   `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
   and `bash scripts/check-doc-style.sh` when documentation changes are staged.
4. Run `python3 Infrastructure/scripts/skill-graph/plan_graph_lint.py .agents/PLANS.md`
   when that plan index is touched.
5. Run the applicable aggregate gate from
   [Validation and Checks](/Docs/agents/04-validation.md), including
   `bash Infrastructure/scripts/validation-and-linting/verify-work.sh` when required.
6. Before merge, review the actual candidate using the uncommitted, base, or
   commit scope described in [Validation and Checks](/Docs/agents/04-validation.md#config-sensitive-checks).

## Failure policy

- Stop dependent checks at the first required failure. In repair mode, fix the
  in-scope cause and rerun the same check. In audit mode, report it without
  inferring edit authority. Continue independent authorized checks.
- Classify pre-existing, unrelated-worktree, and environment failures separately.
  Do not expand the task to repair them or claim their blocked evidence passed.
