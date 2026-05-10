# HE Artifact Routing Contract

Read when: an HE stage writes, revises, or hands off a durable markdown artifact.

## Durable Markdown Roots

| Stage or mode | New artifact root |
| --- | --- |
| `he-ideate` folded mode | `.harness/ideate/**.md` |
| `he-brainstorm` | `.harness/brainstorm/**.md` |
| `he-spec` | `.harness/specs/**.md` |
| `he-plan` | `.harness/plan/**.md` |
| `he-plan` dedicated UI plan | `.harness/plan/**-ui-plan.md` |
| `he-compound` learning capture | `.harness/solutions/**.md` |

Use repo-relative paths in saved artifacts and handoffs. Chat may link absolute
paths, but portable HE docs should keep the `.harness/...` form.

## Routing Rules

- New durable HE docs for the stages above must be created under the matching
  `.harness` root.
- When revising a legacy `Docs/`, `Specs/`, `Plans/`, `docs/brainstorms/`,
  `docs/ui-plan/`, `docs/ui-plans/`, or `docs/solutions/` artifact, read it as
  source evidence and write the replacement artifact under the matching
  `.harness` root. Preserve the legacy path as source evidence.
- `he-work`, `he-code-review`, and `he-compound` may read legacy paths for
  compatibility, but their handoffs should point downstream agents at the
  `.harness` artifact when one exists or is created.
- `docs/ui-plan/**` is treated as a legacy singular spelling of
  `docs/ui-plans/**`; new dedicated UI plans use `.harness/plan/**-ui-plan.md`.
- `docs/solutions/**` is treated as the legacy reusable-solution library; new
  `he-compound` captures use `.harness/solutions/**.md` and sync Project Brain
  when the repo has that operating surface.
- Folded `he-ideate` requests are served by `he-brainstorm`; use
  `.harness/ideate/**.md` only when the request is explicitly ideation/options
  mode rather than a requirements brainstorm.

## Handoff Evidence

Populate `evidence.artifacts` with the concrete `.harness/...` paths that were
created, updated, or selected as the current stage truth. If no durable artifact
is written, set `artifact_status` to `none` or `not_applicable` and explain why.
