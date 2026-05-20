# API Contract Review: Skill SDK Readiness

## Severity-ranked Findings

### P1 - Contract drift: guided valid-actions list advertises `external-review` for `ask skills`, but parser/help do not support it
- Evidence:
  - [Infrastructure/scripts/lib/ask/command_metadata.py:10](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/command_metadata.py:10) includes `"external-review"` in `VALID_ACTIONS["skills"]`.
  - [Infrastructure/scripts/lib/ask/command_metadata.py:64](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/command_metadata.py:64) and [Infrastructure/scripts/lib/ask/command_metadata.py:155](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/command_metadata.py:155) provide `external-review` command examples.
  - [Infrastructure/bin/ask:533](/Users/jamiecraik/dev/agent-skills/Infrastructure/bin/ask:533) through [Infrastructure/bin/ask:614](/Users/jamiecraik/dev/agent-skills/Infrastructure/bin/ask:614) register skills actions, and no `external-review` parser is added.
  - Live CLI help omits `external-review` (captured via `./bin/ask skills --help`), and error payload guidance still includes it.
  - [\.harness/README.md:125](/Users/jamiecraik/dev/agent-skills/.harness/README.md:125) documents this mismatch as a known local gap.
- Contract impact:
  - Client/agent consumers that rely on guided-error valid-action lists receive a false callable action.
  - This is externally visible behavior drift between two public contract surfaces: parser/help vs error guidance.
- Remediation:
  - Make parser/help/error guidance authoritative from one registry and enforce parity tests so `VALID_ACTIONS`, subparser registration, `--help`, and error suggestions cannot diverge.

### P1 - RF-1 acceptance references a new doctor response contract, but no canonical schema artifact path is bound in the plan
- Evidence:
  - [\.harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md:103](/Users/jamiecraik/dev/agent-skills/.harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md:103) defines required doctor fields.
  - [\.harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md:137](/Users/jamiecraik/dev/agent-skills/.harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md:137) defines schema-evolution rules.
  - [\.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md:159](/Users/jamiecraik/dev/agent-skills/.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md:159) and [\.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md:210](/Users/jamiecraik/dev/agent-skills/.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md:210) require field assertions and help registration, but do not point to a single canonical schema file/location that gates compatibility.
- Contract impact:
  - Without a bound schema artifact, additive vs breaking changes can drift across fixtures/tests/output format, risking accidental contract breakage for downstream consumers.
- Remediation:
  - In RF-1 acceptance, require one canonical schema file path plus compatibility tests against it (including required-field and nullability guarantees), not only ad-hoc fixture assertions.

### P2 - Public facade decision remains unresolved and can produce semantic break risk for existing `prove/proof` consumers
- Evidence:
  - [\.harness/README.md:122](/Users/jamiecraik/dev/agent-skills/.harness/README.md:122) states RF-1 must decide whether to add `skills doctor` over existing `prove/proof/explain` or retitle RF-1 around existing contracts.
  - [\.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md:185](/Users/jamiecraik/dev/agent-skills/.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md:185) says `skills prove` is current readiness-adjacent comparison.
- Contract impact:
  - If `doctor` reinterprets/duplicates `prove` semantics without explicit compatibility mapping, clients may observe conflicting readiness meaning between commands.
- Remediation:
  - Add an explicit compatibility matrix in RF-1: `prove/proof` fields -> `doctor` fields, with stated non-goals and deprecation/versioning policy.

### P2 - Referenced source-of-truth artifacts for contract signoff are missing, leaving acceptance criteria partially unverifiable
- Evidence:
  - [\.harness/README.md:108](/Users/jamiecraik/dev/agent-skills/.harness/README.md:108) flags missing strategy source.
  - [\.harness/README.md:113](/Users/jamiecraik/dev/agent-skills/.harness/README.md:113) flags missing apparatus lens.
  - [\.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md:23](/Users/jamiecraik/dev/agent-skills/.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md:23) and [\.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md:95](/Users/jamiecraik/dev/agent-skills/.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md:95) classify apparatus as referenced_missing.
- Contract impact:
  - Missing governing artifacts increase risk of inconsistent interpretation of what constitutes contract pass/fail and signoff boundaries.
- Remediation:
  - Restore or replace missing authority docs before claiming contract readiness closure.

## Open Questions / Assumptions

- Assumption: `external-review` was intentionally removed from parser surfaces and should also be removed from metadata guidance unless reintroduced.
- Open question: Should `skills doctor` be additive-only in RF-1, or should any `prove/proof` semantics move/alias in the same slice?

## Residual Risks

- Even with `doctor` registration, contract drift can recur unless parser actions and metadata-guidance actions are generated from one source.
- `next_command` semantics are specified in planning docs but may still vary in implementation without schema-level nullability enforcement.

## Testing Gaps

- No parity test evidence found that asserts equality between:
  - skills parser registered actions,
  - `VALID_ACTIONS["skills"]`,
  - `./bin/ask skills --help` surfaced actions,
  - guided-error valid-action list.

WROTE: artifacts/reviews/sdk-api-contract-review.md
