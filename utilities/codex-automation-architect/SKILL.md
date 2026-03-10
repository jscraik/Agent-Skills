---
name: codex-automation-architect
description: "Create, review, and merge Codex app automations; use when users need recurring automation design or consolidation with current OpenAI/Codex guidance, environment preflight, and headless multi-runner validation."
---

# Codex Automation Architect

Design, review, consolidate, and validate Codex automations with current Codex and OpenAI guidance, explicit preflight, and policy-aware execution planning.

## Standards snapshot (March 2026)
- Automation quality means safe defaults, explicit schedules, bounded workspace scope, and headless validation evidence.
- Refresh guidance against current OpenAI and Codex docs before making strong claims about automations.
- Design for constrained policies first, especially approval-restricted and unattended runs.
- Prefer merge and retirement decisions backed by overlap evidence, not naming similarity alone.
- Treat the OpenAI Responses API as the current baseline when automation guidance touches modern OpenAI API workflows.

## When to use
- Creating a new recurring Codex automation.
- Reviewing an automation portfolio for overlap or consolidation.
- Hardening an automation for safer unattended use.
- Validating automation prompts, schedules, and runner posture against current guidance.

## Required inputs
- Objective and success criteria.
- Schedule cadence and timezone.
- Target workspace path or paths.
- Existing automation definitions for review or merge work.
- Approval, sandbox, or runtime posture constraints.

## Deliverables
- Automation specs with `name`, `prompt`, `rrule`, `cwds`, and `status`.
- Merge or keep recommendations with rationale.
- Blocker and permission report with remediation steps.
- Validation evidence and freshness date.
- If requested, a structured status report with a `schema_version` field.

## Philosophy
- Reliable, auditable automation beats clever but fragile automation.
- The smallest safe unattended action is usually the right starting point.
- Good automation design includes fallback behavior when policy blocks ideal execution.

## Constraints
- Redact secrets, tokens, and sensitive repo or automation data by default.
- Prefer least-privilege permissions and avoid default full-access posture.
- Do not claim automation safety or portability without validation evidence.
- When commits or destructive actions are blocked by policy, fall back to patch-only or recommendation mode.

## Workflow
1. Choose mode: `create`, `review`, or `hybrid`.
2. Refresh the current guidance baseline from OpenAI and Codex sources.
3. Run environment preflight on paths, binaries, and policy posture.
4. Build or audit automation specs.
5. Produce merge or retirement recommendations from overlap evidence.
6. Run validation gates and report blockers, evidence, and next steps.

## Current baseline
- Treat March 2026 as the current standards floor.
- Refresh:
  - OpenAI docs for Codex and automation guidance
  - Codex release and behavior context
- Date-stamp outputs when recency matters.

## Blocker protocol
- If policy blocks Python heredocs, chained destructive commands, or unattended commits, switch to the documented safe fallback.
- If auth, runtime, or workspace prerequisites are missing, stop with a blocker report instead of building speculative automation output.
- If approval posture is incompatible with the requested automation behavior, surface that mismatch explicitly.

## Tooling and references
- Use current OpenAI and Codex doc sources before final recommendations.
- Reference files:
  - `references/contract.yaml`
  - `references/evals.yaml`
  - `references/plan.md`
  - `references/headless-eval-matrix.md`
  - `references/latest-standards-2026-03-04.md`
  - `agents/openai.yaml`

## Validation
- Verify environment preflight before recommending unattended runs.
- Verify automation definitions are complete and internally consistent.
- Verify overlap evidence before recommending merge or retirement.
- Fail fast at the first missing prerequisite or failed safety gate.

## Anti-patterns
- Merging automations based only on similar names.
- Assuming unattended runs can bypass policy constraints.
- Recommending full-access posture by default.
- Using stale docs when the request is explicitly about current automation behavior.

## Examples
- Create a weekly Codex automation for stale PR triage.
- Review these six automations and tell me which ones should be merged.
- Harden this automation for approval-restricted unattended execution.

## Remember
An automation is production infrastructure. If its boundaries are unclear, it is not ready.
