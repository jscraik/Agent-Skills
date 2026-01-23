# Claude AI Governance

This repository contains governance rules for Claude Code and other AI assistants working in this codebase.
---

# AI Assistance Governance (Model A)

This project follows **Model A** AI artifact governance: prompts and session logs are committed artifacts in the repository.

## When creating PRs with AI assistance

Claude must:

1. **Save artifacts to `artifacts/ai/` directory**:
   - Final prompt → `artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml`
   - Session summary → `artifacts/ai/sessions/YYYY-MM-DD-<slug>.json`

2. **Commit both files in the PR branch**:
   ```bash
   git add artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml artifacts/ai/sessions/YYYY-MM-DD-<slug>.json
   ```

3. **Reference exact paths in PR body**:
   - Under **AI assistance** section:
     - Prompt: `artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml`
     - Session: `artifacts/ai/sessions/YYYY-MM-DD-<slug>.json`
   - In **AI Session Log** details:
     - Log file: `artifacts/ai/sessions/YYYY-MM-DD-<slug>.json`
     - Prompt file: `artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml`

4. **Do NOT**:
   - Embed prompt/log excerpts in the PR body
   - Link to external logs or pastebins
   - Skip creating artifacts when AI assistance is acknowledged

5. **Abort** if artifacts cannot be created and committed.

## Artifact Templates

See `artifacts/ai/prompts/.template.yaml` and `artifacts/ai/sessions/.template.json` for required fields.

## PR Template

All PRs must use `.github/PULL_REQUEST_TEMPLATE.md` which includes required AI disclosure sections.
