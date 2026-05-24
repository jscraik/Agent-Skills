## Simplification Analysis

### Core Purpose
PU-001 needs to fail closed for Codex-targeted runtime proof while keeping default compatibility behavior for existing `skills proof` and `skills doctor` flows.

### Unnecessary Complexity Found
- low - `Infrastructure/tests/test_ask_skills_doctor.py:22-129`
- Why it's unnecessary: PU-001 introduces a full custom JSON Schema subset validator (`$ref`, `oneOf`, `additionalProperties`, etc.) inside a unit test file. For this slice, we only need confidence that the doctor payload preserves key contract fields touched by PU-001 (`runtime_target`, codex parity wiring, blocker classification), and the custom validator adds maintenance burden unrelated to PU-001 behavior.
- Suggested simplification: Move schema conformance checks to a shared lightweight test helper already used across schema tests (or reduce this file to targeted field assertions for PU-001 deltas only). Keep one integration-level schema validation test elsewhere instead of embedding a mini validator here.

- informational - `Infrastructure/bin/ask:137`, `Infrastructure/scripts/lib/ask/commands/skills_impl.py:1114-1124`
- Why it's unnecessary: runtime-target admissibility is validated in both argparse choices and function logic.
- Suggested simplification: Keep both only if direct function calls are a supported public contract. If CLI is the only external entrypoint, centralize the validation path to reduce duplicate rules.

### Code to Remove
- `Infrastructure/tests/test_ask_skills_doctor.py:22-129` - Embedded schema-subset validator can be replaced by narrower assertions or shared helper.
- Estimated LOC reduction: ~100

### Simplification Recommendations
1. Trim the test-local schema engine
   - Current: test file implements its own schema-walking validator.
   - Proposed: assert PU-001 behavior directly in this test file and rely on one centralized schema validation helper/integration test for schema integrity.
   - Impact: ~100 LOC saved; clearer test intent focused on PU-001.

2. Decide on a single source of runtime-target validation truth
   - Current: validation exists in both CLI parser and command implementation.
   - Proposed: document intent (defensive duplicate vs single source) and collapse one layer if function-level invocation is not a supported contract.
   - Impact: small LOC reduction; reduced drift risk.

### YAGNI Violations
- Potential YAGNI: test-local generic schema validator in `Infrastructure/tests/test_ask_skills_doctor.py`.
- Why it violates YAGNI: introduces broad validation infrastructure in a PU-001-focused test without clear immediate requirement for a bespoke validator engine.
- What to do instead: keep PU-001 tests narrowly behavioral and place schema completeness checks in dedicated shared schema tests.

### Final Assessment
Total potential LOC reduction: ~3-5% of PU-001 touched LOC
Complexity score: Low
Recommended action: Proceed with simplifications as follow-up (non-blocking for PM/git triage). No blocker or high-severity simplicity issues found for PU-001.
WROTE: artifacts/reviews/jsc-351-pu001/simplicity.md
