# Agent Skills Index

Canonical skills live in categorized folders below.

Runtime projection is mode-dependent:
- `flat`: selected allowlisted skills are projected directly.
- `rooted`: only root skill sets are projected; latent modules route through `.skillsets/**` manifests.
- `hybrid`: deferred until a named consumer and budget gate exist.

Do not hand-edit runtime projections.

## Table of Contents
- [Summary](#summary)
- [Catalog](#catalog)
- [Skills — Agent Ops](#skills-agent-ops)
- [Skills System](#skills-system)

## Summary
- `total_skills`: 26
- `catalog_source`: default user-visible catalog surface
- `visibility`: default
- `policy_identity`: 8a1c61840a1a02bf

## Catalog

## Skills — Agent Ops

- `agents-md` — Use when reviewing, creating, shrinking, or refactoring AGENTS.md agent instructions, agent config files, routing rules, or repository guidance that need scoped routing, dedupe, contradiction fixes, progressive disclosure, and cleaned instruction surfaces.
- `autofix` — Apply approved fixes for unresolved CodeRabbit review comments, Codex P1-P3 findings, PR feedback, and code review issues with validation evidence. Use when asked to address review comments, fix review findings, clear unresolved comments, or autofix PR feedback.
- `autoresearch` — Run bounded automated experiment iterations by recording baselines, applying hypothesis patches, comparing metrics, protecting regression guards, and deciding keep, discard, rollback, or block. Use when $autoresearch is named or a repo/skill needs evidence-backed research, metric tracking, or safe optimisation loops.
- `bootstrap` — Create, diagnose, and validate a local dev bootstrap. Use when the user asks to clone a repo, install toolchains, install dependencies, and prove the project runs.
- `code-fixes-triage` — Turn Slack #code-fixes, CodeRabbit, Codex Review, CI, and check-status noise into a repo-and-PR action queue. Use when Jamie asks for a daily code-fixes digest, recent review-noise triage, or what needs fixing across active engineering repos.
- `codex-agent-creator` — Create, validate, install, fold, or troubleshoot Codex subagent role TOML, agents-table config, discoverability wiring, and duplicate-role merges. Use when a user asks for a Codex agent role, reviewer agent, role config, TOML role file, subagent setup, or overlapping agents to merge.
- `codex-automation-architect` — Use when designing, reviewing, or updating Codex app automations, cron jobs, scheduled tasks, recurring runs, or heartbeat follow-ups.
- `codex-hooks-builder` — Scaffold hook packs, validate hooks.json schema, verify hook script permissions, migrate hook configuration, and troubleshoot Codex hook execution errors. Use when creating, auditing, upgrading, or validating Codex hook packs, hooks.json files, hook scripts, SubagentStart/SubagentStop lifecycle hooks, PreToolUse/PostToolUse/PreCompact hooks, Stop claim checks, or repo-local/user-level .codex hook installs.
- `codex-review` — Review local dirty changes, committed branches, and PR diffs with Codex CLI; report findings, validation, blockers, and merge-readiness evidence. Use when the user asks for Codex review, autoreview, independent model review, or pre-ship validation.
- `coding-harness` — Use when users need to install, bootstrap, upgrade, audit, diagnose, or explain @brainwav/coding-harness in a repository, including harness init/upgrade, CI migration, governance gates, command discovery, and Codex environment action sync.
- `context7` — Analyze current external library or API docs with Context7 when dependency behavior, version-sensitive references, or ctx7 CLI setup/install guidance is needed.
- `docs-expert` — Audit, rewrite, and validate README, runbook, code-doc, config-doc, and public trust-surface documentation by checking stale instructions, command examples, dependency claims, file paths, configs, workflows, and code references against live repository evidence. Use when documentation needs proof-backed correction or reader-focused validation.
- `fix-mise` — Diagnose, fix, and validate mise runtime failures. Use when commands fail from mise config, missing runtimes, stale pins, trust prompts, or shell activation drift.
- `improve-codebase-architecture` — Use when reviewing or improving codebase architecture needs deeper module boundaries, clearer context language, better interfaces, stronger testability, or Linear-backed decisions.
- `keep-codex-fast` — Diagnose Codex Desktop or CLI local-state bloat and safe recovery options. Use when sessions, archived history, logs, worktrees, or stale Codex config may be making Codex feel slow.
- `npm-release` — Create, review, and validate npm release workflows. Use when preparing or publishing npm packages, release channels, dist-tags, provenance, or 2FA-protected publishes.
- `pnpm-manager` — Run, plan, and validate pnpm workspace operations. Use when a user needs pnpm monorepo installs, tests, builds, filters, changed-package selection, or publish routing.
- `project-brain` — Create, validate, and repair Project Brain .harness memory files when setting up Project Brain, saving repo learnings, recording decisions, or preserving quality rules.
- `simplify` — Review changed code for behavior-preserving simplification by removing dead code, eliminating duplication, extracting shared helpers, improving names, and tightening tests. Use when a user asks for code review, refactor, clean up PR, simplify, tidy up code, review my changes, or maintainability cleanup before merge.
- `skill-pr-delivery` — Ship skill changes to PRs when Codex skills need source edits, rooted sync, strict audit, reviewer evidence, commit, push, and PR status.
- `triage` — Review file-based todo findings into ready, skipped, customized, or blocked states. Use this skill when pending todo files need approval.
- `ubiquitous-language` — Build shared project vocabulary, glossary terms, aliases, prompt translations, domain-grill interviews, and agent instruction links when wording is fuzzy or overloaded.
- `unslopify` — Audit unused functions, dead exports, orphaned modules, stale imports, unreachable code, and tech-debt cleanup candidates with evidence-backed removal guidance. Use when unused code, dead code, remove unused imports, stale-code checks, or scoped cleanup evidence are needed.
- `verification-before-completion` — Review and validate completion claims. Use when you are about to say work is complete, fixed, passing, pushed, or ready for review.

## Skills System

- `imagegen` — Generate or edit raster images when the task benefits from AI-created bitmap visuals such as photos, illustrations, textures, sprites, mockups, or transparent-background cutouts. Use when Codex should create a brand-new image, transform an existing image, or derive visual variants from references, and the output should be a bitmap asset rather than repo-native code or vector. Do not use when the task is better handled by editing existing SVG/vector/code-native assets, extending an established icon or logo system, or building the visual directly in HTML/CSS/canvas.
- `openai-docs` — Use when the user asks how to build with OpenAI products or APIs, asks about Codex itself or choosing Codex surfaces, needs up-to-date official documentation with citations, help choosing the latest model for a use case, or model upgrade and prompt-upgrade guidance; use OpenAI docs MCP tools for non-Codex docs questions, use the Codex manual helper first for broad Codex self-knowledge, and restrict fallback browsing to official OpenAI domains.
