# Project prompt addendum (optional)

Use this file to encode repo-specific conventions so each Ralph iteration stays aligned.

## Conventions
- Follow existing formatting/lint rules; do not introduce new tooling unless explicitly required.
- Prefer editing existing patterns over inventing new ones.

## Safe operating constraints
- Do not delete data unless explicitly asked.
- Avoid broad refactors; keep diffs small and targeted.

## Linkage expectations
- Before edits, identify:
  - Spec section in `.ralph/pin.md`
  - Plan item in `.ralph/plan.md`
  - Exact file paths to change
