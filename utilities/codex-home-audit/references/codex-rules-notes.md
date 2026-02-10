# Codex rules notes (short)

Purpose: keep the SKILL.md lean and put any longer “why” notes here.

## What rules are good for

- Enforcing recurring guardrails (for example: forbid `grep`, prompt `find`, prompt dependency changes, prompt deploy/publish).
- Reducing duplicated prose across `AGENTS.md` / USER_PROFILE / other docs.

## What rules are not good for

- Interaction style (single-threaded, step-by-step) — keep this in USER_PROFILE.
- Medical/cognitive context — keep sensitive content in the profile detail file.

## Local convention

- Prefer narrow, explainable rules with clear justifications.
- Avoid allow-rules that wrap complex shell scripts (e.g. `zsh -lc "<script>"`), because they can hide multiple actions when splitting is not possible.

