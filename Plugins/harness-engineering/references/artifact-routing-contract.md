# HE Artifact Routing Contract

Read when: an HE stage writes, revises, or hands off a durable markdown artifact.

## Artifact Identity

Every new or revised traceable `.harness/**` markdown artifact must carry a
stable identity in frontmatter before the first heading:

```yaml
schema_version: 1
artifact_id: <canonical-slug>-<stage-suffix>
artifact_type: <he-stage-or-index-type>
canonical_slug: <repo-name>-<linear-parent-issue-or-milestone>
title: <human title matching first H1>
harness_stage: he-spec|he-plan|he-eval-report|he-brainstorm|he-compound
status: draft|active|blocked|complete|superseded
date: YYYY-MM-DD
traceability_required: true|false
origin: <repo-relative source artifact path>
linear_issue: <issue key when tracked>
linear_milestone: <milestone when tracked>
```

Use `canonical_slug` as the chain key across `.harness/linear`,
`.harness/specs`, `.harness/plan`, `.harness/evals`, `.harness/review`, and
related proof artifacts. Stage-specific titles may differ only by suffix, such
as `Spec`, `Plan`, `Eval`, or `Technical Review`; the shared `canonical_slug`
and `artifact_id` must make the relationship machine-readable.

Tracked issue artifacts may use either stable or dated filenames:

```text
.harness/specs/<canonical-slug>-spec.md
.harness/plan/YYYY-MM-DD-<optional-category>-<canonical-slug>-plan.md
.harness/review/YYYY-MM-DD-<canonical-slug>-technical-review.md
.harness/evals/<repo-name>-<canonical-slug>-eval.md
```

When an artifact filename or `artifact_id` uses a Linear issue key, the shared
`canonical_slug` must include the lower-case issue key, for example
`jsc-283-packaged-skill-behavior-assurance`. Repo-led chains may instead use a
repo and milestone/parent slug such as
`agent-skills-ask-control-plane-decomposition` while carrying the Linear issue in
frontmatter. Date prefixes are chronology only; they are not the identity. If a
filename starts with `YYYY-MM-DD`, frontmatter `date` must match it.

The first H1 must exactly match frontmatter `title`. If the title needs to
change, update frontmatter, filename, and backlinks in the same edit or mark the
artifact `superseded` and point at the successor.

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

Run the identity lint before claiming a new or revised traceable artifact is
ready:

```bash
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <artifact-path>
```
