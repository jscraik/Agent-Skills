# Architecture Review — JSC-329 T002 goal-governor-review-mode-guard

## Architecture Overview
Goal Governor is structured as a control-surface skill with three canonical layers:
1. Human/runtime policy in `SKILL.md`.
2. Machine-readable contract in `references/contract.yaml`.
3. Behavioral proof in `references/evals.yaml` + validator tests.

The slice adds a review-only lane that intentionally blocks native-goal execution side effects unless explicitly overridden.

## Findings (severity ordered)

### MEDIUM — Output contract ambiguity between base and review mode can cause schema consumers to require impossible fields
- Evidence:
  - `Skills/agent-ops/goal-governor/references/contract.yaml:35-43` declares globally required fields including `goal_path` and `native_goal_status`.
  - `Skills/agent-ops/goal-governor/references/contract.yaml:52-62` declares a distinct review-mode required field set focused on prompt-readiness and launch safety.
  - `Skills/agent-ops/goal-governor/SKILL.md:62-67` documents review responses as prompt-readiness outputs instead of native-goal reconciliation.
- Why this is an architectural issue:
  - The contract currently exposes two required-field authorities without an explicit discriminant/override rule. Consumers that validate only `output_contract.required_fields` may reject valid review-mode outputs or force review mode to leak non-applicable runtime fields, blurring boundaries.
- Suggested remediation:
  - Make mode-discriminated output explicit in the contract (for example, `output_contract.by_mode.review.required_fields` and `by_mode.default.required_fields`, or a top-level `mode_discriminator` with per-mode schemas).
  - Add one validator/eval assertion that review mode MUST NOT require `goal_path`/native status fields.

## Compliance Check
- Pattern compliance:
  - The review guard is consistently represented across policy, contract, evals, and tests.
  - Forbidden side effects in review mode preserve separation between prompt governance and implementation execution.
- Boundary integrity:
  - No deep-module/layering violations found in changed files.
  - Generated-vs-canonical ownership looks intact for this slice; no evidence of editing runtime projection instead of canonical skill/contract surfaces.
- API stability:
  - Existing mode taxonomy remains additive (`review` is an extension), but the ambiguity above is a consumer-contract risk.

## Risk Analysis
- Main risk introduced by this slice is contract interpretation drift for downstream validators/reporters that assume one global required-field set.
- Residual risk after this review:
  - The large linear-plan additions are clearly marked as post-RF1 design input, but they increase conceptual surface area and should stay explicitly non-binding for RF1 implementation gating.

## Recommendations
1. Resolve mode-discriminated contract shape in `references/contract.yaml` before broad consumer adoption.
2. Add one explicit negative eval asserting review outputs do not require native-goal reconciliation fields.
3. Keep RF1 doctor fixture scope isolated from post-RF1 runtime-governance imports (already stated; maintain as a hard guard).

WROTE: .harness/reviews/2026-05-21-jsc-329-goal-governor/architecture.md

