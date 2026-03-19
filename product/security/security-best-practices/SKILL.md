---
name: "security-best-practices"
description: "Perform language and framework specific security best-practice reviews and suggest improvements. Trigger only when the user explicitly requests security best practices guidance, a security review/report, or secure-by-default coding help. Trigger only for supported languages (python, javascript/typescript, go). Do not trigger for general code review, debugging, or non-security tasks."
metadata:
  skill-type: code_quality_review
---

# Security Best Practices

Use language- and framework-specific security guidance to produce secure-by-default advice, focused reports, or scoped remediation plans.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Workflow](#workflow)
- [Reporting](#reporting)
- [Fix strategy](#fix-strategy)
- [Anti-patterns](#anti-patterns)
- [Validation](#validation)
- [References](#references)

## Standards snapshot
- Only trigger on explicit security best-practices intent.
- Limit supported languages to python, javascript/typescript, and go.
- Map web and API findings to `OWASP Top 10:2025` when reporting risk.
- Prefer evidence-backed review findings over speculative vulnerability claims.

## When to use
- The user explicitly asks for security best-practices guidance.
- The user wants a security review, security report, or secure-by-default coding help.
- The task is specifically about supported languages or frameworks in this repo.

## Required inputs
- The target codebase, file scope, or feature area.
- The relevant languages and frameworks in play.
- Whether the task is:
  - secure-by-default implementation guidance;
  - passive review while working;
  - or a full security report.

## Deliverables
- Secure-by-default implementation guidance, or
- A prioritized security report with clear severity and urgency, or
- A narrow remediation plan for one finding at a time.

## Philosophy
- Prefer root-cause security fixes over symptom patches.
- Keep advice explicit, reproducible, and grounded in repo evidence.
- Make tradeoffs visible when security guidance conflicts with project behavior or deployment reality.

## Failure mode
- If the request is general code review, debugging, or non-security work, do not use this skill.
- If the language or framework is unsupported, say so clearly and keep any advice bounded.
- If no relevant reference guidance exists, distinguish between known best practice and uncertainty rather than overstating confidence.

## Constraints
- Redact secrets, tokens, credentials, and PII by default; never echo raw environment values.
- Avoid irreversible or behavior-changing fixes without making regression risk explicit.
- Do not report lack of TLS or `secure` cookie flags naively in local or non-TLS development contexts.

## Workflow
1. Identify all relevant languages and primary frameworks in scope.
2. Load the matching guidance from `references/`:
   - framework-specific files first;
   - then the corresponding general language guidance.
3. If the app spans frontend and backend, inspect both sides.
4. Choose the operating mode:
   - secure-by-default guidance for new work;
   - passive detection of high-impact issues while coding;
   - full report when requested.
5. Ground every finding or recommendation in concrete code evidence or documented best practice.

## Reporting
- Write reports to `security_best_practices_report.md` unless the user specifies a different path.
- Include:
  - a short executive summary;
  - severity-grouped findings;
  - numeric IDs for each finding;
  - one-sentence impact statements for critical issues;
  - file and line references for cited code.
- Summarize the report for the user after writing it and state the output path explicitly.

## Fix strategy
- If a report was produced, let the user decide when to begin fixes.
- When fixing, address one finding at a time.
- Keep comments concise and explain the best-practice alignment only where needed.
- Run the project’s normal tests or verification flow after changes to reduce regression risk.

## Anti-patterns
- Triggering this skill for general code review or unrelated debugging.
- Claiming vulnerabilities without evidence.
- Bundling unrelated findings into one fix or one commit.
- Treating local-dev TLS absence as an automatic reportable issue.

## Validation
- Fail fast: stop at the first major evidence gap or unsupported-language boundary and state it clearly.
- Verify language and framework identification before selecting reference guidance.
- Re-run the project’s required checks before advancing from one fix to the next.
- Keep reports traceable with line-referenced evidence.

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Folded legacy modes: `references/folded-legacy-modes-core60.md`

## See Also

| Skill | When to use together |
|---|---|
| [[security-threat-model]] | Run first to identify trust boundaries and threat model; this skill remediates specific findings |
| [[security-ownership-map]] | Find who owns the highest-risk code after identifying findings |
| [[create-auth]] | Security review often surfaces auth issues — use this for implementation |
| [[1password]] | Findings involving secrets management — use for secure injection patterns |

**Topic map:** [[security-ops]]

<!-- decision-feedback-protocol:v2 -->

**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
