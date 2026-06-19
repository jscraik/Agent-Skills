# Agent Skills Index

Canonical skills live in categorized folders below.

Runtime projection defaults to SDK-flat: first-party repo skills are projected directly unless explicitly hidden.
SDK skill names are the public runtime handles; generated rooted manifests and command-surface metadata are obsolete.

Do not hand-edit runtime projections.

## Table of Contents
- [Summary](#summary)
- [Catalog](#catalog)
- [Skills — Agent Ops](#skills-agent-ops)
- [Skills — Backend Platform](#skills-backend-platform)
- [Skills — Content Publishing](#skills-content-publishing)
- [Skills — Frontend Ui](#skills-frontend-ui)
- [Skills — Mobile Native](#skills-mobile-native)
- [Skills — Product Strategy](#skills-product-strategy)
- [Skills — Security Ops](#skills-security-ops)
- [Skills System](#skills-system)

## Summary
- `total_skills`: 82
- `catalog_source`: default user-visible catalog surface
- `visibility`: default
- `policy_identity`: f766f7003e860bce

## Catalog

## Skills — Agent Ops

- `agents-md` — Use when reviewing, creating, shrinking, or refactoring AGENTS.md agent instructions, agent config files, routing rules, or repository guidance that need scoped routing, dedupe, contradiction fixes, progressive disclosure, and cleaned instruction surfaces.
- `alignment-checkpoint` — Create, review, and validate an alignment checkpoint. Use when a request is ambiguous, high-stakes, multi-step, or requires explicit approval before tool use.
- `autofix` — Apply approved fixes for unresolved CodeRabbit review comments, Codex P1-P3 findings, PR feedback, and code review issues with validation evidence. Use when asked to address review comments, fix review findings, clear unresolved comments, or autofix PR feedback.
- `autoresearch` — Run bounded automated experiment iterations by recording baselines, applying hypothesis patches, comparing metrics, protecting regression guards, and deciding keep, discard, rollback, or block. Use when automated research is requested or a repo/skill needs evidence-backed research, metric tracking, or safe optimisation loops.
- `autoreview` — Run structured AI code review as an advisory closeout gate for local diffs, PR branches, or commits when the user asks for autoreview, Codex review, second-model review, or pre-ship validation.
- `bash-hygiene` — Review, create, and validate Bash scripts when shell work needs strict mode, quoting safety, portability, or interpreter-compatible behavior.
- `biome-linting` — Analyze, fix, and validate Biome linting workflows. Use when JavaScript or TypeScript projects need Biome commands, diagnostics, safe fixes, or CI lint gates.
- `bootstrap` — Create, diagnose, and validate a local dev bootstrap. Use when the user asks to clone a repo, install toolchains, install dependencies, and prove the project runs.
- `code-fixes-triage` — Turn Slack #code-fixes, CodeRabbit, Codex Review, CI, and check-status noise into a repo-and-PR action queue. Use when Jamie asks for a daily code-fixes digest, recent review-noise triage, or what needs fixing across active engineering repos.
- `codex-agent-creator` — Create, validate, install, fold, or troubleshoot Codex subagent role TOML, agents-table config, discoverability wiring, and duplicate-role merges. Use when a user asks for a Codex agent role, reviewer agent, role config, TOML role file, subagent setup, or overlapping agents to merge.
- `codex-automation-architect` — Use when designing, reviewing, or updating Codex app automations, cron jobs, scheduled tasks, recurring runs, or heartbeat follow-ups.
- `codex-environment-creator` — Use when a project or Codex runtime needs environment TOML created, triaged, or updated with safe setup, actions, exec-server providers, and validation evidence.
- `codex-hooks-builder` — Scaffold hook packs, validate hooks.json schema, verify hook script permissions, migrate hook configuration, and troubleshoot Codex hook execution errors. Use when creating, auditing, upgrading, or validating Codex hook packs, hooks.json files, hook scripts, SubagentStart/SubagentStop lifecycle hooks, PreToolUse/PostToolUse/PreCompact hooks, Stop claim checks, or repo-local/user-level .codex hook installs.
- `codex-review` — Review local dirty changes, committed branches, and PR diffs with Codex CLI; report findings, validation, blockers, and merge-readiness evidence. Use when the user asks for Codex review, autoreview, independent model review, or pre-ship validation.
- `coding-harness` — Use when users need to install, bootstrap, upgrade, audit, diagnose, or explain @brainwav/coding-harness in a repository, including harness init/upgrade, CI migration, governance gates, command discovery, and Codex environment action sync.
- `context7` — Analyze current external library or API docs with Context7 when dependency behavior, version-sensitive references, or ctx7 CLI setup/install guidance is needed.
- `decide-build-primitive` — Analyze, compare, and recommend a Codex build primitive. Use when the user is packaging or automating a workflow and the right primitive is unclear.
- `diagram-cli` — Generate, validate, and refresh @brainwav/diagram architecture artifacts when repo diagrams, context packs, PR impact, or CI drift evidence is needed.
- `docs-expert` — Audit, rewrite, and validate README, runbook, code-doc, config-doc, and public trust-surface documentation by checking stale instructions, command examples, dependency claims, file paths, configs, workflows, and code references against live repository evidence. Use when documentation needs proof-backed correction or reader-focused validation.
- `elixir-pro` — Create and review idiomatic Elixir code with OTP patterns, supervision trees, and Phoenix LiveView. Use when building or debugging Elixir services that need reliable concurrency and fault tolerance.
- `evals-router` — Use when evaluating LLM or RAG outputs: audit eval coverage, analyze failed traces, write binary judge prompts, validate judges against labels, generate targeted synthetic cases, evaluate retrieval quality, or plan review tooling. Do not use for general software tests.
- `fix-mise` — Diagnose, fix, and validate mise runtime failures. Use when commands fail from mise config, missing runtimes, stale pins, trust prompts, or shell activation drift.
- `frontend-design` — Analyze ambiguous frontend design requests and route the right UI owner. Use this skill when broad design intent needs classification before implementation.
- `go` — Best practices for working with Go codebases. Use when writing, debugging, or exploring Go code, including reading dependency sources and documentation.
- `goal-governor` — Use when a Codex goal/task is stuck, hanging, not finishing, or needs status. Reads goal.md, state.yaml, receipts.jsonl; syncs reported status with board files; fixes invalid state.yaml; classifies blockers; decides done. Not for ordinary reviews or one-off fixes.
- `improve-agent-native` — Check if a repository or agent-facing product surface is ready for AI coding agents. Use when you need to audit repo agent compatibility, review AGENTS.md, find missing test/build commands, evaluate docs quality, assess tool/action parity, or produce a file-evidence scorecard with specific fixes.
- `improve-codebase-architecture` — Review code architecture, code quality, dependency graphs, coupling, technical debt, modularization, ownership, and test seams. Use when refactors, restructuring, tightly coupled code, or architecture decisions need proof-backed options.
- `insight-report` — Generate local Codex usage reports. Use when users ask for usage analytics, weekly insights, session summaries, telemetry patterns, or prompting help.
- `javascript-pro` — Create and debug modern JavaScript code with ES6+, async patterns, and Node.js APIs. Use when working on runtime behavior, promises, or browser and Node compatibility.
- `keep-codex-fast` — Diagnose Codex Desktop or CLI local-state bloat and safe recovery options. Use when sessions, archived history, logs, worktrees, or stale Codex config may be making Codex feel slow.
- `npm-release` — Create, review, and validate npm release workflows. Use when preparing or publishing npm packages, release channels, dist-tags, provenance, or 2FA-protected publishes.
- `pnpm-manager` — Run, plan, and validate pnpm workspace operations. Use when a user needs pnpm monorepo installs, tests, builds, filters, changed-package selection, or publish routing.
- `pr-green-sweep` — Automate until-green PR review, CI, merge, and cleanup follow-through. Use when open project PRs need GitHub, CodeRabbit, CircleCI, Context7, autofix, heartbeat, and branch/worktree pruning.
- `prek-pro` — Review, configure, and troubleshoot prek hooks when users need prek.toml edits, shim installs, hook validation, or pre-commit migration help.
- `production-deployment` — Plan, execute, and validate production deployments when rollout safety, health checks, observability, rollback, or production-parity verification is required.
- `project-brain` — Create, validate, and repair Project Brain .harness memory files when setting up Project Brain, saving repo learnings, recording decisions, or preserving quality rules.
- `rust-pro` — Create and review Rust 1.75+ systems code with ownership-safe async patterns and production error handling. Use when building or debugging Rust services that need performance and reliability.
- `sdk-scenario-generator` — Create, review, and maintain gold-standard Skills SDK eval scenarios before internal evals, dry Tessl staging, or live private Tessl scoring. Use when creating or updating a skill, importing KnowledgeOS or Tessl scenario suggestions, checking scenario drift, hardening evals that are too easy, or preparing a minimum 20-scenario live Tessl set.
- `session-workflow-miner` — Analyze recent Codex session evidence for repeated manual workflows and route them to skills, subagents, validators, or no artifact when Jamie asks what he keeps doing manually.
- `simplify` — Review changed code for behavior-preserving simplification by removing dead code, eliminating duplication, extracting shared helpers, improving names, and tightening tests. Use when a user asks for code review, refactor, clean up PR, simplify, tidy up code, review my changes, or maintainability cleanup before merge.
- `skill-pr-delivery` — Ship skill changes to PRs when Codex skills need source edits, rooted sync, strict audit, reviewer evidence, commit, push, and PR status.
- `testing` — Select, run, parse, and report repo-native validation evidence, including test commands, failure ownership, coverage gaps, eval artifacts, deterministic scorers, judge calibration, and regression proof. Use when users ask what tests to run, ask to validate a change, fix failing tests, design test coverage, build eval proof, classify validation failures, or prove behavior before closeout.
- `toml` — Create and review TOML configuration with strict typing and predictable structure. Use when editing tool configuration files that require schema-safe TOML.
- `triage` — Review file-based todo findings into ready, skipped, customized, or blocked states. Use this skill when pending todo files need approval.
- `typescript` — Use when authoring or reviewing TypeScript code that requires strict type safety, explicit module contracts, and predictable runtime boundaries.
- `ubiquitous-language` — Build shared project vocabulary, glossary terms, aliases, prompt translations, domain-grill interviews, and agent instruction links when wording is fuzzy or overloaded.
- `unslopify` — Audit dead code, stale exports, unused imports, and cleanup candidates. Use when scoped cleanup needs evidence, rollback notes, and repo-native validation.
- `uv-python-project-setup` — Create, repair, and validate uv Python project setup. Use when initializing Python apps or libraries, managing uv dependencies, virtual environments, or CI-ready uv workflows.
- `vale` — Install, repair, and validate Vale prose linting. Use when users need Vale config, style sync, docs lint gates, or broken Vale workflow diagnosis.
- `verification-before-completion` — Review and validate completion claims. Use when you are about to say work is complete, fixed, passing, pushed, or ready for review.
- `yaml` — Create and review YAML files with safe indentation, schema-aware structure, and low-surprise serialization. Use when editing YAML config or workflow files.

## Skills — Backend Platform

- `backend-engineer` — Plan, implement, and validate backend service changes. Use when patching or adding backend features in an existing API, data, auth, worker, or service codebase.
- `cli-spec` — Create and validate implementation-grade CLI specifications when command trees, JSON contracts, dry-run plans, errors, or agent-ready behavior need a binding spec.
- `mcp-builder` — Design and validate MCP server tools when standard integrations need schemas, safe auth, resources, prompts, and Inspector-ready verification.
- `oak-api` — Build safe Oak Curriculum API learning flows. Use this skill when Oak endpoints, curriculum maps, or child-facing Apps SDK guidance are needed.

## Skills — Content Publishing

- `beautiful-mermaid` — Create, render, and validate Mermaid diagrams when users need Mermaid source converted into SVG, PNG, HTML previews, or polished diagram assets.
- `llm-wiki` — Create or update an Obsidian-friendly local markdown knowledge base. Use when the user wants LLM-maintained notes, wikilinks/backlinks, frontmatter, citations, local attachments, vault cleanup, or reusable research synthesis.
- `release-notes` — Draft evidence-backed release notes and changelog entries. Use this skill when PR notes, GitHub releases, or npm handoff need traceability.
- `video-transcript-downloader` — Download, transcribe, inspect, summarize, or convert video and audio sources. Use when the user wants transcripts, subtitles, audio extraction, or media downloads from a video source.
- `visual-explainer` — Create self-contained HTML visual explainers from technical material. Use this skill when diagrams, matrices, timelines, or browser artifacts beat plain text.
- `youtube-hooks-scripts` — Generate, review, and refine high-retention technical YouTube hooks, outlines, and scripts. Use when the user wants video scripting tailored to a topic, audience, runtime, and evidence-bound claims.

## Skills — Frontend Ui

- `agentation` — Audit, validate, and troubleshoot Agentation integrations in frontend apps. Use when annotations, MCP registration, endpoint sync, webhook delivery, or watch mode readiness are failing.
- `baseline-ui` — Audit UI implementation quality when frontend work needs accessibility, responsiveness, theming, performance, and anti-slop guardrails.
- `better-icons` — Search, compare, and extract SVG icons from Iconify collections. Use when the user needs production-ready UI icons, icon family consistency, or exact SVG markup.
- `design-system` — Govern and validate design-system changes. Use when tokens, typography, spacing, iconography, themes, or style aliases need repository-grounded evidence.
- `fixing-accessibility` — Audit, fix, and validate accessibility issues. Use when adding or reviewing controls, forms, dialogs, keyboard behavior, focus management, ARIA labels, color contrast, or WCAG compliance.
- `fixing-metadata` — Audit, fix, and validate HTML metadata. Use when shipping pages that need titles, descriptions, canonical URLs, Open Graph tags, Twitter cards, favicons, JSON-LD, or robots directives.
- `frontend-ui-design` — Design or implement production-ready frontend screens and components. Use this skill when UI build, redesign, accessibility, layout, or state coverage is needed.
- `og-image-creator` — Generate route-aware Open Graph image workflows from existing web apps. Use this skill when route-specific social preview assets need refresh or creation.
- `ui-ux-creative-coding` — Build and audit polished interaction refinements for existing React or Tauri UI when motion, accessibility, reduced-motion, and browser-verified behavior need focused improvement.
- `ui-visual-regression` — Review, triage, and validate visual regression diffs. Use when the user wants snapshot-change analysis, layout regression evidence, Storybook diffs, Playwright screenshots, or Argos review.

## Skills — Mobile Native

- `atlas` — Automate Atlas on macOS when users explicitly ask to control Atlas tabs, bookmarks, history, or desktop browser state.

## Skills — Product Strategy

- `architecture-interview` — Analyze, review, and plan architecture alternatives through a structured interview. Use when the user needs tradeoffs surfaced before implementation or a Linear decision note instead of an ADR.
- `deep-interview` — Analyze, deepen, and validate an existing doc or topic through a structured interview. Use when refining PRDs, Linear tickets, notes, or draft specs before planning or execution.
- `interview-me` — Analyze underspecified requests with a short decision interview. Use this skill when guessing would risk the wrong plan.

## Skills — Security Ops

- `1password` — Plan, diagnose, and validate 1Password CLI workflows. Use when tasks need op CLI sign-in, secret references, op run, op inject, item reads, env injection, or service-account secret access.
- `best-practices` — Audit, review, and harden Better Auth integrations. Use when the user wants Better Auth security review, config debugging, provider hardening, session checks, or operational risk guidance.
- `create-auth` — Create, migrate, or validate Better Auth implementation work. Use when the user wants Better Auth added or changed in code, including OAuth, passkeys, 2FA, magic links, or org flows.
- `recon-workbench` — Run, audit, and design authorized Recon Workbench workflows when scoped target interrogation needs evidence artifacts, redaction, validation, and safe reporting.
- `security-ownership-map` — Analyze git-history security ownership when sensitive files, CODEOWNERS coverage, bus factor, contributor concentration, and remediation evidence need mapping.

## Skills System

- `imagegen` — Generate or edit raster images when the task benefits from AI-created bitmap visuals such as photos, illustrations, textures, sprites, mockups, or transparent-background cutouts. Use when Codex should create a brand-new image, transform an existing image, or derive visual variants from references, and the output should be a bitmap asset rather than repo-native code or vector. Do not use when the task is better handled by editing existing SVG/vector/code-native assets, extending an established icon or logo system, or building the visual directly in HTML/CSS/canvas.
- `openai-docs` — Use when the user asks how to build with OpenAI products or APIs, asks about Codex itself or choosing Codex surfaces, needs up-to-date official documentation with citations, help choosing the latest model for a use case, or model upgrade and prompt-upgrade guidance; use OpenAI docs MCP tools for non-Codex docs questions, use the Codex manual helper first for broad Codex self-knowledge, and restrict fallback browsing to official OpenAI domains.
