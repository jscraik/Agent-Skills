---
name: he-code-review
description: Review Harness Engineering diffs, PRs, plans, or implemented work for merge readiness and regression risk. Use when users ask for a go/no-go review.
metadata:
  skill-type: code_quality_review
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Philosophy

- Prioritize release-risk clarity over commentary volume.
- Keep findings evidence-backed and action-oriented.
- Resolve review mode and target scope before analysis starts.
- Keep mutation boundaries explicit: broad review stays read-focused unless the selected mode allows safe auto-fix work.

## When to use

- Use when package-level readiness, merge risk, or release go/no-go is the core question.
- Use when merge readiness depends on proving a PR actually satisfies linked Linear QA issues.
- Route to `he-technical-review` when deep implementation-level correctness analysis is needed.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

1. Resolve the target, target mode, and any `mode:` / `base:` / `plan:` overrides before analysis begins.
2. Fail fast on conflicting review-mode flags instead of guessing which one wins.
3. Collect repository evidence from the diff, changed files, linked artifacts, validations, and local review context before reaching for external references.
4. Use the smallest reviewer set that still covers readiness risk; always include agent-operability, institutional learnings, and simplicity lenses.
5. Review for correctness, regression risk, operability, protected-artifact handling, domain-language drift, and release readiness.
6. When Linear QA issues are linked, confirm the PR satisfies expected behavior, preserves reproduction coverage, and includes validation evidence before recommending `go`.
7. Deduplicate and rank findings as `P0`, `P1`, `P2`, or `P3`, then emit an explicit recommendation: `go`, `go-with-conditions`, or `no-go`.
8. Only allow in-skill mutation when the selected mode explicitly permits safe auto-fixes; otherwise stop after the report.

## Validation

- Ensure each finding includes severity, location, impact, and minimal remediation.
- Ensure recommendation is explicit (`go`, `go-with-conditions`, `no-go`).
- Ensure protected artifact cleanup findings are discarded during synthesis.
- Ensure changed domain terms, aliases, and relationships either match `CONTEXT.md` or are reported as drift.
- Ensure linked Linear QA issues are closed by behavior and evidence, not just by code proximity.
- Ensure unresolved `P0` or `P1` findings block a `go` recommendation.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not claim readiness without repository evidence.
- Do not switch a shared checkout for `mode:report-only` or `mode:headless`; require an isolated checkout/worktree or review the current checkout with an explicit base.
- Do not ask blocking questions in `mode:report-only` or `mode:headless`.
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Approving high-risk changes without concrete validation evidence.
- Collapsing multiple blockers into vague summary text without file references.
- Running maximal reviewer fan-out for simple low-risk changes.
- Missing a new project term or renamed concept that should update `CONTEXT.md`.
- Flagging `docs/brainstorms/*`, `docs/plans/*.md`, or `docs/solutions/*.md` for cleanup/removal.
## Examples

Read when: examples or role-routing details are needed, open the archived references for this skill.
