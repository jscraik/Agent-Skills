## Agent-Native Architecture Review

### Summary
This change adds a public-wrapper fixture validator for runtime proof-plane parity and focused tests around the conformance envelope contract. Agent integration exists through `Infrastructure/bin/ask` wrapper commands, and the reviewed fixture script verifies that proof and conformance flows are discoverable and machine-parseable through those public surfaces. Overall parity assessment for this slice is strong: the agent can discover the proof command from explain output, invoke proof/conformance via wrapper commands, and interpret runtime-blocked states without requiring private helper paths.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Request skill explain and discover next proof command | Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:166 | `./bin/ask skills explain <handle> --json --robot` (validated via wrapper call) | N/A (CLI contract) | Must have | Covered |
| Execute proof-plane validation for a skill handle | Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:181 | `./bin/ask skills proof <handle> --runtime-target any --json --robot` | N/A (CLI contract) | Must have | Covered |
| Execute codex-parity conformance evidence run | Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:201 | `./bin/ask skills conformance run --suite codex-parity ... --json --robot` | N/A (CLI contract) | Must have | Covered |
| Parse runtime-blocked conditions as first-class outcome | Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:231 | Envelope field checks on `live_parity_status` and `blocked_runtime.blockers` | N/A (CLI contract) | Must have | Covered |
| Select fixture lane (runtime separation vs proof-only) | Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:250 | Public script flags `--runtime-separation` / `--runtime-proof` | N/A (CLI contract) | Should have | Covered |

### Findings

#### Critical (Must Fix)
1. None.

#### Warnings (Should Fix)
1. None.

#### Observations
1. **Prompt discoverability evidence is indirect** -- `Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:168` checks `data.explanation.reachability.proof_command`, which is strong for command discoverability in machine output, but this slice does not itself verify end-user docs/prompts surface the same capability. Suggestion: keep this as-is for contract coverage and pair with docs-level contract checks in adjacent lanes if closure criteria require explicit human-facing discoverability proof.
2. **Conformance command is validated schema-first rather than success-first by design** -- `Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py:213` sets `require_success=False`, allowing blocked runtime cases to remain contract-valid. This is appropriate for agent-operable parity because blockers are surfaced structurally, and tests confirm this behavior (`Infrastructure/tests/test_verify_wrapper_contract_fixtures.py:77`).

### What's Working Well
- Public-wrapper-only posture is enforced: the fixture script validates through `Infrastructure/bin/ask` commands instead of private internals.
- Envelope guardrails are explicit and robust (`status`, `trace_id`, `metadata.version`, `metadata.next_steps`, `data`), reducing agent ambiguity for orchestration.
- Runtime-blocked state is treated as a first-class machine outcome with required blockers, preventing silent/manual-only failure modes.
- Tests exercise lane-selection defaults and proof-plane edge cases, including invalid `live_parity_status` and malformed `blocked_runtime`.

### Score
- **4/4 high-priority capabilities are agent-accessible**
- **Verdict:** PASS

Validation evidence:
- `python3 -m unittest Infrastructure/tests/test_verify_wrapper_contract_fixtures.py`
- Result: `Ran 10 tests ... OK`

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-004/agent-native-final-reviewer.md
