# Best-Practices Hardening Review: HE Spec/Plan/Work Gaps (14-Day Session Evidence)

## Scope
- Canonical plugin source only: `Plugins/harness-engineering/**`
- Evidence bundle: `/private/tmp/he-session-collector-14d-bundle/**`
- Cross-repo failure notes (implementation reality): `/Users/jamiecraik/dev/coding-harness/.harness/implementation-notes/**`
- Objective: convert repeated failure signals into concrete hardening targets for agent-native behavior, runtime persistence, strict boundaries, and missing template/spec/reference coverage.

## Evidence Highlights
1. Session collector repeatedly classifies HE-related sessions as `coverage-gap`, `environment-blocker`, `quality-regression`, and often `routing-mismatch`/`missing-validation` with failed or blocked outcomes.
   - Source: `/private/tmp/he-session-collector-14d-bundle/skill-refactor-handoffs.json` (examples: `session-1490`, `1697`, `1040`, `1318`, `1620`, `1622`, `1695`).
2. Known real-world failures include “full implementation request silently downscoped to advisory/smallest slice” and “repo guard passed but runtime agent role unavailable (`unknown agent_type`).”
   - Source: `/Users/jamiecraik/dev/coding-harness/.harness/implementation-notes/2026-05-21-full-implementation-downscope-steering-admission.md`
   - Source: `/Users/jamiecraik/dev/coding-harness/.harness/implementation-notes/2026-05-20-internal-agent-runtime-freshness.md`
3. HE skills already include strong contracts for linear mutation truth, artifact shape, BLUF, and confidence ceilings, but they do not yet enforce explicit anti-downscope checks, runtime-freshness admission checks, or coding/testing persona lens declarations at spec/plan generation time.
   - Sources:
     - `Plugins/harness-engineering/skills/he-spec/SKILL.md`
     - `Plugins/harness-engineering/skills/he-plan/SKILL.md`
     - `Plugins/harness-engineering/references/skills/he-spec/spec-artifact-contract.md`
     - `Plugins/harness-engineering/references/skills/he-plan/plan-artifact-contract.md`
     - `Plugins/harness-engineering/references/skills/he-plan/professional-confidence-review.md`

## Severity-Ranked Findings

### 1) CRITICAL: No deterministic “full-implementation vs downscope” gate in HE plan/spec contracts
- Evidence:
  - Downscope failure was real and recurring enough to require a dedicated guard in coding-harness (`docs:steering:guard`), proving this class of mistake is not hypothetical.
  - HE plan/spec artifacts currently require scope and boundaries, but no explicit “if user asks full implementation, any reduction must be admitted as unresolved full scope + explicit acceptance of reduction.”
- Affected surfaces:
  - `Plugins/harness-engineering/references/skills/he-plan/plan-artifact-contract.md`
  - `Plugins/harness-engineering/references/skills/he-spec/spec-artifact-contract.md`
  - `Plugins/harness-engineering/skills/he-plan/SKILL.md`
  - `Plugins/harness-engineering/skills/he-spec/SKILL.md`
- Risk:
  - Allows polished artifact compliance while still violating user intent authority.
- Hardening target:
  - Add mandatory `Scope Authority Check` section and lint rule:
    - input intent class: `full_implementation | bounded_slice | advisory`
    - required when `full_implementation`: explicit list of unimplemented surfaces + “not closure-ready” marker unless user-approved narrowing exists.
    - forbid completion framing when unresolved full-scope surfaces remain.

### 2) HIGH: Runtime persistence/freshness boundary is documented as principle but not required in spec/plan outputs
- Evidence:
  - Runtime role freshness issue (`unknown agent_type`) demonstrates repo-inventory pass != active runtime capability.
  - HE documents source/runtime distinctions, but spec/plan templates do not require a runtime-admission block when execution depends on role/tool/runtime availability.
- Affected surfaces:
  - `Plugins/harness-engineering/skills/he-spec/SKILL.md`
  - `Plugins/harness-engineering/skills/he-plan/SKILL.md`
  - `Plugins/harness-engineering/references/skills/he-plan/professional-confidence-review.md`
- Risk:
  - Plans can look execution-ready while runtime prerequisites are stale or unavailable.
- Hardening target:
  - Add required `Runtime Freshness Admission` fields to spec/plan contracts:
    - `runtime_surface`
    - `runtime_probe_command_or_check`
    - `runtime_probe_status: pass|fail|blocked|not_applicable`
    - `runtime_blocker_class` (e.g., `unknown_agent_type`, `tool_unavailable`)
    - `fallback_authority` and stop condition.
  - Confidence ceiling must auto-cap when runtime probe is missing/blocked for runtime-dependent slices.

### 3) HIGH: Missing standardized blocker taxonomy in stage outputs for swarm/runtime failures
- Evidence:
  - AGENTS contract for review swarms requires `STATUS: blocked_runtime|blocked_missing_artifact|blocked_validation`, but this schema is not mirrored as required status classes inside he-spec/he-plan/he-work output templates.
- Affected surfaces:
  - `Plugins/harness-engineering/skills/he-work/SKILL.md` output template
  - `Plugins/harness-engineering/skills/he-spec/SKILL.md` output format
  - `Plugins/harness-engineering/skills/he-plan/SKILL.md` output format
- Risk:
  - Inconsistent blocker semantics across HE stages and reviewer lanes; weakens machine-level routing and guardrails.
- Hardening target:
  - Add shared enum contract for blocker outputs:
    - `blocked_runtime`
    - `blocked_missing_artifact`
    - `blocked_validation`
    - `blocked_authority`
    - `blocked_source_of_truth`
  - Require one-line “smallest recovery step” for each blocked class.

