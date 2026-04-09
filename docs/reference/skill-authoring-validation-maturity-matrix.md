# Skill Authoring Validation Maturity Matrix

## Table of Contents
- [Purpose](#purpose)
- [Scope](#scope)
- [Status Legend](#status-legend)
- [Critical Validation Layers](#critical-validation-layers)
- [Evidence Notes](#evidence-notes)
- [Smallest Follow-Ups](#smallest-follow-ups)

## Purpose

This matrix is the derived April 2026 readiness view for the governed skill-authoring family:
- `skills-system/skill-creator`
- `utilities/skill-builder`
- `skills-system/skill-installer`
- `skills-system/plugin-creator`

> **Boundary note (2026-04-05):** `utilities/plugin-builder` is an adjacent plugin-packaging handoff surface, not an active gate-family member. Active gate membership is enforced by `scripts/validate_skill_authoring_family.sh`. See `docs/reference/skill-authoring-family-boundary-decision.md` for the canonical decision record.

It is evidence-focused only. The canonical family contract remains:
- [docs/specs/2026-04-03-feat-skill-authoring-family-contract-spec.md](/Users/jamiecraik/dev/agent-skills/docs/specs/2026-04-03-feat-skill-authoring-family-contract-spec.md)

## Scope

Critical layers for rollout closeout:
- family-wide format enforcement
- runnable helper validation
- executable routing coverage
- executable provenance and rollback coverage

## Status Legend

| Status | Meaning |
|---|---|
| `meets` | The layer has current evidence and passed its expected checks in this run. |
| `partial` | The layer is implemented and partially verified, but a required live gate or equivalent proof is still blocked. |
| `missing` | The layer is not yet implemented. |
| `stale` | The layer exists but no longer matches the approved contract or current guidance. |

## Critical Validation Layers

| Layer | Current check | April 2026 expectation | Status | Evidence | Smallest follow-up |
|---|---|---|---|---|---|
| Family-wide format enforcement | `bash scripts/lint_openai_skill_format.sh --mode strict` | Governed skill frontmatter accepts official keys, including `compatibility`, across both `utilities/` and `skills-system/` surfaces. | `meets` | Lint passed after widening roots to include `skills-system`; checked files increased from 119 to 124 with zero errors. | None for phase one. |
| Runnable helper validation | `~/.venvs/pyyaml/bin/python skills-system/skill-creator/scripts/quick_validate.py <path>` and `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py <path>` | Helper validators accept official frontmatter keys, give actionable failures, and remain runnable from repo-root commands. | `meets` | Both direct validator commands passed on governed skills, and a temporary fixture containing `compatibility: codex` passed both helper validators. | Add dedicated validator unit tests only if helper behavior starts drifting again. |
| Executable routing coverage | `python3 utilities/skill-builder/scripts/run_skill_evals.py utilities/skill-builder --list-cases --eval-mode smoke`, `--runner discovery-smoke --eval-mode smoke --case discovery-round-six --format json`, plus smoke cases such as `clarification-package-ambiguous` | Routing-boundary cases exist, are filterable in smoke mode, and can execute successfully through the phase-one harness. | `meets` | Inventory lists the new clarification, plugin-handoff, mixed-authoring, and validation-first cases; repo unit tests passed; discovery smoke passed; the authenticated live Codex rerun for `clarification-package-ambiguous` passed, and the paired live smoke rerun with `provenance-import-rollback` also passed in `/private/tmp/skill-builder-live-smoke-pair-rerun/skill-builder/20260404-164154-350888/summary.json`. | Monitor only for runner intermittency; no phase-one blocker remains. |
| Executable provenance and rollback coverage | `python3 utilities/skill-builder/scripts/run_skill_evals.py utilities/skill-builder --eval-mode smoke --case provenance-import-rollback` | Import/install provenance cases execute successfully and prove trusted-source, pinned-ref, staged-validation, and rollback language under the live harness. | `meets` | Case is present in eval inventory, smoke filter tests passed, and the authenticated live Codex rerun for `provenance-import-rollback` passed individually and in the final paired rerun recorded in `/private/tmp/skill-builder-live-smoke-pair-rerun/skill-builder/20260404-164154-350888/summary.json`. | Monitor only for runner intermittency; no phase-one blocker remains. |

## Evidence Notes

- Repo preflight passed on `2026-04-04`, with the known Local Memory false-negative pattern (`status reported stopped` while REST health on `127.0.0.1:3002` succeeded).
- `python3 utilities/skill-builder/scripts/test_run_skill_evals.py` passed after adding regression assertions for the new family-contract cases, live Codex-home preflight behavior, and the guard that skips acceptance matching when a live runner exits non-zero with no final output.
- The recurring auth and broken-home failures were addressed by Codex-home preflight plus the automation-rule repair, and the final live smoke pair rerun passed for both `clarification-package-ambiguous` and `provenance-import-rollback`.
- Residual risk only: one transient live-runner timeout was observed on an earlier paired rerun before the final successful paired rerun, so future closeout work should still treat occasional live-runner latency as operational noise rather than immediate contract drift.

## Release-Readiness Mode

The family gate supports two operating modes:

| Mode | Invocation | Purpose |
|---|---|---|
| Structural (default) | `bash scripts/validate_skill_authoring_family.sh` | Local iteration; verifies eval case listings, security benchmarks, and format contracts without running live evals. |
| Trusted live | `SKILL_FAMILY_LIVE_EVALS=1 SKILL_FAMILY_LIVE_EVALS_TRUSTED=1 bash scripts/validate_skill_authoring_family.sh` | Runs smoke + release evals against a live Codex runner; required for any release-grade readiness claim. |
| Release-ready | `SKILL_FAMILY_RELEASE_READY=1 SKILL_FAMILY_LIVE_EVALS=1 SKILL_FAMILY_LIVE_EVALS_TRUSTED=1 bash scripts/validate_skill_authoring_family.sh` | Full trusted live execution **plus** evidence artifact capture. Required for closeout. |

### Release-Ready Evidence Requirements

- Evidence must be produced from the current run (not from pre-existing artifacts).
- Evidence must not be older than **7 calendar days** at closeout time.
- Evidence must be produced from the current branch tip or a direct descendant commit.
- An `evidence-index.json` must be present at `artifacts/validation/family-gate/<run-timestamp>/evidence-index.json` capturing: `branch`, `commit_sha`, `generated_at`, and per-skill `outcome`.
- Evidence dir is configurable via `SKILL_FAMILY_EVIDENCE_DIR` (default: `artifacts/validation/family-gate`).

### Degraded-Mode Handling

- Transient runner failures do not excuse missing evidence — retry-limited reruns are required.
- Closeout is blocked until at least one successful trusted run per skill produces retained evidence.
- Runner instability observed during a run should be noted in `.harness/memory/LEARNINGS.md` as operational noise, not reopened as a contract blocker.

## Smallest Follow-Ups

1. Keep using authenticated Codex homes for live smoke and let the built-in preflight reject repo-local unauthenticated homes before execution.
2. If a future live smoke rerun flakes once, rerun the targeted case or pair before reopening a contract-level blocker.
3. If intermittent live-runner latency becomes common again, treat it as a new operational follow-up rather than changing the family routing contract first.
4. Use `SKILL_FAMILY_RELEASE_READY=1` for all gold-standard closeout runs; do not rely on structural mode alone for release-grade claims.
