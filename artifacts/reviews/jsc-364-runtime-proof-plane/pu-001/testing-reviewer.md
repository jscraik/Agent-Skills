# Testing Review — JSC-364 PU-001

## Verdict
No blocking testing findings. The slice can proceed.

## Findings (severity-ranked)
None.

## Evidence Checked
- Behavioral change in [Infrastructure/bin/ask](/Users/jamiecraik/dev/agent-skills/Infrastructure/bin/ask:148): removed argparse `choices` for `skills proof --runtime-target`, allowing invalid values to flow into runtime proof logic.
- Invalid runtime-target branch is explicitly tested in unit and CLI layers:
  - [Infrastructure/tests/test_ask_skills_doctor.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_skills_doctor.py:275) validates function-level invalid target returns `ERR_VALIDATION`, `command-handle-proof.v2`, and `skill-runtime-failure.v1`.
  - [Infrastructure/tests/test_ask_skills_doctor.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_skills_doctor.py:293) validates CLI invalid target returns JSON payload with the same runtime-failure contract and recovery guidance.
- Runtime adapter contract path confirms this is the intended sink:
  - [runtime_adapters.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:48) rejects unsupported targets and emits structured runtime failure.
  - [runtime_adapters.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:51) emits `command-handle-proof.v2`.
  - [runtime_adapters.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:219) emits `skill-runtime-failure.v1` for proof failures.

## Residual Risks
- No direct test in this patch validates case/whitespace normalization from CLI input to runtime target (e.g., `" CODEX "`), although normalization exists in [runtime_adapters.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:15). This is low risk and covered indirectly by normalization in the execution path.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-001/testing-reviewer.md

