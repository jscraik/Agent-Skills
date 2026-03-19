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
- [Github — Greptile](#github-greptile)
- [Interview](#interview)
- [Product — Content](#product-content)
- [Product — Docs](#product-docs)
- [Product — Domain](#product-domain)
- [Product — Ops](#product-ops)
- [Product — Security](#product-security)
- [Product — Specs](#product-specs)
- [Product — Strategy](#product-strategy)
- [Utilities](#utilities)

## Summary
- `total_skills`: 92
- `catalog_source`: `.agents/skills` flat runtime view

## Catalog

## Auth

- `best-practices` — Review Better Auth setups and highlight secure integration best practices. Use for audits, config guidance, or debugging flows (not full implementation). Use when the user requests this capability.
- `create-auth` — Build Better Auth integrations for TS/JS apps with secure defaults. Use for implementation or migration work (not just review). Use when the user requests this capability.

## Backend

- `backend-engineer` — Plan and review safe backend extensions for existing services (Cloudflare Workers + Hono primary). Use this skill when patching or adding backend features in an existing codebase.
- `cli-spec` — Plan and draft CLI UX and surface area (commands, flags, help, output). Use when specifying or refactoring a command-line interface.
- `mcp-builder` — Create general-purpose MCP servers and tool schemas for standard integrations. Use when building MCP services without OAuth/billing/Apps UI requirements.
- `workers-mcp` — Create and deploy production-ready MCP servers on Cloudflare Workers. Use when building a Workers-hosted MCP server with auth, billing, and operational guardrails.

## Frontend

- `stitch-react-components` — Use this skill when the user asks to convert Stitch screens into modular Vite/React components with validated structure, data extraction, and style-system alignment.

## Frontend — Graphics

- `better-icons` — Use this skill to search and extract SVG icons via the better-icons CLI or MCP. Use when you need icons from Iconify collections for UI/UX work, product mocks, or codebases.
- `favicon-generator` — Generate complete favicon/app icon suites with templates and assets. Use when the user needs favicons or app icons for a web/app project.
- `imagegen` — Use when the user asks to generate or edit images via the OpenAI Image API (for example: generate image, edit/inpaint/mask, background removal or replacement, transparent background, product shots, concept art, covers, or batch variants); run the bundled CLI (`scripts/image_gen.py`) and require `OPENAI_API_KEY` for live calls.
- `nano-banana-builder` — Build web applications that use Google's Nano Banana image APIs for generation and iterative editing workflows. Use when a user asks to prototype or ship a Nano Banana powered image product from text-to-image to multi-turn editing.
- `og-image-creator` — Generate brand-aligned Open Graph images for existing routes by inspecting a web codebase and rendering assets with Playwright components. Use when a user asks for route-specific OG image generation or refresh in an existing app.
- `sora` — Use when the user asks to generate, remix, poll, list, download, or delete Sora videos via OpenAI’s video API using the bundled CLI (`scripts/sora.py`), including requests like “generate AI video,” “Sora,” “video remix,” “download video/thumbnail/spritesheet,” and batch video generation; requires `OPENAI_API_KEY` and Sora API access.
- `threejs-builder` — Build and validate simple, performant Three.js web apps using modern ES module patterns. Use this when you need a minimal Three.js scene, interaction, or animation for a web UI or demo.

## Frontend — Tools

- `agentation` — Analyze and verify Agentation integrations in frontend apps when annotations, MCP registration, endpoint sync, or webhook delivery are failing; use this when you need deterministic evidence before edits.
- `figma` — Use this canonical Figma skill to extract design context/screenshots/assets with Figma MCP and build production-ready UI guidance. Use when requests include Figma URLs/node IDs, design-to-code implementation, or Figma MCP setup/troubleshooting.
- `playwright-interactive` — Use a persistent Playwright session through `js_repl` to debug local web or Electron apps without restarting the browser on every step. Use when you need iterative UI automation, visual QA, or Electron inspection in the current workspace.
- `stitch-loop` — Use this skill when the user asks for iterative autonomous website building with Stitch using a baton file (`next-prompt.md`) and multi-pass page generation.
- `ui-cloner` — Build a structured UI replication plan from a target website URL and adapt it to the user's brand with implementation-ready guidance. Use when users ask to clone, recreate, or emulate a site's visual system; do not use for Cloudflare crawl orchestration-only requests or generic deployment work.

## Frontend — Ui

- `baseline-ui` — Validates animation durations, enforces typography scale, checks component accessibility, and prevents layout anti-patterns in Tailwind CSS projects. Use when building UI components, reviewing CSS utilities, styling React views, or enforcing design consistency.
- `design-system` — Analyze and implement repository-grounded design-system work (tokens, typography, iconography, spacing, styles, aliases, and theme variables) for this monorepo. Use when requests involve UI styling systems or token-layer changes; don’t use for backend/MCP-only tasks with no UI impact. Outputs: evidence-backed analysis or changes with canonical file references, layer impact, and validation commands. Success: work aligns to Brand→Alias→Mapped rules and passes design-system checks.
- `frontend-ui-design` — Create and review production-ready UI systems/components with tokens and accessibility. Use for standard UI implementation or redesign (not creative-coding polish). Use when the user requests this capability.
- `react-ui-patterns` — Provide concrete React UI composition patterns for TypeScript + Tailwind + Radix, including state, routing, and component structure examples. Use when building or refactoring React screens and components for maintainability.
- `remotion` — Best-practice guidance for Remotion (React video). Use when building or reviewing Remotion compositions, timing, assets, audio, captions, or rendering.
- `shadcn-ui` — Integrate and customize shadcn/ui components in existing projects. Use when the user asks to set up, add, adapt, or troubleshoot shadcn/ui components, registry items, and implementation patterns.
- `stitch-remotion` — Generate Stitch-to-Remotion walkthrough videos from screen assets. Use this skill when a user asks to transform Stitch screens into narrated or demo-style videos with transitions, overlays, and rendered exports.
- `ui-ux-creative-coding` — UI polish workflow for React/Tauri with motion, accessibility, and implementation-ready validation guidance.
- `ui-visual-regression` — Review and validate UI visual regression diffs (Storybook + Playwright capture + Argos) when snapshot changes or layout regressions appear.

## Frontend — Website

- `fixing-accessibility` — Audit and fix HTML accessibility issues including ARIA labels, keyboard navigation, focus management, color contrast, and form errors. Use when adding interactive controls, forms, dialogs, or reviewing WCAG compliance.
- `fixing-metadata` — Audit and fix HTML metadata including titles, descriptions, canonical URLs, Open Graph tags, Twitter cards, favicons, JSON-LD, and robots directives. Use when adding SEO metadata or shipping pages that need correct meta tags.

## Github

- `gh-fix-ci` — Use when a user asks to debug or fix failing GitHub PR checks that run in GitHub Actions; use `gh` to inspect checks and logs, summarize failure context, draft a fix plan, and implement only after explicit approval. Treat external providers (for example Buildkite) as out of scope and report only the details URL.
- `gh-workflow` — Consolidated GitHub lifecycle skill for agents and users: intake, issue fixing, PR prep, review request/reception, review comment handling, CI diagnosis, and server-side merge via gh. Use when requests involve GitHub issues/PRs/checks/merge operations.

## Github — Greptile

- `check-pr` — Use when a user asks to review a GitHub pull request before merge (or asks how to set up Greptile prerequisites) and return a policy-gated readiness view with check status and remediation priority.

## Interview

- `architecture-interview` — Plan and review architecture decisions via a structured interview and ADR output. Use when choosing between system design alternatives.
- `deep-interview` — Deep, gap-filling interview that enhances an existing doc/spec (preferred) or explores a topic. Use when deepening PRDs, ADRs, tickets, notes, or draft specs; if given a doc path, update it in-place with Delta/Interview Insights and an approval gate.
- `interview-me` — Analyze underspecified requests when tradeoff decisions are missing and run concise interviews to capture assumptions and explicit approval before implementation begins.

## Product — Content

- `video-transcript-downloader` — Extract, summarize, and download video/audio/subtitles using yt-dlp/ffmpeg. Use when the user requests downloads or transcripts.
- `youtube-hooks-scripts` — Create high-retention hooks and full scripts for technical YouTube videos tailored to topic, audience, and length. Use when the user asks for a hook, outline, or full script.
- `youtube-titles-thumbnails` — Generate multiple SEO/CTR-optimized YouTube title and thumbnail text options with variants and rationale. Use when the user wants packaging ideas, titles, or thumbnail copy.

## Product — Docs

- `agents-md` — Refactor or create AGENTS.md using progressive disclosure: keep root guidance minimal, split detailed instructions into linked docs, and flag contradictions or redundancy. Use this skill when the user asks to create, update, or refactor AGENTS.md.
- `context7` — Extract current library documentation via Context7 when users need up-to-date API details, version checks, or dependency troubleshooting for external libraries.
- `docs-expert` — Use when asked to audit or rewrite repository docs (README, docs, runbooks, community-health files) or when code has missing in-code documentation (JSDoc/DocC/config docs): enforce official brand guidance, harden GitHub visibility signals, and deliver evidence-bundled docs QA.
- `openai-docs` — Use when the user asks how to build with OpenAI products or APIs and needs up-to-date official documentation with citations, help choosing the latest model for a use case, or explicit GPT-5.4 upgrade and prompt-upgrade guidance; prioritize OpenAI docs MCP tools, use bundled references only as helper context, and restrict any fallback browsing to official OpenAI domains.

## Product — Domain

- `arscontexta` — Use when you need to install, validate, or maintain Ars Contexta parity in Codex; mirrors skills/prompts/agents/automations and returns a parity report with any Codex-vs-Claude deltas.
- `chatgpt-apps` — Build, scaffold, refactor, and troubleshoot ChatGPT Apps SDK applications that combine an MCP server and widget UI. Use when Codex needs to design tools, register UI resources, wire the MCP Apps bridge or ChatGPT compatibility APIs, apply Apps SDK metadata or CSP or domain settings, or produce a docs-aligned project scaffold grounded in current OpenAI docs.
- `cloudflare-deploy` — Deploy applications and infrastructure to Cloudflare using Workers, Pages, and related platform services. Use when the user asks to deploy, host, publish, or set up a project on Cloudflare.
- `oak-api` — Build or adapt Oak Curriculum API driven learning experiences, especially for child-facing, interactive ChatGPT Apps SDK workflows. Use when working with Oak API endpoints, curriculum data (subjects, units, lessons, quizzes, search), or when translating Oak content into adaptive learning activities with age-appropriate guardrails and compliance reminders.

## Product — Ops

- `compound-engineering-router` — Route Codex compound-engineering requests to the correct workflow prompt or meta-mode in the config repo, with optional NotebookLM evidence for spec quality, agent orchestration, and Codex operating patterns. Use when a user wants brainstorm, spec, plan, work, review, technical review, compound workflow guidance, context compaction, or guardrail extraction rather than direct feature coding.
- `decide-build-primitive` — Analyze and decide the right Codex primitive (Skill, Custom Prompt, or Agent automation) for a capability. Use this when you need to plan how to package or automate a workflow.
- `linear` — Manage Linear issues, projects, and docs through the Linear MCP workflow with consistent read/create/update operations. Use when a user asks to triage, create, update, or report on Linear work items.
- `release` — Create and publish a new project release (semver) when you need to cut a main-branch, clean-tree release via just release X.Y.Z for Cargo publish and git tag creation.

## Product — Security

- `security-best-practices` — Perform language and framework specific security best-practice reviews and suggest improvements. Trigger only when the user explicitly requests security best practices guidance, a security review/report, or secure-by-default coding help. Trigger only for supported languages (python, javascript/typescript, go). Do not trigger for general code review, debugging, or non-security tasks.
- `security-ownership-map` — Analyze git repositories to map security ownership (people-to-file), compute bus-factor and sensitive-code risk, and export CSV/JSON/graph artifacts for visualization. Use only when the user explicitly requests security-focused ownership analysis grounded in git history.
- `security-threat-model` — Repository-grounded threat modeling that enumerates trust boundaries, assets, attacker capabilities, abuse paths, and mitigations, and writes a concise Markdown threat model. Trigger only when the user explicitly asks to threat model a codebase or path, enumerate threats/abuse paths, or perform AppSec threat modeling. Do not trigger for general architecture summaries, code review, or non-security design work.

## Product — Specs

- `product-spec` — Create or review implementation-ready product specifications from ideas or existing docs. Use when you need a full PRD+UX+build plan pipeline or a focused mode (clarify_prd, ux_only, api_spec, arch_spec, testplan).

## Product — Strategy

- `brainstorming` — Use before planning or implementation when a request is ambiguous, has multiple valid approaches, or needs trade-off exploration. Clarify what to build, compare 2-3 approaches, and recommend a direction before moving into planning.
- `product-design-critic` — Use this skill when the user asks to critique or shape a software product surface, workflow, card, panel, or chat UX. It analyzes and reviews product decisions with opinionated recommendations grounded in jobs-to-be-done, hierarchy, trust/governance cues, and explicit tradeoffs beyond visual polish.
- `project-improver` — Analyze an existing project and design high-leverage improvements when the user wants stronger functionality, sharper product judgment, rigorous idea filtering, premortems, hybrid plan revisions, or immediate implementation of the best upgrades.

## Utilities

- `1password` — Plan, validate, and use 1Password CLI setup for secret injection and auth. Use when tasks need 1Password CLI usage, secret references, op run/read/inject, or provisioning secrets via env vars/.env files and scripts.
- `agent-browser` — Use this skill to extract page state and automate web interactions with the agent-browser CLI (navigate, snapshot, click, fill, screenshot). Use this when you need deterministic browser automation or scraping via ref-based elements.
- `alignment-checkpoint` — Intent-alignment gate for ambiguous/high-stakes requests. Use this when you want to extract goal/assumptions/criteria and require an explicit /proceed approval gate before any tool use.
- `apple-app-creator` — Orchestrate iOS/macOS app scaffolding and optional subskill adoption for existing projects. Use when users need a guided wizard to scaffold with XcodeGen and optionally install xcode-makefiles and simple-tasks.
- `atlas` — macOS-only AppleScript control for the ChatGPT Atlas desktop app. Use only when the user explicitly asks to control Atlas tabs/bookmarks/history on macOS and the "ChatGPT Atlas" app is installed; do not trigger for general browser tasks or non-macOS environments.
- `beautiful-mermaid` — Render Mermaid diagrams to SVG and PNG with Beautiful Mermaid. Use when the user asks to render or convert Mermaid diagrams into images.
- `bootstrap` — Bootstrap a local development environment from a GitHub repository URL. Use when the user asks to clone a repo, install toolchains/dependencies, and validate a working dev setup automatically.
- `cf-crawl` — Crawl websites with Cloudflare Browser Rendering's /crawl API and export markdown or JSON results locally. Use when a user needs an authenticated Cloudflare crawl job started, monitored, or exported; do not use it for generic scraping or browser automation outside Cloudflare.
- `circleci` — Use this skill when the user asks for CircleCI migration, orchestration, testing, deployment, optimization, security/secrets, config policy, integration, or developer toolkit guidance.
- `codex-agent-creator` — Create and install Codex custom multi-agent roles when role creation, validation, or safe update is requested, using secure minimal-change configuration.
- `codex-automation-architect` — Create, review, and merge Codex app automations; use when users need recurring automation design or consolidation with current OpenAI/Codex guidance, environment preflight, and headless multi-runner validation.
- `codex-home-audit` — Audit and improve a Codex home directory (AGENTS.md, USER_PROFILE, instructions/, rules/, config.toml) when you want a dated report of risks, duplication, and recommended cleanups.
- `codex-plugin-builder` — Create, convert, and validate Codex plugin packages that include focused skills, prompts, hooks, agents, and MCP metadata. Use this skill when the user asks to scaffold plugin bundles, safely convert external plugin sources, or quality-gate plugin-owned skills; do not use it for unrelated app feature work.
- `codex-sessions-skill-scan` — Session-driven skill intelligence: run daily health scans over ~/.codex sessions to detect skill failures and, when requested, audit project-local skill coverage to recommend merge/fold/improve-existing/install-new decisions grounded in memory and rollout evidence.
- `diagram-cli` — Generate, validate, and refresh @brainwav/diagram architecture artifacts (.mmd/.svg/.diagram manifest + context packs). Use this skill when users need fast repository understanding for onboarding, PR architecture impact, and CI drift checks; do not use it for hand-drawn product/UI mock diagrams.
- `evals-router` — Use when tasks involve designing, auditing, debugging, or scaling LLM evaluation workflows such as error analysis, judge prompt design, evaluator validation, RAG evaluation, synthetic eval-data generation, or human review interfaces; do not use for generic product analytics, ordinary QA, or unrelated UI implementation.
- `fix-mise` — Diagnose and repair mise trust/runtime failures and reconcile `~/.config/mise/config.toml` with required versions; use when commands fail due to trust blockers or stale tool config.
- `insight-report` — Generate a high-fidelity Codex usage insights HTML report from local Codex session data. Use this skill when a user asks for an insights report, usage report, or session analysis.
- `markdown-converter` — Convert source files into Markdown outputs using the bundled converter workflow. Use when a user asks to transform documents, notes, or technical files into clean Markdown format.
- `notebooklm` — Manage, analyze, and generate Google NotebookLM workflows for notebook/source management, notebook question answering, and audio/video overview generation. Use this skill when a user asks to run NotebookLM actions from this environment; do not use it for unrelated general web/chat requests.
- `process-watch` — Analyze system processes and resource usage to diagnose runaway CPU/memory/IO, identify culprits, and propose next diagnostic steps. Use when investigating performance spikes or leaks.
- `recon-workbench` — Run authorized, evidence-backed Recon Workbench (rwb) workflows (doctor/authorize/plan/run/summarize/manifest/validate/reconcile) and produce evidence-cited findings. Use when interrogating macOS/iOS, web/React, or OSS targets under explicit scope/permission.
- `repoprompt` — Plan and guide Repo Prompt integration and usage in AI coding workflows. Use when integrating Repo Prompt with editors/agents or when needing MCP/CLI tool guidance.
- `simple-tasks` — Install a fast local task workflow for single-project planning with scripts/task.sh (claim, done, status, reporting) backed by tasks/TASKS.md and optional tasks/details/ notes. Use when you need lightweight in-progress task coordination rather than full team issue tracking.
- `skill-builder` — Create, revise, benchmark, and quality-gate Codex skills (SKILL.md plus scripts, references, evals, and packaging). Use this skill when the user asks to build, audit, improve, compare, package, or safely install local/imported skill folders. Scope exclusions: unrelated app features, generic bug fixing, plugin package conversion, or session-log audits.
- `slides` — Use when tasks involve creating, editing, recreating, validating, or visually debugging presentation slide decks (`.pptx`) with editable PowerPoint output, PptxGenJS authoring, bundled layout helpers, and render/overflow checks; do not use for generic web UI design, prose editing, or non-presentation visual explainers.
- `spreadsheet` — Use when tasks involve creating, editing, analyzing, or formatting spreadsheets (`.xlsx`, `.csv`, `.tsv`) with formula-aware workflows, cached recalculation, and visual review.
- `systematic-debugging` — Analyze evidence from production bugs, regressions, and failed checks and diagnose root causes when users need a safe, evidence-backed fix plan before any code changes.
- `test-driven-development` — Create test-first Red-Green-Refactor delivery for behavior changes. Use when implementing a feature or bugfix before writing production code.
- `using-git-worktrees` — Create and validate Codex app and Claude CLI git worktree workflows with safe branch/sync strategy and cleanup guidance. Use when users request isolated checkouts; do not use for explicit in-place same-branch edits.
- `verification-before-completion` — Validate completion claims with fresh command evidence. Use when you are about to claim work is complete, fixed, or passing.
- `visual-explainer` — Generate beautiful, self-contained HTML pages that visually explain systems, code changes, plans, and data. Use when the user asks for a diagram, architecture overview, diff review, plan review, project recap, comparison table, or any visual explanation of technical concepts. Also use proactively when you are about to render a complex ASCII table (4+ rows or 3+ columns) — present it as a styled HTML page instead.
- `writing-plans` — Create execution-ready implementation plans with task sequencing and checks. Use when requirements are known but implementation is multi-step.
- `xcode-makefiles` — Install strict Xcode Makefile tooling for iOS/macOS projects, including build/run/test scripts with AGENT_NAME-based per-agent isolation under build/. Use when a project needs reproducible local CLI builds without full app scaffolding.

