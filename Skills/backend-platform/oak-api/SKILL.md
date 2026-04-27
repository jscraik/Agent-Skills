---
name: oak-api
description: Build safe Oak Curriculum API learning flows. Use this skill when Oak endpoints, curriculum maps, or child-facing Apps SDK guidance are needed.
metadata:
  skill-type: library_api_reference
  risk: medium
---

# Oak API

## Philosophy
Learner safety, age fit, and compliance come before product cleverness.

## When To Use
- The task depends on Oak API subjects, units, lessons, quizzes, search, or endpoint mapping.
- The user wants Oak content turned into a learner-facing flow or implementation plan.
- A child-facing app needs age fit, attribution, API-key handling, and rate-limit reminders.

## Avoid
- Do not create generic educational content with no Oak data dependency.
- Do not dump Oak lesson material verbatim.
- Do not imply Oak endorsement or skip licensing and rate-limit reminders.

## Inputs
- User request and target repo or artifact.
- Evidence source such as files, diffs, issues, releases, or existing workflow state.
- Any safety, privacy, compliance, or approval constraints.

## Outputs
- Schema-bound outputs include `schema_version`.
- Age-appropriate learning flow or endpoint map.
- Compliance checklist and attribution.
- Implementation guidance when requested.

## Workflow
1. Collect age range, key stage, subject, learning goal, interaction style, and constraints.
2. Confirm no learner PII and restore age/compliance context if the task drifts.
3. Load only the archived Oak reference needed for the current request.
4. Map content into explain -> practice -> check flows.
5. Include required age, flow, compliance, attribution, pagination, and rate-limit markers when relevant.
6. Use authenticated fetch tooling only when explicitly needed and keep keys in environment variables.

## Constraints
- Redact secrets, API keys, and learner details by default.
- Use Oak endpoint claims only from archived references or live verified docs.
- Do not log credentials or imply Oak endorsement.
- Fail fast with `Missing inputs: age range, key stage, subject.` when core context is absent.

## Validation
- Run Plugin Eval and strict skill audit after editing this skill.
- Report exact validation commands and pass/fail outcomes.
- Fail fast: stop at the first failed gate, fix it, and rerun before continuing.

## Anti-Patterns
- Do not create generic educational content with no Oak data dependency.
- Do not dump Oak lesson material verbatim.
- Do not imply Oak endorsement or skip licensing and rate-limit reminders.

## Examples
- "Turn a KS2 maths unit into an Oak-backed practice flow."
- "Build the Oak flow, but age range and subject are missing."

## Progressive Disclosure
- Archived full context: `Infrastructure/references/deferred-skill-context/backend-platform-oak-api/`.
- Load archived references only when the active workflow needs that exact detail.
- Keep the active path compact; do not remove important context for budget trimming.

## See Also

| Skill | When to use together |
|---|---|
| [[verification-before-completion]] | Confirm gate outcomes and report deterministic pass/fail evidence before closeout |
| [[project-brain]] | Capture durable repo learnings and route updates into the canonical memory surface |
