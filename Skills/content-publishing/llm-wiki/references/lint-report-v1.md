# Lint Report v1

Use this output shape for formal LLM Wiki lint sweeps. It lets an agent improve
a vault incrementally without turning review into broad reorganization.

## Report Header

```md
# LLM Wiki Lint Report

- schema_version: lint-report/v1
- vault_root:
- inspected_paths:
- generated_at:
- workflow: review-only | fixed-low-risk | mixed
- edit_authority:
```

## Summary Counts

```md
## Summary

- P1:
- P2:
- P3:
- fixed:
- needs_human_judgment:
- skipped:
```

Use severities consistently:

- `P1`: privacy, source-of-truth, destructive reorganization, or serious
  contradiction risk.
- `P2`: navigation, citation, naming, attachment, or stale-claim problems that
  materially reduce vault quality.
- `P3`: cleanup, small consistency issues, or optional graph improvements.

## Findings Table

```md
| id | severity | category | page | evidence | suggested action | status |
|---|---|---|---|---|---|---|
| LW-001 | P2 | orphan_page | wiki/concepts/example.md | No inbound links found from inspected pages. | Add contextual links or mark as intentionally isolated. | needs_human_judgment |
```

Allowed categories:

- `contradiction`
- `stale_claim`
- `orphan_page`
- `missing_concept`
- `weak_cross_link`
- `duplicate_or_alias_collision`
- `unsupported_claim`
- `brittle_attachment`
- `privacy_or_redaction`
- `index_or_log_drift`

Allowed statuses:

- `fixed`: low-risk change made and logged.
- `needs_human_judgment`: source authority, privacy, rename, merge, or meaning
  requires the user.
- `blocked`: missing file access, missing redaction policy, or unsafe authority.
- `skipped`: out of requested scope.

## Resolution Rules

- Low-risk fixes: add missing backlinks from relevant pages, update index/log
  entries, mark unsupported claims, repair local relative attachment links, or
  add aliases without renaming.
- Human-judgment fixes: resolve contradictions, merge or rename pages, delete
  pages, publish content, promote private notes into shared pages, or decide
  source authority.
- Unresolved wikilinks are acceptable when they represent intentional stubs for
  important future pages. They are findings only when they are numerous,
  misspelled, ambiguous, or disconnected from actual user goals.
- Duplicate pages should first become alias or merge candidates. Do not merge
  until backlinks, source citations, and user approval are clear.
- Unsupported claims are fixed only when they gain a citation, become explicitly
  marked `needs-source`, or are removed with approval.

## Closeout

```md
## Closeout

- Changes made:
- Changes intentionally not made:
- Validation:
- Next human decisions:
```
