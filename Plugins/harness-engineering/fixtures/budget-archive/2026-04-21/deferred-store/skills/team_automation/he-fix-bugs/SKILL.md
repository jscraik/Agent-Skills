---
name: he-fix-bugs
description: Debug Harness Engineering bugs with reproduction evidence and regression coverage. Use when defects are reproducible, QA failures have expected behavior, or bugfix validation is required.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Philosophy

- Reproduce first, then diagnose, then fix.
- Root-cause clarity beats patch velocity.
- Investigate before proposing changes, and keep the causal chain from trigger to symptom explicit.

## When to use

- Use when regressions, runtime failures, or tracker defects require evidence-backed debugging.
- Use when issue reproduction and verification are required before coding changes.
- Use when prior fix attempts failed and the request needs disciplined root-cause analysis instead of more trial-and-error edits.
- Use when the user starts a QA session or reports bugs conversationally and wants durable Linear issues.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

1. Parse intake first: symptom report, tracker context, expected behavior, and any prior failed attempts.
2. If the request is a QA session or conversational report, run QA intake: ask at most 2-3 focused questions, lightly inspect domain language, decide single issue vs breakdown, and file or prepare Linear issue payloads before diagnosis.
3. Compare issue language with `CONTEXT.md` when present so aliases or domain misunderstandings do not become false bug scope.
4. Reproduce and stabilize the failing behavior before proposing changes.
5. Trace backward from the symptom to the point where valid state first became invalid.
6. Test one hypothesis at a time, and for uncertain links require a prediction that can confirm or falsify the chain.
7. Present the root cause, proposed fix scope, and test recommendations before remediation when the request is diagnosis-first or confidence is still settling.
8. When remediation is in scope, check workspace safety, prefer failing-test-first validation, apply the minimal fix, and verify no regressions.

## Validation

- Confirm reproduction and post-fix verification are both recorded.
- Confirm the causal chain from trigger to symptom is explicit before fix work proceeds.
- Confirm fix addresses root cause instead of symptom masking.
- Confirm Linear issue wording, expected behavior, and domain terms agree or explicitly name the mismatch.
- Confirm QA-created Linear issues avoid file paths and line numbers, include reproduction steps, and use behavior-focused domain language.
- Confirm blocked or partial outcomes name the exact missing condition, evidence gap, or next safest route.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not mark issue fixed without successful verification evidence.
- Do not skip straight to edits when reproduction or root-cause evidence is still missing.
- Do not patch around a domain-model contradiction; route to `he-deepen-spec` when behavior meaning is unclear.
- Do not create GitHub issues or ADRs for QA intake unless the user explicitly overrides the Linear-first project convention.
- Do not over-interview during QA intake; ask only the minimum short questions needed to file a durable issue.
- Do not use shotgun debugging or bundle unrelated changes into one bug fix.
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Skipping deterministic reproduction and guessing a fix.
- Shipping fixes that lack regression checks.
- Accepting a symptom fix when the causal chain prediction failed.
- Treating tracker intake, diagnosis, and issue management as one speculative step.
## Examples

Read when: examples or role-routing details are needed, open the archived references for this skill.
