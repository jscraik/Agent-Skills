# Code Review Standards

## Table of Contents
- [Scope](#scope)
- [Mandatory review triggers](#mandatory-review-triggers)
- [Pre-review requirements](#pre-review-requirements)
- [Severity model](#severity-model)
- [Security review triggers](#security-review-triggers)
- [Approval criteria](#approval-criteria)
- [Enforcement](#enforcement)

## Scope
- This module defines consistent review criteria before merge.

## Mandatory review triggers
- Review is required for:
  - New features and bug fixes.
  - Security-sensitive surfaces.
  - Architectural or workflow-governance changes.
  - Any change that alters public behavior or release-critical scripts.

## Pre-review requirements
- Before requesting review:
  - Confirm branch is up to date with target base.
  - Resolve merge conflicts.
  - Run required validation gates and capture results.

## Severity model
- `CRITICAL`: security/data-loss risk; merge blocker.
- `HIGH`: functional correctness risk; merge blocker unless explicit risk acceptance is documented and approved by the repo owner.
- `MEDIUM`: maintainability/design risk; fix when feasible in current scope.
- `LOW`: style or minor improvement; optional unless policy demands.

## Security review triggers
- Require dedicated security review when changes involve:
  - Authentication/authorization.
  - Secrets, credentials, tokens, or key management.
  - Input handling with execution/query implications.
  - Payment or sensitive data pathways.

## Approval criteria
- Approve when no CRITICAL/HIGH unresolved findings remain.
- If a HIGH finding remains by explicit decision, document approved risk acceptance and accountable owner in the PR.

## Enforcement
- Review artifacts MUST reference concrete file paths and impacted behavior.
- Validation and review outcomes MUST be explicit and evidence-backed.
- Repo review wrappers MUST stay aligned with the independent-review contract. When review or comment-resolution behavior changes, validate the wrapper surface and preserve external reviewer independence.
- Review evidence MUST distinguish human, Codex, CodeRabbit, CI, and security-check status instead of collapsing them into a single generic approval.