### 4) HIGH: Coding/testing persona lenses are optional and implicit, not enforced where decisions are made
- Evidence:
  - User request asks for coding/testing persona expertise as an additional layer.
  - `he-work` references cookbook/software-literature lens packs, but `he-spec` and `he-plan` contracts do not require explicit persona-lens admission/mapping in generated artifacts.
- Affected surfaces:
  - `Plugins/harness-engineering/skills/he-work/SKILL.md`
  - `Plugins/harness-engineering/references/skills/he-work/work-execution-contract.md`
  - `Plugins/harness-engineering/references/skills/he-spec/spec-artifact-contract.md`
  - `Plugins/harness-engineering/references/skills/he-plan/plan-artifact-contract.md`
- Risk:
  - Inconsistent use of adversarial/correctness/testing lenses; “review depth” depends on operator memory rather than contract.
- Hardening target:
  - Add required `Expertise Lens Matrix` in spec/plan/work:
    - `coding_correctness_lens`
    - `testing_rigor_lens`
    - `maintainability_lens`
    - `reliability_lens`
    - each row: trigger condition, evidence used, gate command, unresolved risk.
  - Add eval acceptance checks for presence/quality of lens matrix in non-trivial plans/specs.

### 5) MEDIUM: Collector evidence is present but under-integrated into contract-level anti-regression checks
- Evidence:
  - `skill-refactor-handoffs.json` records recurring root causes and blocker taxonomy, yet contract/evals do not enforce targeted checks against top recurrent causes (coverage-gap, routing-mismatch, missing-validation).
- Affected surfaces:
  - `Plugins/harness-engineering/skills/he-spec/references/evals.yaml`
  - `Plugins/harness-engineering/skills/he-plan/references/evals.yaml`
  - `Plugins/harness-engineering/skills/he-work/references/*`
- Risk:
  - Repeats known failures without turning them into deterministic fail conditions.
- Hardening target:
  - Add “recurrence gate” eval scenarios seeded from collector classes:
    - downscope without admission
    - runtime-dependency without runtime probe
    - missing validation claims
    - routing mismatch without explicit blocker.
  - Require explicit `collector_evidence_ref` field when session evidence is used.

### 6) MEDIUM: Spec/plan templates are strong on format but weaker on “closure-proof vs local-progress” anti-fog checks
- Evidence:
  - HE includes linear mutation statuses and confidence language, but real-world pattern still required external correction to prevent advisory progress from masquerading as completion.
- Affected surfaces:
  - `Plugins/harness-engineering/references/skills/he-plan/professional-confidence-review.md`
  - `Plugins/harness-engineering/references/skills/he-plan/plan-artifact-contract.md`
- Risk:
  - High-quality documents can still overstate closure readiness.
- Hardening target:
  - Add mandatory `Closure Proof Boundary` section:
    - local evidence status
    - remote/tracker/PR evidence status
    - explicit “not done until” criteria.
  - Add unresolved-marker lint for closure wording (“ready”, “complete”, “shipped”) when required proof fields are absent.

## Patch-Ready Hardening Targets

1. Add a shared reference contract:
   - New file proposal: `Plugins/harness-engineering/references/full-implementation-boundary-contract.md`
   - Defines downscope admission, intent authority, unresolved-full-scope markers, forbidden completion language.
2. Add runtime admission contract:
   - New file proposal: `Plugins/harness-engineering/references/runtime-freshness-contract.md`
   - Shared by he-spec/he-plan/he-work; includes runtime probe and blocker taxonomy.
3. Extend artifact shape validator:
   - Update `Plugins/harness-engineering/scripts/check_generated_artifact_shape.py`
   - New checks:
     - required scope authority block when full implementation requested
     - runtime freshness block for runtime-dependent slices
     - blocker taxonomy compliance.
4. Extend lint/marker checks:
   - Add unresolved-marker patterns for downscope + closure-overclaim.
5. Promote expertise lenses from optional to contract fields:
   - Require `Expertise Lens Matrix` in plan/spec/work templates for non-trivial slices.
6. Add targeted eval fixtures:
   - Update `he-spec/references/evals.yaml` and `he-plan/references/evals.yaml`
   - Include recurrence fixtures for downscope, runtime-freshness, and missing-validation regressions.

## Keep / Discard Guidance

### Keep
- Existing artifact identity + linear traceability + BLUF + confidence ceiling contracts.
- Existing strict source/runtime ownership language in HE AGENTS and skill front doors.
- Existing non-mutation boundaries and handoff discipline.

### Discard / Replace
- Implicit handling of full-implementation intent.
- Implicit runtime readiness assumptions.
- Optional persona-lens usage for non-trivial planning/specification.
- Free-form blocker wording that cannot be routed consistently.

## Confidence
- High on fault classes and affected surfaces because evidence is direct from:
  - 14-day session collector outputs
  - canonical HE skill/reference contracts
  - concrete coding-harness admission notes documenting realized failures.
- Medium on implementation effort sizing because validator internals were not exhaustively inspected in this pass.

## Residual Risk
- Until contract + validator + eval changes land together, behavior may drift back to “format-passing but intent-failing” outputs.
- Runtime freshness remains a practical blocker in any environment where role/tool registry differs from repo inventory.
- Persona-layer quality will remain operator-dependent without schema-level enforcement.

WROTE: /Users/jamiecraik/dev/agent-skills/artifacts/reviews/he-spec-plan-gap-hardening/best-practices-researcher.md
