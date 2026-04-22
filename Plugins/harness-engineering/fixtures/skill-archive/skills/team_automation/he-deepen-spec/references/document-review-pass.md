# Document Review Pass

Read when: an existing requirements document, system spec, or UI spec mostly needs refinement before planning rather than deeper contract expansion.

Canonical source: `Plugins/harness-engineering/skills/shared/references/document-review-pass.md`

This lane intentionally tracks upstream `ce-doc-review` doctrine from snapshot commit `d8436b9a3c5b5370e51ec168a251ccb45f0d826e`, while `he-brainstorm` references commit `847ce3f156a5cdf75667d9802e95d68e6b3c53a4` from the brainstorm workflow. The divergence is intentional because the source workflows differ.

Spec-specific notes:
- default search locations prefer `Docs/specs/` and `docs/ui-specs/`
- review should verify readiness for `he-plan` handoff
- use `request_user_input` for interactive decisions, with numbered fallback only when the question tool is unavailable
- support optional `mode:headless` when callers need report-style output without prompts (explicit path required)
