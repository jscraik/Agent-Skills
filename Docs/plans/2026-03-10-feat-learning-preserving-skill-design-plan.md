---
title: feat: Learning-Preserving Skill Design Delivery Plan
type: feat
status: active
date: 2026-03-10
origin: docs/brainstorms/2026-03-10-learning-preserving-skills-brainstorm.md
spec: Docs/specs/2026-03-10-feat-learning-preserving-skill-design-spec.md
deepened: 2026-03-10
---

# feat: Learning-Preserving Skill Design Delivery Plan

## Enhancement Summary

**Deepened on:** 2026-03-10
**Key areas improved:** phase ordering, pilot readiness gates, validator coverage, rollout hold rules, evidence paths

- Added explicit pilot-baseline and readiness checks so skill edits do not start before current profiles, evals, and diagnostics are confirmed.
- Tightened the metadata and validator phase with a clear decision fork: extend `Infrastructure/references/task-profile.json` safely or stop and use a bounded companion artifact.
- Expanded rollout guidance with concrete gate commands, partial-vs-blocked handling, and a short post-implementation review cadence.
- Added an evidence-path section so implementers know which docs, pilot files, and validators must stay in sync.
- Added a no-regression execution contract: canonical pilot targets are fixed, every candidate change must beat a recorded five-gate baseline, and checklist advancement is blocked until that bar is met.

