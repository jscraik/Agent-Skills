# PU-012 Breaker Loop 3, Pass 1 Review

## Findings

### High: Lockfile-error fixtures can still be classified as either fail or blocked
- **Evidence:** `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:263-265` allows `missing_with_installed_evidence` and invalid lockfile JSON to return `fail` or `blocked`, while `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:274-281` pins project-state drift after a valid root is accepted to `fail` and says each fixture must map to one deterministic status and exit family.
- **Why it matters:** This leaves the implementation room to pick different exit families for the same fixture without violating the text. A project with installed evidence but no lockfile, or with invalid lockfile JSON, could therefore be reported as `fail` by one implementation and `blocked` by another, which breaks downstream automation and makes the "deterministic status and exit semantics" contract non-deterministic in practice.
- **Concrete fix:** Replace the `fail or blocked` language for each lockfile-error class with one pinned status/exit-family mapping, and add acceptance or validation rows that assert the exact `conformance_status` and exit family for `missing_with_installed_evidence` and invalid lockfile JSON.

## Accountability Receipt

- **status:** complete
- **artifact_paths:**
  - `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/reviews/pu-012-breaker-loop-3-pass-1.md`
- **manifest_path:** `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/artifacts/agent-runs/adversarial-reviewer-019e9ded-9987-7fd1-8d16-c0049d2f9773/manifest.json`
- **findings_count:** 1
- **failures_or_blockers:** none
- **improvement_opportunities:**
  - Tighten the lockfile-error taxonomy so every fixture maps to one exit family.
- **strengths:**
  - Earlier gaps around omitted `--project-root`, launch-time mise env, capability-row visibility, and broad-root identity are now explicitly spelled out in the spec.
  - The current spec also has a concrete no-discovery test and doctor parity rows, which closes the obvious false-positive paths.
- **validation_evidence:** static review of the spec text only; no runtime implementation tests were executed for this pass.
- **next_action:** pin the remaining lockfile-error status mapping, then re-run the breaker review on the updated spec.
- **useful_findings:**
  - Deterministic exit semantics need exact fixture-to-status mapping, not just a broad status table.
- **avoided_false_positive:**
  - I did not re-flag the mise launch environment or omitted-root cases because the current spec now encodes both in executable validation and acceptance rows.
- **evidence_quality:** high
- **followed_scope:** reviewed only the PU-012 spec and the directly relevant lines needed to judge the remaining status-semantic gap.
- **reusable_learning:** when a read-only gate is supposed to be deterministic, every "fail or blocked" allowance should be eliminated or narrowed to one exact class.
- **coordinator_score:** 8/10

WROTE: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/reviews/pu-012-breaker-loop-3-pass-1.md
