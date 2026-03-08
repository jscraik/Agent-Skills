---
name: notebooklm
description: Manage, analyze, and generate Google NotebookLM workflows for notebook/source management, notebook question answering, and audio/video overview generation. Use this skill when a user asks to run NotebookLM actions from this environment; do not use it for unrelated general web/chat requests.
---

# Notebooklm

Operate NotebookLM workflows with script-backed execution and explicit verification.

## When to use
- Use this skill for NotebookLM notebook/source management tasks.
- Use this skill for question answering against notebook content.
- Use this skill for audio/video overview generation requests.

## Inputs
- User objective and target notebook/source context.
- Required action type (list, create, add source, ask, generate media).
- Constraints on output format, latency, or safety boundaries.

## Outputs
- Completed NotebookLM action or clear blocked state.
- Evidence summary of commands executed and validation checks.
- Next action if additional user confirmation is required.

## Philosophy
- Prefer deterministic script execution over ad hoc browser actions.
- Keep scope narrow and reversible where possible.
- What is the smallest safe action that completes the request?
- What evidence proves completion?
- Which tradeoff matters here: speed, completeness, or traceability?

## Constraints
- Redact secrets, tokens, credentials, and sensitive source content by default.
- Do not run unrelated automation outside NotebookLM scope.
- Stop and report blockers when auth or required context is missing.

## Procedure
1. Confirm requested NotebookLM operation and target notebook context.
2. Use scripts in `scripts/` for the selected workflow.
3. Capture outputs and verify success conditions.
4. Summarize result, residual risks, and next step.

## Validation
- Verify script exit status and expected NotebookLM effect.
- Verify returned IDs/objects match requested target notebook/source.
- Fail fast: stop at first failed gate and report exact blocker.

## Anti-patterns
- Do not bypass validation after script execution.
- Never fabricate NotebookLM state when verification fails.
- Do not mix unrelated repo tasks into this workflow.
- Avoid repetitive, generic responses when operation context differs.
- Warn on common pitfalls such as stale auth and missing notebook IDs.

## Variation
- Adapt workflow by operation type: query, source management, or media generation.
- Use different verification depth for read-only versus mutating actions.
- Customize response detail for quick status checks versus deep audits.

## Examples
- List notebooks, then add a source to a selected notebook.
- Ask a notebook question and return concise answer plus provenance pointers.
- Generate an audio overview and verify output artifact metadata.

## Resource map
- Scripts: `scripts/run.py`, `scripts/ask_question.py`, `scripts/add_source.py`, `scripts/video_generator.py`
- References: `references/contract.yaml`, `references/evals.yaml`, `references/api_reference.md`, `references/troubleshooting.md`

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
