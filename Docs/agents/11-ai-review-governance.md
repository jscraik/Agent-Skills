# AI Review Governance

## Table of Contents
- [Purpose](#purpose)
- [Authoring-family review scope](#authoring-family-review-scope)
- [Claude Invocation Policy](#claude-invocation-policy)
- [Gate dependency policy](#gate-dependency-policy)
- [Approval expectations](#approval-expectations)

## Purpose
This document defines review-time governance for AI-authored changes and AI-centered skill infrastructure updates in this repository.

## Authoring-family review scope
For changes touching skill authoring family behavior (`skill-builder`, `skill-creator`, `skill-installer`, `plugin-creator`), reviewers must require the `authoring-family-gate` CI job.

The gate is implemented by:
- `bash Infrastructure/scripts/validate_skill_authoring_family.sh`

Reviewers should expect this gate to enforce:
- Contract schema and benchmark parity across all four family skills.
- Evals contract/security coverage including prompt-injection fail cases.
- OpenClaw security guard execution.
- Structural smoke/release eval case coverage (or trusted-lane live eval execution when explicitly enabled).
- In CI this gate runs with `SKILL_FAMILY_LOCAL_MEMORY_MODE=optional`, so local-memory preflight is advisory there; reviewers should still require all remaining contract/eval/security checks to pass.

## Claude Invocation Policy
Claude workflow invocation is restricted to trusted actors only:
- Allowed `author_association` values: `OWNER`, `MEMBER`, `COLLABORATOR`.
- Applies to these events: `issue_comment`, `pull_request_review_comment`, `pull_request_review`, and `issues`.
- The `issues` trigger is restricted to `opened` events only, to avoid assigner/author ambiguity on `assigned`.

Traceability:
- Workflow file: `.github/workflows/claude.yml`
- Job condition fragment:
  - Mention gate: `@claude` must be present in the relevant event body/title.
  - Trust gate: event-specific `author_association` must be in `["OWNER","MEMBER","COLLABORATOR"]`.

## Gate dependency policy
See [CI Required Checks](/Docs/agents/12-ci-required-checks.md) for the canonical PR gate dependency policy.

Any change that removes or bypasses the `harness-preflight -> [repo-validate, authoring-family-gate]` dependency must be treated as governance-impacting and reviewed explicitly.

## Approval expectations
- Do not grant final merge-ready status for relevant PRs while `authoring-family-gate` is failing or absent.
- Require evidence in PR checks that dependency ordering remained intact when workflow changes are included.
- If live eval mode is used, ensure trusted-lane safeguards are explicit and documented.
