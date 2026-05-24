## Agent-Native Architecture Review

### Summary
This slice updates the public CLI surface for `ask skills proof` so invalid `--runtime-target` values are handled by the skills proof runtime layer instead of being blocked by argparse. Agent integration already exists through command-handle proof and runtime diagnostics contracts, and this change improves action parity for failure handling by returning the same machine-readable payloads agents can consume for recovery guidance.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Run skill proof with runtime constraint (`--runtime-target any|codex|agents`) | Infrastructure/bin/ask:146 | `skills_proof(..., runtime_target=...)` via `ask skills proof` | Yes (CLI help + contract tests) | Must have | Pass |
| Submit invalid runtime target and receive recoverable diagnostics | Infrastructure/bin/ask:148 | `build_command_handle_proof` + `invalid_runtime_target_failure` | Yes (JSON envelope tested) | Must have | Pass |
| Validate recovery path through command suggestions | Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:30 | `skills_validation_command("proof", ... "--runtime-target", "any")` | Yes | Should have | Pass |

### Findings

#### Critical (Must Fix)
None.

#### Warnings (Should Fix)
None.

#### Observations
1. **Argparse no longer enforces enum constraints** -- Infrastructure/bin/ask:148 -- This is intentional for agent-native recovery, but it broadens accepted raw input at parser level. Suggest keeping/expanding schema-contract tests around `runtime_failure` to prevent regressions in downstream validation behavior.

### What's Working Well
- Invalid runtime-target handling is now centralized in runtime proof logic, producing structured `command-handle-proof.v2` and `skill-runtime-failure.v1` payloads that agents can parse and act on.
- Error classification preserves agent-operable remediation guidance (`recovery_guidance` + `validation_commands`) instead of parser-only prose.
- CLI-level contract coverage verifies this behavior end-to-end, including non-zero exit and machine-readable JSON response (Infrastructure/tests/test_ask_skills_doctor.py:293).

### Score
- **3/3 high-priority capabilities are agent-accessible**
- **Verdict:** PASS

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-001/agent-native-reviewer.md
