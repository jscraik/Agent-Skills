---
name: notebooklm
description: Manage, analyze, and generate Google NotebookLM workflows for notebook/source management, notebook question answering, and audio/video overview generation. Use this skill when a user asks to run NotebookLM actions from this environment; do not use it for unrelated general web/chat requests.
---

# Notebooklm

Operate NotebookLM workflows with script-backed execution and explicit verification.

## Table of Contents
- [When to use](#when-to-use)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Failure mode](#failure-mode)
- [Philosophy](#philosophy)
- [Constraints](#constraints)
- [Procedure](#procedure)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Variation](#variation)
- [Examples](#examples)
- [Resource map](#resource-map)
- [Decision feedback protocol](#decision-feedback-protocol)

## When to use
- Use this skill for NotebookLM notebook/source management tasks.
- Use this skill for question answering against notebook content.
- Use this skill for audio/video overview generation requests.

## Standards snapshot (March 2026)
- Prefer script-backed NotebookLM operations over ad hoc browser choreography.
- Verify notebook identity and target resources before mutating actions.
- Treat auth, returned object IDs, and observable side effects as first-class validation gates.
- Report blocked or partial outcomes explicitly instead of guessing NotebookLM state.

## Inputs
- User objective and target notebook/source context.
- Required action type (list, create, add source, ask, generate media).
- Constraints on output format, latency, or safety boundaries.

## Outputs
- Completed NotebookLM action or clear blocked state.
- Evidence summary of commands executed and validation checks.
- Next action if additional user confirmation is required.

## Failure mode
If auth is stale, the target notebook/source cannot be identified, or the script result cannot be verified, stop at that blocker, report the exact failed gate, and do not fabricate a successful NotebookLM action.

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

## Decision feedback protocol
<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
