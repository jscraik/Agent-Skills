---
name: agents-md
description: Create or update a repository-level AGENTS.md contributor guide with clear sections, commands, and repo-specific conventions. Use when asked to draft, improve, or standardize AGENTS.md files or when a repo needs concise contributor instructions.
metadata:
  version: "1.0.0"
  last_updated: "2026-01-15"
---

# Agents Md

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Philosophy

Prefer concise, verifiable instructions over comprehensive prose. Every command and path must be real and sourced from the repo. Treat AGENTS.md as an operator checklist: short, direct, and actionable.

Guiding principles:
- Optimize for reader success in under 2 minutes.
- Favor deterministic steps over narrative.
- Keep scope tight; expand only when the repo requires it.

## When to use

- The user asks to create or update AGENTS.md.
- The repo needs a short contributor guide for agents or humans.
- The user requests “Repository Guidelines” content under 400 words.

## Inputs

- Target repo root path.
- Existing AGENTS.md content (if present).
- Verified commands and paths from the repo (README, docs, config files).

## Outputs

- A single Markdown file named `AGENTS.md` titled `Repository Guidelines`.
- Include `schema_version: 1` as the first line of the output file.
- 200–400 words, with short sections and concrete examples.

## Constraints

- Do not invent commands, scripts, or paths.
- Redact secrets and sensitive data by default.
- Use ASCII only unless the repo already uses non-ASCII.
- Keep the document between 200 and 400 words.
- Do not add dependencies or tools.

## Workflow

1) Discover repo facts
- Read README and `docs/` for real commands and structure.
- Inspect config files (for example `pyproject.toml`, package scripts).
- If commit conventions are not visible, state “not observed.”
- Read global instructions from `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md` if present.
- Also check `~/.codex/instructions/` for applicable global standards and guidance.
- Then read project instructions from repo root down to the working directory and treat them as canonical.

2) Draft AGENTS.md
- Title must be `# Repository Guidelines`.
- Use clear headings; include required sections below.
- Include examples for commands and paths.

3) Validate content
- Confirm commands exist and are runnable.
- Confirm naming conventions match the codebase.
- Ensure no secrets or private endpoints appear.

## Required sections

- Project Structure & Module Organization
- Build, Test, and Development Commands
- Coding Style & Naming Conventions
- Testing Guidelines
- Commit & Pull Request Guidelines
- Working With Project Instructions
  - Include global scope (`~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md`) then project scope.
  - Include per-directory discovery order: `AGENTS.override.md`, `AGENTS.md`, then `project_doc_fallback_filenames`.
  - Mention `project_doc_max_bytes` is a byte cap (32 KiB default), not a token window.
  - Note `CODEX_HOME` for profile overrides.
  - Add a short troubleshooting list (empty files ignored, wrong overrides, truncation).
- ExecPlans (state requirement for complex features/significant refactors)
- Philosophy (include the “codebase will outlive you” guidance)
- Optional: Security & Configuration Tips (only if relevant)

## Variation

- Vary examples and commands to match the target repo’s stack (Python vs Node vs Swift).
- Use repo-specific paths and filenames; avoid repeating generic defaults across repos.

## Empowerment

- Offer two to three clear next-step options after drafting (accept, revise, or add missing info).
- Call out unknowns explicitly and ask for confirmation before finalizing.
- Encourage the user to prioritize sections when the scope is broad.
- Empower the user to choose between a minimal or detailed guideline set.

## Validation

- Fail fast: stop at the first failed validation gate, fix it, then re-run.
- Run `python scripts/quick_validate.py <skill>` if available.
- Run `python scripts/skill_gate.py <skill>` and fix any missing sections.
- If needed, consult `references/contract.yaml` and `references/evals.yaml`.

## Anti-patterns

- Generic boilerplate that ignores repo specifics.
- Fabricated commands or paths.
- Exceeding the 200–400 word limit.
- Omitting PR/commit guidance when the user asked for it.
- Burying risks or assumptions in long prose.
- Using vague headings like “Misc” or “Notes.”
- Presenting unverified commands as facts.
- Mixing unrelated policies into the same section.

## Example prompts that should trigger this skill

- "Draft an AGENTS.md for this repo."
- "Create a Repository Guidelines AGENTS.md under 400 words."
- "Standardize our AGENTS.md using actual repo commands."
