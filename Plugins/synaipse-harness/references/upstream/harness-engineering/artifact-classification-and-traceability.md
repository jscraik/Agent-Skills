# Artifact Classification and Traceability

Read when: classifying, searching, generating, revising, or linking `.harness`
artifacts across the HE lifecycle.

## Core Rule

Content shape beats path.

A file path is a routing hint, not final authority. Classify an artifact from
its frontmatter, first H1, required sections, source links, Linear identifiers,
and evidence shape. If path and content disagree, record a traceability defect
and repair it only when the current stage is allowed to edit that artifact.

## Classification Order

1. Frontmatter `artifact_type`, `harness_stage`, `canonical_slug`, and Linear
   fields.
2. First H1 and required section shape.
3. Source artifact links and evidence matrix.
4. Dated Linear filename pattern.
5. Directory path as a final hint.

## Traceability Requirements

Every tracked artifact should preserve:

- `artifact_id`
- `canonical_slug`
- `title` matching the first H1
- `date`
- Linear Project
- Linear Milestone
- Linear Parent Issue
- Linear Sub-Issues, when present
- source artifacts read
- proof or validation links when relevant

Use dated Linear filenames for new tracked artifacts unless the file is an
intentionally stable policy or core invariant. Date prefixes improve regression
search and chronological review, but identity comes from `canonical_slug` and
frontmatter.

## Mismatch Handling

- Title mismatch: update frontmatter, H1, filename, and backlinks together or
  mark the artifact `superseded`.
- Path/content mismatch: classify from content, then record the path mismatch
  as a traceability defect.
- Missing Linear identifiers: mark traceability incomplete and state whether it
  blocks planning, implementation, or closure.
- Duplicate canonical slugs: select the current artifact by status, date,
  source chain, and explicit successor links; do not silently merge.

## Output Fields

```yaml
artifact_classification_status: matched|mismatch|incomplete|not_applicable
artifact_classification_basis: frontmatter|h1|sections|source_links|filename|path
artifact_traceability_defects:
  - "<defect or none>"
canonical_slug_status: stable|missing|duplicate|mismatch|not_applicable
dated_linear_style_status: used|legacy|not_applicable|missing
```

## Anti-Patterns

- Trusting `.harness/review/` or `.harness/strategy/` path alone when the content
  is actually a plan, spec, or eval.
- Treating date prefixes as identity.
- Allowing different titles to fragment one Linear slice into unrelated-looking
  artifacts.
- Renaming artifacts without preserving backlinks and canonical slug continuity.
