---
title: Skill Authoring Family — Residual Risk Register
type: reference
status: active
date: 2026-04-05
next_review: 2026-07-05
owner: jscraik
---

# Skill Authoring Family — Residual Risk Register

## Table of Contents
- [Purpose](#purpose)
- [Risk Register](#risk-register)
- [Acceptance Criteria](#acceptance-criteria)
- [Mitigation Actions](#mitigation-actions)
- [Approval](#approval)

## Purpose

This document records residual risks accepted for the skill authoring family (skill-builder, skill-creator, skill-installer, plugin-creator) as part of the gold-standard upgrade programme. Risks are assessed after mitigations and accepted with explicit owner sign-off.

**Governed skills:** `Skills/skill-builder`, `Skills/skill-creator`, `Skills/skill-installer`, `Skills/plugin-creator`

## Risk Register

| ID | Risk Description | Likelihood | Impact | Residual Risk | Owner | Mitigation | Status |
|----|-----------------|-----------|--------|--------------|-------|-----------|--------|
| R-01 | Live eval runs depend on Codex availability; gate fails if Codex is rate-limited or down | Medium | Medium | Low — structural contract checks run in isolation; live evals gated by `SKILL_FAMILY_LIVE_EVALS=1` | jscraik | Structural-only mode (`SKILL_FAMILY_LIVE_EVALS=0`) provides a safe fallback for all non-release checks | Accepted |
| R-02 | Telemetry freshness is checked against a 24h window but health artifacts can be up to 5 days stale in practice | Medium | Low | Low — readiness wave blocks on `TELEMETRY_HEALTH_STALE` before any release claim proceeds | jscraik | `wave-readiness.json` blockers gate the release; stale telemetry surfaces before final approval | Accepted |
| R-03 | `openclaw_skill_guard.py` regex patterns may miss obfuscated exfiltration patterns | Low | High | Medium — pattern coverage is defence-in-depth, not a complete security boundary | jscraik | Combined with PI guards (`--pi-high-fail`) and separate ruff/semgrep scans; patterns are updated per incident | Accepted, monitor |
| R-04 | Baseline regression comparison in `validate_skill_authoring_family_benchmarks.py` uses severity ordering but new finding codes not in baseline are flagged as regressions | Low | Low | Low — only worsened or new codes fail; improvements are transparent | jscraik | Baseline can be rewritten via `--write-baseline` after intentional scope changes | Accepted |

## Acceptance Criteria

A residual risk is accepted when all of the following are true:
- Likelihood × Impact ≤ Medium (or explicit maintainer override with documented rationale)
- At least one active mitigation is in place
- Owner is named and has reviewed the entry
- Risk is reviewed quarterly or after any gate failure that relates to the risk area

## Mitigation Actions

| Risk ID | Action | Due Date | Status |
|---------|--------|----------|--------|
| R-01 | Document structural-only fallback in gate README | 2026-07-05 | Implemented (gate script logs this) |
| R-02 | Add telemetry freshness alerting to daily-skill-health generation | 2026-07-05 | Backlog |
| R-03 | Add integration test covering variable-URL fetch patterns to openclaw test suite | 2026-07-05 | Backlog |
| R-04 | Add `--check-baseline` to CI gate for release-ready runs | 2026-07-05 | Implemented |

## Approval

| Role | Name | Date | Sign-off |
|------|------|------|---------|
| Maintainer | jscraik | 2026-04-05 | Accepted — all risks are within tolerable range given current mitigations |

**Next review:** 2026-07-05
