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

## When to use

- Use when package-level readiness, merge risk, or release go/no-go is the core question.
- Route to `he-technical-review` when deep implementation-level correctness analysis is needed.

## Inputs

- Review target (PR, branch, diff, plan, or release artifact).
- Access to changed files, validation logs, and related context.

## Outputs

- Severity-ranked readiness findings with exact locations.
- Explicit go/no-go recommendation with blocking conditions.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Confirm target scope and collect evidence from the repository.
2. Review for correctness, regression risk, operability, and release readiness.
3. Emit prioritized findings plus merge-readiness recommendation.

## Validation

- Ensure each finding includes severity, location, impact, and minimal remediation.
- Ensure recommendation is explicit (`go`, `go-with-conditions`, `no-go`).
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not claim readiness without repository evidence.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Approving high-risk changes without concrete validation evidence.
- Collapsing multiple blockers into vague summary text without file references.

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
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
