## Simplification Analysis

### Core Purpose
Validate that selected `Infrastructure/bin/ask ... --json` wrapper invocations emit the expected top-level envelope and key runtime-proof/runtime-separation payload fields.

### Unnecessary Complexity Found
- Low: [Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:106](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:106)
- `_data_object(...)` is only called once and its return value is unused.
- The next two assertions already traverse `["data", ...]`, which fails if `data` is missing/not an object, so this is redundant.
- Suggested simplification: delete `_data_object` and the call at line 159.

- Low: [Infrastructure/tests/test_verify_wrapper_contract_fixtures.py:24](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_verify_wrapper_contract_fixtures.py:24)
- Re-loading the module in every `setUp` is slightly heavier than needed for pure main-routing tests.
- Suggested simplification: load once in `setUpClass` unless test isolation requires per-test reload.

### Code to Remove
- [Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:106](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:106) - redundant helper and single call site.
- Estimated LOC reduction: 6-8.

### Simplification Recommendations
1. Remove redundant `_data_object` check.
   - Current: separate helper validates `data` object before deeper path assertions.
   - Proposed: rely on existing `_assert_string_field(... ["data", ...])` path traversal.
   - Impact: small LOC reduction, less surface area, same behavior for all asserted paths.

2. Optional test harness trim.
   - Current: module import per test via `setUp`.
   - Proposed: use `setUpClass` once for this class.
   - Impact: minor speed/readability improvement; no behavior change.

### YAGNI Violations
- `_data_object` currently acts as a one-off extensibility point without differentiated behavior from existing assertions.
- This is a mild YAGNI case because it adds an abstraction that is not buying new capability.

### Final Assessment
Total potential LOC reduction: ~3-5% for this patch.
Complexity score: Low
Recommended action: Minor tweaks only; no blocking simplicity issues.
WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-004/simplify-reviewer.md
