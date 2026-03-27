---
name: notebooklm
description: Run NotebookLM workflows for notebook management, question answering, and audio or video overviews. Use when the user wants NotebookLM actions from this environment, not general browsing or note writing.
metadata:
  skill-type: data_fetch_analysis

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
- Always use the `scripts/run.py` wrapper so the local `.venv` and Python dependencies are bootstrapped before execution.
- Verify notebook identity and target resources before mutating actions.
- Treat auth, returned object IDs, and observable side effects as first-class validation gates.
- Distinguish "stored auth metadata exists" from "this exact notebook URL was verified in the current run".
- Report blocked or partial outcomes explicitly instead of guessing NotebookLM state.

## Required inputs
- User objective and target notebook/source context.
- Required action type (list, create, add source, ask, generate media).
- Constraints on output format, latency, or safety boundaries.

## Deliverables
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
- Do not treat cached auth files, cookies, or a past login timestamp as proof that a target notebook is currently accessible.

## Procedure
1. Confirm the requested NotebookLM operation and the target notebook context.
2. If the user provides a notebook URL, extract the notebook identifier and verify whether it exists in the local library or will be accessed directly by URL.
3. Check auth state and library state separately:
   - auth state (`auth_info.json`, browser state, wrapper status);
   - notebook registration state (`data/library.json`, active notebook, cached source summaries).
4. Run NotebookLM scripts through the wrapper only:
   ```bash
   python3 scripts/run.py <script>.py ...
   ```
5. Capture outputs and verify success conditions using returned IDs, notebook identity, and observable side effects.
6. If the notebook is auth-gated or cannot be matched to the requested notebook, stop and report a blocked/partial outcome instead of guessing.
7. Summarize result, residual risks, and next step.

## Validation
- Verify script exit status and expected NotebookLM effect.
- Verify returned IDs/objects match requested target notebook/source.
- Verify wrapper-backed execution was used for live operations; direct script execution is only acceptable for static inspection such as `--help` checks when no imports fail.
- Verify notebook identity separately from auth state; a stored auth timestamp or local browser metadata is not enough.
- Fail fast: stop at first failed gate and report exact blocker.

## Anti-patterns
- Do not bypass validation after script execution.
- Never fabricate NotebookLM state when verification fails.
- Do not mix unrelated repo tasks into this workflow.
- Avoid repetitive, generic responses when operation context differs.
- Warn on common pitfalls such as stale auth and missing notebook IDs.
- Do not claim a specific NotebookLM URL was verified when the local library is empty or the current run never matched the returned notebook ID to that URL.
- Do not instruct users to run scripts directly when the wrapper is required to provision `patchright`, browser binaries, and the local `.venv`.

## Variation
- Adapt workflow by operation type: query, source management, or media generation.
- Use different verification depth for read-only versus mutating actions.
- Customize response detail for quick status checks versus deep audits.

## Examples
- List notebooks, then add a source to a selected notebook.
- Ask a notebook question and return concise answer plus provenance pointers.
- Generate an audio overview and verify output artifact metadata.

## Resource map
- Scripts:
  - `scripts/run.py` - wrapper that bootstraps `.venv`, dependencies, and browser tooling
  - `scripts/auth_manager.py` - auth setup/status/reauth/clear
  - `scripts/notebook_manager.py` - notebook library CRUD, activation, source summary refresh
  - `scripts/ask_question.py` - question answering against NotebookLM notebooks
  - `scripts/add_source.py`, `scripts/list_sources.py`, `scripts/remove_source.py` - source management
  - `scripts/audio_generator.py`, `scripts/video_generator.py` - media overview generation
  - `scripts/auto_sync.py` - incremental local-folder sync to a notebook
  - `scripts/setup_environment.py`, `scripts/cleanup_manager.py`, `scripts/source_filter.py`, `scripts/source_extractor.py` - environment and support utilities
- References: `references/contract.yaml`, `references/evals.yaml`, `references/api_reference.md`, `references/troubleshooting.md`

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[video-transcript-downloader]] | Download transcripts to feed as NotebookLM sources |
| [[markdown-converter]] | Convert docs to markdown before uploading to NotebookLM |
| [[insight-report]] | Feed session insights into NotebookLM for deeper analysis |
| [[compound-engineering-router]] | Use NotebookLM evidence to inform compound workflow routing |

**Topic map:** [[product-strategy]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
