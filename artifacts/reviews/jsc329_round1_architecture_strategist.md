# JSC-329 Round 1 Architecture Review (Adversarial)

## Findings (Severity-ranked)

### 1) High - Required-field contract allows empty evidence, enabling false-green "shape-only" passes
- Evidence:
  - `.harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:203-215` marks top-level fields as required but does not constrain non-emptiness or minimal content for readiness-bearing fields (`checks`, `blockers`, `warnings`, `operation_context`, `contract_schemas`, `target_summary`).
  - `.harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md:313-317` acceptance criteria focus on presence/separation/precedence but do not require meaningful payload content.
  - `.harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md:132` PU-001 assertion scope is presence-only.
- Why this is a closure risk:
  - Implementation can satisfy the contract with structurally present but semantically empty fields and still pass SA coverage, producing an SDK contract that is machine-readable but not decision-usable.
- Remediation:
  - Add explicit minimum semantic constraints to SA-001/FR-001 and PU-001:
    - `target_summary` must include stable handle identifier.
    - `checks` must contain at least one readiness-class check for the observed run.
    - `operation_context` must include command/profile identifiers.
    - `contract_schemas` must include at least one declared schema key/value.
  - Add one negative fixture asserting failure on empty-object/empty-list placeholders for required semantic fields.

### 2) Medium - Check-class naming drift between spec and plan can break boundary integrity silently
- Evidence:
  - Spec canonical check class is `package_readiness` (`.harness/specs/...spec.md:231`).
  - Plan PU-003 allows/mentions `capability_metadata or package-facing metadata` (`.harness/plan/...plan.md:210-212`) without explicit mapping rule back to spec class.
  - Spec requires classes be preserved or mapped when observable (`.harness/specs/...spec.md:224-235`), but plan does not force documentation/assertion of mapping for this specific drift.
- Why this is a closure risk:
  - A test suite could pass using internal names that no longer match the public contract vocabulary, creating consumer breakage or ambiguous interpretation while appearing compliant.
- Remediation:
  - Add a PU-003 assertion and closeout note: any internal alias (`capability_metadata`, etc.) MUST map to public contract class `package_readiness` in `data.skill_doctor.checks`.
  - Add a fixture assertion that rejects unmapped internal-only class names in the exported contract object.

### 3) Medium - Representativeness requirement is under-specified and can be satisfied without cross-boundary confidence
- Evidence:
  - Spec requires one additional skill class for representativeness (`.harness/specs/...spec.md:295,319`).
  - Plan default says "verify he-plan first" (`.harness/plan/...plan.md:464`) and candidate selection is broad (`.harness/plan/...plan.md:293-294`) but does not codify class-diversity criteria.
- Why this is a closure risk:
  - Teams can choose a near-identical handle path and claim representativeness without materially testing boundary variance (ownership/layout/class differences), leaving context7-specific assumptions unchallenged.
- Remediation:
  - Tighten PU-005 acceptance: selected handle must differ from context7 on at least one declared axis (plugin family, directory ownership boundary, or lifecycle profile).
  - Require the eval artifact to record the axis and why it is representativeness-relevant.

## Overall verdict
- Not yet 100% implementation-ready for a professional SDK readiness-contract slice. The plan is strong, but these three contract precision gaps can permit compliant-looking, low-truth outcomes.

WROTE: artifacts/reviews/jsc329_round1_architecture_strategist.md
