# Agent Skills Index

Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/.agents/skills`.

## Table of Contents
- [Summary](#summary)
- [Catalog](#catalog)
- [Plugins — Harness Engineering — Skills](#plugins-harness-engineering-skills)
- [Plugins — Harness Engineering — Skills — Code_Quality_Review](#plugins-harness-engineering-skills-code_quality_review)
- [Plugins — Harness Engineering — Skills — Team_Automation](#plugins-harness-engineering-skills-team_automation)
- [Plugins — Plugin Factory — Skills — Team_Automation](#plugins-plugin-factory-skills-team_automation)
- [Plugins — Skill Factory — Skills](#plugins-skill-factory-skills)
- [Plugins — Skill Factory — Skills — Code_Quality_Review](#plugins-skill-factory-skills-code_quality_review)
- [Plugins — Skill Factory — Skills — Data_Fetch_Analysis](#plugins-skill-factory-skills-data_fetch_analysis)
- [Plugins — Skill Factory — Skills — Scaffolding_Templates](#plugins-skill-factory-skills-scaffolding_templates)
- [Skills — Agent Ops](#skills-agent-ops)

## Summary
- `total_skills`: 28
- `catalog_source`: default user-visible catalog surface
- `visibility`: default
- `policy_identity`: 9cc448c9e5cb4ca3

## Catalog

## Plugins — Harness Engineering — Skills

- `he-router` — Analyze Harness Engineering requests and choose one stage plus next command. Use when intent is unclear.

## Plugins — Harness Engineering — Skills — Code_Quality_Review

- `he-code-review` — Review PRs, branches, diffs, and workflow artifacts for package-level go/no-go readiness with severity-ranked synthesis. Use when users need readiness synthesis rather than detailed technical-risk critique.
- `he-technical-review` — Review diffs, PRs, specs, plans, or review-feedback items and return severity-ranked engineering findings with exact locations. Use when technical risks or feedback correctness must be verified before implementation.

## Plugins — Harness Engineering — Skills — Team_Automation

- `he-prune-branches` — Automate stale local git branch cleanup with worktree-aware deletion and explicit confirmation gates. Use this skill when the user asks to prune local branches whose remote tracking refs are gone.
- `he-work` — Execute a plan, todo list, or tightly scoped spec with traceable progress, validation, contract-drift control, UI execution gates, and optional external delegation. Use when the user wants Harness Engineering work implemented, not just planned.

## Plugins — Plugin Factory — Skills — Team_Automation

- `plugin-router` — Route plugin requests to the right factory lane

## Plugins — Skill Factory — Skills

- `skill-factory-router` — Route skill lifecycle requests to a Skill Factory lane. Use when users ask to create, harden, install, audit, or skillify skills.

## Plugins — Skill Factory — Skills — Code_Quality_Review

- `skill-builder` — Analyze and harden Codex skills and plugin packages for contract quality, eval coverage, and safety compliance. Use this skill when an existing package is approaching release and needs evidence-backed validation.

## Plugins — Skill Factory — Skills — Data_Fetch_Analysis

- `skill-refactor` — Scan Codex session history for skill failures, usage patterns, and coverage gaps. Use when the user wants daily skill-health monitoring or evidence-backed recommendations about installing, improving, merging, or pruning skills.

## Plugins — Skill Factory — Skills — Scaffolding_Templates

- `skillify` — Capture a completed Codex workflow as a reusable SKILL.md package by analyzing session context plus optional session-collector evidence, interviewing the user with structured prompts, and writing a validated skill artifact. Use when the user asks to skillify or operationalize a repeatable process.

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
- `fix-mise` — Use this skill to operate and repair mise workflows, including trust/runtime failures, activation drift, and local/global version pinning, when commands fail or toolchain behavior is non-deterministic.
- `gh-workflow` — Operate the GitHub lifecycle through `gh`: issue work, PR readiness checks, PR preparation, review handling, CI diagnosis, and merge execution. Use when the user wants GitHub state changed, advanced, or reconciled.
- `npm-release` — Create and validate npm release workflows end to end, including deterministic dependency/install discipline, semver bumping, dist-tags, provenance publishing, and 2FA-aware safeguards.
- `pnpm-manager` — Run pnpm workspace operations with recursive and filter selectors for scoped install, test, build, and publish flows. Use when a user needs pnpm monorepo command routing.
- `project-brain` — Bootstrap and operate Project Brain
- `simplify` — Review changed code for reuse, quality, efficiency, and behavior-preserving refactor polish. This skill should be used when users request post-implementation simplification or pre-merge maintainability cleanup on an existing diff.
- `triage` — Review and triage file-based `todos/` findings into ready, skipped, or revised states before execution. Use this skill when the repo already uses the file-based todo workflow and the user wants approval-style triage, not tracker triage or todo execution.
- `verification-before-completion` — Validate completion claims with fresh command evidence. Use when you are about to claim work is complete, fixed, or passing.

