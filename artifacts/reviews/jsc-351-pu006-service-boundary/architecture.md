# Architecture Review - JSC-351 PU-006 Skills SDK Service Boundary

## Verdict
No blocker findings. The slice largely preserves the intended command-facade to service-module dependency direction and reduces command-layer ownership for runtime-proof and package-contract logic.

## Findings

### low - contracts module is becoming a multi-domain utility hub (cohesion risk)
- Evidence:
  - Infrastructure/scripts/lib/ask/skills_sdk/contracts.py:8-29 defines package metadata contracts.
  - Infrastructure/scripts/lib/ask/skills_sdk/contracts.py:31-113 defines doctor blocker and warning taxonomies plus eval blocker classes.
  - Infrastructure/scripts/lib/ask/skills_sdk/contracts.py:116-125 defines ask and skills validation command composition.
  - Infrastructure/scripts/lib/ask/skills_sdk/contracts.py:141-199 defines SKILL.md frontmatter parsing helpers.
- Why this matters:
  - The extraction moved code out of skills_impl.py correctly, but contracts.py now mixes command invocation formatting, doctor policy taxonomy, and parsing utilities. That increases change coupling across unrelated concerns.
- Remediation:
  - Split contracts.py into narrower modules over time:
    - doctor_contracts.py for doctor taxonomies and schema refs.
    - frontmatter_parsing.py for frontmatter parsing primitives.
    - validation_commands.py for command string builders.
  - Keep contracts.py as a compatibility re-export shim during migration.

### informational - boundary tests are present and correctly enforce dependency direction
- Evidence:
  - Infrastructure/tests/test_skills_sdk_boundaries.py:33-40 asserts ask.skills_sdk modules do not import ask.commands.
  - Infrastructure/tests/test_skills_sdk_boundaries.py:43-60 asserts extracted helper functions are no longer defined in skills_impl.py.
  - Infrastructure/tests/test_ask_skills_doctor.py:206-216 adds source-level checks for runtime adapter extraction and command-layer independence.
  - Infrastructure/tests/test_ask_skills_package_contract.py:236-254 adds source and module ownership checks for package-contract logic.
- Why this matters:
  - These tests directly guard the architecture objective and reduce regression risk where logic drifts back into the command facade.

## Architecture fit summary
- Command facade thinness: improved; skills_impl.py now delegates key runtime and package behavior to ask.skills_sdk modules.
- Dependency direction: correct in this slice (command layer imports services; services avoid importing command layer).
- Boundary drift: none observed beyond expected evidence hash churn in governance snapshot.
- Type 1 decisions requiring ADR or approval: none identified.
