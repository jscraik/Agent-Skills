# Skill Refactor Taxonomy

Use this reference when classifying lifecycle evidence for `skill-refactor` outputs.

## Root Cause Labels

- coverage gap: the skill does not cover an expected scenario, file type, or workflow.
- instruction drift: the skill guidance diverges from current repo policy or user steering.
- routing mismatch: the wrong skill handles the request, or the right skill does not trigger.
- quality regression: recent changes reduce score, clarity, correctness, or reliability.
- artifact-shape gap: produced reports, evals, or handoffs do not match the required schema.
- reader-contract gap: a human or evaluator cannot infer the intended action from the skill text.
- context-package conflict: entrypoint content belongs in references, scripts, or eval fixtures.
- missing observation path: there is no durable evidence stream for the recurring failure.
- missing validation: the skill lacks a command, eval, or gate proving the intended behavior.
- environment blocker: auth, sandboxing, tooling, or workspace state prevents trustworthy analysis.

## Evidence Strength

- weak: one unconfirmed signal, stale artifact, broad impression, or unverified transcript excerpt.
- moderate: one current report plus matching local evidence, or two related weak signals.
- strong: two independent current anchors, or one user-corrected failure plus matching validation evidence.

Do not recommend broad canonical changes from weak evidence. Use weak evidence to request the smallest missing artifact or propose observation.
