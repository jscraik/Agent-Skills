---
name: he-technical-review
description: Review diffs, PRs, specs, plans, or feedback for technical correctness. Use when engineering risks or review-feedback validity must be verified before implementation.
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

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

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
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-Patterns

- Blindly implementing feedback without verification.
- Treating terminology-only drift as harmless when it changes behavior or user meaning.
- Reviewing style while missing correctness/regression risks.
- Partial implementation when interdependent items are unclear.
## Examples

Read when: examples or role-routing details are needed, open the archived references for this skill.
