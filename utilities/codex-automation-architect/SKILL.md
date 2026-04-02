---
name: codex-automation-architect
description: Design, review, or merge Codex app automations using current OpenAI/Codex guidance and validation. Use when the user wants recurring Codex automation workflows built, audited, or consolidated.
metadata:
  skill-type: team_automation
---

# Codex Automation Architect

Design, review, consolidate, and validate Codex automations with current Codex and OpenAI guidance, explicit preflight, and policy-aware execution planning.

## Standards snapshot (March 30, 2026)
- Codex app automations run in the background, and the Codex app plus selected project path must be available on disk.
- In Git repositories, automations can run in local mode or dedicated background worktrees; in non-version-controlled projects they run directly in the project directory.
- Automations are unattended and inherit default sandbox settings; full access carries elevated risk and should not be the default.
- When allowed, automations use `approval_policy = "never"`; if org requirements disallow that, behavior falls back to the selected approval mode.
- Configuration precedence remains CLI override -> profile -> project `.codex/config.toml` -> user config -> system -> built-in defaults.
- Profiles are still marked experimental and are not currently supported in the Codex IDE extension.
- Release freshness floor should be checked at runtime; current codexRepo MCP baseline is stable `0.117.0` and alpha `0.118.0-alpha.3` (published March 26-27, 2026).
- For RRULE design work, prefer RFC 5545-compatible patterns: explicit `dtstart`, avoid mixing `count` and `until` unless intentional, and set timezone context (`tzid`) when local-time recurrences matter.

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

## Response format
For non-trivial outputs, return this compact structure:
- `schema_version`
- `mode` (`create` | `review` | `hybrid`)
- `automation_specs` (when creating/updating)
- `merge_recommendations` (when reviewing overlaps)
- `blockers`
- `validation_evidence`
- `freshness` (sources + verification date)
- `next_step`

## Philosophy
- Reliable, auditable automation beats clever but fragile automation.
- The smallest safe unattended action is usually the right starting point.
- Good automation design includes fallback behavior when policy blocks ideal execution.
- Start with the smallest viable package boundary on the first pass and keep scope tight before expanding.
- Use 2-3 focused automation surfaces first, then adapt with context-specific variation after baseline validation.
- Why this approach: it helps teams stay capable under policy constraints while enabling predictable scale-up.
- Guiding questions:
  - Which tradeoff matters most here: speed, isolation, or reviewability?
  - Which constraints are real policy constraints versus optional preferences?
  - What is the smallest viable schedule and prompt that can still deliver value?

## Constraints
- Redact secrets, tokens, and sensitive repo or automation data by default.
- Prefer least-privilege permissions and avoid default full-access posture.
- Do not claim automation safety or portability without validation evidence.
- When commits or destructive actions are blocked by policy, fall back to patch-only or recommendation mode.

## Workflow
0. Start with a narrow first pass: limit scope to the smallest viable package boundary and 2-3 focused modules.
1. Choose mode: `create`, `review`, or `hybrid`.
2. Refresh the current guidance baseline from:
   - OpenAI docs MCP (`codex/app/automations`, approvals/security, config precedence/profiles)
   - codexRepo MCP (latest stable/alpha release context)
   - Context7 MCP (RRULE/RFC 5545 implementation guidance when schedule design is requested)
3. Run environment preflight on paths, binaries, and policy posture.
4. Build or audit automation specs.
5. Produce merge or retirement recommendations from overlap evidence.
6. Run validation gates and report blockers, evidence, and next steps.

## Variation guidance
- Vary recommendations by context-specific risk posture (solo maintainer, team workflow, managed org policy).
- Use different fallback paths for different constraints (network disabled, read-only sandbox, approval restrictions).
- Avoid repetition and generic cookie-cutter automation specs when existing workflows differ materially.
- Customize cadence and prompt detail to the task class (triage, summarization, release hygiene, CI drift checks).

## Current baseline
- Treat March 30, 2026 as the current standards floor.
- Refresh:
  - OpenAI docs for Codex and automation guidance
  - Codex release and behavior context via codexRepo MCP
  - RRULE best-practice guidance via Context7 when recurrence strings are in scope
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
  - `references/latest-standards-2026-03-30.md`
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
- NEVER recommend destructive or bypass-oriented commands as a first-choice path.
- DO NOT ignore managed requirements (`requirements.toml`) when they restrict approval/sandbox posture.
- DON'T converge every workflow into one giant automation when separate schedules are safer and clearer.

## Examples
- User says: "Can you set up a weekly Codex automation that inspects stale PRs and posts a concise triage summary?"
- User says: "Please inspect these six automations and help me decide what to merge versus keep separate."
- User says: "Can you harden this recurring automation for a managed environment where `approval_policy = never` is disallowed?"

## See Also

| Skill | When to use together |
|---|---|
| [[codex-agent-creator]] | Create the agent role the automation will run under |
| [[decide-build-primitive]] | Confirm automation is the right primitive before building |
| [[ce-plan]] | Plan the automation contract before implementing |
| [[verification-before-completion]] | Validate automation output before declaring done |

**Topic map:** [[agent-ops]]

## Remember
An automation is production infrastructure. If its boundaries are unclear, it is not ready.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If the trigger, execution environment, or safety guardrails are unclear, stop, report the missing assumptions, and fall back to an automation design sketch instead of shipping a brittle workflow.
