# Source Prompt Preservation

Use this reference when an eval report must prove that original source-prompt
behavior survived implementation, routing, projection, or lifecycle hardening.

## Coverage Matrix

| Source prompt family | `he-eval-report` responsibility | Required enforcement surfaces |
| --- | --- | --- |
| Closure-Grade Eval Report | Primary owned lane | `eval-report-contract.md`, `eval-report-template.md`, `contract.yaml`, `closure-proof-report`, and `source-prompt-closure-preservation` evals |
| Drift Detection & Source-Prompt Closure | Primary owned lane | `drift-taxonomy.md`; `partial-source-coverage-blocks-repo-wide-closure`, `inherited-drift-signal-dropped-blocks-closure`, and `source-prompt-closure-preservation` evals |
| Linear Completion Safety | Recommendation only, no mutation | `linear-completion-policy.md`; accept/challenge/rework and implementation-only evals |
| Reinforcement / Learning Capture | Handoff boundary only | `he-reinforce` handoff rules; eval report may recommend capture but must not write learning artifacts as closure proof |
| Reframe / Strategy / Plan Source Coverage | Inherited evidence only | Compare approved upstream artifacts and report gaps; route missing cognition back to owning HE stage |

If a prompt family is named here without a matching report field, blocker, and
eval, classify `he-eval-report` as underspecified before claiming closure proof.

## Required Status

When source-prompt closure is in scope, every report must include
`source_prompt_family_status` with:

- covered upstream skill or prompt family
- evidence source and confidence
- inherited drift signals preserved or explicitly absent
- validation/proof artifacts that support closure
- blockers for partial coverage, missing proof, or local-only validation

## Non-Negotiables

- Implementation status is not closure proof.
- Missing validation is blocked or not-run, never pass.
- Partial source-prompt coverage blocks repo-wide or milestone closure.
- Live Linear closure requires explicit approval outside this skill.
- A closure report can recommend reinforcement, but learning capture belongs to
  `he-reinforce`.
