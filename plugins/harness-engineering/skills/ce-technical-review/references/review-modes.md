# CE Technical Review Modes

## Table of Contents
- [Purpose](#purpose)
- [Template scaffold workflow](#template-scaffold-workflow)
- [External evidence rule](#external-evidence-rule)
- [Code-diff review](#code-diff-review)
- [Document review](#document-review)
- [Reviewer coverage map](#reviewer-coverage-map)
- [Required finding format](#required-finding-format)

## Purpose
This note preserves the original technical-review prompt mechanics while keeping the main skill concise.

## Template scaffold workflow

Canonical scaffold files for this skill:
- `finding.md.tmpl`
- rendered baseline: `references/finding-template.md`

Render / refresh:

```bash
python3 plugins/harness-engineering/skills/ce-technical-review/scripts/render_finding_template.py
python3 plugins/harness-engineering/skills/ce-technical-review/scripts/check_finding_template_drift.py --update
```

Verify no drift:

```bash
python3 plugins/harness-engineering/skills/ce-technical-review/scripts/check_finding_template_drift.py
```

## External evidence rule
Use local evidence first:
- diff, files, tests, linked spec/plan artifacts, and repo patterns

Escalate to current external docs only when:
- the finding depends on framework or library behavior
- version-specific defaults, deprecations, or lifecycle semantics matter
- security-sensitive integration guidance matters
- a claimed best practice needs current authoritative grounding

Source preference:
1. official product or framework documentation
2. Context7 for current library documentation when official behavior needs fast confirmation
3. secondary best-practice material only when primary docs do not answer the question cleanly

OpenAI rule:
- when the review touches OpenAI APIs, models, SDKs, Apps SDK, or platform semantics, prefer official OpenAI docs first
- do not turn every technical review into an external-doc pass when repo evidence already settles the issue

## Code-diff review
Use when the target is a PR, branch, current diff, file path, or current `HEAD`.

Review order:
1. resolve the exact diff or file set
2. determine primary language and risk areas
3. read linked plan/spec artifacts when present
4. retrieve current official docs or Context7 evidence only for findings that depend on external framework or library behavior
5. run the relevant reviewer lenses
6. merge and rank findings

## Document review
Use when the target is a spec, plan, UI spec, UI plan, or explicitly provided markdown design artifact.

Read the target document fully.
If frontmatter or body references linked artifacts such as `origin`, `spec`, or `parent_spec`, read those too.

### Spec review rubric
- `2 pts` scope and non-goals are crisp
- `2 pts` core domain model is explicit
- `2 pts` lifecycle/state/timing is covered where needed
- `2 pts` failure/recovery behavior is explicit
- `1 pt` observability and validation are defined
- `1 pt` implementer can act without guessing

Thresholds:
- `8.5-10` ready for planning
- `7.0-8.4` usable, but revise targeted weak spots
- `below 7.0` not ready; major ambiguity remains

### Plan review rubric
- `2 pts` aligned with linked spec or brainstorm
- `2 pts` sequencing and dependencies are sound
- `2 pts` validation and testing plan is credible
- `2 pts` rollout, migration, and monitoring are covered where needed
- `1 pt` risks and blockers are explicit
- `1 pt` work can proceed without guessing next steps, and adherence can be audited during execution and review

## Reviewer coverage map
Use deterministic, technical-first reviewer selection.

Always include:
- `correctness-reviewer`
- `testing-reviewer`
- `code-simplicity-reviewer`

Document-review baseline:
- `spec-flow-analyzer`
- `feasibility-reviewer`

Add by language and risk signal:
- `kieran-rails-reviewer` for Ruby/Rails changes
- `kieran-typescript-reviewer` for TypeScript/JavaScript changes
- `kieran-python-reviewer` for Python changes
- `api-contract-reviewer` for public API/contract surface changes
- `julik-frontend-races-reviewer` for async UI timing and DOM lifecycle risk
- `security-reviewer` for auth/authz, secrets, trust boundaries, or untrusted input
- `performance-reviewer` for hot paths, query scale, or latency regressions
- `data-integrity-guardian` for schema, migration, or persistence correctness risks
- `schema-drift-detector` when schema dump drift is part of the change
- `reliability-reviewer` for partial-state, retry, and failure-mode hazards
- `deployment-verification-agent` when rollout/rollback verification is contract-critical
- `architecture-strategist` for multi-module design or architecture-heavy changes
- `maintainability-reviewer` when complexity/coupling risk is elevated

Execution order:
1. baseline reviewers
2. language specialists
3. risk specialists
4. architecture/maintainability cross-cuts when needed

Run reviewers in bounded parallel when platform and policy allow; otherwise apply the same selection serially.

Avoid in technical baseline mapping:
- editorial-only roles
- style-first convention critics before correctness/testing risk is covered

## Required finding format
For each finding include:
- severity (`P0 | P1 | P2 | P3`)
- exact location:
  - `file:line` when available
  - section heading for docs
- why it matters
- recommended minimal fix
- confidence `0-1`
