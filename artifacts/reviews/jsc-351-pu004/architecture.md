# JSC-351 PU-004 Architecture Review

## Architecture Overview
PU-004 introduces a Codex-facing package contract surface in `skills_package` and formalizes it with two JSON schemas:
- `skill-package.v1` for SkillMetadata-aligned package identity.
- `skill-package-readiness.v1` for the broader readiness payload and compatibility snapshot identity.

The change keeps package-readiness logic in `Infrastructure/scripts/lib/ask/commands/skills_impl.py` and uses fixture-backed compatibility snapshots for public output stability.

## Findings (Severity-ranked)

### High: Cross-repo absolute path hardcodes Codex ABI source, creating boundary coupling and portability drift
- Evidence:
  - `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2936`
  - `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2970`
- Detail:
  - `codex_abi_source.path` is hardcoded to an absolute machine-local path: `/Users/jamiecraik/dev/codex/codex-rs/core-skills/src/model.rs`.
  - This couples `agent-skills` payload contracts to a host-specific filesystem layout and to another repository’s checkout location.
  - Architecturally this shifts source-of-truth resolution from a stable contract identifier to an environment-specific path, which can drift across machines/CI and breaks reproducible provenance.
- Why this matters:
  - Violates ownership boundary expectations for a repo-owned contract surface.
  - Introduces non-determinism for consumers that treat `codex_abi_source` as evidence.
- Remediation:
  - Replace absolute path with a repository-neutral reference, e.g.:
    - logical source identifier (`codex-rs/core-skills/src/model.rs`), plus
    - optional `evidence_ref`/`doc_url` for ABI provenance.
  - Keep machine-local resolution out of payload; if needed, expose it in debug-only diagnostics, not public contract output.

### Medium: Snapshot compatibility projection omits new ABI-evidence fields, weakening drift-proof identity
- Evidence:
  - `Infrastructure/tests/test_ask_skills_package_contract.py:143`
  - `Infrastructure/tests/test_ask_skills_package_contract.py:161`
  - `Infrastructure/tests/test_ask_skills_package_contract.py:173`
- Detail:
  - `_snapshot_projection` intentionally narrows compared fields and does not include `skill_package_contract.codex_abi_source` or other newly added optional metadata surfaces (`dependencies/policy/scope/plugin_id`).
  - Result: fixture stability checks can pass even if ABI-source evidence drifts or regresses.
- Why this matters:
  - The slice objective explicitly includes “drift-proof schema identity.” Excluding the ABI evidence block reduces that guarantee.
- Remediation:
  - Include at least `codex_abi_source.struct` and `codex_abi_source.evidence_fields` in snapshot projection.
  - Optionally include `codex_abi_source.path` after normalizing per high-severity remediation above.

### Low: Schema openness (`additionalProperties: true`) on core contract objects dilutes strict contract governance
- Evidence:
  - `Infrastructure/config/schemas/skill-package.v1.schema.json:6`
  - `Infrastructure/config/schemas/skill-package.v1.schema.json:48`
  - `Infrastructure/config/schemas/skill-package-readiness.v1.schema.json:6`
- Detail:
  - Both schemas permit extra keys at top level (and in key nested structures), reducing fail-closed detection for accidental payload expansion.
- Why this matters:
  - For externally consumed contracts, permissive schemas can hide unintended API changes and increase long-term maintenance load.
- Remediation:
  - Consider staged tightening:
    - Keep permissive mode for now, but add explicit TODO/governance note for v2.
    - Add CI guardrails that detect newly introduced top-level keys even before strict schema closure.

## Change Assessment
The implementation generally aligns with intended architecture:
- Package-readiness and SkillMetadata contract concerns stay inside the skills command layer.
- Versioned schemas and snapshot IDs are introduced cleanly.
- Existing compatibility behavior appears preserved (`blocked_missing_source`, warning/strict semantics).

Primary misalignment is not in logic flow but in boundary integrity of ABI evidence and strength of drift-proof checks.

## Compliance Check
- Separation of concerns: Mostly upheld (contract generation vs readiness evaluation are separate helpers).
- Boundary integrity: Partially violated by absolute cross-repo path hardcoding.
- Contract stability/versioning: Improved via explicit schema versions and fixture IDs.
- Drift detection: Present but incomplete for ABI-evidence payload fields.
- Dependency direction: No circular-dependency signal surfaced in this slice.

## Risk Analysis
- Architectural drift risk: Medium-High until absolute ABI path is normalized.
- Portability risk: High for non-local environments consuming payload provenance.
- Future evolution risk: Medium if schema permissiveness remains without compensating key-drift checks.

## Recommendations
1. Replace machine-local `codex_abi_source.path` with repository-neutral ABI reference.
2. Extend compatibility snapshot projection to include ABI evidence fields.
3. Add explicit contract-key drift guard (test or validator) while planning stricter `additionalProperties` posture in v2.
4. Document ABI evidence policy (what is normative vs informational) to avoid accidental coupling in downstream consumers.

## Completion Recommendation
- recommended_completion_state: `changes_requested`
- rationale: The core capability is functional, but the high-severity boundary-coupling issue should be fixed before treating this slice as architecturally closed.

WROTE: artifacts/reviews/jsc-351-pu004/architecture.md

