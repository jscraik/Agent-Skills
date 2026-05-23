# Testing Review: JSC-351 PU-003

## Findings (severity-ranked)

### medium - Missing end-to-end CLI regression test for invalid `--runtime-target` payload path
- Evidence:
  - `Infrastructure/bin/ask:531` wires `args.runtime_target` into `skills_proof(...)`, and downstream user-facing JSON/human output is rendered from the CLI entrypoint logic.
  - `Infrastructure/tests/test_ask_skills_doctor.py:298-309` asserts invalid runtime-target behavior only via direct `skills_proof(...)` function call, not via public CLI parsing/dispatch/output.
- Why this matters:
  - PU-003 explicitly hardens public CLI runtime-target handling. A future argparse/dispatch/output refactor could regress user-visible payload shape or exit behavior while unit tests still pass because they bypass the CLI boundary.
- Remediation:
  - Add one integration test that invokes `Infrastructure/bin/ask` with `skills proof <handle> --runtime-target cloud --json --robot`, then asserts:
    - non-zero exit (expected validation failure),
    - emitted `runtime_failure.schema_version == "skill-runtime-failure.v1"`,
    - `failed_check_id == "runtime_target"`,
    - and presence of recovery/validation command guidance in output payload.

## Positive coverage noted
- Deterministic schema subset validation does fail closed on unsupported schema keywords and missing required fields (`Infrastructure/tests/test_ask_skills_doctor.py:153-191,310-321`).
- `next_command_decision` precedence and runtime-blocker routing are asserted and schema-validated (`Infrastructure/tests/test_ask_skills_doctor.py:424-441,649-672`).
- Runtime failure context propagation into doctor runtime checks is explicitly asserted (`Infrastructure/tests/test_ask_skills_doctor.py:443-482`).

WROTE: artifacts/reviews/jsc-351-pu003/testing.md
