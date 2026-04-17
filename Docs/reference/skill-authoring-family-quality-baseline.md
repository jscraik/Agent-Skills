---
title: Skill Authoring Family — Quality Baseline
type: reference
status: active
date: 2026-04-05
freeze_timestamp: 2026-04-05T17:38:51Z
freeze_branch: main
freeze_commit: 6240bf1a5fb3ed983d171bef3586656a55c7da3b
---

# Skill Authoring Family — Quality Baseline

## Table of Contents
- [Purpose](#purpose)
- [Baseline Methodology](#baseline-methodology)
- [Frozen Pre-Uplift Baseline](#frozen-pre-uplift-baseline)
- [Post-Uplift Scores](#post-uplift-scores)
- [Hybrid Threshold Policy](#hybrid-threshold-policy)
- [No-Regression Guardrails](#no-regression-guardrails)
- [Commands to Reproduce](#commands-to-reproduce)
- [Baseline Freeze Metadata](#baseline-freeze-metadata)

## Purpose

This document records the frozen pre-uplift baseline and post-uplift target scores for the P3 quality uplift pass. It defines the hybrid threshold policy for `skill-installer` and `plugin-creator` that must be maintained on an ongoing basis.

**Governed skills:** `Skills/skill-installer`, `Skills/plugin-creator`  
**Analyzer:** `Skills/skill-builder/Infrastructure/scripts/analyze_skill.py`  
**Gate:** `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`

## Baseline Methodology

Baseline was captured from the `main` branch before any P3 SKILL.md edits were applied. The commit SHA below is the authoritative baseline reference.

- Scores below are from `analyze_skill.py --min-pass 60 --no-emoji`
- Baseline freeze: **2026-04-05T17:38:51Z** on `main` at commit `6240bf1a5fb3ed983d171bef3586656a55c7da3b`
- Mid-pass baseline replacement requires an explicit change note linked from the scorecard

## Frozen Pre-Uplift Baseline

### skill-installer (pre-uplift)

| Dimension | Score | Max |
|---|---|---|
| Variation | 0 | 15 |
| Empowerment | 0 | 5 |
| Scope Focus | 12 | 15 |

### plugin-creator (pre-uplift)

| Dimension | Score | Max |
|---|---|---|
| Variation | 0 | 15 |
| Empowerment | 0 | 5 |
| Scope Focus | 6 | 15 |

## Post-Uplift Scores

Measured after P3 SKILL.md edits on 2026-04-05.

### skill-installer (post-uplift)

| Dimension | Score | Max | Delta |
|---|---|---|---|
| Variation | 10 | 15 | +10 |
| Empowerment | 5 | 5 | +5 |
| Scope Focus | 12 | 15 | 0 |

### plugin-creator (post-uplift)

| Dimension | Score | Max | Delta |
|---|---|---|---|
| Variation | 13 | 15 | +13 |
| Empowerment | 5 | 5 | +5 |
| Scope Focus | 15 | 15 | +9 |

## Hybrid Threshold Policy

These thresholds must be satisfied for any release-grade readiness claim. They are enforced during the P3 gate check and ongoing quality monitoring.

### Absolute Floors

| Skill | Dimension | Floor |
|---|---|---|
| `skill-installer` | Variation | ≥ 8/15 |
| `skill-installer` | Empowerment | ≥ 3/5 |
| `skill-installer` | Scope Focus | ≥ 12/15 |
| `plugin-creator` | Variation | ≥ 8/15 |
| `plugin-creator` | Empowerment | ≥ 3/5 |
| `plugin-creator` | Scope Focus | ≥ 12/15 |

### Required Uplift Delta from Pre-Uplift Baseline

| Skill | Dimension | Required Delta |
|---|---|---|
| `skill-installer` | Variation | ≥ +2 (achieved: +10) |
| `skill-installer` | Empowerment | ≥ +1 (achieved: +5) |
| `plugin-creator` | Variation | ≥ +2 (achieved: +13) |
| `plugin-creator` | Empowerment | ≥ +1 (achieved: +5) |
| `plugin-creator` | Scope Focus | ≥ +1 (achieved: +9) |

All required uplift deltas were exceeded in the P3 pass.

## No-Regression Guardrails

These rules apply to any future SKILL.md changes for `skill-installer` and `plugin-creator`:

1. **Overall analyzer score must not decrease** from the post-uplift baseline.
2. **No individual dimension score may decrease by more than 1 point** from post-uplift values without an explicit change note in this document.
3. **No role-overlap regressions**: routing language must not re-introduce cross-family confusion or scope ambiguity.
4. **Scope focus for plugin-creator**: the improvement achieved by reducing surface mentions (from 6 to ≤3 surface patterns in body text) must be preserved. If future edits re-introduce `\bhooks?\b`, `\bapps?\b`, or `\bmcp\b` references in prose, scope focus will regress. Use generic descriptions (e.g., "companion folder flags") when discussing optional scaffold types.

## Commands to Reproduce

```bash
# Reproduce analyzer baseline check
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/analyze_skill.py Skills/skill-installer --min-pass 60 --no-emoji
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/analyze_skill.py Skills/plugin-creator --min-pass 60 --no-emoji

# Full family gate
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```

## Baseline Freeze Metadata

| Field | Value |
|---|---|
| Branch | main |
| Commit SHA (pre-uplift) | 6240bf1a5fb3ed983d171bef3586656a55c7da3b |
| Freeze timestamp | 2026-04-05T17:38:51Z |
| Uplift timestamp | 2026-04-05 |
| Analyzer script | Skills/skill-builder/Infrastructure/scripts/analyze_skill.py |
| Replacement policy | Mid-pass baseline replacement prohibited without an explicit change note linked from the scorecard |
