# Adversarial Review — JSC-364 PU-001

## Conclusion
No blocking adversarial findings for PU-001. The slice can proceed.

## Findings (Severity-ranked)

### 1) Low — Invalid `--runtime-target` now fails through proof contract rather than argparse gate
- Evidence:
  - Parser-level `choices` constraint was removed from `--runtime-target` in [Infrastructure/bin/ask](/Users/jamiecraik/dev/agent-skills/Infrastructure/bin/ask:148).
  - `skills_proof` now always forwards normalized target values to runtime-proof construction in [skills_impl.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:1302).
  - Unsupported values are rejected in runtime adapters and returned as structured failure payloads in [runtime_adapters.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:48).
  - The explicit invalid-target failure contract is emitted via `skill-runtime-failure.v1` builder in [runtime_adapters.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:19).
- Failure scenario:
  - Trigger: caller passes `--runtime-target cloud`.
  - Path: CLI parse succeeds -> `skills_proof` executes -> runtime adapter rejects target.
  - Outcome: deterministic `ERR_VALIDATION` with `command-handle-proof.v2` + embedded `skill-runtime-failure.v1`.
- Risk:
  - Any external automation that previously depended on argparse usage-shape failures (stderr/help text patterns) may need to key on structured failure payloads instead.
- Remediation suggestion:
  - Treat this as intentional contract behavior and ensure consumers validate `runtime_failure.failed_check_id == "runtime_target"` instead of argparse usage output.

## Residual Risks
- Consumer compatibility drift if downstream scripts parse old argparse failure shape instead of JSON failure contract.

## Coverage Notes
- Existing tests already cover invalid runtime target at function and CLI surfaces:
  - [test_ask_skills_doctor.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_skills_doctor.py:275)
  - [test_ask_skills_doctor.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_skills_doctor.py:293)
- Runtime-specific gate behavior is covered in:
  - [test_command_surface_handles.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_command_surface_handles.py:732)
  - [test_command_surface_handles.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_command_surface_handles.py:784)

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-001/adversarial-reviewer.md

