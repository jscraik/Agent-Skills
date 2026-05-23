# Testing Review — JSC-351 PU-001 (Re-review)

## Findings (severity-ranked)

No blocker/high/medium findings remain in the reviewed PU-001 scope.

## Residual risks / testing gaps

### low — CLI parser wiring is still unit-indirect in this slice
- Evidence:
  - Infrastructure/bin/ask:132
  - Infrastructure/bin/ask:137
  - Infrastructure/bin/ask:528
  - Infrastructure/bin/ask:535
  - Infrastructure/tests/test_ask_skills_doctor.py:232
- Why this matters:
  - The new flags are validated through direct function tests, but there is no command-entry integration assertion in this file proving argparse-to-dispatch wiring end-to-end.
- Remediation:
  - Add one lightweight CLI-level test invoking ./bin/ask skills proof <handle> --runtime-target codex --json --robot and ./bin/ask skills doctor <handle> --codex-parity --json --robot with patched internals.

### low — Schema fallback validator remains intentionally partial vs canonical jsonschema
- Evidence:
  - Infrastructure/tests/test_ask_skills_doctor.py:23
  - Infrastructure/tests/test_ask_skills_doctor.py:152
  - Infrastructure/tests/test_ask_skills_doctor.py:181
- Why this matters:
  - The new guard now fail-closes on unsupported keywords and includes minItems, which is a meaningful hardening step.
  - It is still a maintained subset validator, so full Draft7 parity depends on another lane running canonical jsonschema.
- Remediation:
  - Keep this deterministic fallback and ensure at least one CI lane validates the payload against canonical jsonschema.

WROTE: artifacts/reviews/jsc-351-pu001/testing.md
