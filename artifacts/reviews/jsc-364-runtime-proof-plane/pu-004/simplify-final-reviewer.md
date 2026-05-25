## Simplification Analysis

### Core Purpose
Validate JSON envelope contracts for two wrapper fixture lanes (runtime-separation and runtime-proof) with clear failure messages, while keeping CLI behavior backward-compatible.

### Unnecessary Complexity Found
- Infrastructure/tests/test_verify_wrapper_contract_fixtures.py:122
- Unit tests directly cover private helpers `_assert_path` and `_assert_string_field`, which are implementation details.
- Suggested simplification: Remove direct helper tests and keep behavior coverage through `_assert_runtime_proof_fixtures` tests that already exercise these paths.

- Infrastructure/tests/test_verify_wrapper_contract_fixtures.py:135
- `_runtime_proof_envelope_stub` multiplexes three command fixtures with inline branching, which adds indirection for a small surface.
- Suggested simplification: Inline stubs per test (or split into two smaller helper builders: explain/proof payload and conformance payload) to reduce reader hopping.

- Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:250
- Boolean derivation for lane selection is correct but harder to scan than explicit branch structure.
- Suggested simplification: Use one explicit `if/elif/else` dispatch based on flags to make default “run both” behavior obvious at first read.

### Code to Remove
- Infrastructure/tests/test_verify_wrapper_contract_fixtures.py:122 - Private helper lock-in; test via public function outcomes instead.
- Infrastructure/tests/test_verify_wrapper_contract_fixtures.py:127 - Same private helper lock-in with overlapping assertions already implied by runtime-proof tests.
- Estimated LOC reduction: 12-20

### Simplification Recommendations
1. Drop private-helper unit tests
   - Current: Tests couple to `_assert_path` and `_assert_string_field` internals.
   - Proposed: Keep only public-behavior tests on `_assert_runtime_proof_fixtures` and `main()`.
   - Impact: ~12 LOC saved, less brittle tests, easier future refactors.

2. Flatten runtime-proof test stubbing
   - Current: Shared stub function contains branching by command shape.
   - Proposed: Build minimal per-test stubs near each assertion or split helper by fixture type.
   - Impact: ~8-15 LOC saved and lower cognitive overhead.

3. Make lane dispatch explicit
   - Current: Dual boolean expressions for `run_runtime_separation` / `run_runtime_proof`.
   - Proposed: `if args.runtime_separation and not args.runtime_proof` / `elif args.runtime_proof and not args.runtime_separation` / `else`.
   - Impact: Neutral-to-small LOC change, better readability for common maintenance edits.

### YAGNI Violations
- Infrastructure/tests/test_verify_wrapper_contract_fixtures.py:122
- Direct testing of private helper utilities is extra abstraction coupling not needed for current contract guarantees.
- What to do instead: Assert only observable behavior from exported execution paths (`main`, fixture-check orchestration).

### Final Assessment
Total potential LOC reduction: ~6-10% across these two files.
Complexity score: Low-Medium (good trajectory; a bit of test over-structuring remains).
Recommended action: Minor tweaks only.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-004/simplify-final-reviewer.md
