# Plan — @steipete persona refresh (2026-02-22)

## Goal
Upgrade the `steipete` persona skill using the 2024-2026 public corpus so routing, voice, constraints, and eval boundaries are stronger and more evidence-aware.

## Completed
1. Rewrote `SKILL.md` as a concise map with Table of Contents and stronger trigger boundaries.
2. Added explicit evidence window (2024-01-01 to 2026-02-22, Europe/London).
3. Added clear Objective/Plan/Next step response contract and loop-closure heuristics.
4. Added authenticity, impersonation, privacy, and latest-facts guardrails.
5. Upgraded evals with happy/edge/negative cases including latest-fact and impersonation boundaries.
6. Added `references/persona-evidence.md` for progressive disclosure of corpus-backed anchors.
7. Updated `references/contract.yaml` to encode sources, risks, and output requirements.

## Validation steps
- `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py personas/steipete`
- `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py personas/steipete`
- `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py personas/steipete --mode both`
- Optional: `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/analyze_skill.py personas/steipete`
