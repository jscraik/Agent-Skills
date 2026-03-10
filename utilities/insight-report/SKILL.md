---
name: insight-report
description: Generate a high-fidelity Codex usage insights HTML report from local Codex session data. Use this skill when a user asks for an insights report, usage report, or session analysis.
---

# Insight Report

Generate evidence-backed HTML insight reports from local Codex session history without drifting into anecdotal storytelling.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Workflow](#workflow)
- [Anti-patterns](#anti-patterns)
- [Validation](#validation)
- [Examples](#examples)
- [References](#references)

## Standards snapshot
- Prefer reproducible metrics over narrative guesswork.
- Keep confidence limits explicit when session coverage is partial or noisy.
- Use HTML output when the request is for a report artifact, not just a quick summary.
- Distinguish observed patterns from speculative causality.

## When to use
- The user asks for an insights report, usage report, or session analysis from local Codex history.
- The task needs a durable HTML artifact rather than a short terminal-only summary.
- A time-bounded retrospective or workflow analysis is needed from session data.

## Required inputs
- Time window, scope, or session subset if specified.
- Source session or log paths when the workflow is not using default local locations.
- Desired report detail level and any audience constraints.

## Deliverables
- HTML insights report artifact.
- Summary of key metrics, notable patterns, and blockers.
- Explicit note of missing data, uncertainty, or confidence limits.

## Philosophy
- Metrics should support decisions, not decorate the report.
- Interpret patterns conservatively when evidence is sparse.
- Make the report easy to reopen, compare, and iterate on later.

## Failure mode
- If the user wants live operational remediation rather than retrospective analysis, route to the more appropriate diagnostic workflow.
- If the source data is missing or incomplete, stop at evidence limitations instead of forcing conclusions.
- If the request is really for prose rewriting, summarization, or editorial packaging, use a writing-oriented skill after the report data is gathered.

## Constraints
- Redact secrets, tokens, credentials, and personal data in report outputs.
- Do not infer unsupported causal claims from sparse data.
- Keep analysis scoped to the requested period and available evidence.

## Workflow
1. Collect session data for the requested scope.
2. Compute summary metrics and trend slices.
3. Check for obvious evidence gaps or skew before interpreting results.
4. Generate the HTML report with clear sections and confidence notes.
5. Return concise highlights plus the artifact path and any follow-up suggestions.

## Anti-patterns
- Fabricating trends when the data is incomplete.
- Hiding uncertainty behind polished charts or phrasing.
- Shipping a report without metric sanity checks.

## Validation
- Fail fast: stop on broken or incomplete source data and report the blocker.
- Verify report generation completed successfully.
- Verify key metrics are populated and internally consistent.
- Confirm the final report distinguishes hard evidence from inference.

## Examples
- Generate a 7-day usage report with top workflows and blockers.
- Generate a monthly trend report with confidence notes and action items.

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- README: `references/README.md`

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
