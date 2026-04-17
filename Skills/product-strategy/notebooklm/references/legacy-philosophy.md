# Legacy Philosophy and Constraints

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
   python3 Infrastructure/scripts/run.py <script>.py ...
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

