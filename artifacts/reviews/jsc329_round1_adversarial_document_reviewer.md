# JSC-329 Adversarial Document Review

## Verdict
Not approved yet. The spec/plan are close, but there are contract gaps that still allow a formally “passing” implementation to mislead agents or hide cross-skill fragility.

## Findings

### 1) \`next_command\` is required but under-specified, allowing unsafe or non-deterministic guidance
Severity: High
Confidence: 75

Evidence:
- \`.harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:152\` requires \`next_command\` for every status and allows null only when no safe command exists.
- \`.harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:214\` defines only “safe next command string or explicit null,” but no priority/selection rule.
- \`.harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:276-280\` describes recovery scenarios but still does not define deterministic command selection when multiple blockers/warnings coexist.
- \`.harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md:172\` and \`:395\` test presence/nullable behavior, not command-choice determinism or safety class.

Why this can fail in reality:
An implementation can satisfy the field-presence contract while emitting inconsistent or low-safety commands between runs (or across mixed blocker/warning states). Agents could loop on a non-remediating command or take a command that addresses a warning while a blocker remains unresolved.

Concrete remediation:
- Add a normative \`next_command\` decision ladder to the spec (for example: highest-severity actionable blocker first; if no actionable blocker then highest-severity warning; if no safe command exists => null).
- Add one acceptance criterion asserting deterministic command choice under multi-signal input.
- Add PU-002 tests for at least two mixed-state fixtures where more than one candidate command exists, verifying deterministic and safe selection.

### 2) \`contract_schemas\` is mandatory but can be satisfied with unverifiable placeholders
Severity: Medium
Confidence: 75

Evidence:
- \`.harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:147\` and \`:212\` make \`contract_schemas\` required.
- \`.harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md:465\` explicitly allows RF-1 to proceed without concrete schema files, using “declared schema names and required fields.”

Why this can fail in reality:
A producer can emit nominal schema names that do not resolve to any governed schema source, while still passing this slice. That creates a false “SDK-grade” signal for downstream consumers expecting actionable schema contracts.

Concrete remediation:
- Tighten spec semantics for \`contract_schemas\` to require either:
  - resolvable local schema references, or
  - an explicit constrained fallback structure (name + version + stability + ownership + missing_schema_reason).
- Add a fixture assertion that disallows empty/opaque placeholders.
- Add a plan step clarifying what constitutes minimally valid \`contract_schemas\` evidence in RF-1.

### 3) Representativeness gate is non-binding and can mask cross-skill contract breakage
Severity: Medium
Confidence: 75

Evidence:
- \`.harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:155\` requires one additional read-only representativeness check.
- \`.harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:319\` allows “pass or coverage gap.”
- \`.harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md:306\` routes immediate incompatibility to RF-2 unless direct JSC-329 bug.

Why this can fail in reality:
The slice can close “green” even if the very next skill class immediately violates the required doctor shape, by classifying it as a deferred gap. This weakens the claimed professional readiness contract and risks shipping a context7-only truth.

Concrete remediation:
- Define a blocking threshold for representativeness failures (for example: missing any FR-001 required fields in selected non-context7 handle is blocking for JSC-329 unless explicitly waivered with owner/date).
- Require closeout to include a binary representativeness outcome class (\`pass\`, \`blocked_contract_gap\`, \`deferred_by_waiver\`) with owner and follow-up issue link if deferred.
- Update PU-005/PU-006 validation text so unresolved incompatibility cannot silently pass as informational.

## Overall risk statement
The current documents strongly improve structure, but they still permit three false-green paths: non-deterministic remediation guidance, unverifiable schema contract claims, and non-binding cross-skill representativeness. Closing these will materially improve “agent-safe by contract” behavior before implementation.

WROTE: artifacts/reviews/jsc329_round1_adversarial_document_reviewer.md
