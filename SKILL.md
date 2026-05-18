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

## Summary
- `total_skills`: 22
- `catalog_source`: default user-visible catalog surface
- `visibility`: default
- `policy_identity`: fabbe04d4ccdc50e

## Catalog

## Skills — Agent Ops

- `agents-md` — Use when reviewing, creating, shrinking, or refactoring AGENTS.md, agent setup, agent prompts, system instructions, routing rules, or repo guidance that need scoped routing, dedupe, contradiction fixes, or progressive disclosure.
- `autofix` — Apply approved fixes for unresolved CodeRabbit review comments, Codex P1-P3 findings, PR feedback, and code review issues with validation evidence. Use when asked to address review comments, fix review findings, clear unresolved comments, or autofix PR feedback.
- `autoresearch` — Run bounded automated experiment iterations by recording baselines, applying hypothesis patches, comparing metrics, protecting regression guards, and deciding keep, discard, rollback, or block. Use when $autoresearch is named or a repo/skill needs evidence-backed research, metric tracking, or safe optimisation loops.
- `bootstrap` — Create, diagnose, and validate a local dev bootstrap. Use when the user asks to clone a repo, install toolchains, install dependencies, and prove the project runs.
- `codex-agent-creator` — Create, validate, install, fold, or troubleshoot Codex custom subagent roles, role TOML config files, agent configuration, custom roles, subagent setup, and discoverability wiring. Use when a user asks for a Codex agent role, reviewer agent, role config, TOML role file, or overlapping agents to merge.
- `codex-automation-architect` — Use when designing, reviewing, or updating Codex app automations, cron jobs, scheduled tasks, recurring runs, or heartbeat follow-ups.
- `codex-hooks-builder` — Scaffold hook packs, validate hooks.json schema, verify hook script permissions, migrate hook configuration, and troubleshoot Codex hook execution errors. Use when creating, auditing, upgrading, or validating Codex hook packs, hooks.json files, hook scripts, PreToolUse/PostToolUse/PreCompact hooks, or repo-local/user-level .codex hook installs.
- `codex-review` — WHAT: Review local dirty changes, committed branches, and PR diffs with Codex CLI. Use when the user asks for Codex review, autoreview, independent model review, pre-ship validation, or merge-readiness evidence.
- `coding-harness` — Use when users need to install, bootstrap, upgrade, audit, diagnose, or explain @brainwav/coding-harness in a repository, including harness init/upgrade, CI migration, governance gates, command discovery, and Codex environment action sync.
- `context7` — Analyze current external library or API docs with Context7 when dependency behavior, version-sensitive references, or ctx7 CLI setup/install guidance is needed.
- `docs-expert` — Audit, rewrite, and validate README, runbook, code-doc, config-doc, and public trust-surface documentation by checking stale instructions, command examples, dependency claims, file paths, configs, workflows, and code references against live repository evidence. Use when documentation needs proof-backed correction or reader-focused validation.
- `fix-mise` — Diagnose, fix, and validate mise runtime failures. Use when commands fail from mise config, missing runtimes, stale pins, trust prompts, or shell activation drift.
- `improve-codebase-architecture` — Reviews architecture change pressure in module boundaries, coupling, ownership, hidden state, tests, and decisions. Use when asked for architecture review, design review, refactoring assessment, code-structure analysis, patch-vs-interface tradeoffs, tracer proof, or repo decision evidence; not for cleanup, bugs, naming, or style refactors.
- `keep-codex-fast` — Diagnose Codex Desktop or CLI local-state bloat and safe recovery options. Use when sessions, archived history, logs, worktrees, or stale Codex config may be making Codex feel slow.
- `npm-release` — Create, review, and validate npm release workflows. Use when preparing or publishing npm packages, release channels, dist-tags, provenance, or 2FA-protected publishes.
- `pnpm-manager` — Run, plan, and validate pnpm workspace operations. Use when a user needs pnpm monorepo installs, tests, builds, filters, changed-package selection, or publish routing.
- `project-brain` — Create, validate, and repair Project Brain .harness memory files when setting up Project Brain, saving repo learnings, recording decisions, or preserving quality rules.
- `simplify` — Review changed code for behavior-preserving simplification by removing dead code, eliminating duplication, extracting shared helpers, improving names, and tightening tests. Use when a user asks for code review, refactor, clean up PR, simplify, tidy up code, review my changes, or maintainability cleanup before merge.
- `skill-pr-delivery` — Ship skill changes to PRs when Codex skills need source edits, rooted sync, strict audit, reviewer evidence, commit, push, and PR status.
- `triage` — Review file-based todo findings into ready, skipped, customized, or blocked states. Use this skill when pending todo files need approval.
- `ubiquitous-language` — Build shared project vocabulary, glossary terms, aliases, prompt translations, and agent instruction links when wording is fuzzy or overloaded.
- `verification-before-completion` — Review and validate completion claims. Use when you are about to say work is complete, fixed, passing, pushed, or ready for review.

