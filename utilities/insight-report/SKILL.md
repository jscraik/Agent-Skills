---
name: insight-report
description: Generate a high-fidelity Codex usage insights HTML report from local Codex session data. Use this skill when a user asks for an insights report, usage report, or session analysis.
---

# Insight Report

Generate evidence-backed usage insights from local Codex session history.

## When to use
- Use this skill for requests to analyze Codex usage patterns.
- Use this skill for HTML report generation from local session data.

## Inputs
- Time window or scope (if provided).
- Source session/log paths.
- Output preferences for report format and detail.

## Outputs
- HTML insights report artifact.
- Summary of key metrics and notable trends.
- Clear note of missing data or confidence limits.

## Philosophy
- Prefer reproducible metrics over anecdotal interpretation.
- Keep conclusions grounded in observable evidence.
- Why does this metric matter for user decisions?
- What evidence supports this conclusion?
- Which tradeoff matters: depth, speed, or interpretability?

## Constraints
- Redact secrets, tokens, credentials, and personal data in report outputs.
- Do not infer unsupported causal claims from sparse data.
- Keep analysis scoped to requested period and available evidence.

## Procedure
1. Collect session data for the requested scope.
2. Compute summary metrics and trend slices.
3. Generate HTML report with clear sections and evidence notes.
4. Provide concise highlights and follow-up suggestions.

## Validation
- Verify report generation completed successfully.
- Verify key metrics are populated and internally consistent.
- Fail fast: stop on broken or incomplete source data and report blocker.

## Anti-patterns
- Do not fabricate trends when data is incomplete.
- Never expose sensitive data in report output.
- Do not ship a report without metric sanity checks.
- Avoid repetitive, generic commentary with no actionable signal.
- Warn on confidence limits when sample size is small.

## Variation
- Adapt granularity by request (quick pulse vs deep retrospective).
- Use different section emphasis for productivity, quality, or reliability goals.
- Customize output narrative for technical versus stakeholder audiences.

## Examples
- Generate a 7-day usage report with top workflows and blockers.
- Generate a monthly trend report with confidence notes and action items.

## Resource map
- References: `references/contract.yaml`, `references/evals.yaml`, `references/README.md`

## Quality Uplift
- Philosophy and approach: apply a clear framework, explain why, consider tradeoff decisions, and use a practical mental model for execution.
- Guiding question: Why is this the right context-specific path?
- Guiding question: What tradeoff is being made and how is risk reduced?
- Guiding question: How do we verify behavior end-to-end before completion?
- Anti-pattern warning: avoid generic or repetitive output; DO NOT hide failures; NEVER skip validation; avoid common pitfall and mistake patterns.
- Anti-pattern warning: treat incorrect or wrong assumptions as blockers, and call out anti-pattern risks explicitly.
- Variation: vary recommendations by context-specific constraints; adapt, customize, and use different approaches when constraints differ.
- Variation: prefer diverse, unique alternatives and avoid repetition or cookie-cutter template convergence.
- Empowerment: enable users to explore options confidently, be capable and creative, unlock safe choices, and empower execution.
