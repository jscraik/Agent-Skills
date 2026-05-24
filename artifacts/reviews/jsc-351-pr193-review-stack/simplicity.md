# Simplicity Review — PR #193 (efcade54646527beff3b60b37af898488e2df2a7)

## Scope reviewed
- Diff from origin/main (38ded61b31063bc1b5efe259ba4902cf65500b29) to PR head.
- Focus: simplification, overbuilding, duplication, terminology clarity, and minimal PR boundary.

## Findings (severity-ranked)

### HIGH — Duplicate policy truth introduced for default-visible system bridges
- Evidence:
  - Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py:39
  - Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py:267
  - Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py:44
  - Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py:259
  - Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py:355
- Why this is unnecessary complexity:
  - The PR introduces two new hard-coded sets ({"imagegen", "openai-docs"}) in separate modules instead of using a single policy-derived source.
  - This creates avoidable drift risk between discovery and budget validation logic for the same business rule.
- Simpler alternative:
  - Define one canonical constant in policy exports and import it in both modules.
  - Keep SYSTEM_BRIDGE_SKILL_NAMES for full bridge universe and a single DEFAULT_VISIBLE_SYSTEM_BRIDGE_SKILL_NAMES policy constant for default surface.

### MEDIUM — README normalization path in sync_skills_impl.sh is overbuilt and brittle
- Evidence:
  - Infrastructure/scripts/lifecycle-and-sync/sync_skills_impl.sh:1192-1273
- Why this is unnecessary complexity:
  - Multiple overlapping re.subn and re.sub passes target similar sentences, then add a dedupe cleanup regex.
  - The sequence is difficult to reason about, order-sensitive, and expensive to maintain for minor copy changes.
- Simpler alternative:
  - Normalize README summary with a single structured update path:
    1. Parse first paragraph block after # Agent Skills.
    2. Replace it with canonical text exactly once.
    3. Apply one numeric replacement for catalog count.
  - If regex must remain, reduce to one canonical pattern plus one fallback and fail hard when neither matches.

### LOW — PR boundary contains substantial historical artifact churn not required for runtime behavior
- Evidence:
  - artifacts/reviews/jsc-351-pr192-triage-lane/branch-after-merge-5df1682.md:1
  - artifacts/reviews/jsc-351-pr192-triage-lane/governor-remediation-5f20d84.md:1
  - artifacts/reviews/jsc-351-pr192-triage-lane/post-push-5f20d84.md:1
  - artifacts/reviews/jsc-351-pr193-triage-lane/post-push-128e534b.md:1
- Why this is unnecessary complexity:
  - These files add narrative/process history to the code-change PR and increase review noise without changing command-surface behavior.
- Simpler alternative:
  - Keep this PR limited to the behavior fix, tests, and generated catalog artifacts needed by contract.
  - Move historical triage narratives to a dedicated operational log PR or out-of-band evidence channel.

## Residual risks if unchanged
- Rule drift between discovery and runtime-budget validation when default bridge visibility changes again.
- Future maintenance regressions in README sync due to regex-order coupling.
- Slower reviews and weaker signal-to-noise ratio from broad artifact payloads.

## Overall minimality assessment
- Core functional fixes are small and mostly direct.
- Main simplification opportunity is reducing duplicated policy constants and collapsing README rewrite logic.
- Estimated removable/reducible LOC in this PR boundary: ~35-70 lines (mostly README rewrite fallback chain and duplicated constant wiring).

WROTE: artifacts/reviews/jsc-351-pr193-review-stack/simplicity.md
