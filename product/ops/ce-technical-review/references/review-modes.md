# CE Technical Review Modes

## Table of Contents
- [Purpose](#purpose)
- [External evidence rule](#external-evidence-rule)
- [Code-diff review](#code-diff-review)
- [Document review](#document-review)
- [Reviewer coverage map](#reviewer-coverage-map)
- [Required finding format](#required-finding-format)

## Purpose
This note preserves the original technical-review prompt mechanics while keeping the main skill concise.

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
Baseline defaults:
- `code-simplicity-reviewer` always
- `architecture-strategist` for specs, plans, and architecture-heavy diffs

Add by signal:
- `dhh-rails-reviewer` when Ruby/Rails review quality is central
- `kieran-rails-reviewer` when Ruby/Rails files changed
- `kieran-typescript-reviewer` when TypeScript or JavaScript files changed
- `kieran-python-reviewer` when Python files changed
- `julik-frontend-races-reviewer` when async frontend controllers or DOM lifecycle risks appear
- `security-sentinel` for auth, secrets, trust boundaries, or untrusted-input handling
- `performance-oracle` for hot paths, query scale, latency, or performance regressions
- `data-integrity-guardian` for schema, migration, persistence, or correctness-sensitive changes
- `schema-drift-detector` when schema dump drift is part of the change
- `deployment-verification-agent` when rollout or operational verification is part of the contract
- `spec-flow-analyzer` for flow, edge-case, and requirements gaps in document review
- `every-style-editor` only after the technical pass when wording cleanup materially helps

Run reviewers in bounded parallel when platform and policy allow. Otherwise apply the same lenses serially.

## Required finding format
For each finding include:
- severity
- exact location:
  - `file:line` when available
  - section heading for docs
- why it matters
- recommended minimal fix
- confidence `0-1`