## Table of Contents
- [Enhancement Summary](#enhancement-summary)
- [Overview](#overview)
- [Origin Traceability](#origin-traceability)
- [Problem Statement / Motivation](#problem-statement--motivation)
- [Scope and Non-Goals](#scope-and-non-goals)
- [Implementation Phases](#implementation-phases)
- [Task Graph (id / depends_on)](#task-graph-id--depends_on)
- [Planned File Map](#planned-file-map)
- [Dependencies and Risks](#dependencies-and-risks)
- [Evidence Paths and Gate Commands](#evidence-paths-and-gate-commands)
- [Test and Validation Strategy](#test-and-validation-strategy)
- [Rollout / Migration / Monitoring](#rollout--migration--monitoring)
- [Acceptance Checklist](#acceptance-checklist)
- [Sources & References](#sources--references)

## Overview

Implement the learning-preserving skill design pilot as a spec-preserving repo improvement across docs, pilot skills, evaluation metadata, telemetry classification, and conformance reporting.

Plan posture:
- contract-first, not implementation-first
- preserve canonical delegation mode semantics
- propagate the concept once at repo level, then into a bounded pilot set
- require evaluation and observability before claiming pilot completion

Execution rules:
- do not edit pilot skill behavior before Phase 0 baseline evidence exists
- do not let posture metadata mutate or shadow `delegation.mode`
- treat missing eval or telemetry support as a rollout hold, not a documentation follow-up
- treat git-history baseline recovery as the first safe fallback when a pilot-skill rewrite degrades quality gates
- keep canonical validation targets explicit:
  - `Skills/skill-builder`
  - `frontend/tools/agentation`
  - `Skills/systematic-debugging`
  - `interview/interview-me`
- do not treat `.agents/skills/*` mirrors as gold-bar pilot targets unless they carry the same validator-grade support files as the canonical skill path

## Origin Traceability

Mapped from the brainstorm and spec into this execution plan:
- bounded-autonomy compatibility from the brainstorm is preserved by keeping `LearningPosture` separate from canonical delegation mode
- pilot-first rollout from the brainstorm is preserved by freezing the four named pilot skills before broader template propagation
- spec compatibility rules are preserved by making metadata/validator work complete before skill prose and eval changes ship
- spec degraded/blocked handling is preserved by treating weak telemetry or invalid posture/mode pairings as hold conditions rather than silent success

## Problem Statement / Motivation

The spec defines `LearningPosture` as a second dimension alongside existing `DelegationMode`, but the repo does not yet have the implementation sequence needed to add that concept safely.

Without a plan, execution risks:
- mixing `LearningPosture` into existing `delegation.mode` contracts
- updating skill prose without matching eval or telemetry support
- drifting across pilot skills without a canonical repo-level definition
- claiming pilot success without a conformance summary or degraded-state handling

This plan defines the implementation order, dependencies, and validation gates needed to deliver the pilot without changing the spec’s core behavior.

## Scope and Non-Goals

In scope:
- define and publish the repo-level `LearningPosture` contract
- extend the skill authoring surface for pilot adoption
- add pilot machine-readable metadata or validation hooks needed for posture-aware evals
- update the four pilot skills named by the spec
- add pilot evaluation and telemetry coverage
- produce a conformance summary artifact for the pilot

Non-goals:
- repo-wide migration of all skills
- changing canonical `autopilot | co-pilot | manual` semantics
- redesigning question lifecycle or promotion-gate ownership
- adding runtime auto-classification of posture beyond what the spec allows
- implementing unrelated skill quality improvements while touching pilot files

## Implementation Phases

### Phase 0: Contract Freeze and Pilot Baseline

Objective: establish the authoritative source set and freeze pilot boundaries before touching pilot skills.

Work:
- Confirm the linked spec remains the source of truth.
- Freeze the initial pilot skill set from the spec:
  - `Skills/skill-builder`
  - `frontend/tools/agentation`
  - `Skills/systematic-debugging`
  - `interview/interview-me`
- Capture the current baseline for each pilot skill:
  - current `SKILL.md`
  - current `Infrastructure/references/task-profile.json` where present
  - current `Infrastructure/references/evals.yaml` where present
- Record the exact conformance questions the implementation must answer:
  - does the skill declare posture support?
  - does posture preserve the spec boundary from delegation mode?
  - do evals test posture-specific behavior?
  - do telemetry/conformance artifacts distinguish `pass | partial | blocked`?
- Run current-state diagnostics for each pilot skill:
  - `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py skill-builder`
  - `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py agentation`
  - `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py systematic-debugging`
  - `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py interview-me`
- Confirm each pilot skill currently has both `Infrastructure/references/task-profile.json` and `Infrastructure/references/evals.yaml` before metadata design begins.
- Persist a dated baseline snapshot bundle for each pilot (`SKILL.md`, `Infrastructure/references/task-profile.json`, `Infrastructure/references/evals.yaml`, plus raw diagnostics) for replayability and evidence diffs.
- Record a per-pilot no-regression matrix before any edits:
  - `quick_validate`
  - `skill_gate`
  - `analyze_skill`
  - `openclaw_skill_guard`
  - `run_skill_evals`
- Store the baseline matrix alongside the pilot evidence bundle so every later rerun can be compared mechanically against the original bar.
- For `frontend/tools/agentation`, record the upstream compatibility anchors used for future comparisons:
  - `npx skills add benjitaylor/agentation`
  - `ln -s "$(pwd)/skills/agentation-self-driving" ~/.codex/skills/agentation-self-driving`
- Record the current public-web evidence source for Agentation separately from repo history. If the public site is unavailable, parked, or otherwise non-authoritative, mark the web evidence as blocked instead of silently replacing it with unstated assumptions.

Exit criteria:
- Pilot skill list is frozen.
- Baseline files and validation commands are recorded.
- No unresolved contract-level ambiguity remains about posture vocabulary or pilot scope.
- All four pilot skills pass baseline diagnostics with no missing-profile warnings.
- All four pilot skills have a recorded five-gate baseline matrix that later edits can be compared against.

Hold rules:
- If any pilot skill is missing baseline metadata or eval files, stop before Phase 1 and resolve the pilot surface mismatch first.
- If the linked spec changes materially during baseline capture, restart Phase 0 and re-freeze scope.
- If a pilot skill does not have a trustworthy historical or current baseline, do not start improvements for that skill until the missing baseline evidence is reconstructed.

### Phase 1: Repo-Level Contract and Authoring Surface

Objective: define the concept once at repo level and create the canonical propagation path.

Work:
- Add the canonical `LearningPosture` definition to `docs/skill-graphs/index.md`.
- Add a contributor-facing summary to `README.md`.
- Extend `Infrastructure/templates/SKILL.md.template` with a reusable pilot-ready contract shape for posture guidance.
- If needed, add a short reference doc for posture semantics rather than overloading `SKILL.md` bodies.
- Keep repo-level language aligned with the existing all-skills onboarding contract so the new posture language reads as an additive layer, not a replacement vocabulary.
- Run `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json` immediately after this phase.

Exit criteria:
- There is one authoritative repo-level definition of `LearningPosture`.
- The authoring template can express posture support without redefining delegation mode.
- Repo docs do not contradict the spec or each other.

Hold rules:
- If repo-level docs and template wording disagree on posture names or semantics, stop here and reconcile them before touching pilot skills.

### Phase 2: Machine-Readable Metadata and Validation Hooks

Objective: make posture-aware validation possible without corrupting existing task-profile contracts.

Work:
- Decide the machine-readable home for pilot posture metadata consistent with the spec:
  - `Infrastructure/references/task-profile.json`
  - or a tightly-scoped companion artifact if that proves safer
- Record the required fork resolution in a machine-readable decision artifact before starting pilot skill edits:
  - `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home-decision.json`
  - required fields:
    - `selected_metadata_home` (either `Infrastructure/references/task-profile.json` or `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home.json`)
    - `pilot_profile_candidates`
    - `compatibility_rationale`
    - `approver`
    - `approval`
    - `decision_status`
    - `decision_rationale`
    - `decided_at`
- Single source of truth rule: `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home-decision.json` is the only authoritative fork decision artifact and must exist before pilot skill-file changes.
- Update the relevant schema docs or validation expectations without redefining `delegation.mode`.
- Add or extend validator logic to fail closed on:
  - missing posture declaration for pilot skills
  - invalid/degraded posture-plus-mode combinations
  - contradictory repo-level vs pilot-skill posture semantics
- Keep legacy compatibility behavior explicit and bounded.
- Prefer extending existing freshness/diagnostic checks before inventing a parallel validator entrypoint.
- Validation sequence for this phase:
  - `python3 Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict`
  - pilot-skill reruns of `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py <skill-name>`
- Gate command required before Phase 3 starts:
  - ```bash
    python3 - <<'PY'
    from pathlib import Path
    import json

    path = Path("Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home-decision.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("selected_metadata_home") not in {
        "Infrastructure/references/task-profile.json",
        "Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home.json",
    }:
        raise SystemExit("selected_metadata_home must be explicitly constrained to a known option")
    if (
        not payload.get("approver")
        or not payload.get("approval")
        or not payload.get("decision_status")
        or not payload.get("decision_rationale")
        or not payload.get("decided_at")
    ):
        raise SystemExit("decision artifact is missing approver/approval/decision audit fields")
    if payload.get("decision_status") != "approved":
        raise SystemExit("Phase 2 must produce an approved decision before Phase 3")
    if not payload.get("pilot_profile_candidates"):
        raise SystemExit("pilot_profile_candidates is empty")
    print("metadata-home decision artifact is explicit and complete")
    PY
    ```
- If `Infrastructure/references/task-profile.json` cannot hold the posture data without compromising the schema boundary, freeze that decision explicitly and route the pilot to a companion artifact rather than half-extending the current contract.

Exit criteria:
- Pilot metadata can express posture in a machine-readable way.
- Invalid pairings such as `autopilot + learn` are caught deterministically.
- Existing delegation-mode validation remains intact.
- Phase-2 decision artifact exists and is explicit before any pilot skill changes begin.

Hold rules:
- If validator design requires redefining `delegation.mode`, Phase 2 fails closed and must be redesigned before Phase 3.
- If the metadata location remains ambiguous after design review, do not begin skill edits.

### Phase 3: Pilot Skill Propagation

Objective: update each pilot skill to declare posture support and behavior expectations in spec-preserving language.

Work:
- Update `Skills/skill-builder` first to establish the standards-setting pattern other pilot skills should follow.
- Update `frontend/tools/agentation` second to distinguish throughput-first autopilot behavior from learning-preserving guidance without weakening its execution contract.
- For `frontend/tools/agentation`, treat both source families as required inputs before any wording change is accepted:
  - public workflow/install compatibility sources captured in `frontend/tools/agentation/Infrastructure/references/public-sources.md`
  - local annotation-format and output-contract sources captured in `frontend/tools/agentation/Infrastructure/references/annotation-format.md`
- Update `Skills/systematic-debugging` third to reflect `learn` and `guided` posture expectations for diagnosis-heavy work.
- Update `interview/interview-me` last to reinforce posture-aware clarification and explain-back behavior where relevant.
- Keep each skill’s routing and existing core scope intact.
- Change one pilot skill at a time and finish its full validation comparison before editing the next pilot skill.
- Keep prose/routing changes separate from harness, validator, or telemetry changes so regressions can be attributed cleanly.
- After each pilot skill update:
  - run `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py <skill-name>`
  - rerun `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json` if the change touches shared docs or linked references
  - rerun the full five-gate matrix for that skill and compare it to the Phase 0 baseline before moving on

Exit criteria:
- All four pilot skills declare posture support consistently.
- No pilot skill redefines delegation/runtime mode.
- Execution-first warnings are explicit where required by the spec.
- No pilot skill lands below its Phase 0 five-gate baseline.

Hold rules:
- If one pilot skill requires posture semantics that contradict the repo-level definition, stop propagation and resolve the contract before continuing to the next skill.
- If any pilot skill regresses on any of the five gates relative to its recorded baseline, restore the last acceptable version before attempting another improvement round.

### Phase 4: Evaluation Coverage

Objective: ensure pilot posture claims are tested, not just documented.

Work:
- Extend pilot evals to cover posture-sensitive behavior:
  - explanation quality
  - code-reading or reasoning support
  - debugging independence or hypothesis-first behavior
  - delegation-risk detection
- Add negative or pressure cases for invalid posture/mode combinations where applicable.
- Preserve existing trigger and safety coverage while expanding posture coverage.
- Ensure each pilot skill has at least one evaluation that can fail on weak explanation or weak supervisory support even when the artifact itself looks correct.
- Treat blocked combinations (`autopilot + learn`) and degraded combinations (`autopilot + guided` without explicit critique-style limits) as separate negative cases.
- Canonical pilot posture eval gate commands (one command per pilot, must all pass):
  - `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --runner codex`
  - `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py frontend/tools/agentation --runner codex`
  - `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/systematic-debugging --runner codex`
- Merge-bar rule for pilot skill changes:
  - a skill change is only acceptable when `quick_validate`, `skill_gate`, `analyze_skill`, `openclaw_skill_guard`, and `run_skill_evals` are all acceptable versus that skill's recorded baseline
  - acceptable means pass-for-pass parity and no analyzer score regression unless an explicitly approved tradeoff is documented in the rollout note
  - checklist item `703` stays unchecked until the full pilot validation set is green and baseline comparisons are attached
  - `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py interview/interview-me --runner codex`

Exit criteria:
- Pilot skills have posture-aware eval coverage.
- Output-only success cannot mask posture-contract failure in pilot checks.
- Negative cases cover blocked or degraded combinations explicitly.
- All four canonical eval commands above complete with exit code `0`.

Hold rules:
- If a pilot skill has updated posture prose but no posture-specific eval coverage, it cannot be marked complete or included in rollout review.

### Phase 5: Telemetry and Conformance Summary

Objective: make the pilot observable as an operational contract, not just a prose change.

Work:
- Add structured interaction-pattern tags aligned to the spec:
  - `conceptual_inquiry`
  - `explain_then_generate`
  - `generate_then_explain`
  - `full_delegation`
  - `ai_led_debugging`
- Define these tag names as an explicit canonical enum in the summary schema and reject unknown values during generation.
- Add conformance reporting for each pilot skill:
  - declared posture
  - selected/default posture if available
  - eval coverage state
  - telemetry coverage state
  - conformance state: `pass | partial | blocked`
- Reuse existing artifact/reporting patterns where possible instead of inventing a parallel reporting system.
- Keep telemetry additions inside the existing event-envelope and reporting conventions described under `docs/skill-graphs/telemetry/` and existing `Infrastructure/artifacts/skill-graphs/` reporting trees.
- Introduce a versioned summary schema used by both generator and gate checks:
  - `docs/skill-graphs/schemas/learning-posture-pilot-conformance-summary.schema.json`
  - required root fields: `pilot_version`, `generated_at`, `overall_state`, `pilot_skills`
  - required per-skill fields: `skill`, `declared_posture`, `selected_posture`, `eval_state`, `telemetry_state`, `conformance_state`, `interaction_pattern_tags`, `warnings`
- Produce one canonical pilot summary under existing skill-graph artifact trees:
  - `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json`
- Build and generate this summary with one canonical script so it is always machine-produced, never hand-edited:
  - `python3 Infrastructure/scripts/lifecycle-and-sync/build_learning_posture_pilot_summary.py --out-json Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json`
- Validate against the schema in the same phase:
  - `python3 -m jsonschema -i Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json docs/skill-graphs/schemas/learning-posture-pilot-conformance-summary.schema.json`
- Freshness gate for rollout:
  - ```bash
    python3 - <<'PY'
    from pathlib import Path
    import json

    artifact = Path("Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json")
    sources = [
        Path("Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home-decision.json"),
        Path("Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home.json"),
        Path("Skills/skill-builder/Infrastructure/references/task-profile.json"),
        Path("Skills/skill-builder/Infrastructure/references/evals.yaml"),
        Path("frontend/tools/agentation/Infrastructure/references/task-profile.json"),
        Path("frontend/tools/agentation/Infrastructure/references/evals.yaml"),
        Path("Skills/systematic-debugging/Infrastructure/references/task-profile.json"),
        Path("Skills/systematic-debugging/Infrastructure/references/evals.yaml"),
        Path("interview/interview-me/Infrastructure/references/task-profile.json"),
        Path("interview/interview-me/Infrastructure/references/evals.yaml"),
    ]

    if not artifact.exists() or artifact.stat().st_mtime < max(p.stat().st_mtime for p in sources if p.exists()):
        raise SystemExit("conformance summary is missing or stale")

    summary = json.loads(artifact.read_text(encoding="utf-8"))
    required_root = {"pilot_version", "generated_at", "overall_state", "pilot_skills"}
    missing_root = required_root - set(summary)
    if missing_root:
        raise SystemExit(f"conformance summary missing required root fields: {sorted(missing_root)}")

    if summary.get("overall_state") not in {"pass", "partial", "blocked"}:
        raise SystemExit("overall_state must be one of: pass, partial, blocked")

    entries = summary.get("pilot_skills")
    if not isinstance(entries, list) or not entries:
        raise SystemExit("pilot_skills must be a non-empty list")

    required_entry = {
        "skill",
        "declared_posture",
        "selected_posture",
        "eval_state",
        "telemetry_state",
        "conformance_state",
        "interaction_pattern_tags",
        "warnings",
    }
    valid_tags = {
        "conceptual_inquiry",
        "explain_then_generate",
        "generate_then_explain",
        "full_delegation",
        "ai_led_debugging",
    }

    for item in entries:
        missing = required_entry - set(item)
        if missing:
            raise SystemExit(f"pilot skill summary entry missing fields: {sorted(missing)}")

        if item.get("conformance_state") not in {"pass", "partial", "blocked"}:
            raise SystemExit("conformance_state must be one of: pass, partial, blocked")

        tags = item.get("interaction_pattern_tags")
        if not isinstance(tags, list):
            raise SystemExit("interaction_pattern_tags must be a list")
        extra = set(tags) - valid_tags
        if extra:
            raise SystemExit(f"invalid interaction_pattern_tags: {sorted(extra)}")

    print("conformance summary is present, current, and valid")
    PY
    ```

Exit criteria:
- Pilot conformance can be inspected in one summary artifact or report.
- Missing telemetry is surfaced as degraded or partial, not silent success.
- The summary is machine-diffable and usable for follow-up rollout decisions.

Hold rules:
- If telemetry cannot distinguish interaction-pattern categories without schema drift or ambiguous tagging, mark the pilot `partial` and stop before rollout expansion.

### Phase 6: Validation, Rollout Gate, and Handoff

Objective: complete the pilot with explicit evidence and a safe handoff for broader work.

Work:
- Run focused validation on docs, metadata, and pilot-specific validators.
- Run broader repo validation using canonical commands.
- Review pilot outcomes against the spec’s conformance expectations.
- Produce a rollout decision note for the pilot:
  - keep pilot-only
  - expand to more skills
  - revise contract before expansion
- Required gate commands for this phase:
  - `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
  - `python3 Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict`
  - `python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py --strict --run-state-check`
  - `bash Infrastructure/scripts/validate_all.sh`

Exit criteria:
- Validation passes with evidence.
- Pilot conformance summary exists and is reviewable.
- Remaining open questions are implementation-shaped, not contract-shaped.
- The repo is ready for follow-on work without reopening the spec.

Hold rules:
- Any failing strict validator or missing conformance summary blocks rollout signoff.
- If the rollout decision is `revise contract before expansion`, the handoff must route back to spec/plan refinement rather than implementation expansion.

## Task Graph (id / depends_on)

```yaml
tasks:
  - id: P0
    title: Freeze pilot scope and baseline existing pilot files
    depends_on: []
  - id: P1
    title: Add canonical LearningPosture docs to repo-level skill graph docs
    depends_on: [P0]
  - id: P2
    title: Add contributor/template propagation path for posture-aware authoring
    depends_on: [P1]
  - id: P2b
    title: Record metadata-home decision artifact for pilot posture metadata location
    depends_on: [P2]
  - id: P3
    title: Add machine-readable posture metadata contract and validator hooks
    depends_on: [P2, P2b]
  - id: P4
    title: Update pilot skill-builder contract for posture-aware behavior
    depends_on: [P2b, P3]
  - id: P5
    title: Update pilot agentation contract for posture-aware behavior
    depends_on: [P2b, P3]
  - id: P6
    title: Update pilot systematic-debugging contract for posture-aware behavior
    depends_on: [P2b, P3]
  - id: P7
    title: Update pilot interview-me contract for posture-aware behavior
    depends_on: [P2b, P3]
  - id: P8
    title: Extend pilot eval coverage for posture-sensitive behavior
    depends_on: [P4, P5, P6, P7]
  - id: P9
    title: Add telemetry classification and pilot conformance summary
    depends_on: [P3, P8]
  - id: P10
    title: Run pilot validation and produce rollout decision note
    depends_on: [P8, P9]
```

## Planned File Map

- `docs/skill-graphs/index.md`
  - primary repo-level home for `LearningPosture`
- `README.md`
  - contributor-facing summary and discoverability
- `Infrastructure/templates/SKILL.md.template`
  - propagation point for future skill creation
- `docs/skill-graphs/schemas/task-profile.schema.md`
  - preserve canonical delegation mode contract; extend only if posture metadata is formally added here
- `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home-decision.json`
  - records the fork decision and approver for machine-readable posture metadata location
- `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home.json`
  - optional companion metadata home if `Infrastructure/references/task-profile.json` cannot be safely extended
- `Infrastructure/scripts/lifecycle-and-sync/build_learning_posture_pilot_summary.py`
  - authoritative pilot conformance summary generator
- `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`
  - candidate validator surface for posture declaration or metadata quality checks
- `Infrastructure/scripts/validate_all.sh`
  - broader validation runner
- `Skills/skill-builder/SKILL.md`
  - pilot skill contract update
- `Skills/skill-builder/Infrastructure/references/evals.yaml`
  - pilot eval extension
- `Skills/skill-builder/Infrastructure/references/task-profile.json`
  - pilot metadata declaration
- `frontend/tools/agentation/SKILL.md`
  - pilot skill contract update
- `frontend/tools/agentation/Infrastructure/references/annotation-format.md`
  - local durable summary of Agentation annotation lifecycle, event envelope, and copied-output contract
- `frontend/tools/agentation/Infrastructure/references/evals.yaml`
  - pilot eval extension
- `frontend/tools/agentation/Infrastructure/references/public-sources.md`
  - dated trust-ranked public source memo for install, MCP, webhook, and self-driving compatibility claims
- `frontend/tools/agentation/Infrastructure/references/task-profile.json`
  - pilot metadata declaration
- `Skills/systematic-debugging/SKILL.md`
  - pilot skill contract update
- `Skills/systematic-debugging/Infrastructure/references/evals.yaml`
  - pilot eval extension
- `Skills/systematic-debugging/Infrastructure/references/task-profile.json`
  - pilot metadata declaration
- `interview/interview-me/SKILL.md`
  - pilot skill contract update
- `interview/interview-me/Infrastructure/references/evals.yaml`
  - pilot eval extension
- `interview/interview-me/Infrastructure/references/task-profile.json`
  - pilot metadata declaration
- `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json`
  - authoritative machine-diffable pilot conformance summary

## Open Questions (Resolved in this plan)

- Which artifact is the single approved home for posture metadata if `Infrastructure/references/task-profile.json` proves unsafe?
  - Approved decision file: `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home-decision.json`.
  - Required decision keys include `approver`, `approval`, `decision_status: approved`, and `decided_at`.
  - If `Infrastructure/references/task-profile.json` is unsafe, approved fallback is `Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home.json`.
- Which script is the canonical producer for the pilot conformance summary?
  - `python3 Infrastructure/scripts/lifecycle-and-sync/build_learning_posture_pilot_summary.py --out-json Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json`.
  - Canonical summary schema: `docs/skill-graphs/schemas/learning-posture-pilot-conformance-summary.schema.json`.
- Which evaluator command is the canonical gate for each pilot `Infrastructure/references/evals.yaml`?
  - `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py <pilot-path> --runner codex` for each pilot:
    - `Skills/skill-builder`
    - `frontend/tools/agentation`
    - `Skills/systematic-debugging`
    - `interview/interview-me`

## Dependencies and Risks

### Dependencies

- The linked spec remains authoritative.
- Pilot skills must stay within their existing routing boundaries.
- Existing validation and promotion contracts remain unchanged.
- The implementation must reuse existing repo validation/reporting patterns where possible.
- Repo-level docs and template changes must land before per-skill wording diverges.
- Human review is required for any decision that would move posture metadata outside the current task-profile path.
- Pilot rollout judgment depends on both eval coverage and telemetry evidence; either missing dimension keeps the pilot out of expansion review.

### Risks

- **Mode collision risk**
  - posture metadata could accidentally be merged into `delegation.mode`
  - mitigation: gate this in schema docs and validators early in Phase 2

- **Prose-only pilot risk**
  - skills could be updated without matching eval or telemetry coverage
  - mitigation: block pilot completion on Phases 4 and 5

- **Template drift risk**
  - repo-level docs, template wording, and pilot skills could diverge
  - mitigation: define the concept once in Phase 1 and validate propagation against that source

- **Telemetry ambiguity risk**
  - interaction tags may be too noisy to support real conclusions
  - mitigation: keep the initial tag set small and degrade to `partial` when signal is weak

- **Scope bloat risk**
  - pilot work could drift into repo-wide migration or runtime redesign
  - mitigation: freeze the pilot set in Phase 0 and reject non-pilot expansion in this plan

## Evidence Paths and Gate Commands

Primary evidence paths:
- [Docs/specs/2026-03-10-feat-learning-preserving-skill-design-spec.md](/Users/jamiecraik/dev/agent-skills/Docs/specs/2026-03-10-feat-learning-preserving-skill-design-spec.md)
- [docs/brainstorms/2026-03-10-learning-preserving-skills-brainstorm.md](/Users/jamiecraik/dev/agent-skills/docs/brainstorms/2026-03-10-learning-preserving-skills-brainstorm.md)
- [docs/skill-graphs/index.md](/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/index.md)
- [Infrastructure/templates/SKILL.md.template](/Users/jamiecraik/dev/agent-skills/Infrastructure/templates/SKILL.md.template)
- [Skills/skill-builder/Infrastructure/references/task-profile.json](/Users/jamiecraik/dev/agent-skills/Skills/skill-builder/Infrastructure/references/task-profile.json)
- [frontend/tools/agentation/Infrastructure/references/task-profile.json](/Users/jamiecraik/dev/agent-skills/frontend/tools/agentation/Infrastructure/references/task-profile.json)
- [Skills/systematic-debugging/Infrastructure/references/task-profile.json](/Users/jamiecraik/dev/agent-skills/Skills/systematic-debugging/Infrastructure/references/task-profile.json)
- [interview/interview-me/Infrastructure/references/task-profile.json](/Users/jamiecraik/dev/agent-skills/interview/interview-me/Infrastructure/references/task-profile.json)
- [Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home.json](/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home.json)
- [Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home-decision.json](/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home-decision.json)
- [Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json](/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json)
- [Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py)
- [Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py)
- [Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py)
- [Infrastructure/scripts/lifecycle-and-sync/build_learning_posture_pilot_summary.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/build_learning_posture_pilot_summary.py)

Gate commands:
- Baseline per-skill diagnostics:
  - `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py skill-builder`
  - `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py agentation`
  - `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py systematic-debugging`
  - `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py interview-me`
- Metadata and catalog integrity:
  - `python3 Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict`
- Metadata-home decision verification:
  - `python3 - <<'PY'
from pathlib import Path
import json

path = Path("Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home-decision.json")
payload = json.loads(path.read_text(encoding="utf-8"))
if payload.get("selected_metadata_home") not in {
    "Infrastructure/references/task-profile.json",
    "Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home.json",
}:
    raise SystemExit("selected_metadata_home must be constrained to a documented option")
required = {
    "selected_metadata_home",
    "pilot_profile_candidates",
    "compatibility_rationale",
    "approver",
    "approval",
    "decision_status",
    "decision_rationale",
    "decided_at",
}
if not required.issubset(payload):
    raise SystemExit("Decision artifact missing required keys")
if not payload.get("pilot_profile_candidates"):
    raise SystemExit("Decision artifact has no profile candidates")
if payload.get("decision_status") != "approved":
    raise SystemExit("metadata-home decision has not been approved")
print("metadata-home decision artifact verified")
PY`
- Pilot conformance summary generation and freshness check:
  - `python3 Infrastructure/scripts/lifecycle-and-sync/build_learning_posture_pilot_summary.py --out-json Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json`
  - `python3 - <<'PY'
from pathlib import Path
artifact = Path("Infrastructure/artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json")
sources = [
    Path("Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home-decision.json"),
    Path("Infrastructure/artifacts/skill-graphs/pilot/learning-posture-metadata-home.json"),
    Path("Skills/skill-builder/Infrastructure/references/task-profile.json"),
    Path("Skills/skill-builder/Infrastructure/references/evals.yaml"),
    Path("frontend/tools/agentation/Infrastructure/references/task-profile.json"),
    Path("frontend/tools/agentation/Infrastructure/references/evals.yaml"),
    Path("Skills/systematic-debugging/Infrastructure/references/task-profile.json"),
    Path("Skills/systematic-debugging/Infrastructure/references/evals.yaml"),
    Path("interview/interview-me/Infrastructure/references/task-profile.json"),
    Path("interview/interview-me/Infrastructure/references/evals.yaml"),
]
if not artifact.exists() or artifact.stat().st_mtime < max(p.stat().st_mtime for p in sources if p.exists()):
    raise SystemExit("conformance summary is missing or stale")
print("conformance summary freshness check passed")
PY`
- Repo docs and plan structure:
  - `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
  - `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py /Users/jamiecraik/dev/agent-skills/Docs/plans/2026-03-10-feat-learning-preserving-skill-design-plan.md`
- Artifact and telemetry integrity:
  - `python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py --strict --run-state-check`
- Final broad verification:
  - `bash Infrastructure/scripts/validate_all.sh`

## Test and Validation Strategy

Focused checks after each major phase:
- Phase 1: docs lint after repo-level doc/template edits
- Phase 2: relevant strict validator checks after metadata/validation changes
- Phase 3: per-skill diagnostics after each pilot skill update
- Phase 4: pilot eval checks after skill/eval updates using canonical `run_skill_evals.py` commands
- Phase 5: artifact/conformance verification after telemetry summary changes

Broader checks before completion:
- `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
- `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py Docs/plans/2026-03-10-feat-learning-preserving-skill-design-plan.md`
- `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --runner codex`
- `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py frontend/tools/agentation --runner codex`
- `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/systematic-debugging --runner codex`
- `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py interview/interview-me --runner codex`
- `bash Infrastructure/scripts/validate_all.sh`
- `python3 Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict`
- `python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py --strict --run-state-check`

Coverage expectations:
- invalid posture/mode pairings are blocked or degraded explicitly
- pilot skills all declare posture support consistently
- pilot evals test learning-preserving behavior, not just routing/output success
- conformance summary distinguishes `pass`, `partial`, and `blocked`
- no change rewrites canonical `autopilot | co-pilot | manual` semantics
- failures stop the phase they belong to; do not defer strict-validator fixes to final cleanup

## Rollout / Migration / Monitoring

Rollout shape:
- pilot-only rollout
- no all-skills adoption in this plan
- expansion only after human review of conformance results

Monitoring expectations:
- inspect pilot conformance summary after each implementation pass
- inspect posture-specific eval failures separately from general output failures
- treat missing telemetry coverage as degraded pilot health
- use a short evidence cadence after implementation completes:
  - `+10m`: rerun focused diagnostics and strict metadata checks for pilot skills
  - `+1h`: review pilot conformance summary for `pass | partial | blocked` distribution and telemetry ambiguity
  - `+24h`: rerun broad repo validation and artifact-integrity checks before deciding whether to expand beyond the pilot

Migration notes:
- existing non-pilot skills remain unchanged
- legacy artifacts remain readable; new posture metadata must not break current consumers
- if posture metadata proves unstable in the chosen machine-readable location, stop at pilot scope and revise before expansion
- if any pilot skill remains `partial` because telemetry or eval coverage is weak, expansion is held even if docs and routing changes are otherwise complete

## Acceptance Checklist

- [ ] Plan stays consistent with `Docs/specs/2026-03-10-feat-learning-preserving-skill-design-spec.md`
- [ ] Enhancement summary and execution gates remain aligned with the linked spec and brainstorm
- [x] P0 baseline freeze and pilot diagnostics are complete with reproducible snapshots for all four pilots
- [x] P1 repo-level docs and template contract updates are in place
- [x] P2 metadata-home decision artifact exists and is approved
- [x] P2 machine-readable pilot metadata contract and validator updates are implemented
- [x] Repo-level `LearningPosture` definition is added once and reused consistently
- [x] Pilot authoring surface is defined through docs/template updates
- [x] Pilot machine-readable posture metadata and validation hooks are implemented safely
- [x] Phase 2 metadata-home decision artifact is approved before pilot skill propagation starts
- [ ] All four pilot skills are updated without changing their core routing intent
- [x] All four pilot skills pass `python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py <skill-name>` after updates
- [x] Pilot evals cover posture-sensitive behavior
- [x] Pilot telemetry/conformance reporting exists and is machine-diffable
- [x] Invalid or degraded posture/mode combinations are surfaced explicitly rather than normalized silently
- [ ] Validation commands pass
- [x] Rollout decision note exists for the pilot

## Sources & References

- [Learning-preserving brainstorm](/Users/jamiecraik/dev/agent-skills/docs/brainstorms/2026-03-10-learning-preserving-skills-brainstorm.md)
- [Learning-preserving spec](/Users/jamiecraik/dev/agent-skills/Docs/specs/2026-03-10-feat-learning-preserving-skill-design-spec.md)
- [Skill graph index](/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/index.md)
- [Task profile schema](/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/schemas/task-profile.schema.md)
- [Question lifecycle contract](/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/question-lifecycle.md)
- [Promotion gate workflow](/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/workflows/promotion-gate.md)
- [Validation guidance](/Users/jamiecraik/dev/agent-skills/Docs/agents/04-validation.md)
- [Skill template](/Users/jamiecraik/dev/agent-skills/Infrastructure/templates/SKILL.md.template)
- [Agentation annotation-format reference](/Users/jamiecraik/dev/agent-skills/frontend/tools/agentation/Infrastructure/references/annotation-format.md)
- [Agentation public sources memo](/Users/jamiecraik/dev/agent-skills/frontend/tools/agentation/Infrastructure/references/public-sources.md)
