# Agent Skills Index

Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/.agents/skills`.

## Table of Contents
- [Summary](#summary)
- [Catalog](#catalog)
- [.Agents — Skills — .System](#.agents-skills-.system)
- [Skills — Agent Ops](#skills-agent-ops)
- [Skills — Backend Platform](#skills-backend-platform)
- [Skills — Content Publishing](#skills-content-publishing)
- [Skills — Frontend Ui](#skills-frontend-ui)
- [Skills — Mobile Native](#skills-mobile-native)
- [Skills — Product Strategy](#skills-product-strategy)
- [Skills — Security Ops](#skills-security-ops)

## Summary
- `total_skills`: 93
- `catalog_source`: repository skill scan
- `visibility`: default
- `policy_identity`: 7b5d4c75b7d19338

## Catalog

## .Agents — Skills — .System

- `imagegen` — Generate or edit raster images when the task benefits from AI-created bitmap visuals such as photos, illustrations, textures, sprites, mockups, or transparent-background cutouts. Use when Codex should create a brand-new image, transform an existing image, or derive visual variants from references, and the output should be a bitmap asset rather than repo-native code or vector. Do not use when the task is better handled by editing existing SVG/vector/code-native assets, extending an established icon or logo system, or building the visual directly in HTML/CSS/canvas.
- `openai-docs` — Use when the user asks how to build with OpenAI products or APIs and needs up-to-date official documentation with citations, help choosing the latest model for a use case, or explicit GPT-5.4 upgrade and prompt-upgrade guidance; prioritize OpenAI docs MCP tools, use bundled references only as helper context, and restrict any fallback browsing to official OpenAI domains.
- `plugin-creator` — Create and scaffold plugin directories for Codex with a required `.codex-plugin/plugin.json`, optional plugin folders/files, and baseline placeholders you can edit before publishing or testing. Use when Codex needs to create a new local plugin, add optional plugin structure, or generate or update repo-root `.agents/plugins/marketplace.json` entries for plugin ordering and availability metadata.
- `skill-creator` — Create or update a skill
- `skill-installer` — Install curated skills from openai/skills or other repos

## Skills — Agent Ops

- `alignment-checkpoint` — Intent-alignment gate for ambiguous/high-stakes requests. Use this when you want to extract goal/assumptions/criteria and require an explicit /proceed approval gate before any tool use.
- `autoresearch` — Analyze and improve this repo's skills and plugin packages through bounded experiment loops. Use this skill when users request autonomous research passes with hypothesis-validation-keep/discard decisions.
- `bash-hygiene` — Write and review Bash scripts with safe structure and portability guardrails. Use when shell work needs strict mode defaults, robust quoting, and interpreter-compatible behavior.
- `biome-linting` — Guide Biome linting and formatting workflows with safe-fix strategy and CI-ready rule triage. Use when a user needs Biome command, diagnostics, or remediation guidance in JavaScript/TypeScript projects.
- `claude-alias` — Diagnose, repair, and harden Claude wrapper alias routing (`ck`, `cz`, `cc`) when provider configs drift or auth/model conflicts return the wrong backend.
- `codex-agent-creator` — Create, install, and validate Codex custom subagents as standalone TOMLs with canonical global defaults (`~/dev/configs/codex/agents/{name}/{name}.toml`, `~/dev/configs/codex/config.toml`) plus optional project scope (`${project_root}/.codex/agents/{name}/{name}.toml`), where project config writes occur only when runtime-limit flags are explicitly requested.
- `codex-automation-architect` — Design, review, or merge Codex app automations using current OpenAI/Codex guidance and validation. Use when the user wants recurring Codex automation workflows built, audited, or consolidated.
- `codex-home-audit` — Audit a Codex home directory for control-plane drift, risky state, and cleanup opportunities across config, agents, hooks, skills, plugins, and telemetry. Use when the user wants a dated Codex home health review.
- `codex-hooks-builder` — Create, upgrade, or audit Codex hook packs for repo-local or user-level `.codex` installs. Use when the user wants hook runtime files or hook-script hardening, not general agent role creation.
- `coding-harness` — Use when a repository needs `@brainwav/coding-harness` installed, bootstrapped, updated, audited, or explained. Covers `harness init`, harness-managed CI migration, governance checks, and Codex environment action-sync guidance. Do not use for unrelated coding, general deployment, or broad cloud work.
- `diagram-cli` — Generate, validate, and refresh @brainwav/diagram architecture artifacts and context packs. Use when the user wants repository architecture diagrams for onboarding, PR impact, or CI drift checks, not hand-drawn product mock diagrams.
- `elixir-pro` — Write idiomatic Elixir code with OTP patterns, supervision trees, and Phoenix LiveView. Masters concurrency, fault tolerance, and distributed systems.
- `evals-router` — Route and guide LLM evaluation work such as evaluator design, error analysis, RAG evals, and synthetic eval data. Use when the user wants eval-specific workflow help, not product analytics or ordinary QA.
- `frontend-design` — Analyze broad frontend design requests and route them to the correct local UI skill after classifying intent and maturity. Use when the user asks for frontend design generally and the specific design owner is not yet clear.
- `go` — Best practices for working with Go codebases. Use when writing, debugging, or exploring Go code, including reading dependency sources and documentation.
- `insight-report` — WHAT: Generate comprehensive HTML insights from Codex OTEL data using local Ollama LLMs. WHEN: Use when the user asks for usage analytics, workflow patterns, Codex session summaries, or recommendations for improving their development workflow.
- `javascript-pro` — Master modern JavaScript with ES6+, async patterns, and Node.js APIs. Handles promises, event loops, and browser/Node compatibility.
- `mise-tooling` — Operate mise tool-version workflows with trust-aware config loading, local/global version pinning, and deterministic runtime execution. Use when a user needs mise commands or trust/activation troubleshooting.
- `npm-release` — Create and validate npm package release workflows using semver bumping, dist-tags, provenance publishing, and 2FA-aware safeguards. Use when users need npm publish/version guidance in CI or local release lanes.
- `npm-workflow-discipline` — Manage deterministic npm dependency workflows and package script contracts. Use when users need lockfile discipline, npm ci-based CI installs, or consistent package.json script behavior.
- `orchestrating-subagents` — Plan and run Codex subagent workflows using installed roles and Codex-native delegation tools. Use when the user explicitly wants subagents, parallel delegation, or swarm-style orchestration, not ordinary single-agent work or role creation.
- `pnpm-manager` — Run pnpm workspace operations with recursive and filter selectors for scoped install, test, build, and publish flows. Use when a user needs pnpm monorepo command routing.
- `powershell` — PowerShell cmdlet conventions for this project. Apply when writing or reviewing any .ps1 or module file.
- `prek-pro` — Provide docs-backed guidance for configuring and troubleshooting `prek` hooks when users need to edit `prek.toml`, install shims, validate hook behavior, or migrate from pre-commit.
- `project-brain` — Bootstrap and operate Project Brain
- `rclone` — Upload, sync, verify, or inspect files in remote storage with rclone. Use when the user wants S3, R2, B2, Google Drive, Dropbox, or similar remote file operations, not local file moves or app deployment.
- `repoprompt` — Plan and troubleshoot Repo Prompt integration across editors, agents, MCP, and CLI workflows. Use when the user wants Repo Prompt configured, adopted, or compared inside an AI coding setup.
- `reproduce-bug` — Reproduce or investigate a bug from a Linear issue or GitHub issue, preserving tracker context, symptoms, and repro steps. Use when the user wants issue-driven debugging rather than a freeform root-cause review.
- `resolve-pr-parallel` — Resolve multiple unresolved GitHub PR review threads in parallel by applying fixes, responding, and closing verified threads. Use when the user wants a broad PR-comment cleanup sweep, not readiness classification or one-off comment handling.
- `rust-pro` — Master Rust 1.75+ with modern async patterns, advanced type system features, and production-ready systems programming.
- `scaffolding-expert` — Use when users ask how to scaffold or re-scaffold a repo: this skill chooses the right tier (`lite|growth|strict`), audits drift/conflict from file evidence, and returns minimal-change remediation aligned to the user's `~/dev` git-project style.
- `sql-pro` — Master modern SQL with cloud-native databases, OLTP/OLAP optimization, and advanced query techniques.
- `swift-development` — Swift language patterns and best practices including concurrency, performance, and modern idioms. Use for Swift language-level code review or architecture guidance.
- `systematic-debugging` — Diagnose production bugs, regressions, or failing checks from concrete evidence before code changes. Use when the user wants a safe root-cause analysis and fix plan, not immediate speculative implementation.
- `test-browser` — Run or plan browser-based verification for changed web surfaces using sanctioned browser automation tools. Use when a user needs deterministic QA for routes, flows, or PR scope instead of ad hoc manual browsing.
- `toml` — Write and review TOML configuration files with predictable structure, strict typing, and tool-safe edits.
- `typescript` — Use when authoring or reviewing TypeScript code that requires strict type safety, explicit module contracts, and predictable runtime boundaries.
- `uv-python-project-setup` — Python project initialization and dependency management with uv. Use when starting new CLI tools or libraries, configuring pyproject.toml, managing virtual environments, or setting up development workflows. Covers project types, dependency commands, and environment synchronization.
- `verification-before-completion` — Validate completion claims with fresh command evidence. Use when you are about to claim work is complete, fixed, or passing.
- `writing-plans` — Compatibility wrapper for generic implementation planning. Use when the user asks for a general plan and route the work to `ce-plan` in `generic-plan` mode.
- `yaml` — Write and review YAML files with safe indentation, schema-aware structure, and low-surprise serialization.

## Skills — Backend Platform

- `backend-engineer` — Plan and review safe backend extensions for existing services (Cloudflare Workers + Hono primary). Use this skill when patching or adding backend features in an existing codebase.
- `bootstrap` — Bootstrap a local development environment from a GitHub repository URL. Use when the user asks to clone a repo, install toolchains/dependencies, and validate a working dev setup automatically.
- `circleci` — Plan, migrate, debug, or harden CircleCI pipelines and related delivery workflows. Use when the user wants CircleCI-specific config, testing, deployment, secrets, or policy help, not generic CI advice.
- `cli-spec` — Create an implementation-grade CLI specification when the user requests a binding technical contract for a new or existing command-line interface.
- `fix-mise` — Use this skill to diagnose and repair mise trust or runtime selection problems and reconcile `~/.Infrastructure/config/mise/config.toml` with required tool versions when commands fail because mise shims or trust state are broken.
- `gh-workflow` — Operate the GitHub lifecycle through `gh`: issue work, PR readiness checks, PR preparation, review handling, CI diagnosis, and merge execution. Use when the user wants GitHub state changed, advanced, or reconciled.
- `mcp-builder` — Create general-purpose MCP servers and tool schemas for standard integrations. Use when building MCP services without OAuth/billing/Apps UI requirements.
- `using-git-worktrees` — Create and validate Codex app and Claude CLI git worktree workflows with safe branch/sync strategy and cleanup guidance. Use when users request isolated checkouts; do not use for explicit in-place same-branch edits.

## Skills — Content Publishing

- `markdown-converter` — Convert source files into Markdown outputs using the bundled converter workflow. Use when a user asks to transform documents, notes, or technical files into clean Markdown format.
- `spreadsheet` — Create, edit, analyze, or format spreadsheets with formula-aware workflows and visual review. Use when the user wants `.xlsx`, `.csv`, or `.tsv` work, not plain text tables.

## Skills — Frontend Ui

- `agent-browser` — Inspect and automate browser pages deterministically with the `agent-browser` CLI. Use when the user wants ref-based navigation, extraction, clicks, fills, or screenshots, not general browsing advice.
- `agentation` — Audit or troubleshoot Agentation integrations in frontend apps with deterministic evidence gathering before edits. Use when annotations, MCP registration, endpoint sync, or webhook delivery are failing.
- `baseline-ui` — Check Tailwind UI work for accessibility, performance, theming, responsive behavior, and anti-patterns. Use when the user wants guardrail-style UI validation, scored technical audits, or targeted cleanup, not a full redesign.
- `beautiful-mermaid` — Render Mermaid diagrams to SVG and PNG with Beautiful Mermaid. Use when the user asks to render or convert Mermaid diagrams into images.
- `better-icons` — Search and extract SVG icons from Iconify collections through the better-icons CLI or MCP. Use when the user needs production-ready icons for UI work, not custom illustration design.
- `design-system` — Analyze and implement repository-grounded design-system work (tokens, typography, iconography, spacing, styles, aliases, and theme variables) for this monorepo. Use when requests involve UI styling systems or token-layer changes; don’t use for backend/MCP-only tasks with no UI impact. Outputs: evidence-backed analysis or changes with canonical file references, layer impact, and validation commands. Success: work aligns to Brand→Alias→Mapped rules and passes design-system checks.
- `favicon-generator` — Generate complete favicon/app icon suites with templates and assets. Use when the user needs favicons or app icons for a web/app project.
- `fixing-accessibility` — Audit and fix HTML accessibility issues including ARIA labels, keyboard navigation, focus management, color contrast, and form errors. Use when adding interactive controls, forms, dialogs, or reviewing WCAG compliance.
- `fixing-metadata` — Audit and fix HTML metadata including titles, descriptions, canonical URLs, Open Graph tags, Twitter cards, favicons, JSON-LD, and robots directives. Use when adding SEO metadata or shipping pages that need correct meta tags.
- `frontend-ui-design` — Design or implement production-ready frontend UI components and screens with strong visual direction, layout rhythm, spacing hierarchy, accessibility, and reusable structure. Use when the user wants standard UI build or redesign work, including fixing crowded or structurally weak layouts, not design-system governance or post-direction polish only.
- `nano-banana-builder` — Build web applications that use Google's Nano Banana image APIs for generation and iterative editing workflows. Use when a user asks to prototype or ship a Nano Banana powered image product from text-to-image to multi-turn editing.
- `og-image-creator` — Generate brand-aligned Open Graph images for existing routes by inspecting a web codebase and rendering assets with Playwright components. Use when a user asks for route-specific OG image generation or refresh in an existing app.
- `playwright-interactive` — Use a persistent Playwright session through `js_repl` to debug local web or Electron apps without restarting the browser on every step. Use when you need iterative UI automation, visual QA, or Electron inspection in the current workspace.
- `react-ui-patterns` — Provide concrete React UI composition patterns for TypeScript + Tailwind + Radix, including state, routing, and component structure examples. Use when building or refactoring React screens and components for maintainability.
- `remotion` — Best-practice guidance for Remotion (React video). Use when building or reviewing Remotion compositions, timing, assets, audio, captions, or rendering.
- `shadcn-ui` — Integrate and customize shadcn/ui components in existing projects. Use when the user asks to set up, add, adapt, or troubleshoot shadcn/ui components, registry items, and implementation patterns.
- `slides` — Create, edit, validate, or debug PowerPoint-compatible slide decks with PptxGenJS and visual overflow checks. Use when the user wants `.pptx` work, not generic web UI design or prose editing.
- `sora` — Generate, remix, manage, or download videos through OpenAI's Sora API using the bundled CLI. Use when the user wants AI video generation or asset retrieval, not traditional video editing.
- `stitch-loop` — Run iterative autonomous website-building loops with Stitch using a baton file and multi-pass page generation. Use when the user wants Stitch to keep building or refining a site over repeated passes, not one-shot UI extraction.
- `stitch-react-components` — Convert Stitch screens into modular Vite or React components with extracted structure and style-system alignment. Use when the user wants Stitch-to-React componentization, not generic React UI design.
- `stitch-remotion` — Generate Stitch-to-Remotion walkthrough videos from screen assets. Use this skill when a user asks to transform Stitch screens into narrated or demo-style videos with transitions, overlays, and rendered exports.
- `threejs-builder` — Build and validate simple, performant Three.js web apps using modern ES module patterns. Use this when you need a minimal Three.js scene, interaction, or animation for a web UI or demo.
- `ui-ux-creative-coding` — UI polish workflow for React/Tauri with motion, accessibility, and implementation-ready validation guidance.
- `ui-visual-regression` — Review and validate Storybook, Playwright, and Argos visual regression diffs. Use when the user wants snapshot-change triage or layout regression analysis, not broad frontend QA.
- `visual-explainer` — Generate self-contained HTML explainers for systems, diffs, plans, or data with clearer visual presentation than plain text. Use when the user wants a diagram or visual technical explainer, or when a large ASCII table would be hard to scan.

## Skills — Mobile Native

- `atlas` — Control the ChatGPT Atlas desktop app on macOS via AppleScript. Use when and only when the user explicitly wants Atlas tabs, bookmarks, or history manipulated on macOS, not general browser automation.
- `process-watch` — Analyze system processes and resource usage to diagnose runaway CPU/memory/IO, identify culprits, and propose next diagnostic steps. Use when investigating performance spikes or leaks.
- `test-driven-development` — Create test-first Red-Green-Refactor delivery for behavior changes. Use when implementing a feature or bugfix before writing production code.

## Skills — Product Strategy

- `architecture-interview` — Use this skill to analyze architecture alternatives through a structured interview that produces an ADR-style decision record when the user is choosing between system design options and wants tradeoffs surfaced before implementation.
- `deep-interview` — Deepen an existing doc or topic through a structured gap-filling interview that adds missing assumptions, edge cases, and approval gates. Use when refining PRDs, ADRs, tickets, notes, or draft specs before planning or execution.
- `interview-me` — Use this skill to analyze underspecified requests through a short interview and surface missing tradeoffs, assumptions, and approval gates before implementation when a prompt is underdefined and guessing would be risky.
- `notebooklm` — Analyze NotebookLM workflows for notebook management, question answering, and audio or video overviews. Use when the user wants NotebookLM actions from this environment, not general browsing or note writing.
- `ui-cloner` — Plan a branded UI clone from a target website URL with implementation-ready guidance. Use when the user wants a site's visual system recreated or adapted, not raw crawling or deployment work.

## Skills — Security Ops

- `1password` — Plan, validate, and use 1Password CLI setup for secret injection and auth. Use when tasks need 1Password CLI usage, secret references, op run/read/inject, or provisioning secrets via env vars/.env files and scripts.
- `best-practices` — Audit Better Auth integrations for secure patterns, config mistakes, and operational gaps. Use when the user wants Better Auth review, hardening, or debugging guidance, not a fresh implementation.
- `create-auth` — Implement or migrate Better Auth in TypeScript or JavaScript apps with secure defaults. Use when the user wants Better Auth added or changed in code, not just reviewed.
- `recon-workbench` — Run authorized, evidence-backed Recon Workbench (rwb) workflows (doctor/authorize/plan/run/summarize/manifest/validate/reconcile) and produce evidence-cited findings. Use when interrogating macOS/iOS, web/React, or OSS targets under explicit scope/permission.

