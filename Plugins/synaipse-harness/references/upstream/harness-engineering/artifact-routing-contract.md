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
harness_stage: he-spec|he-plan|he-eval-report|he-brainstorm|he-reconcile|he-reinforce|he-strategy|he-reframe|he-linear-plan|he-phase-work
status: draft|active|blocked|complete|superseded
date: YYYY-MM-DD
traceability_required: true|false
origin: <repo-relative source artifact path>
linear_issue: <issue key when tracked>
linear_milestone: <milestone when tracked>
```

Use `canonical_slug` as the chain key across `.harness/features`,
`.harness/review`, `.harness/triage`, `.harness/strategy`,
`.harness/reframes`, `.harness/decisions`, `.harness/core`,
`.harness/linear`, `.harness/specs`, `.harness/plan`, `.harness/solutions`,
`.harness/evals`, and related proof artifacts. Stage-specific titles may differ
only by suffix, such as `Intent`, `Strategy`, `Refactor`, `Spec`, `Plan`,
`Eval`, or `Technical Review`; the shared `canonical_slug` and `artifact_id`
must make the relationship machine-readable.

Classify existing artifacts by content shape before path. Frontmatter,
`artifact_type`, `harness_stage`, H1, required sections, source links, and Linear
identifiers outrank the directory name. If path and content disagree, record a
traceability defect and use
`references/artifact-classification-and-traceability.md` before routing or
renaming.

New tracked issue artifacts should prefer dated Linear filenames:

```text
.harness/features/YYYY-MM-DD-JSC-###-<canonical-slug>-intent.md
.harness/review/YYYY-MM-DD-JSC-###-<canonical-slug>-architecture-review.md
.harness/triage/YYYY-MM-DD-JSC-###-<canonical-slug>-triage.md
.harness/strategy/YYYY-MM-DD-JSC-###-<canonical-slug>-strategy.md
.harness/reframes/YYYY-MM-DD-JSC-###-<reframe-slug>.md
.harness/linear/YYYY-MM-DD-JSC-###-<repo-name>-<slice-slug>-linear-plan.md
.harness/specs/YYYY-MM-DD-JSC-###-<canonical-slug>-spec.md
.harness/plan/YYYY-MM-DD-JSC-###-<canonical-slug>-plan.md
.harness/evals/YYYY-MM-DD-JSC-###-<repo-name>-<canonical-slug>-eval.md
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

## Parser-Safe Frontmatter

Traceable `.harness/**` artifacts are machine-readable contracts. Keep
frontmatter conservative enough for simple parsers:

- Start the file with a single YAML frontmatter block delimited by `---`.
- Keep scalar values on one line unless the field is explicitly a YAML list.
- Quote scalar values that contain `:`, `#`, brackets, braces, or commas.
- Keep `canonical_slug` lowercase kebab-case and stable across the chain.
- Match date-prefixed filenames to frontmatter `date`.
- Match frontmatter `title` to the first H1 exactly.
- Do not mix dated filenames, Linear issue prefixes, and unrelated titles unless
  `canonical_slug`, `artifact_id`, and frontmatter Linear identifiers connect
  them deterministically.

## Durable Markdown Roots

| Stage or mode | New artifact root |
| --- | --- |
| `he-ideate` folded mode | `.harness/ideate/**.md` |
| `he-brainstorm` | `.harness/brainstorm/**.md` |
| `he-strategy` intent mode | `.harness/features/**.md` |
| `he-strategy` architecture-review mode | `.harness/review/**.md` |
| `he-strategy` triage mode | `.harness/triage/**.md` |
| `he-strategy` strategic-compression mode | `.harness/strategy/**.md` |
| `he-strategy` decision-compression mode | `.harness/decisions/**.md` |
| `he-strategy` core-compression mode | `.harness/core/**.md` |
| `he-reframe` | `.harness/reframes/**.md` |
| `he-linear-plan` | `.harness/linear/**.md` |
| `he-phase-work` | automation/thread heartbeat plus phase status report |
| `he-spec` | `.harness/specs/**.md` |
| `he-plan` | `.harness/plan/**.md` |
| `he-plan` dedicated UI plan | `.harness/plan/**-ui-plan.md` |
| `he-reinforce` learning capture | `.harness/solutions/**.md` |

Use repo-relative paths in saved artifacts and handoffs. Chat may link absolute
paths, but portable HE docs should keep the `.harness/...` form.

## Routing Rules

- New durable HE docs for the stages above must be created under the matching
  `.harness` root.
- When revising a legacy `Docs/`, `Specs/`, `Plans/`, `docs/brainstorms/`,
  `docs/ui-plan/`, `docs/ui-plans/`, or `docs/solutions/` artifact, read it as
  source evidence and write the replacement artifact under the matching
  `.harness` root. Preserve the legacy path as source evidence.
- `he-work`, `he-code-review`, and `he-reinforce` may read legacy paths for
  compatibility, but their handoffs should point downstream agents at the
  `.harness` artifact when one exists or is created.
- `docs/ui-plan/**` is treated as a legacy singular spelling of
  `docs/ui-plans/**`; new dedicated UI plans use `.harness/plan/**-ui-plan.md`.
- `docs/solutions/**` is treated as the legacy reusable-solution library; new
  `he-reinforce` captures use `.harness/solutions/**.md` and sync Project Brain
  when the repo has that operating surface.
- Folded `he-ideate` requests are served by `he-brainstorm`; use
  `.harness/ideate/**.md` only when the request is explicitly ideation/options
  mode rather than a requirements brainstorm.

## Handoff Evidence

Populate `evidence.artifacts` with the concrete `.harness/...` paths that were
created, updated, or selected as the current stage truth. If no durable artifact
is written, set `artifact_status` to `none` or `not_applicable` and explain why.

Run the identity lint before claiming a new or revised traceable artifact is
ready. Run the parser-safety lint when the artifact is intended to be consumed
by another HE stage, Linear backlinking, Project Brain, or an eval report:

```bash
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <artifact-path>
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py <artifact-path>
```
