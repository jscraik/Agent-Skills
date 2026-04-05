# AI Review Governance

## Table of Contents
- [Purpose](#purpose)
- [Authoring-family review scope](#authoring-family-review-scope)
- [Gate dependency policy](#gate-dependency-policy)
- [Approval expectations](#approval-expectations)

## Purpose
This document defines review-time governance for AI-authored changes and AI-centered skill infrastructure updates in this repository.

## Authoring-family review scope
For changes touching skill authoring family behavior (`skill-builder`, `skill-creator`, `skill-installer`, `plugin-creator`), reviewers must require the `authoring-family-gate` CI job.

The gate is implemented by:
- `bash scripts/validate_skill_authoring_family.sh`

Reviewers should expect this gate to enforce:
- Contract schema and benchmark parity across all four family skills.
- Evals contract/security coverage including prompt-injection fail cases.
- OpenClaw security guard execution.
- Structural smoke/release eval case coverage (or trusted-lane live eval execution when explicitly enabled).

## Gate dependency policy
PR orchestration for these checks follows this dependency model:
1. `pr-template`
2. `repo-validate` and `authoring-family-gate` (in parallel after template pass)
3. `harness-preflight` (must depend on both jobs above)

Any change that removes or bypasses the `harness-preflight -> [repo-validate, authoring-family-gate]` dependency must be treated as governance-impacting and reviewed explicitly.

## Approval expectations
- Do not grant final merge-ready status for relevant PRs while `authoring-family-gate` is failing or absent.
- Require evidence in PR checks that dependency ordering remained intact when workflow changes are included.
- If live eval mode is used, ensure trusted-lane safeguards are explicit and documented.
