# Skill Builder Advanced Workflow

Use this reference when you need the extended mechanics that are intentionally kept out of `SKILL.md` for progressive disclosure.

## Deterministic response details
- Keep first response compact and install-focused.
- Include deconflict-first ordering when installation/distribution is in scope.
- Include a capability overlap matrix when comparing primitives or nearby skills.
- Include an artifact-uplift scan plan before writing migration changes.

## Output contract
For non-trivial `create`, `improve`, `eval`, or `benchmark-lite`, include:
- `schema_version`
- `mode`
- `skill_path`
- `findings`
- `validations`
- `security`
- `next_step`

## Skill creation process
1. Confirm target path, boundary, and naming constraints.
2. Lock trigger intent early with should-trigger and should-not-trigger coverage.
3. Choose minimal structure (single-file vs router-style).
4. Scaffold and author route-critical `SKILL.md` guidance.
5. Add `references/`, `scripts/`, and `assets/` only when they add clear value.
6. Validate, fix first failing gate, then rerun.
7. Optimize `description` for trigger coverage and false-positive control.
8. Deliver only after category/coverage/gate criteria are met (or explicitly triaged).

## Description optimization checklist
- Add exact trigger phrases for likely misses in should-trigger cases.
- Add explicit negative guards for likely false positives.
- Keep description natural and under 1024 chars.
- Document before/after description changes when optimization was required.

## Final delivery checklist
- Category intent confirmed.
- Trigger coverage meets minimum counts.
- Description optimization complete and documented.
- Required gates pass, or failures are triaged with owner decisions.
