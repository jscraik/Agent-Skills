# JSC-329 Adversarial Review

## Finding 1: False green path: contract can pass with structurally wrong field types

Severity: High
Evidence:

- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:147 requires presence of required fields but not their concrete JSON types.
- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:203-215 defines semantics for required fields but not strict shape constraints.
- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:191-192 says consumers should rely on named machine-readable fields in data.skill_doctor.

Constructed failure scenario:

1. Implementation returns all required keys but wrong shapes (for example blockers as a string, checks as prose, next_command as object).
2. Presence-focused fixture still passes SA-001 behavior check.
3. Harness or agents parse payload as machine-readable contract and fail or silently mis-handle gating logic.

Why this blocks readiness:

- The slice can report “contract satisfied” while producing payloads unsafe for automation consumers, violating the intent of SDK-grade readiness.

Remediation:

- Add normative type/shape rules per required field and enforce them in fixture tests, including negative tests for malformed field shapes.

## Finding 2: Status precedence can misclassify unevaluated readiness as pass

Severity: High
Evidence:

- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:148 defines final status precedence based on blockers/warnings emptiness.
- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:269 says skipped/not-run evidence must not be collapsed.
- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:218-220 constrains final status enum to pass|warning|blocked with no mapping rule for skipped/not-run.

Constructed failure scenario:

1. One critical check is skipped/not-run due to environment.
2. Implementation does not materialize skipped/not-run as blocker or warning.
3. blockers and warnings remain empty.
4. Precedence rule emits pass even though critical readiness evidence was unevaluated.

Why this blocks readiness:

- Consumers get a green status from an incomplete evaluation state, exactly the trust failure this contract is meant to prevent.

Remediation:

- Define mandatory mapping from skipped/not-run classes to warning or blocked, and add fixture cases proving pass cannot occur with unevaluated critical checks.

## Finding 3: Command-exit semantics are under-specified, enabling command-failure/readiness-failure confusion

Severity: Medium
Evidence:

- .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md:173 says preserve non-zero behavior when blockers are present.
- .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md:255 says classify exit 2 as blocked-readiness evidence.
- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:292 captures non-zero blocked-readiness evidence but does not specify exit-code contract boundaries.

Constructed failure scenario:

1. Refactor changes exit-code mapping while leaving JSON payload shape intact.
2. One path returns the same exit code for transport failure and domain blocked-readiness.
3. Downstream automation gates on process exit before payload parse.
4. Valid blocked-readiness evidence is dropped or true command failures are misreported as readiness status.

Why this matters:

- The same numeric exit may represent incompatible meanings, creating fragile and misleading operational behavior.

Remediation:

- Specify exit-code contract classes or require explicit payload discriminator for command/runtime failure versus domain blocked-readiness, with dedicated tests for both paths.

## Finding 4: Representativeness probe can be marked complete without meaningful cross-skill coverage

Severity: Medium
Evidence:

- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:319 allows SA-007 completion by recording a coverage gap.
- .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md:306 allows routing immediate incompatibility to RF-2 unless direct JSC-329 bug.
- .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md:293 chooses candidate handles at implementation time based on availability.

Constructed failure scenario:

1. Additional handle selection finds an awkward or unavailable target.
2. Probe records a coverage gap and proceeds.
3. Closeout still claims representativeness criterion satisfied.
4. Context7-only assumptions survive and break on first real non-context7 consumer.

Why this matters:

- “Representativeness complete” can become a paper pass without actual cross-class contract confirmation.

Remediation:

- Require one successful additional-skill doctor parse with required-field assertions; allow gap fallback only with a blocking follow-up issue and ownership.

WROTE: artifacts/reviews/jsc329_round1_adversarial_reviewer.md
