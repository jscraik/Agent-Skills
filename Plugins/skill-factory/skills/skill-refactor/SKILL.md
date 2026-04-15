---
name: skill-refactor
description: Scan Codex session history for skill failures, usage patterns, and coverage gaps. Use when the user wants daily skill-health monitoring or evidence-backed recommendations about installing, improving, merging, or pruning skills.
metadata:
  skill-type: data_fetch_analysis
---

# Skill Refactor

## Table of Contents
- [Overview](#overview)
- [Modes](#modes)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Scope and triggers](#scope-and-triggers)
- [Quick start](#quick-start-daily)
- [Philosophy](#philosophy)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Constraints](#constraints)
- [Reliability hardening](#reliability-hardening-from-recurring-failures)
- [Procedure](#procedure)
- [Guardrails](#guardrails-non-negotiable)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Validation](#validation)
- [Decision feedback protocol](#decision-feedback-protocol)

## Overview
This skill has two complementary modes:
- `health-scan`: daily scan over Codex sessions to catch skill paper cuts (broken paths, failing commands, stale references).
- `project-audit`: targeted audit of project-local skills plus memory/rollout evidence to recommend `merge`, `fold`, `improve-existing`, or `install-new`.

Both modes are evidence-first and privacy-aware.

## Modes
- `health-scan` (default): use for daily or incident-driven skill reliability checks.
- `project-audit`: use when the user asks what skills a project needs or how to avoid duplicate skills.

## Standards snapshot (March 2026)
- Keep the scan evidence-first, bounded, and safe for local session analysis.
- Treat personal-skill regressions, stale paths, and broken validation commands as the main output classes.
- Preserve privacy by default: summarize failures without replaying full sessions.
- Keep the workflow read-only unless the user explicitly asks for a patch follow-up.

## When to use
- “Scan yesterday’s Codex sessions for skill failures (personal skills only).”
- “Why does `$some-skill` keep failing? Look at recent session logs and tell me what’s wrong.”
- “Daily check: any broken skill references or validation commands in the last 24 hours?”
- “Audit our project skills and tell me what should be merged/folded versus installed new.”
- “Use MEMORY.md + rollout summaries to recommend which local skills to update first.”

## Quick start (daily)
Run:
```bash
cd ~/dev/agent-skills
python3 Plugins/skill-factory/skills/skill-refactor/Infrastructure/scripts/scan_codex_sessions.py --days 1 --include-otel
```

## Philosophy
- **Single-threaded:** scan → summarize → (optional) patch only the smallest diff.
- **Evidence-led:** cite the specific error snippets + point to the exact personal SKILL.md path when possible.
- **Safety-first:** redact secrets; do not copy full transcripts.

## Required inputs
- `mode`: `health-scan` or `project-audit` (default `health-scan`).
- `--days <float>`: how far back to scan (default `1`).
- `--sessions-root <path>`: where to scan (default `~/.codex/sessions`).
- `--include-dev-project-sessions` (enabled by default): also scan per-project `.codex/sessions` under `~/dev`. Use `--no-include-dev-project-sessions` to disable.
- `--max-samples-per-skill <int>`: cap snippets per skill (default `3`).
- `--include-otel`: include best-effort OTel signals (Codex OTLP endpoint listening status + repo-local OTLP-derived trace artifacts under `.narrative/trace/`).
- `--include-otel-collector`: include summary from `~/.agents/otel-collector/data/processed/stats.json`.
- `--otel-collector-stats <path>`: override collector stats path (default `~/.agents/otel-collector/data/processed/stats.json`).
- `--codex-config-toml <path>`: path to read Codex `[otel]` endpoints from (default `~/.codex/config.toml`).
- For `project-audit` mode:
  - repository root/cwd;
  - `$CODEX_HOME` (fallback `~/.codex`) memory and rollout paths;
  - local skill paths (`.agents/skills`, `.codex/skills`, `skills`).

## Deliverables
- A “daily skill health report” in Markdown (skills invoked, skills with issues, sample error snippets).
- A list of *suggested fix patterns* (no changes applied).
- For `project-audit` mode:
  - existing skill inventory;
  - suggested updates;
  - suggested new skills only when distinct;
  - ranked priority list;
  - explicit deconflict decision: `merge|fold|improve-existing|install-new`.

## Constraints
- Personal skills only: do not patch `Skills/` or `.system` skills.
- Do not auto-install dependencies or change system settings as part of scanning.
- Keep output small (snippets only); avoid dumping raw logs.
- Redact secrets/sensitive data by default; never paste tokens/keys from logs into chat or files.

## Reliability hardening (from recurring failures)
- **rg/fd preflight:** before any repo-wide search commands, run `command -v rg` and `command -v fd`. If missing, report the missing binary and stop (or use absolute paths such as `/opt/homebrew/bin/rg` and `/opt/homebrew/bin/fd` when available).
- **No direct network curl:** do not run external `curl` commands in this workflow. Use local Infrastructure/scripts/MCP tools instead.
- **TTY for interactive/streaming commands:** if a command expects stdin or may run interactively (for example auth/login flows), run it with `tty=true`; otherwise avoid `write_stdin` follow-ups.
- **Claude auth check:** when `claude_projects` emits auth failures, verify with `claude auth status` and treat `loggedIn=false` as environment/auth state, not a skill regression.

## Procedure
### A) Scan (read-only)
1) Run the scan script (Quick start).
2) If exit code is `2`, issues were found (see report).

### B) Triage (human-in-the-loop)
For each flagged skill:
1) Identify if it’s a **personal skill** (lives under `~/dev/agent-skills/` and is *not* under `Skills/`).
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
cd ~/dev/agent-skills
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py <skill-folder>
python3 Skills/skill-builder/Infrastructure/scripts/skill_gate.py <skill-folder>
```

### D) Project audit mode (read-first)
1) Read project guidance (`AGENTS.md`, `README.md`, workflow docs).
2) Resolve memory path from `$CODEX_HOME` (fallback `~/.codex`).
3) Read in order: memory summary -> 1-3 rollout summaries -> raw sessions only if needed.
4) Inventory project-local skills (`.agents/skills`, `.codex/skills`, `skills`).
5) Run full-scan deconflict across installed operational skills.
   Exclude `.system` and meta/creator scaffolding skills unless user explicitly requests them.
6) Return decision record with one of: `merge`, `fold`, `improve-existing`, `install-new`.

## Guardrails (non-negotiable)
- Personal skills only: do not patch `Skills/` or `.system` skills.
- Redact: do not paste secrets/tokens from session logs into chat, files, or issues.
- Do not auto-fix: always propose patches first; only apply after confirmation.

## Anti-patterns
- Editing skills automatically just because the scan found an issue.
- “Fixing” system skills (`Skills/`, `.system`) when the user asked for personal skills only.
- Copy/pasting full session logs into chat/issues (high risk for secrets/PII).
- Recommending new skills from themes alone without repeated workflow evidence.
- Skipping deconflict and proposing duplicate installs by default.

## Examples
- “Scan my Codex sessions from the last day and tell me if any skills are failing. Personal skills only.”
- “Why does `$product-spec` keep referencing missing files? Scan yesterday’s sessions and suggest the smallest fix.”
- “Daily scan: any broken validation commands or missing paths from the last 24 hours?”
- “Audit this project’s local skills and tell me what to fold versus install new.”
- “Use rollout summaries and session evidence to prioritize skill updates.”

## Validation
- Fail fast: stop at the first failed gate, fix it, then re-run.
- This skill’s scan script is stdlib-only; run it with `python3`.
- When changing skill files, validate with:
  - `python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/skill-factory/skills/skill-refactor`
  - `python3 Skills/skill-builder/Infrastructure/scripts/skill_gate.py Plugins/skill-factory/skills/skill-refactor`

References used by skill-gate:
- `Infrastructure/references/contract.yaml`
- `Infrastructure/references/evals.yaml`

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[insight-report]] | Turn session scan findings into a polished usage report |
| [[codex-home-audit]] | Run alongside a full home directory audit |
| [[evals-router]] | Route evaluation work for under-performing skills |

**Topic map:** [[agent-ops]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If session inputs, scan scope, or telemetry evidence cannot be read safely, stop, report the blocked source, and fall back to a smaller local-only scan instead of inferring results.
