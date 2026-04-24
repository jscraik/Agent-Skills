# Agent Skills Index

Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/.agents/skills`.

## Table of Contents
- [Summary](#summary)
- [Catalog](#catalog)
- [Skills — Agent Ops](#skills-agent-ops)

## Summary
- `total_skills`: 19
- `catalog_source`: default user-visible catalog surface
- `visibility`: default
- `policy_identity`: 346ed21dd594983a

## Catalog

## Skills — Agent Ops

- `agents-md` — Create or refactor AGENTS.md and linked instruction docs using progressive disclosure. Use when the user wants repo-specific agent guidance organized, deduplicated, or routed cleanly, not ordinary product documentation edits.
- `autofix` — Review and apply CodeRabbit PR review-thread feedback from GitHub with per-change approval. Use this skill when a branch PR has unresolved CodeRabbit issues that need safe, human-approved fixes.
- `autoresearch` — Analyze and improve this repo's skills and plugin packages through bounded experiment loops. Use this skill when users request autonomous research passes with hypothesis-validation-keep/discard decisions.
- `bootstrap` — Bootstrap a local development environment from a GitHub repository URL. Use when the user asks to clone a repo, install toolchains/dependencies, and validate a working dev setup automatically.
- `codex-agent-creator` — Create, install, validate, and orchestrate Codex custom subagents as standalone TOMLs with canonical global defaults (`~/dev/configs/codex/agents/{name}/{name}.toml`, `~/dev/configs/codex/config.toml`) plus optional project scope (`${project_root}/.codex/agents/{name}/{name}.toml`), where project config writes occur only when runtime-limit flags are explicitly requested.
- `codex-automation-architect` — Design, review, or merge Codex app automations using current OpenAI/Codex guidance and validation. Use when the user wants recurring Codex automation workflows built, audited, or consolidated.
- `codex-hooks-builder` — Create, upgrade, or audit Codex hook packs for repo-local or user-level `.codex` installs. Use when the user wants hook runtime files or hook-script hardening, not general agent role creation.
- `coding-harness` — Use when a repository needs `@brainwav/coding-harness` installed, bootstrapped, updated, audited, or explained. Covers `harness init`, harness-managed CI migration, governance checks, and Codex environment action-sync guidance. Do not use for unrelated coding, general deployment, or broad cloud work.
- `context7` — Analyze current external library/API documentation and generate Context7 CLI guidance when the user asks for version-sensitive dependency behavior, library API references, or Context7 skills/setup/auth command help.
- `docs-expert` — Audit and rewrite repository documentation, runbooks, and in-code docs with repo-visibility and brand-quality checks. Use when the user wants README, docs, JSDoc, DocC, or config documentation improved, not editorial house-style copyediting.
- `fix-mise` — Diagnose and repair mise trust, runtime, activation, and version-drift failures. Use when commands fail from mise config, missing runtimes, stale pins, or shell activation drift.
- `gh-workflow` — Operate the GitHub lifecycle through `gh`: issue work, PR readiness checks, PR preparation, review handling, CI diagnosis, and merge execution. Use when the user wants GitHub state changed, advanced, or reconciled.
- `npm-release` — Create and validate npm package release workflows with deterministic installs, semver, dist-tags, provenance, and 2FA safeguards. Use when preparing or publishing npm releases.
- `pnpm-manager` — Run pnpm workspace operations with recursive and filter selectors for scoped install, test, build, and publish flows. Use when a user needs pnpm monorepo command routing.
- `project-brain` — Bootstrap and operate Project Brain
- `simplify` — Review changed code for reuse, quality, efficiency, and behavior-preserving refactor polish. This skill should be used when users request post-implementation simplification or pre-merge maintainability cleanup on an existing diff.
- `triage` — Review and triage file-based `todos/` findings into ready, skipped, or revised states before execution. Use this skill when the repo already uses the file-based todo workflow and the user wants approval-style triage, not tracker triage or todo execution.
- `ubiquitous-language` — Build or update a shared project vocabulary, DDD-style glossary, and prompt translation map from the current conversation, project docs, and relevant session evidence. Use when terminology is fuzzy, the user wants consistent naming, asks what to call something, wants agents to interpret their wording consistently, mentions glossary, domain model, DDD, ubiquitous language, naming, vocabulary, terminology, or says they do not know the technical term.
- `verification-before-completion` — Validate completion claims with fresh command evidence. Use when you are about to claim work is complete, fixed, or passing.

