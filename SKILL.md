# Agent Skills Index

Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/.agents/skills`.

## Table of Contents
- [Summary](#summary)
- [Catalog](#catalog)
- [Auth](#auth)
- [Backend](#backend)
- [Frontend](#frontend)
- [Frontend — Graphics](#frontend-graphics)
- [Frontend — Tools](#frontend-tools)
- [Frontend — Ui](#frontend-ui)
- [Frontend — Website](#frontend-website)
- [Github](#github)
- [Interview](#interview)
- [Product — Content](#product-content)
- [Product — Docs](#product-docs)
- [Product — Domain](#product-domain)
- [Product — Ops](#product-ops)
- [Product — Review](#product-review)
- [Product — Security](#product-security)
- [Product — Specs](#product-specs)
- [Product — Strategy](#product-strategy)
- [Skills System](#skills-system)
- [Utilities](#utilities)

## Summary
- `total_skills`: 117
- `catalog_source`: repository skill scan
- `visibility`: default
- `policy_identity`: b380bfd98ba54e86

## Catalog

## Auth

- `best-practices` — Audit Better Auth integrations for secure patterns, config mistakes, and operational gaps. Use when the user wants Better Auth review, hardening, or debugging guidance, not a fresh implementation.
- `create-auth` — Implement or migrate Better Auth in TypeScript or JavaScript apps with secure defaults. Use when the user wants Better Auth added or changed in code, not just reviewed.

## Backend

- `backend-engineer` — Plan and review safe backend extensions for existing services (Cloudflare Workers + Hono primary). Use this skill when patching or adding backend features in an existing codebase.
- `cli-spec` — Create an implementation-grade CLI specification when the user requests a binding technical contract for a new or existing command-line interface.
- `mcp-builder` — Create general-purpose MCP servers and tool schemas for standard integrations. Use when building MCP services without OAuth/billing/Apps UI requirements.

## Frontend

- `stitch-react-components` — Convert Stitch screens into modular Vite or React components with extracted structure and style-system alignment. Use when the user wants Stitch-to-React componentization, not generic React UI design.

## Frontend — Graphics

- `better-icons` — Search and extract SVG icons from Iconify collections through the better-icons CLI or MCP. Use when the user needs production-ready icons for UI work, not custom illustration design.
- `favicon-generator` — Generate complete favicon/app icon suites with templates and assets. Use when the user needs favicons or app icons for a web/app project.
- `nano-banana-builder` — Build web applications that use Google's Nano Banana image APIs for generation and iterative editing workflows. Use when a user asks to prototype or ship a Nano Banana powered image product from text-to-image to multi-turn editing.
- `og-image-creator` — Generate brand-aligned Open Graph images for existing routes by inspecting a web codebase and rendering assets with Playwright components. Use when a user asks for route-specific OG image generation or refresh in an existing app.
- `sora` — Generate, remix, manage, or download videos through OpenAI's Sora API using the bundled CLI. Use when the user wants AI video generation or asset retrieval, not traditional video editing.
- `threejs-builder` — Build and validate simple, performant Three.js web apps using modern ES module patterns. Use this when you need a minimal Three.js scene, interaction, or animation for a web UI or demo.

## Frontend — Tools

- `agentation` — Audit or troubleshoot Agentation integrations in frontend apps with deterministic evidence gathering before edits. Use when annotations, MCP registration, endpoint sync, or webhook delivery are failing.
- `playwright-interactive` — Use a persistent Playwright session through `js_repl` to debug local web or Electron apps without restarting the browser on every step. Use when you need iterative UI automation, visual QA, or Electron inspection in the current workspace.
- `stitch-loop` — Run iterative autonomous website-building loops with Stitch using a baton file and multi-pass page generation. Use when the user wants Stitch to keep building or refining a site over repeated passes, not one-shot UI extraction.
- `test-browser` — Run or plan browser-based verification for changed web surfaces using sanctioned browser automation tools. Use when a user needs deterministic QA for routes, flows, or PR scope instead of ad hoc manual browsing.
- `ui-cloner` — Plan a branded UI clone from a target website URL with implementation-ready guidance. Use when the user wants a site's visual system recreated or adapted, not raw crawling or deployment work.

## Frontend — Ui

- `baseline-ui` — Check Tailwind UI work for accessibility, performance, theming, responsive behavior, and anti-patterns. Use when the user wants guardrail-style UI validation, scored technical audits, or targeted cleanup, not a full redesign.
- `design-system` — Analyze and implement repository-grounded design-system work (tokens, typography, iconography, spacing, styles, aliases, and theme variables) for this monorepo. Use when requests involve UI styling systems or token-layer changes; don’t use for backend/MCP-only tasks with no UI impact. Outputs: evidence-backed analysis or changes with canonical file references, layer impact, and validation commands. Success: work aligns to Brand→Alias→Mapped rules and passes design-system checks.
- `frontend-design` — Analyze broad frontend design requests and route them to the correct local UI skill after classifying intent and maturity. Use when the user asks for frontend design generally and the specific design owner is not yet clear.
- `frontend-ui-design` — Design or implement production-ready frontend UI components and screens with strong visual direction, layout rhythm, spacing hierarchy, accessibility, and reusable structure. Use when the user wants standard UI build or redesign work, including fixing crowded or structurally weak layouts, not design-system governance or post-direction polish only.
- `react-ui-patterns` — Provide concrete React UI composition patterns for TypeScript + Tailwind + Radix, including state, routing, and component structure examples. Use when building or refactoring React screens and components for maintainability.
- `remotion` — Best-practice guidance for Remotion (React video). Use when building or reviewing Remotion compositions, timing, assets, audio, captions, or rendering.
- `shadcn-ui` — Integrate and customize shadcn/ui components in existing projects. Use when the user asks to set up, add, adapt, or troubleshoot shadcn/ui components, registry items, and implementation patterns.
- `stitch-remotion` — Generate Stitch-to-Remotion walkthrough videos from screen assets. Use this skill when a user asks to transform Stitch screens into narrated or demo-style videos with transitions, overlays, and rendered exports.
- `ui-ux-creative-coding` — UI polish workflow for React/Tauri with motion, accessibility, and implementation-ready validation guidance.
- `ui-visual-regression` — Review and validate Storybook, Playwright, and Argos visual regression diffs. Use when the user wants snapshot-change triage or layout regression analysis, not broad frontend QA.

## Frontend — Website

- `fixing-accessibility` — Audit and fix HTML accessibility issues including ARIA labels, keyboard navigation, focus management, color contrast, and form errors. Use when adding interactive controls, forms, dialogs, or reviewing WCAG compliance.
- `fixing-metadata` — Audit and fix HTML metadata including titles, descriptions, canonical URLs, Open Graph tags, Twitter cards, favicons, JSON-LD, and robots directives. Use when adding SEO metadata or shipping pages that need correct meta tags.

## Github

- `gh-workflow` — Operate the GitHub lifecycle through `gh`: issue work, PR readiness checks, PR preparation, review handling, CI diagnosis, and merge execution. Use when the user wants GitHub state changed, advanced, or reconciled.
- `prek-pro` — Provide docs-backed guidance for configuring and troubleshooting `prek` hooks when users need to edit `prek.toml`, install shims, validate hook behavior, or migrate from pre-commit.
- `resolve-pr-parallel` — Resolve multiple unresolved GitHub PR review threads in parallel by applying fixes, responding, and closing verified threads. Use when the user wants a broad PR-comment cleanup sweep, not readiness classification or one-off comment handling.

## Interview

- `architecture-interview` — Use this skill to analyze architecture alternatives through a structured interview that produces an ADR-style decision record when the user is choosing between system design options and wants tradeoffs surfaced before implementation.
- `deep-interview` — Deepen an existing doc or topic through a structured gap-filling interview that adds missing assumptions, edge cases, and approval gates. Use when refining PRDs, ADRs, tickets, notes, or draft specs before planning or execution.
- `interview-me` — Use this skill to analyze underspecified requests through a short interview and surface missing tradeoffs, assumptions, and approval gates before implementation when a prompt is underdefined and guessing would be risky.

## Product — Content

- `changelog` — Create engaging changelogs for recent merges to main branch with a witty, enthusiastic marketing voice. Use when the user wants a daily or weekly engineering summary, release-note style update, or Discord-ready changelog that highlights features, bugs, and gives contributor credit with personality.
- `every-style-editor` — Edit prose to conform to Every's editorial house style, including grammar, punctuation, mechanics, and naming conventions. Use when the user wants articles, newsletters, social copy, or other branded editorial writing polished, not repo docs QA.
- `feature-video` — Produce a concise feature walkthrough video and package the result for review or release workflows. Use when a user needs a demo artifact, PR-ready walkthrough, or polished clip for a shipped product change.
- `video-transcript-downloader` — Download video or audio and extract transcripts or subtitles with yt-dlp and ffmpeg. Use when the user wants media downloaded, transcribed, summarized, or converted from a video source.
- `youtube-hooks-scripts` — Use this skill to create high-retention hooks, outlines, and full scripts for technical YouTube videos when the user wants YouTube scripting help tailored to a topic, audience, and target runtime.
- `youtube-titles-thumbnails` — Generate SEO/CTR-oriented YouTube title options and thumbnail copy variants with rationale. Use when the user wants video packaging ideas, not a full script or production plan.

## Product — Docs

- `agents-md` — Create or refactor AGENTS.md and linked instruction docs using progressive disclosure. Use when the user wants repo-specific agent guidance organized, deduplicated, or routed cleanly, not ordinary product documentation edits.
- `context7` — Analyze current external library/API documentation and generate Context7 CLI guidance when the user asks for version-sensitive dependency behavior, library API references, or Context7 skills/setup/auth command help.
- `docs-expert` — Audit and rewrite repository documentation, runbooks, and in-code docs with repo-visibility and brand-quality checks. Use when the user wants README, docs, JSDoc, DocC, or config documentation improved, not editorial house-style copyediting.
- `llm-wiki` — Create and maintain an LLM-managed markdown wiki that incrementally compiles source material into a persistent, queryable knowledge base; use this skill when users ask for persistent wiki architecture, ingest/query/lint workflows, or schema governance.

## Product — Domain

- `agent-native-architecture` — Build applications where agents are first-class citizens. Use this skill when designing autonomous agents, creating MCP tools, implementing self-modifying systems, or building apps where features are outcomes achieved by agents operating in a loop.
- `chatgpt-apps` — Build, refactor, or troubleshoot ChatGPT Apps SDK apps that combine MCP tools and widget UI. Use when the user wants Apps SDK tool registration, UI resources, bridge wiring, CSP or domain setup, or docs-aligned scaffolding.
- `oak-api` — Build or adapt Oak Curriculum API learning experiences, especially child-facing Apps SDK flows. Use when the user wants Oak endpoints or curriculum data turned into guided learning interactions with age-appropriate guardrails.

## Product — Ops

- `decide-build-primitive` — Use this skill to analyze whether a capability should become a Skill, Custom Prompt, or Agent automation when the user is packaging or automating a workflow and the right Codex primitive is not yet clear.
- `fallback-release` — Execute deterministic fallback releases when primary CI is unavailable. Use when GitHub Actions is stalled due to queue congestion, rate limits, or incidents, and critical releases cannot wait.
- `production-deployment` — Deploy and manage production services across various platforms with automated verification and rollback safety.
- `release` — Cut a clean semver release from the main branch using the repo's release flow. Use when the user wants a tagged Cargo release, not generic deployment or changelog drafting.
- `resolve-todo-parallel` — WHAT: Resolve file-based `todos/` items with dependency-aware serial or bounded-parallel execution, verification, and cleanup controls. WHEN: Use when a todo-sweep is the primary task, not generic single-feature implementation.
- `triage` — Triage file-based `todos/` findings into ready, skipped, or revised states before execution. Use when the repo already uses the file-based todo workflow and the user wants approval-style triage, not tracker triage or todo execution.

## Product — Review

- `agent-native-audit` — Audit a repository, workflow, or feature against agent-native operating principles and return evidence-backed gaps plus remediation priorities. Use when a user asks whether agents can realistically discover, execute, verify, and maintain a workflow end to end.

## Product — Security

- `security-best-practices` — Review code or architecture against language-specific security best practices. Use when the user explicitly wants a security best-practices review or secure-by-default guidance, not general debugging or code review.
- `security-ownership-map` — Use this skill to analyze security ownership in a git repository by linking people, files, bus factor, and sensitive-code risk when the user explicitly wants security-focused ownership analysis from git history.
- `security-threat-model` — Produce a repository-grounded threat model covering assets, trust boundaries, attackers, abuse paths, and mitigations. Use when the user explicitly wants AppSec threat modeling, not general architecture review.

## Product — Specs

- `product-spec` — Create or review product-planning specifications from ideas or existing docs. Use when the user wants a PRD, UX, API, architecture, operator, or test-plan artifact, not the narrower CE spec stage.

## Product — Strategy

- `brainstorming` — Clarify ambiguous product or implementation directions by comparing a few viable approaches and recommending one. Use when the user wants general brainstorming before planning or building, not the compound-engineering stage artifact.
- `product-design-critic` — Critique product surfaces and flows with opinionated UX judgment about hierarchy, trust, and jobs-to-be-done. Use when the user wants product-level interaction or workflow critique, not pure visual styling advice.
- `project-improver` — Analyze an existing project and propose or implement high-leverage improvements with strong product judgment. Use when the user wants grounded improvement opportunities ranked and refined, not a single-feature spec.

## Skills System

- `imagegen` — Generate or edit raster images when a task needs bitmap outputs such as photos, illustrations, textures, sprites, mockups, or transparent-background cutouts. Use for net-new images, edits to existing images, or variants from references. Prefer repo-native SVG/code workflows for vector icon/logo systems or deterministic code-built graphics.
- `openai-docs` — Use when the user asks how to build with OpenAI products or APIs and needs up-to-date official documentation with citations, help choosing the latest model for a use case, or explicit GPT-5.4 upgrade and prompt-upgrade guidance; prioritize OpenAI docs MCP tools, use bundled references only as helper context, and restrict any fallback browsing to official OpenAI domains.

## Utilities

- `1password` — Plan, validate, and use 1Password CLI setup for secret injection and auth. Use when tasks need 1Password CLI usage, secret references, op run/read/inject, or provisioning secrets via env vars/.env files and scripts.
- `agent-browser` — Inspect and automate browser pages deterministically with the `agent-browser` CLI. Use when the user wants ref-based navigation, extraction, clicks, fills, or screenshots, not general browsing advice.
- `alignment-checkpoint` — Intent-alignment gate for ambiguous/high-stakes requests. Use this when you want to extract goal/assumptions/criteria and require an explicit /proceed approval gate before any tool use.
- `atlas` — Control the ChatGPT Atlas desktop app on macOS via AppleScript. Use when and only when the user explicitly wants Atlas tabs, bookmarks, or history manipulated on macOS, not general browser automation.
- `autoresearch` — Analyze and improve this repo's skills and plugin packages through bounded experiment loops. Use this skill when users request autonomous research passes with hypothesis-validation-keep/discard decisions.
- `bash-hygiene` — Write and review Bash scripts with safe structure and portability guardrails. Use when shell work needs strict mode defaults, robust quoting, and interpreter-compatible behavior.
- `beautiful-mermaid` — Render Mermaid diagrams to SVG and PNG with Beautiful Mermaid. Use when the user asks to render or convert Mermaid diagrams into images.
- `biome-linting` — Guide Biome linting and formatting workflows with safe-fix strategy and CI-ready rule triage. Use when a user needs Biome command, diagnostics, or remediation guidance in JavaScript/TypeScript projects.
- `bootstrap` — Bootstrap a local development environment from a GitHub repository URL. Use when the user asks to clone a repo, install toolchains/dependencies, and validate a working dev setup automatically.
- `circleci` — Plan, migrate, debug, or harden CircleCI pipelines and related delivery workflows. Use when the user wants CircleCI-specific config, testing, deployment, secrets, or policy help, not generic CI advice.
- `claude-alias` — Diagnose, repair, and harden Claude wrapper alias routing (`ck`, `cz`, `cc`) when provider configs drift or auth/model conflicts return the wrong backend.
- `codex-agent-creator` — Create, install, and validate Codex custom subagents as standalone TOMLs with canonical global defaults (`~/dev/configs/codex/agents/{name}/{name}.toml`, `~/dev/configs/codex/config.toml`) plus optional project scope (`${project_root}/.codex/agents/{name}/{name}.toml`), where project config writes occur only when runtime-limit flags are explicitly requested.
- `codex-automation-architect` — Design, review, or merge Codex app automations using current OpenAI/Codex guidance and validation. Use when the user wants recurring Codex automation workflows built, audited, or consolidated.
- `codex-home-audit` — Audit a Codex home directory for control-plane drift, risky state, and cleanup opportunities across config, agents, hooks, skills, plugins, and telemetry. Use when the user wants a dated Codex home health review.
- `codex-hooks-builder` — Create, upgrade, or audit Codex hook packs for repo-local or user-level `.codex` installs. Use when the user wants hook runtime files or hook-script hardening, not general agent role creation.
- `coding-harness` — Use when a repository needs `@brainwav/coding-harness` installed, bootstrapped, updated, audited, or explained. Covers `harness init`, harness-managed CI migration, governance checks, and Codex environment action-sync guidance. Do not use for unrelated coding, general deployment, or broad cloud work.
- `diagram-cli` — Generate, validate, and refresh @brainwav/diagram architecture artifacts and context packs. Use when the user wants repository architecture diagrams for onboarding, PR impact, or CI drift checks, not hand-drawn product mock diagrams.
- `elixir-pro` — Write idiomatic Elixir code with OTP patterns, supervision trees, and Phoenix LiveView. Masters concurrency, fault tolerance, and distributed systems.
- `evals-router` — Route and guide LLM evaluation work such as evaluator design, error analysis, RAG evals, and synthetic eval data. Use when the user wants eval-specific workflow help, not product analytics or ordinary QA.
- `fix-mise` — Use this skill to diagnose and repair mise trust or runtime selection problems and reconcile `~/.config/mise/config.toml` with required tool versions when commands fail because mise shims or trust state are broken.
- `go` — Best practices for working with Go codebases. Use when writing, debugging, or exploring Go code, including reading dependency sources and documentation.
- `insight-report` — WHAT: Generate comprehensive HTML insights from Codex OTEL data using local Ollama LLMs. WHEN: Use when the user asks for usage analytics, workflow patterns, Codex session summaries, or recommendations for improving their development workflow.
- `javascript-pro` — Master modern JavaScript with ES6+, async patterns, and Node.js APIs. Handles promises, event loops, and browser/Node compatibility.
- `markdown-converter` — Convert source files into Markdown outputs using the bundled converter workflow. Use when a user asks to transform documents, notes, or technical files into clean Markdown format.
- `mise-tooling` — Operate mise tool-version workflows with trust-aware config loading, local/global version pinning, and deterministic runtime execution. Use when a user needs mise commands or trust/activation troubleshooting.
- `notebooklm` — Analyze NotebookLM workflows for notebook management, question answering, and audio or video overviews. Use when the user wants NotebookLM actions from this environment, not general browsing or note writing.
- `npm-release` — Create and validate npm package release workflows using semver bumping, dist-tags, provenance publishing, and 2FA-aware safeguards. Use when users need npm publish/version guidance in CI or local release lanes.
- `npm-workflow-discipline` — Manage deterministic npm dependency workflows and package script contracts. Use when users need lockfile discipline, npm ci-based CI installs, or consistent package.json script behavior.
- `orchestrating-subagents` — Plan and run Codex subagent workflows using installed roles and Codex-native delegation tools. Use when the user explicitly wants subagents, parallel delegation, or swarm-style orchestration, not ordinary single-agent work or role creation.
- `pnpm-manager` — Run pnpm workspace operations with recursive and filter selectors for scoped install, test, build, and publish flows. Use when a user needs pnpm monorepo command routing.
- `powershell` — PowerShell cmdlet conventions for this project. Apply when writing or reviewing any .ps1 or module file.
- `process-watch` — Analyze system processes and resource usage to diagnose runaway CPU/memory/IO, identify culprits, and propose next diagnostic steps. Use when investigating performance spikes or leaks.
- `project-brain` — Bootstrap and operate Project Brain
- `rclone` — Upload, sync, verify, or inspect files in remote storage with rclone. Use when the user wants S3, R2, B2, Google Drive, Dropbox, or similar remote file operations, not local file moves or app deployment.
- `recon-workbench` — Run authorized, evidence-backed Recon Workbench (rwb) workflows (doctor/authorize/plan/run/summarize/manifest/validate/reconcile) and produce evidence-cited findings. Use when interrogating macOS/iOS, web/React, or OSS targets under explicit scope/permission.
- `repoprompt` — Plan and troubleshoot Repo Prompt integration across editors, agents, MCP, and CLI workflows. Use when the user wants Repo Prompt configured, adopted, or compared inside an AI coding setup.
- `reproduce-bug` — Reproduce or investigate a bug from a Linear issue or GitHub issue, preserving tracker context, symptoms, and repro steps. Use when the user wants issue-driven debugging rather than a freeform root-cause review.
- `rust-pro` — Master Rust 1.75+ with modern async patterns, advanced type system features, and production-ready systems programming.
- `scaffolding-expert` — Use when users ask how to scaffold or re-scaffold a repo: this skill chooses the right tier (`lite|growth|strict`), audits drift/conflict from file evidence, and returns minimal-change remediation aligned to the user's `~/dev` git-project style.
- `slides` — Create, edit, validate, or debug PowerPoint-compatible slide decks with PptxGenJS and visual overflow checks. Use when the user wants `.pptx` work, not generic web UI design or prose editing.
- `spreadsheet` — Create, edit, analyze, or format spreadsheets with formula-aware workflows and visual review. Use when the user wants `.xlsx`, `.csv`, or `.tsv` work, not plain text tables.
- `sql-pro` — Master modern SQL with cloud-native databases, OLTP/OLAP optimization, and advanced query techniques.
- `swift-development` — Swift language patterns and best practices including concurrency, performance, and modern idioms. Use for Swift language-level code review or architecture guidance.
- `systematic-debugging` — Diagnose production bugs, regressions, or failing checks from concrete evidence before code changes. Use when the user wants a safe root-cause analysis and fix plan, not immediate speculative implementation.
- `test-driven-development` — Create test-first Red-Green-Refactor delivery for behavior changes. Use when implementing a feature or bugfix before writing production code.
- `toml` — Write and review TOML configuration files with predictable structure, strict typing, and tool-safe edits.
- `typescript` — Use when authoring or reviewing TypeScript code that requires strict type safety, explicit module contracts, and predictable runtime boundaries.
- `using-git-worktrees` — Create and validate Codex app and Claude CLI git worktree workflows with safe branch/sync strategy and cleanup guidance. Use when users request isolated checkouts; do not use for explicit in-place same-branch edits.
- `uv-python-project-setup` — Python project initialization and dependency management with uv. Use when starting new CLI tools or libraries, configuring pyproject.toml, managing virtual environments, or setting up development workflows. Covers project types, dependency commands, and environment synchronization.
- `verification-before-completion` — Validate completion claims with fresh command evidence. Use when you are about to claim work is complete, fixed, or passing.
- `visual-explainer` — Generate self-contained HTML explainers for systems, diffs, plans, or data with clearer visual presentation than plain text. Use when the user wants a diagram or visual technical explainer, or when a large ASCII table would be hard to scan.
- `yaml` — Write and review YAML files with safe indentation, schema-aware structure, and low-surprise serialization.

