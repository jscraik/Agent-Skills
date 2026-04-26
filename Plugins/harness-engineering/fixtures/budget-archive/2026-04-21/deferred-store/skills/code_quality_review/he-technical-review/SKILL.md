---
name: he-technical-review
description: Review diffs, PRs, specs, plans, or review-feedback items and return severity-ranked engineering findings with exact locations. Use when technical risks or feedback correctness must be verified before implementation.
metadata:
  skill-type: code_quality_review
---

# Harness Engineering Technical Review

Progressive-disclosure entrypoint for findings-first technical review in Harness Engineering.

## Philosophy

- Findings first, implementation second.
- Verify feedback before implementation.

## When To Use

- Technical review of a PR, branch diff, file set, spec, or plan.
- Validation of incoming review feedback before implementing requested changes.
- Validation that a proposed fix addresses the reported Linear QA behavior instead of hiding a symptom.
- Review of domain-language drift when code, specs, or plans introduce project terms.

Route elsewhere:
- `he-code-review` for broader readiness recommendation and stage routing.
- `he-work` for implementation.
- `he-deepen-spec` or `he-deepen-plan` for document rewriting.

## Inputs

- Review target (`PR`, `branch`, `current diff`, `file path`, `spec`, or `plan`).
- Access to target evidence (diff/files/docs/tests).
- Relevant `CONTEXT.md` or `CONTEXT-MAP.md` when domain language is part of the change.
- Optional Linear QA issue, reproduction steps, or expected-behavior claim to verify.
- Optional review-feedback items to validate.

## Outputs

- `schema_version: 1` when structured output is requested.
- `review_mode` (`code-diff-review` or `document-review`)
- findings (`P0-P3`) with location, impact, minimal fix, confidence
- `no_critical_findings` statement when appropriate
- `feedback_response_plan` (`accept`, `clarify`, `push_back_with_evidence`)

## Procedure

1. Resolve mode and target; stop if unusable.
2. Review with repo-first evidence and deduplicate findings.
3. Check domain-language drift when the change introduces terms, aliases, relationships, or behavior boundaries.
4. For Linear QA reports: compare reported behavior, expected behavior, reproduction path, and proposed fix evidence before accepting the implementation.
5. For incoming feedback: read, clarify unclear items, verify, then respond technically.
6. Return findings-first output plus open questions and next action.

## Validation

- Ensure mode matches target and findings contain severity, location, impact, minimal fix, confidence.
- Ensure domain drift findings include the code/spec location and the relevant `CONTEXT.md` mismatch or missing update.
- Ensure QA-related findings distinguish symptom hiding from behavior correction.
- Fail fast: stop at first blocking prerequisite or failed validation gate.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not implement unclear or unverified feedback.
- If feedback conflicts with prior user decisions, escalate with evidence first.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-Patterns

- Blindly implementing feedback without verification.
- Treating terminology-only drift as harmless when it changes behavior or user meaning.
- Reviewing style while missing correctness/regression risks.
- Partial implementation when interdependent items are unclear.

## Examples

- "Can you review this PR diff for correctness before I implement the CodeRabbit feedback?"
- "Please check whether the plan is technically sound before `he-work`, especially the migration and rollback steps."
- "The branch renames `Customer` to `Account`; can you validate whether that matches `CONTEXT.md` and the linked Linear issue?"
- "Can you validate whether this proposed fix solves the Linear QA report or only masks the symptom?"

## References

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Findings template and assets: [./finding.md.tmpl](./finding.md.tmpl), [./assets/icon-small.png](./assets/icon-small.png), [./assets/icon-large.png](./assets/icon-large.png)
- Domain model routing: [../../../references/domain-model-routing.md](../../../references/domain-model-routing.md)
- QA intake routing: [../../../references/qa-intake-routing.md](../../../references/qa-intake-routing.md)
Read when: a technical review target changes project terminology, `CONTEXT.md`, or Linear issue meaning.
Read when: reviewing whether a fix actually satisfies a reported QA behavior and its reproduction path.
Read when: deeper doctrine, templates, or compatibility details are needed.

## Subagent Routing

- Canonical map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Load stage policy from `routing-map.json` and resolve roles from `~/.codex/agents/manifest.json`.
- If auto-spawn is unavailable or required roles are missing, continue inline, list manual-launch roles, and route role provisioning to `[[codex-agent-creator]]` ([../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md)).
