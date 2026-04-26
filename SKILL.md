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
- `total_skills`: 21
- `catalog_source`: repository skill scan
- `visibility`: default
- `policy_identity`: 14c1588c6febe0c0

## Catalog

## Skills — Agent Ops

- `agents-md` — Review or refactor AGENTS.md instruction surfaces with progressive disclosure. Use this skill when repo agent guidance needs routing, dedupe, or contradiction fixes.
- `autofix` — Review, validate, and apply scoped CodeRabbit PR feedback when unresolved GitHub review threads need human-approved code fixes and repo-check evidence.
- `autoresearch` — Analyze and improve skills or plugins through bounded experiments when the user wants hypothesis-driven research loops with keep, discard, blocked, and validation decisions.
- `bootstrap` — Create, diagnose, and validate a local dev bootstrap. Use when the user asks to clone a repo, install toolchains, install dependencies, and prove the project runs.
- `codex-agent-creator` — Create or validate Codex custom subagent TOML files. Use this skill when users need agent config, install, or bounded orchestration.
- `codex-automation-architect` — Design, review, and validate Codex app automations when recurring background workflows need safe scheduling, scope, preflight, and consolidation.
- `codex-hooks-builder` — Create, audit, and validate Codex hook packs when repo-local or user-level .codex installs need hook runtime files or hook-script hardening.
- `coding-harness` — Install, update, audit, diagnose, and explain @brainwav/coding-harness when repository governance, harness init, CI migration, or action-sync needs live command evidence.
- `context7` — Analyze current external library or API docs with Context7 when dependency behavior, version-sensitive references, or ctx7 CLI setup/install guidance is needed.
- `docs-expert` — Audit, rewrite, and validate repository documentation when README, runbook, code-doc, config-doc, or public trust-surface claims must match live repo evidence.
- `fix-mise` — Diagnose, fix, and validate mise runtime failures. Use when commands fail from mise config, missing runtimes, stale pins, trust prompts, or shell activation drift.
- `gh-workflow` — Operate GitHub issue, PR, review, CI, and merge workflows through gh when repository state must be advanced, reconciled, or verified with live evidence.
- `improve-codebase-architecture` — Review and improve codebase architecture when deeper module boundaries, clearer context language, better interfaces, testability, or Linear-backed decisions are needed.
- `npm-release` — Create, review, and validate npm release workflows. Use when preparing or publishing npm packages, release channels, dist-tags, provenance, or 2FA-protected publishes.
- `pnpm-manager` — Run, plan, and validate pnpm workspace operations. Use when a user needs pnpm monorepo installs, tests, builds, filters, changed-package selection, or publish routing.
- `project-brain` — Create, validate, and repair Project Brain .harness memory files when setting up Project Brain, saving repo learnings, recording decisions, or preserving quality rules.
- `simplify` — Review changed code for reuse, quality, efficiency, and behavior-preserving refactor polish. This skill should be used when users request post-implementation simplification or pre-merge maintainability cleanup on an existing diff.
- `skill-pr-delivery` — Ship skill changes to PRs when Codex skills need source edits, rooted sync, strict audit, reviewer evidence, commit, push, and PR status.
- `triage` — Review file-based todo findings into ready, skipped, customized, or blocked states. Use this skill when pending todo files need approval.
- `ubiquitous-language` — Build or update a shared project vocabulary, DDD-style glossary, and prompt translation map from the current conversation, project docs, and relevant session evidence. Use when terminology is fuzzy, the user wants consistent naming, asks what to call something, wants agents to interpret their wording consistently, mentions glossary, domain model, DDD, ubiquitous language, naming, vocabulary, terminology, or says they do not know the technical term.
- `verification-before-completion` — Review and validate completion claims. Use when you are about to say work is complete, fixed, passing, pushed, or ready for review.

