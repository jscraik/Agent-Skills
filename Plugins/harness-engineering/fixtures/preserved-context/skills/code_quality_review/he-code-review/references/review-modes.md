# Harness Engineering Code Review Modes

## Table of Contents
- [Purpose](#purpose)
- [Argument parsing and overrides](#argument-parsing-and-overrides)
- [Boundary against he-technical-review](#boundary-against-he-technical-review)
- [Protected artifacts](#protected-artifacts)
- [External evidence rule](#external-evidence-rule)
- [PR and branch review](#pr-and-branch-review)
- [Artifact review](#artifact-review)
- [Reviewer coverage map](#reviewer-coverage-map)
- [Execution strategy](#execution-strategy)
- [Mode-driven post-review flow](#mode-driven-post-review-flow)
- [Todo follow-up](#todo-follow-up)
- [Optional runtime verification](#optional-runtime-verification)

## Purpose
This note preserves the stronger parts of the legacy broad-review workflow while keeping the main skill concise and scoped.

## Argument parsing and overrides
Parse optional modifiers before reviewer selection:
- `mode:interactive` keeps the default broad review flow
- `mode:report-only` stops after findings and recommendation
- `mode:autofix` allows only the smallest safe fixer follow-up after synthesis
- `mode:headless` runs the same review logic without blocking questions and returns a machine-friendly completion signal
- `base:<ref>` overrides the diff base for branch or diff review
- `plan:<path>` injects a plan artifact as extra review context

Guardrails:
- fail fast on conflicting `mode:` tokens
- do not invent a `base:` override when the user did not supply one
- do not treat `plan:<path>` as the primary review target unless the rest of the request makes that explicit

## Boundary against he-technical-review
Use `he-code-review` when the user wants:
- broad readiness
- package-level synthesis
- blockers plus recommendation
- artifact-aware review with next-step routing

Use `he-technical-review` when the user wants:
- deep engineering critique
- findings-first technical issues
- readiness scoring for a spec or plan without the broader package-review framing

It is acceptable for `he-code-review` to borrow technical-review semantics during artifact review, but not to replace or duplicate `he-technical-review` wholesale.

## Protected artifacts
The following paths are workflow artifacts and must never produce deletion, cleanup, or gitignore findings:
- `Docs/specs/*.md`
- `Docs/plans/*.md`
- `docs/ui-specs/*.md`
- `docs/ui-plans/*.md`
- `docs/solutions/*.md`
- `prototypes/ui/*.html` while the prototype direction is still active

Discard those findings during synthesis instead of surfacing them.

## External evidence rule
Use local evidence first:
- diff
- files
- tests
- linked artifacts
- repo patterns
- reviewer context from local config
- institutional learnings such as `.harness/memory/LEARNINGS.md`, `instructions/Learnings.md`, and targeted `docs/solutions/`

Escalate to current external docs only when:
- a finding depends on framework or library behavior
- version-specific defaults, deprecations, or lifecycle semantics matter
- security-sensitive integration guidance matters
- the review touches OpenAI products and current official behavior must be confirmed

Source preference:
1. official OpenAI docs for OpenAI-product behavior
2. official framework or library docs
3. Context7 for current library documentation when the exact behavior needs quick confirmation
4. secondary guidance only when primary sources do not answer the question cleanly

## PR and branch review
Use when the target is a PR, branch, `current`, `latest`, or explicit diff.

Review order:
1. resolve the exact branch, PR, or diff
2. load the correct branch or worktree before analysis
3. fetch PR metadata when GitHub context exists
4. determine changed files, languages, and risk areas
5. read linked specs, plans, and solution artifacts when clearly relevant
6. run the reviewer set
7. synthesize and rank findings

## Artifact review
Use when the target is a workflow artifact such as a spec, plan, UI artifact, or solution document.

Review order:
1. read the target document fully
2. read linked artifacts referenced in frontmatter or body, such as `origin`, `spec`, or `parent_spec`
3. apply technical-review semantics first
4. add broader readiness, rollout, operational, and workflow-stage coverage where useful
5. synthesize findings and return a readiness recommendation instead of a merge recommendation

## Reviewer coverage map
Use deterministic readiness-reviewer selection.

Always include:
- `agent-native-reviewer`
- `learnings-researcher`
- `code-simplicity-reviewer`

Add by signal:
- `architecture-strategist` for architecture-heavy diffs or artifacts
- `kieran-rails-reviewer` for Ruby/Rails
- `kieran-typescript-reviewer` for TypeScript/JavaScript
- `kieran-python-reviewer` for Python
- `julik-frontend-races-reviewer` for async frontend timing or DOM lifecycle risk
- `design-implementation-reviewer` for Figma-sensitive or visual implementation review
- `data-integrity-guardian` for schema, persistence, or correctness-sensitive changes
- `schema-drift-detector` when schema dump drift is present
- `api-contract-reviewer` for public/downstream API changes
- `security-reviewer` for auth, trust boundaries, secrets, or untrusted input
- `performance-reviewer` for hot paths, scale, query load, or latency concerns
- `reliability-reviewer` for failure, retry, and partial-state hazards
- `deployment-verification-agent` for rollout-sensitive changes

Execution order:
1. baseline readiness lanes
2. language specialists
3. risk specialists
4. deployment verification where rollout risk exists

For deterministic per-target role selection, use `references/sub-agent-map.md`.

Optional deeper-think lane for high-risk or broad reviews:
- run a stakeholder/scenario synthesis pass across developer, operations, user, security, and business lenses
- use it to improve prioritization and recommendation quality, not to inflate the output

## Execution strategy
Default to bounded parallel reviewer fanout.

Switch to serial when:
- the session is already long
- the configured reviewer count is large
- the platform cannot safely hold all reviewer results inline

If local config defines `review_agents`, respect that set first, then add required baseline reviewers when missing.

## Mode-driven post-review flow
Keep collection, reviewer coverage, and synthesis consistent across modes. Only the handoff changes.

`interactive`:
- review-first default
- after safe synthesis, ask at most one blocking question before any mutating follow-up
- no automatic todo creation unless the user asked for it or the repo convention requires it

`report-only`:
- no fixer queue
- no todo creation
- no run artifact
- stop after findings, blockers, and recommendation

`autofix`:
- allow only the smallest safe fixer pass after synthesis
- keep unresolved `manual`, `human`, or rollout-owned findings as residual work
- create durable todos only for residual actionable findings that still belong to downstream execution

`headless`:
- no blocking questions
- one safe fixer pass at most
- no todo creation
- emit a structured text envelope plus a terminal `Review complete` signal for callers

Shared checkout safety:
- do not run a mutating review loop concurrently with browser or simulator verification on the same checkout
- if both need to proceed in parallel, keep review in `mode:report-only` or isolate mutation in a separate worktree

## Todo follow-up
If the repo has a `todos/` review workflow or the user explicitly asks for structured follow-up:
- create or update todo artifacts after findings are synthesized
- keep the review report small; point to the todo artifacts for detail
- preserve `P1`, `P2`, `P3` severity in the todo metadata or naming convention
- use the exact `file-todos` workflow defined in `references/findings-and-todos.md`

Mode nuance:
- default broad review findings normally land as `pending`
- residual actionable findings left over after `mode:autofix` land as `ready` because they have already been triaged during synthesis
- do not create todos for advisory-only, release-owned, or protected-artifact cleanup findings

If there is no local todo convention and the user did not ask for todo capture, return structured findings directly instead of fabricating a todo dependency.

## Optional runtime verification
After the review:
- recommend `test-browser` when web runtime verification would materially improve confidence
- recommend `test-xcode` when iOS/macOS runtime verification would materially improve confidence
- do not automatically mutate or remediate from review mode unless the user explicitly asks for the follow-up stage
