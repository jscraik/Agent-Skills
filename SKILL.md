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
- `total_skills`: 22
- `catalog_source`: default user-visible catalog surface
- `visibility`: default
- `policy_identity`: 0194570d229fbe4d

## Catalog

## Skills — Agent Ops

- `agents-md` — Use when reviewing, creating, shrinking, or refactoring AGENTS.md instruction surfaces that need scoped routing, dedupe, contradiction fixes, or progressive disclosure.
- `autofix` — Review, validate, and fix every current unresolved CodeRabbit thread and Codex P1-P3 finding. Use when PR review feedback needs approved fixes with safety checks and validation evidence.
- `autoresearch` — Analyze bounded autonomous experiment loops with baselines, hypothesis patches, noisy metric policy, fixed evaluation safety, protected regression guards, and keep/discard/block decisions. Use when $autoresearch is named or a repo/skill needs evidence-backed research iterations.
- `bootstrap` — Create, diagnose, and validate a local dev bootstrap. Use when the user asks to clone a repo, install toolchains, install dependencies, and prove the project runs.
- `codex-agent-creator` — Use when asked to create, validate, install, fold, or troubleshoot Codex custom subagent role TOML and agent discoverability config.
- `codex-automation-architect` — Design, review, and validate Codex app automations when recurring background workflows need safe scheduling, scope, preflight, and consolidation.
- `codex-hooks-builder` — Use when creating, auditing, upgrading, or validating Codex hook packs, hooks.json files, hook scripts, or repo-local/user-level .codex hook installs.
- `coding-harness` — Use when users need to install, bootstrap, upgrade, audit, diagnose, or explain @brainwav/coding-harness in a repository, including harness init/upgrade, CI migration, governance gates, command discovery, and Codex environment action sync.
- `context7` — Analyze current external library or API docs with Context7 when dependency behavior, version-sensitive references, or ctx7 CLI setup/install guidance is needed.
- `docs-expert` — Use when README, runbook, code-doc, config-doc, or public trust-surface documentation must be audited, rewritten, or validated against live repository evidence.
- `fix-mise` — Diagnose, fix, and validate mise runtime failures. Use when commands fail from mise config, missing runtimes, stale pins, trust prompts, or shell activation drift.
- `improve-codebase-architecture` — Use when reviewing or improving codebase architecture needs deeper module boundaries, clearer context language, better interfaces, stronger testability, or Linear-backed decisions.
- `keep-codex-fast` — Diagnose Codex Desktop or CLI local-state bloat and safe recovery options. Use when sessions, archived history, logs, worktrees, or stale Codex config may be making Codex feel slow.
- `npm-release` — Create, review, and validate npm release workflows. Use when preparing or publishing npm packages, release channels, dist-tags, provenance, or 2FA-protected publishes.
- `pnpm-manager` — Run, plan, and validate pnpm workspace operations. Use when a user needs pnpm monorepo installs, tests, builds, filters, changed-package selection, or publish routing.
- `project-brain` — Create, validate, and repair Project Brain .harness memory files when setting up Project Brain, saving repo learnings, recording decisions, or preserving quality rules.
- `simplify` — WHAT: Review changed code for behavior-preserving simplification. WHEN: Use when a diff needs reuse, quality, efficiency, duplication, naming, or maintainability cleanup before merge.
- `skill-pr-delivery` — Ship skill changes to PRs when Codex skills need source edits, rooted sync, strict audit, reviewer evidence, commit, push, and PR status.
- `triage` — Review file-based todo findings into ready, skipped, customized, or blocked states. Use this skill when pending todo files need approval.
- `ubiquitous-language` — Build shared project vocabulary, glossary terms, aliases, prompt translations, and agent instruction links when wording is fuzzy or overloaded.
- `verification-before-completion` — Review and validate completion claims. Use when you are about to say work is complete, fixed, passing, pushed, or ready for review.

## Skills System

- `imagegen` — Generate or edit raster images when the task benefits from AI-created bitmap visuals such as photos, illustrations, textures, sprites, mockups, or transparent-background cutouts. Use when Codex should create a brand-new image, transform an existing image, or derive visual variants from references, and the output should be a bitmap asset rather than repo-native code or vector. Do not use when the task is better handled by editing existing SVG/vector/code-native assets, extending an established icon or logo system, or building the visual directly in HTML/CSS/canvas.

