---
name: codex-sessions-skill-scan
description: "Daily skill health scan: analyze ~/.codex/sessions (default last 1 day) and summarize skill invocations + likely failures for personal skills in ~/dev/agent-skills (missing paths, tool failures). Use when you ask to scan recent Codex sessions for skill issues or when a skill keeps failing. Optional: include best-effort local OTel signals."
---

# Codex Sessions Skill Scan

## Overview
This skill runs a **daily scan** over Codex session logs to catch repeated “paper cuts” when using skills (broken file paths, missing scripts, validation commands that don’t run) and produces a short report + suggested fixes.

## Scope and triggers
- “Scan yesterday’s Codex sessions for skill failures (personal skills only).”
- “Why does `$some-skill` keep failing? Look at recent session logs and tell me what’s wrong.”
- “Daily check: any broken skill references or validation commands in the last 24 hours?”

## Quick start (daily)
Run:
```bash
cd /Users/jamiecraik/dev/agent-skills
python3 utilities/codex-sessions-skill-scan/scripts/scan_codex_sessions.py --days 1 --include-otel
```

## Philosophy
- **Single-threaded:** scan → summarize → (optional) patch only the smallest diff.
- **Evidence-led:** cite the specific error snippets + point to the exact personal SKILL.md path when possible.
- **Safety-first:** redact secrets; do not copy full transcripts.

## Required inputs
- `--days <float>`: how far back to scan (default `1`).
- `--sessions-root <path>`: where to scan (default `~/.codex/sessions`).
- `--max-samples-per-skill <int>`: cap snippets per skill (default `3`).
- `--include-otel`: include best-effort OTel signals (Codex OTLP endpoint listening status + repo-local OTLP-derived trace artifacts under `.narrative/trace/`).
- `--codex-config-toml <path>`: path to read Codex `[otel]` endpoints from (default `~/.codex/config.toml`).

## Deliverables
- A “daily skill health report” in Markdown (skills invoked, skills with issues, sample error snippets).
- A list of *suggested fix patterns* (no changes applied).

## Constraints
- Personal skills only: do not patch `skills-system/` or `.system` skills.
- Do not auto-install dependencies or change system settings as part of scanning.
- Keep output small (snippets only); avoid dumping raw logs.
- Redact secrets/sensitive data by default; never paste tokens/keys from logs into chat or files.

## Procedure
### A) Scan (read-only)
1) Run the scan script (Quick start).
2) If exit code is `2`, issues were found (see report).

### B) Triage (human-in-the-loop)
For each flagged skill:
1) Identify if it’s a **personal skill** (lives under `~/dev/agent-skills/` and is *not* under `skills-system/`).
2) Confirm whether the failure is:
   - wrong file path in a SKILL.md reference
   - wrong interpreter for validation scripts (PyYAML required)
   - `~` not expanding (needs absolute path)
   - missing/moved file in the repo

### C) Patch (optional; requires explicit user request)
If the user asks to apply fixes:
1) Make the smallest possible edits to the referenced personal skill files.
2) Re-run skill gates (fail fast on first failure):
```bash
cd /Users/jamiecraik/dev/agent-skills
~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/quick_validate.py <skill-folder>
~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/skill_gate.py <skill-folder>
```

## Guardrails (non-negotiable)
- Personal skills only: do not patch `skills-system/` or `.system` skills.
- Redact: do not paste secrets/tokens from session logs into chat, files, or issues.
- Do not auto-fix: always propose patches first; only apply after confirmation.

## Anti-patterns
- Editing skills automatically just because the scan found an issue.
- “Fixing” system skills (`skills-system/`, `.system`) when the user asked for personal skills only.
- Copy/pasting full session logs into chat/issues (high risk for secrets/PII).

## Examples
- “Scan my Codex sessions from the last day and tell me if any skills are failing. Personal skills only.”
- “Why does `$product-spec` keep referencing missing files? Scan yesterday’s sessions and suggest the smallest fix.”
- “Daily scan: any broken validation commands or missing paths from the last 24 hours?”

## Validation
- Fail fast: stop at the first failed gate, fix it, then re-run.
- This skill’s scan script is stdlib-only; run it with `python3`.
- When changing skill files, validate with:
  - `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/quick_validate.py utilities/codex-sessions-skill-scan`
  - `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/skill_gate.py utilities/codex-sessions-skill-scan`

References used by skill-gate:
- `references/contract.yaml`
- `references/evals.yaml`
