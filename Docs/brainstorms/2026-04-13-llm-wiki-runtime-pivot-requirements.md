---
title: LLM Wiki Pivot and Scaffold Re-organization
date: 2026-04-13
status: draft
spec_required: full
risk_level: high
complexity: large
schema_version: 1
---

# LLM Wiki Pivot and Scaffold Re-organization

## Table of Contents

- [Problem Frame](#problem-frame)
- [Pressure Test](#pressure-test)
- [Approaches](#approaches)
- [Recommendation](#recommendation)
- [Requirements](#requirements)
- [Success Criteria](#success-criteria)
- [Scope Boundaries](#scope-boundaries)
- [Key Decisions](#key-decisions)
- [Dependencies and Assumptions](#dependencies-and-assumptions)
- [Outstanding Questions](#outstanding-questions)
- [Next Steps](#next-steps)

## Problem Frame

The current skill-graph-heavy operating lane is stalled in practice due to repeated validation and governance blockers, while the repository also carries unresolved scaffold organization drift. The current state combines three blockers that repeatedly prevent clean closeout:

- certification and readiness artifacts remain blocked by unresolved skill-graph envelope/parity conditions;
- runtime-separation remains degraded at control-plane level;
- ask CLI contract completion is partial, leaving at least one contract-grade error-code behavior not fully aligned.

This creates a repeated pattern: implementation progresses, but closeout and trust signals degrade before completion. The pivot goal is to make the knowledge and graph workflow operationally durable by moving from skill-graph-first governance pressure to a simpler LLM-wiki-first operating model, with Obsidian as the primary graph viewer, while still preserving compatibility and auditability.

## Pressure Test

- Do nothing or patch-in-place? This is low effort short-term but has already shown repeated stall/degrade behavior.
- Is this really a product-direction issue or only execution hygiene? Both. The current operating model is over-coupled to high-friction gates, so process and architecture both need adjustment.
- Is there a lower-complexity path than full skill-graph remediation? Yes: pivot primary knowledge operations to markdown wiki + Obsidian graph and degrade skill-graph to compatibility/legacy mode.
- Is there a high-upside alternative worth considering? Yes: explicitly define anti-stall governance contracts (ownership, freshness, fail-closed transitions) in the same pivot scope so this does not recur.

## Approaches

### A. Continue skill-graph-first closeout

Keep current primary workflow centered on skill-graph artifacts and remediate blockers directly.

Pros:

- No directional change in architecture.
- Reuses existing contracts and tooling surface.

Cons:

- Highest recurrence risk for stall/degrade based on current evidence.
- Maintains operational overhead on already-fragile closeout path.

Best fit:

- Teams that must preserve existing skill-graph centrality at all costs.

### B. Pivot to LLM wiki primary with skill-graph degraded compatibility (recommended)

Adopt `llm-wiki` as primary knowledge workflow and Obsidian as graph-view surface, while explicitly degrading skill-graph to compatibility mode with bounded obligations and non-blocking status outside defined gates.

Pros:

- Reduces operational coupling and closeout friction.
- Keeps durable markdown knowledge as first-class source.
- Preserves optional compatibility rather than disruptive hard removal.

Cons:

- Requires a coordinated migration contract and governance updates.
- Temporary dual-mode complexity until compatibility boundaries are complete.

Best fit:

- Teams prioritizing durable knowledge operations and predictable delivery.

### C. Hard cutover away from skill-graph

Immediately retire skill-graph gating and replace with wiki-only governance.

Pros:

- Fastest simplification of runtime and governance surface.
- Eliminates dual-mode ambiguity quickly.

Cons:

- Highest migration risk and largest change blast radius.
- Greater chance of regressions in legacy consumers.

Best fit:

- Greenfield or low-dependency environments.

## Recommendation

Choose **Approach B**.

This is the best balance of risk and leverage: shift the primary system to an easier-to-operate wiki model, keep compatibility controls for legacy skill-graph consumers, and add explicit anti-stall governance so the same degradation pattern does not recur.

## Requirements

### Pivot and Mode Contract

- R1. The repository must define one explicit primary knowledge operating mode: `llm_wiki_primary`.
- R2. Skill-graph lane must be reclassified as `degraded_compatibility` with clear non-blocking defaults and explicit blocking exceptions.
- R3. Obsidian graph usage must be defined as a viewer/inspection surface over wiki markdown links, not as an alternate source-of-truth.

### Source-of-Truth and Ownership

- R4. Wiki markdown content under a defined canonical wiki root must become the primary human and agent knowledge source.
- R5. Raw-source, wiki-content, and governance/schema layers must remain separated with explicit ownership boundaries.
- R6. Runtime/projection/generated surfaces must have one authoritative writer each, with documented deny-by-default behavior for non-authoritative writers.

### Re-organization and Scaffold Integrity

- R7. Re-organization must produce a stable, documented scaffold contract that removes ambiguity between canonical sources, factory mechanics, and runtime/projection outputs.
- R8. Scaffold contract must include machine-checkable parity and freshness controls for all required discovery surfaces.
- R9. Path and command compatibility needed by existing operators must be declared explicitly, not implied.

### Anti-Stall Governance

- R10. Every required gate must have named owner, escalation window, and deterministic blocker code taxonomy.
- R11. A gate can block promotion only when its blocker conditions and evidence paths are contract-defined.
- R12. Plan/spec/requirements status must be synchronized with execution evidence; status/checklist drift is a validation failure.
- R13. The pivot must include a recurring closeout health check that reports unresolved blockers, stale evidence, and ownership gaps.
- R14. Every gate and spec must include freshness metadata (timestamp, source, TTL or equivalent); absence of freshness metadata or indeterminate freshness must be treated as a blocker; recurring closeout health checks must surface unresolved blockers and ownership gaps with missing or unknown freshness.

### Alignment for Existing Blocked Lanes (1, 2, 4)

- R15. The new spec/plan must explicitly absorb and resolve the currently blocked certification/readiness concerns without keeping skill-graph as the primary delivery dependency.
- R16. The new spec/plan must include runtime-separation recovery obligations and success gates that return control-plane status to healthy.
- R17. The new spec/plan must include ask CLI contract completion obligations for remaining contract gaps that affect deterministic governance signaling.

### Safety and Privacy

- R18. Privacy classification and redaction policy must be defined before ingesting sensitive corpora into wiki pages.
- R19. Governance outputs must avoid leaking sensitive runtime details while preserving actionable diagnostics.

### Installation and Inspection Orchestration

- R20. Any installation or migration flow in this pivot lane must run with an explicit skill stack that includes `llm-wiki`, `coderabbit:simplify`, `uv-python-project-setup`, and `baseline-ui`; skipping one requires an explicit blocked reason with evidence.
- R21. Installation flows must execute with inspection support roles, prioritizing `skill-inspector` and `plugin-inspector`, with deterministic fallback roles and recorded rationale when either role is unavailable. Canonical role identifiers and fallback roles are defined in `docs/specs/2026-04-13-feat-llm-wiki-runtime-pivot-spec.md` section "Core Domain Model" under `InstallationOrchestrationContract` (source of truth). UI/display aliases may use prefixed forms like `@skill-inspector`, but canonical contract tokens are bare identifiers without the `@` prefix.
- R22. Role availability must be checked before execution and captured in run evidence so missing inspector roles cannot silently degrade installation quality.
- R23. The spec/plan must define a fail-closed policy for installation quality checks: if required skill stack or inspection support cannot run, promotion is blocked until fallback or remediation path is complete.

## Success Criteria

- A new pivot spec exists and is approved, with explicit mode contract (`llm_wiki_primary` + `degraded_compatibility`).
- A new pivot plan exists and is approved, with phase gates, owner mapping, and anti-stall controls.
- Wiki scaffold and governance boundaries are documented and verifiable.
- Control-plane health no longer reports degraded status for runtime-separation-related checks.
- Status/checklist drift across active requirements/spec/plan artifacts is detectably prevented.
- Legacy compatibility is preserved where required, with explicit deprecation posture and migration signals.
- Operators can use Obsidian as graph viewer against wiki links without introducing a second source-of-truth.
- Installation runs in this lane prove required skill-stack usage and inspector-role availability/fallback evidence.

## Scope Boundaries

In scope:

- Pivot decision and requirements for wiki-first operating model.
- Scaffold re-organization requirements and ownership contracts.
- Anti-stall governance requirements and closeout health rules.
- Alignment requirements for blocked lanes 1, 2, and 4.
- Installation-orchestration policy for required skills and inspector roles.

Out of scope:

- Full implementation sequencing and file-by-file migration tasks.
- Detailed schema, endpoint, or script-level implementation design.
- Immediate deletion of all skill-graph artifacts.
- Any broad feature work unrelated to this pivot and scaffold reliability.

## Key Decisions

- Primary knowledge model shifts to `llm-wiki`.
- Obsidian is a graph-view consumer, not canonical storage.
- Skill-graph lane is degraded to compatibility mode instead of hard-cut removal.
- Anti-stall governance is part of core requirements, not optional follow-up.
- New spec and plan must explicitly absorb blocked-lane obligations to avoid split ownership.

## Dependencies and Assumptions

- Existing `llm-wiki` skill and markdown workflow can be used as the base operating pattern.
- Existing runtime-separation governance artifacts are retained and updated, not replaced ad hoc.
- Existing operator commands and validation surfaces remain available during migration.
- Team accepts staged compatibility rather than immediate hard cutover.

## Outstanding Questions

### Resolve Before Planning

- Q1. Which exact wiki root path is canonical for this pivot (for example `wiki/` or an existing equivalent), and is this required to be repo-root scoped?
- Q2. Which current skill-graph gates remain true release blockers after degradation, and which become monitor-only?

### Deferred to Planning

- Exact phase breakdown and migration sequencing.
- Concrete command contracts and automation schedule for recurring health checks.
- Specific artifact rewrite/archive policy for legacy skill-graph outputs.
- Exact CI wiring and failure severity mapping for status/checklist drift checks.

## Next Steps

Recommended next stage: **`ce-spec`**.

Spec work should lock:

1. Mode/state contract for `llm_wiki_primary` and `degraded_compatibility`.
2. Canonical scaffold boundaries and writer/reader authority matrix.
3. Gate taxonomy, blocker semantics, owner/escalation contract, and closeout health policy.
4. Compatibility and deprecation policy for legacy skill-graph consumers.

After spec approval, proceed to **`ce-plan`** for execution sequencing.
