# CE Deepen Spec Rewrite Rules

Read when: you are rewriting selected sections, adding the Enhancement Summary, or running final checks before writing the deepened spec.

## Table of Contents
- [Purpose](#purpose)
- [Enhancement Summary template](#enhancement-summary-template)
- [Allowed changes](#allowed-changes)
- [Not allowed](#not-allowed)
- [Final checks](#final-checks)

## Purpose
This reference keeps spec deepening bounded, evidence-backed, and safe for downstream planning.

## Enhancement Summary template
Add a short summary near the top when substantive changes were made:

```markdown
## Enhancement Summary

**Deepened on:** YYYY-MM-DD
**Mode:** targeted-confidence | max-coverage
**Key areas improved:** boundaries, lifecycle, failures, observability, validation

- Major improvement 1
- Major improvement 2
- Major improvement 3
```

## Allowed changes
- clarify boundary ownership, entities, fields, defaults, and constraints
- strengthen lifecycle, retry, cancel, timeout, and cleanup semantics
- expand failure classes, recovery rules, durability treatment, or operator expectations
- add missing safety, permission, trust-boundary, or data-handling language
- strengthen observability, readiness gates, and post-deploy verification expectations
- improve `SA` or `VAC` precision and add new items by appending cleanly
- update frontmatter with `deepened: YYYY-MM-DD` when the spec was substantively improved

## Not allowed
- implementation code
- imports, exact method signatures, framework-specific implementation snippets, or shell command recipes
- converting the spec into a task plan or exact execution choreography
- rewriting the whole spec from scratch unless explicitly requested
- silently adding new product requirements or widening scope
- renumbering stable `SA` or `VAC` identifiers unless the user explicitly asks for a matrix reset

## Final checks
- the spec is stronger in specific ways, not merely longer
- the selected weak sections were the ones actually improved
- linked origin, parent, or plan artifacts still align with the updated contract
- the spec boundary is intact
- stable acceptance IDs were preserved and extended safely
- the Enhancement Summary matches the real changes made
- if artifact-backed mode was used, temporary artifacts are cleaned up unless the user asked to keep them
