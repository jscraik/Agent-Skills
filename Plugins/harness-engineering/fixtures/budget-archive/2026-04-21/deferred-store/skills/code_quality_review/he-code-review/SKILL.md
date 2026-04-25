---
name: he-code-review
description: Review PRs, branches, diffs, and workflow artifacts for package-level go/no-go readiness with severity-ranked synthesis. Use when users need readiness synthesis rather than detailed technical-risk critique.
metadata:
  skill-type: code_quality_review
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering code-review stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Prioritize release-risk clarity over commentary volume.
- Keep findings evidence-backed and action-oriented.
- Resolve review mode and target scope before analysis starts.
- Keep mutation boundaries explicit: broad review stays read-focused unless the selected mode allows safe auto-fix work.

## When to use

- Use when package-level readiness, merge risk, or release go/no-go is the core question.
- Route to `he-technical-review` when deep implementation-level correctness analysis is needed.

## Inputs

- Review target (PR, branch, diff, plan, or release artifact).
- Access to changed files, validation logs, and related context.
- Optional mode modifiers such as `mode:interactive`, `mode:report-only`, `mode:autofix`, `mode:headless`, `base:<ref>`, and `plan:<path>`.

## Outputs

- Severity-ranked readiness findings with exact locations.
- Explicit go/no-go recommendation with blocking conditions.
- Resolved target mode (`pr-branch-review` or `artifact-review`) and next action.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Resolve the target, target mode, and any `mode:` / `base:` / `plan:` overrides before analysis begins.
2. Fail fast on conflicting review-mode flags instead of guessing which one wins.
3. Collect repository evidence from the diff, changed files, linked artifacts, validations, and local review context before reaching for external references.
4. Use the smallest reviewer set that still covers readiness risk; always include agent-operability, institutional learnings, and simplicity lenses.
5. Review for correctness, regression risk, operability, protected-artifact handling, domain-language drift, and release readiness.
6. Deduplicate and rank findings as `P0`, `P1`, `P2`, or `P3`, then emit an explicit recommendation: `go`, `go-with-conditions`, or `no-go`.
7. Only allow in-skill mutation when the selected mode explicitly permits safe auto-fixes; otherwise stop after the report.

## Validation

- Ensure each finding includes severity, location, impact, and minimal remediation.
- Ensure recommendation is explicit (`go`, `go-with-conditions`, `no-go`).
- Ensure protected artifact cleanup findings are discarded during synthesis.
- Ensure changed domain terms, aliases, and relationships either match `CONTEXT.md` or are reported as drift.
- Ensure unresolved `P0` or `P1` findings block a `go` recommendation.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not claim readiness without repository evidence.
- Do not switch a shared checkout for `mode:report-only` or `mode:headless`; require an isolated checkout/worktree or review the current checkout with an explicit base.
- Do not ask blocking questions in `mode:report-only` or `mode:headless`.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Approving high-risk changes without concrete validation evidence.
- Collapsing multiple blockers into vague summary text without file references.
- Running maximal reviewer fan-out for simple low-risk changes.
- Missing a new project term or renamed concept that should update `CONTEXT.md`.
- Flagging `docs/brainstorms/*`, `docs/plans/*.md`, or `docs/solutions/*.md` for cleanup/removal.

## Examples

- "When the user asks, `Can you review GitHub PR #482 and tell me whether anything still blocks merge?`"
- "Please inspect the current branch against `origin/main`, validate the risky changes, and give me the go/no-go call."
- "Review `Docs/plans/2026-03-23-001-feat-example-plan.md` and tell me whether it is ready for the next workflow stage."

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Domain model routing: [../../../references/domain-model-routing.md](../../../references/domain-model-routing.md)
Read when: a review target changes project terminology, `CONTEXT.md`, or Linear issue meaning.
- Template: [./review-todo.md.tmpl](./review-todo.md.tmpl)
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, route to [codex-agent-creator](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) and provide the exact role names to create or install.
