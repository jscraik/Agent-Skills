---
name: agents-md
description: "Refactor or create AGENTS.md using progressive disclosure: keep root guidance minimal, split detailed instructions into linked docs, and flag contradictions or redundancy. Use this skill when the user asks to create, update, or refactor AGENTS.md."
---

# Agents Md

Create and maintain concise, high-signal AGENTS guidance with progressive disclosure.

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
- [Shared guidance propagation](#shared-guidance-propagation)
- [Anti-patterns](#anti-patterns)
- [Variation](#variation)
- [Mandatory workflow snippet](#mandatory-workflow-snippet)
- [Examples](#examples)
- [Resource map](#resource-map)
- [Decision feedback protocol](#decision-quality-feedback)

## When to use
- Use this skill when the user asks to create or update `AGENTS.md`.
- Use this skill when AGENTS docs are too large, duplicated, or contradictory.
- Use this skill when instruction routing needs to be split into linked files.

## Standards snapshot (March 2026)
- Keep root `AGENTS.md` minimal and route depth into linked docs.
- Base commands, paths, and conventions on verified repo evidence only.
- Treat contradiction detection and instruction precedence as first-class outputs.
- Prefer progressive disclosure over megadoc accumulation.

## Inputs
- Target repository root path.
- Existing `AGENTS.md` and related instruction docs.
- Verified commands/paths from repository sources.
- Preferred instruction tree (`instructions/agents` or `docs/agents`) based on repo convention.

## Outputs
- Updated minimal root `AGENTS.md`.
- Linked category docs for deeper instructions.
- Contradiction list and deletion candidates.
- Evidence-backed command map and validation notes.

## Failure mode
If command truth, path ownership, or instruction precedence cannot be verified, stop at that contradiction, state the conflict clearly, and request a decision instead of writing speculative AGENTS guidance.

## Philosophy
- Prefer concise, verifiable guidance over comprehensive prose.
- Keep root AGENTS as an operator map, with depth in linked docs.
- Optimize for reader success in under two minutes.
- Why keep this instruction in root instead of a linked doc?
- What evidence confirms this command/path is real?
- Which tradeoff is best here: brevity or explicitness?

## Constraints
- Redact secrets, tokens, credentials, and PII by default.
- Do not invent commands, scripts, or paths.
- Keep ASCII by default unless repository conventions require otherwise.
- Avoid adding dependencies, legacy shims, or compatibility layers unless explicitly requested.

## Procedure
1. Discover repo facts and instruction hierarchy.
2. Detect command/style conventions from actual repo evidence.
3. Identify contradictions and duplicate guidance.
4. Write minimal root AGENTS and link deeper docs.
5. Add table of contents for generated docs.
6. Validate links, commands, and instruction consistency.

## Validation
- Confirm commands exist in repo scripts/docs.
- Confirm file paths exist and links resolve.
- Confirm no contradictory instructions remain unresolved.
- Fail fast: stop at first critical contradiction and request decision.

## Shared guidance propagation
- When a user asks to add guidance under named AGENTS sections, place it in the canonical AGENTS file for that repo scope and update that file's Table of Contents.
- If the named section does not exist, create it with concise, action-oriented bullets instead of scattering equivalent guidance across multiple unrelated files.
- Keep cross-repo guidance consistent by mirroring durable section-level rules in this skill when they affect how AGENTS refactors should be performed.
- For section-level additions touching operational safety, preserve explicit checks for:
  - quality validation after config/CI/dependency edits,
  - external tool authentication readiness (including 1Password/env cache checks),
  - git-history risk escalation before complex rebase/conflict workflows,
  - tool/skill existence verification before fallback assumptions,
  - exact path verification against documented locations before commit.
- When external integration guidance is requested, preserve a strict preflight order:
  1. env vars resolved,
  2. `op account list` succeeds,
  3. simple MCP/API connectivity check,
  4. then full operations.
  If auth fails, require auth-layer debugging before operation retries.
- When git safety guidance is requested, require explicit pre-operation briefing for rebasing 5+ commits, merge conflict resolution, and force-pushes, including branch state, strategy with risks, alternatives, and user confirmation.
- When validation guidance is requested for config-sensitive files (for example `package.json`, CI workflows, `settings.json`, config files), require running applicable validation commands and reporting pass status before commit.
- When command preflight guidance is requested, preserve explicit `exec_command` preflight rules: run shell via `zsh -lc`, use `which` before `mise` installs, and verify destructive-operation paths with `fd` before execution.
- When policy guidance is requested, include sandbox tuning rules that review rejected patterns, whitelist safe frequent commands, and keep strict controls for destructive operations.
- When MCP workflow guidance is requested, require `codex mcp list` before implementation and require fixing missing server setup first.
- When delivery workflow guidance is requested, require separate implementation and verification `codex exec` workflows, and require `codex review --uncommitted` before merge.

## Anti-patterns
- Do not dump full policy documents into root AGENTS.
- Never duplicate the same instruction across many files without need.
- Do not keep vague guidance that cannot be executed.
- Avoid repetitive, generic, cookie-cutter templates that ignore repo context.
- Warn on conflicting package manager instructions and unresolved hierarchy conflicts.

## Variation
- Adapt structure for small repos versus multi-package monorepos.
- Use different category splits based on repo domains (frontend, backend, ops, docs).
- Customize guidance depth to team maturity and operational risk.

## Mandatory workflow snippet
1. Explore project first, then invoke skill.
2. IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any React, Tauri, Apps-SDK-ui, Tailwind, Vite, Storybook + Chat Widget tasks.
3. Add a Table of Contents for docs.

## Examples
- Refactor an overloaded AGENTS file into root plus `instructions/agents/*` docs.
- Merge AGENTS/CLAUDE/GEMINI shared rules to canonical AGENTS links.
- Audit contradictions and return an explicit conflict-decision list.

## Resource map
- References: `references/contract.yaml`, `references/evals.yaml`, `references/folded-legacy-modes-core60.md`, `references/task-profile.json`

<!-- decision-feedback-protocol:v2 -->
## Decision Quality Feedback
- If post-run feedback capture is enabled, emit non-blocking `post_run_feedback` after result delivery.
- Capture `decision`, `outcome`, and `confidence`.
- Persist with `python3 utilities/skill-builder/scripts/record_skill_feedback.py`.
<!-- /decision-feedback-protocol -->
