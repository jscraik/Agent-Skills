# Harness Engineering Deepen Plan Rewrite Rules

Read when: you are rewriting selected sections, adding the Enhancement Summary, or running final checks before writing the deepened plan.

## Table of Contents
- [Purpose](#purpose)
- [Enhancement Summary template](#enhancement-summary-template)
- [Allowed changes](#allowed-changes)
- [Not allowed](#not-allowed)
- [Final checks](#final-checks)

## Purpose
This reference keeps plan deepening bounded and evidence-backed.

## Enhancement Summary template
Add a short summary near the top when substantive changes were made:

```markdown
## Enhancement Summary

**Deepened on:** YYYY-MM-DD
**Mode:** targeted-confidence | max-coverage
**Key areas improved:** sequencing, validation, risks, rollout, monitoring

- Major improvement 1
- Major improvement 2
- Major improvement 3
```

## Allowed changes
- clarify or strengthen decision rationale
- reorder or split implementation units when sequencing is weak
- add missing file paths, test paths, or verification outcomes
- expand system-wide impact, risks, dependencies, rollout, monitoring, or migration treatment when justified
- strengthen or add a non-prescriptive high-level technical design section
- reclassify open questions when evidence supports the move
- add targeted research-insight material only where it materially improves execution quality
- update frontmatter with `deepened: YYYY-MM-DD` when the plan was substantively improved

## Not allowed
- implementation code
- imports, exact method signatures, framework-specific implementation snippets, or shell command recipes
- git choreography, release command scripts, or exact test-command cookbooks
- generic research-insights sections pasted everywhere
- rewriting the whole plan from scratch unless explicitly requested
- silently adding new product requirements or widening scope

## Final checks
- the plan is stronger in specific ways, not merely longer
- the selected weak sections were the ones actually improved
- origin decisions still hold when origin artifacts exist
- the planning boundary is intact
- enhancement summary matches the real changes made
- if artifact-backed mode was used, temporary artifacts are cleaned up unless the user asked to keep them
