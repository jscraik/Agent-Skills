# Shared Guidance Propagation

Reference: per-section placement rules for adding or aligning guidance across `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`.

**Read when:** the user asks to update a specific section across tool instruction files, add a new cross-tool policy, or align divergent instruction surfaces.

## Table of Contents
- [General propagation defaults](#general-propagation-defaults)
- [Command preflight defaults](#command-preflight-defaults)
- [Policy calibration defaults](#policy-calibration-defaults)
- [Completion requirements](#completion-requirements)

---

## General propagation defaults
- When a user asks to add guidance under named AGENTS sections, place it in the canonical AGENTS file for that repo scope and update that file's Table of Contents.
- If the named section does not exist, create it with concise, action-oriented bullets instead of scattering equivalent guidance across multiple unrelated files.
- Keep cross-repo guidance consistent by mirroring durable section-level rules in this skill when they affect how AGENTS refactors should be performed.
- When users request a reusable Python runtime policy, auto-populate `## Python Environment and Dependency Management` when missing in the target AGENTS scope and keep it as a root-visible operating section.
- For that Python section, preserve these defaults unless the repo explicitly overrides them: `uv`-only environment/dependency management, Python `3.12` default for new environments, explicit dependency declaration files (`pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `requirements.lock`), project-local `.venv` preference, activation-before-execution, and global fallback via `source ~/personal/bin/activate` only when no dependency files exist.
- When users request preflight enforcement defaults, auto-populate both the mandatory workflow snippet (`PREFLIGHT REQUIRED` + explore-then-skill + retrieval-led rule + docs TOC rule) and a `## Preflight Enforcement (REQUIRED)` section when missing, while still validating that prescribed commands/flags exist for that repo before insertion.
- When users request stronger coding standards, auto-populate a `## Quality Checks` section (or strengthen it in place) across in-scope instruction files and require repo-native formatter, linter, typecheck, and test commands plus explicit pass-state reporting before work is marked complete.
- When a user wants the same operating rule reflected across `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, keep the rule semantically consistent across all three files but preserve target-specific wording and file structure instead of forcing one identical block everywhere.
- For durable cross-tool behavioral rules that the user wants agents to always see, keep the rule as its own top-level section in each of `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` instead of hiding it only in linked docs.
- Use progressive disclosure, not rule burial: keep the short, operative rule in the root instruction file and move only deeper rationale or procedure into linked docs when needed.
- When `agents-md` is asked to update a project's instruction surface, treat the task as an audit-and-repair pass by default: inspect which instruction files should exist for that repo, verify the current files are accurate and current, create or repair missing canonical files when needed, and disclose any intentional omissions or legacy files explicitly.
- By default, verify the active shared instruction set for all supported surfaces the repo actually uses, such as `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, instead of updating only one file in isolation unless the user explicitly asks for a narrower scope.
- When one instruction file is current but its sibling surface is missing, stale, or materially weaker, either align that sibling file in the same pass or report the exact reason it was left untouched.
- When `agents-md` updates shared operational guidance across `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, include a policy-calibration section by default unless the repo already has an equivalent section covering approvals, trusted prefixes, destructive-command gating, and rejection-trend review.
- When a repo uses `CLAUDE.md`, prefer Anthropic's official style guidance: concise, specific, verifiable instructions, structured headings, and stronger wording over duplicate bullets when a weaker rule already exists.
- When a repo uses `GEMINI.md`, preserve Gemini CLI's configured context-file behavior and avoid assuming the filename is always the default when the repo or tool config sets `context.fileName` differently.
- When users request cross-tool additions for `Error Handling Protocol` or `Reporting & Insights`, place them near the top of each instruction file because they govern common report-generation and failure-recovery behavior.
- When users request cross-tool additions under `Communication`, `Efficiency`, or `Browser/Playwright`, create those sections when missing and keep each rule short enough to remain a fast-start instruction rather than a hidden policy block.
- In `Communication`, if the user explicitly states the root cause, require agents to confirm that understanding and proceed instead of continuing to suggest alternative fixes.
- In `Efficiency`, require a pause before multi-file edits or automation for simple information requests and explicitly ask whether a direct answer or simple command would suffice.
- In `Browser/Playwright`, require starting `python3 -m http.server` in the relevant directory as the default fallback when browser tooling cannot open local files directly.
- For validation follow-up guidance in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, place the rule under `## Startup workflow`, `## Validation`, or the nearest validation-results section. Require that if validation surfaces durable repo work, agents create or update a Linear issue in the named `[[ project ]]` instead of leaving the finding only in chat. If equivalent wording already exists, strengthen it instead of duplicating it.
- For TypeScript validation guidance in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, place repo-native test and lint instructions under `## Quality Checks`. If that section does not exist, create it. In npm-based repos, require `npm run lint` and `npm run test` after TypeScript changes and require both to pass before the session is marked complete. If equivalent guidance already exists, strengthen it instead of duplicating it.
- For CI guidance in `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`, place the rule under `## CI/CD Workflow` when present or create that section when it is missing. Require confirmation of the final authoritative pipeline or workflow-run status before ending CI/CD work, not just a local fix or partial rerun.
- For pull-request coordination guidance in `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`, place the rule under `## GitHub Workflow` or `## PR Management`. Require checking merge-conflict state up front for multi-repo PR work, flagging blocked PRs early, and calling out blockers before spending effort on downstream merge prep.
- For worktree reliability guidance in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, if the repo ships a helper such as `scripts/prepare-worktree.sh`, add a consistent rule under startup/preflight sections: run that helper before first push from a fresh worktree so pre-push hooks execute with dependencies installed. Verify the script path exists before adding the rule.
- When repo operating rules are requested, tailor sections like `Repository rules`, `Stack detection`, `Required tooling`, `Required repo paths`, `Local Memory policy`, `Startup workflow`, and `Supplemental context` from verified repo evidence instead of copying a fixed block unchanged.
- For section-level additions touching operational safety, preserve explicit checks for:
  - quality validation after config/CI/dependency edits,
  - external tool authentication readiness (including 1Password/env cache checks),
  - git-history risk escalation before complex rebase/conflict workflows,
  - tool/skill existence verification before fallback assumptions,
  - exact path verification against documented locations before commit.
- When preflight guidance is requested, prefer `./scripts/codex-preflight.sh --stack auto --mode required` only if the repo really ships that script and supports its documented flags. Preserve supported overrides like `--repo-fragment`, `--bins`, and `--paths` only when they are part of the repo's actual script.
- When stack detection guidance is requested, derive it from root manifests such as `package.json`, `pyproject.toml`, and `Cargo.toml`, and mention override flags only when the repo's scripts or docs support them.
- When required path guidance is requested, mention `docs/` and `docs/plans/` only if they are present or explicitly standardized by the repo.
- When architecture-context guidance is requested, treat the repo's documented architecture-diagram surface as valuable quick-start context when it exists, because diagrams often help agents form a correct system model faster than prose alone.
- Never silently normalize between diagram-path variants such as `.diagram/`, `.diagrams/`, or `AI/diagrams/`. Verify the repo's documented path first and then use that exact location consistently in AGENTS guidance.
- When project learnings guidance is requested, require `.harness/memory/LEARNINGS.md` only for repos that explicitly adopt the harness-memory convention. Otherwise, treat it as `not observed` rather than promoting it into a universal required path.
- When a repo uses legacy guidance files like `FORJAMIE.md`, do not present them as canonical by default. Either migrate durable guidance into `AGENTS.md`, register the file through `project_doc_fallback_filenames`, or mention it only as supplemental context when the file actually exists.
- When external integration guidance is requested, preserve a strict preflight order:
  1. env vars resolved,
  2. `op account list` succeeds,
  3. simple MCP/API connectivity check,
  4. then full operations.
  If auth fails, require auth-layer debugging before operation retries.
- When Local Memory guidance is requested, preserve the script's explicit mode handling (`off`, `optional`, `required`) and required-mode checks for installation, daemon health, config path resolution (`LOCAL_MEMORY_CONFIG_PATH` or `~/.local-memory/config.yaml`), `host: 127.0.0.1`, `auto_port: false`, numeric `rest_api_port`, REST health, smoke cycle (`observe`, `relate`, `search`), malformed payload rejection, duplicate-observe snapshot capture, daemon-log migration signal check when available, and stop-on-failure behavior in required mode.
- When git safety guidance is requested, require explicit pre-operation briefing for rebasing 5+ commits, merge conflict resolution, and force-pushes, including branch state, strategy with risks, alternatives, and user confirmation.
- When validation guidance is requested for config-sensitive files (for example `package.json`, CI workflows, `settings.json`, config files), require running applicable validation commands and reporting pass status before commit.
- When config-edit guidance is requested for `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` progressive-build instructions, require copy-paste-safe single-line commands, then require anchored verification checks (`rg -n '^\s*<key>\s*=' <file>` plus a bounded line preview like `nl -ba <file> | sed -n '1,16p'`) before proceeding. For root Codex policy defaults, prefer string form such as `approval_policy = "on-request"` unless that repo has verified table-style policy support in its current runtime and validators.
- When command preflight guidance is requested, preserve explicit `exec_command` preflight rules: run shell via `zsh -lc`, use `which` before `mise` installs, and verify destructive-operation paths with `fd` before execution.

---

## Command preflight defaults
- By default, express shared command-reliability guidance under `## Command Preflight`, `## Path Contract`, or another repo-native operational heading in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` when those files carry execution guidance. Keep the rule concise and operator-facing:
  - confirm cwd and repo root before path-sensitive work,
  - confirm required binaries with `command -v`,
  - confirm targets with `test -e`, `fd`, or `rg --files` before acting,
  - prefer dry-run or check modes before destructive changes,
  - and prefer absolute file references in generated command chains.
- When writing that preflight block, keep runtime metrics out of committed instruction text. Fetch failure-rate or path-miss signals at runtime from dashboards, logs, or a non-versioned metrics snapshot instead of committing live counts into `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or this skill file.
- If an instruction example needs a number for illustration, label it explicitly as an example rather than a live value.
- When path-sensitive workflow guidance is requested, require a path-contract guardrail that prints or resolves the repo root first, uses discovery before edits or deletions, validates every critical path explicitly, and avoids relative-path guesswork in generated commands.

---

## Policy calibration defaults
- When `agents-md` updates shared operational guidance across `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, include a policy-calibration section by default unless the repo already has an equivalent section covering approvals, trusted prefixes, destructive-command gating, and rejection-trend review.
- When policy guidance is requested, include sandbox tuning rules that review rejected patterns, whitelist safe frequent commands, and keep strict controls for destructive operations.
- By default, express the shared policy-calibration rule under `## Policy`, `## Sandbox`, `## Approvals`, or another repo-native governance heading in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` using target-native wording but the same operating rule:
  - record the current rejection signal for the latest review window,
  - keep baseline `approval_policy = "on-request"` unless the user explicitly wants a different default,
  - add trusted command prefixes only for repeated, demonstrably safe patterns,
  - keep destructive command families explicitly gated,
  - and require re-checking the rejection trend in the next reporting window before broadening policy further.
- When writing that policy-calibration block, prefer concise operator language such as `## Policy Calibration (Dynamic)` with short bullets instead of prose paragraphs.
- Keep live rejection counts out of committed instruction files. Reference runtime telemetry, dashboards, logs, or a non-versioned metrics snapshot instead, and label any in-text numbers as illustrative examples when they are not fetched live.
- Only omit that section when:
  - the repo already contains a materially equivalent policy-calibration section, or
  - the user explicitly asks to exclude approval/sandbox governance from the generated instruction files.

---

## Completion requirements
- When MCP workflow guidance is requested, require `codex mcp list` before implementation and require fixing missing server setup first.
- When delivery workflow guidance is requested, require separate implementation and verification `codex exec` workflows, and require `codex review --uncommitted` before merge.
- When startup workflow guidance is requested, preserve the operator sequence: read `AGENTS.md` and task-relevant docs, run the required preflight, summarize repo structure and blockers before editing, make the smallest change that satisfies the task, and run the narrowest validation that proves the change works.
- When supplemental context guidance is requested, mention organization-level `instructions/Learning.md` or `instructions/Learnings.md` only if those files exist and the repo wants them as extra context. Keep them supplemental, not a replacement for repo-local instructions.
- When finishing an instruction-surface update, return a concise coverage summary that says which files are canonical, which linked docs were updated, which expected files were missing and created, which files were already current, and which legacy files remain for migration or deletion.
