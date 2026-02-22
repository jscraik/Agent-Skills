# Agent Skills Index

Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/skills`.

## Auth

- `best-practices` — Review Better Auth setups and highlight secure integration best practices. Use for audits, config guidance, or debugging flows (not full implementation). Use when the user requests this capability.
- `create-auth` — Build Better Auth integrations for TS/JS apps with secure defaults. Use for implementation or migration work (not just review). Use when the user requests this capability.

## Backend

- `backend-engineer` — Plan and review safe backend extensions for existing services (Cloudflare Workers + Hono primary). Use this skill when patching or adding backend features in an existing codebase.
- `cli-spec` — Plan and draft CLI UX and surface area (commands, flags, help, output). Use when specifying or refactoring a command-line interface.
- `mcp-builder` — Create general-purpose MCP servers and tool schemas for standard integrations. Use when building MCP services without OAuth/billing/Apps UI requirements.
- `mkit-builder` — Create MCP servers with OAuth, billing/licensing, and Apps SDK UI integration. Use when you need enterprise-grade MCP patterns beyond the standard MCP builder.
- `workers-mcp` — Create and deploy production-ready MCP servers on Cloudflare Workers. Use when building a Workers-hosted MCP server with auth, billing, and operational guardrails.

## Design

- `better-icons` — Use this skill to search and extract SVG icons via the better-icons CLI or MCP. Use this when you need icons from Iconify collections for UI/UX work, product mocks, or codebases.

## Frontend

- `agentation` — Use when a user wants to install, verify, or troubleshoot Agentation in React/Next.js/Vite/Tauri apps; this skill validates toolbar wiring, MCP health, live webhook delivery, and automation modes (self-driving autopilot + critique mode) with end-to-end submit verification.
- `design-md` — Use this skill when the user wants to analyze a Stitch project and create a reusable DESIGN.md design system file with semantic style tokens and prompting guidance.
- `enhance-prompt` — Use this skill when the user asks to improve a Stitch prompt. It transforms vague UI ideas into specific, design-aware prompts that generate higher-quality screens.
- `react-components` — Use this skill when the user asks to convert Stitch screens into modular Vite/React components with validated structure, data extraction, and style-system alignment.
- `shadcn-ui` — Integrate and customize shadcn/ui components in existing projects. Use when the user asks to set up, add, adapt, or troubleshoot shadcn/ui components, registry items, and implementation patterns.
- `stitch-loop` — Use this skill when the user asks for iterative autonomous website building with Stitch using a baton file (`next-prompt.md`) and multi-pass page generation.
- `stitch-remotion` — Generate Stitch-to-Remotion walkthrough videos from screen assets. Use when the user asks to transform Stitch screens into narrated or demo-style videos with transitions, overlays, and rendered exports.

## Frontend — Graphics

- `favicon-generator` — Generate complete favicon/app icon suites with templates and assets. Use when the user needs favicons or app icons for a web/app project.
- `imagegen` — Use when the user asks to generate or edit images via the OpenAI Image API (for example: generate image, edit/inpaint/mask, background removal or replacement, transparent background, product shots, concept art, covers, or batch variants); run the bundled CLI (`scripts/image_gen.py`) and require `OPENAI_API_KEY` for live calls.
- `og-image-creator` — Generate brand-aligned Open Graph images for existing routes by inspecting a web codebase and rendering assets with Playwright components. Use when a user asks for route-specific OG image generation or refresh in an existing app.
- `sora` — Use when the user asks to generate, remix, poll, list, download, or delete Sora videos via OpenAI\u2019s video API using the bundled CLI (`scripts/sora.py`), including requests like \u201cgenerate AI video,\u201d \u201cSora,\u201d \u201cvideo remix,\u201d \u201cdownload video/thumbnail/spritesheet,\u201d and batch video generation; requires `OPENAI_API_KEY` and Sora API access.
- `threejs-builder` — Build and validate simple, performant Three.js web apps using modern ES module patterns. Use this when you need a minimal Three.js scene, interaction, or animation for a web UI or demo.

## Frontend — Seo

- `seo-optimizer` — Implement practical SEO improvements in a web app (metadata, sitemap, robots, structured data, social cards) based on repository analysis. Use when a user asks to improve discoverability, indexing, or search/social preview quality.

## Frontend — Tools

- `agent-trace-debug` — Analyze Agent Trace data flow when AIAttributionPanel shows empty/incorrect trace by tracing expected vs actual shapes across agentTraceStore and API.
- `codex-ui-kit-installer` — Scaffold and install codex-ui-kit assets, prompts, and optional config into an existing repo. Use when adding or refreshing codex-ui-kit folders and wiring prompts.
- `nano-banana-builder` — Build web applications that use Google's Nano Banana image APIs for generation and iterative editing workflows. Use when a user asks to prototype or ship a Nano Banana powered image product from text-to-image to multi-turn editing.

## Frontend — Ui

- `design-system` — Analyze and implement repository-grounded design-system work (tokens, typography, iconography, spacing, styles, aliases, and theme variables) for this monorepo. Use when requests involve UI styling systems or token-layer changes; don’t use for backend/MCP-only tasks with no UI impact. Outputs: evidence-backed analysis or changes with canonical file references, layer impact, and validation commands. Success: work aligns to Brand→Alias→Mapped rules and passes design-system checks.
- `figma-implement-design` — DEPRECATED alias of figma. Convert legacy invocations when requests explicitly name figma-implement-design; immediately route to figma in implement_design mode.
- `figma` — Use this canonical Figma skill to extract design context/screenshots/assets with Figma MCP and build production-ready UI guidance. Use when requests include Figma URLs/node IDs, design-to-code implementation, or Figma MCP setup/troubleshooting.
- `frontend-ui-design` — Create and review production-ready UI systems/components with tokens and accessibility. Use for standard UI implementation or redesign (not creative-coding polish). Use when the user requests this capability.
- `interface-craft` — Interface Craft by Josh Puckett helps build polished React interfaces with storyboard motion, live tuning controls, critique frameworks, and concept workflows; use when requests involve UI motion, critique, refinement, concept exploration, or interaction craft.
- `react-best-practices` — React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements.
- `react-ui-patterns` — Provide concrete React UI composition patterns for TypeScript + Tailwind + Radix, including state, routing, and component structure examples. Use when building or refactoring React screens and components for maintainability.
- `ui-visual-regression` — Review and validate UI visual regression diffs (Storybook + Playwright capture + Argos) when snapshot changes or layout regressions appear.
- `web-design-guidelines` — Review UI code against Web Interface Guidelines with file:line findings. Use for rule-based compliance checks (not experiential critiques). Use when the user requests this capability.

## Github

- `automate-github-issues` — Use when the user asks to automate GitHub issue triage with parallel Jules agents; output a validated fleet setup and runbook for analyze, plan, dispatch, and merge.
- `gh-actions-fix` — DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name gh-actions-fix; immediately route to gh-workflow in ci_diagnose mode.
- `gh-address-comments` — DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name gh-address-comments; immediately route to gh-workflow in pr_review_comments mode.
- `gh-fix-ci` — Use when a user asks to debug or fix failing GitHub PR checks that run in GitHub Actions; use `gh` to inspect checks and logs, summarize failure context, draft a fix plan, and implement only after explicit approval. Treat external providers (for example Buildkite) as out of scope and report only the details URL.
- `gh-issue-fix` — DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name gh-issue-fix; immediately route to gh-workflow in issue_fix mode.
- `gh-pr-local` — DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name gh-pr-local; immediately route to gh-workflow in pr_prepare mode.
- `gh-workflow` — Consolidated GitHub lifecycle skill for agents and users: intake, issue fixing, PR prep, review request/reception, review comment handling, CI diagnosis, and server-side merge via gh. Use when requests involve GitHub issues/PRs/checks/merge operations.
- `local-action-verification` — Use when the user asks to validate GitHub Actions locally with act; output setup guidance, AGENTS.md instructions, and fail-fast checks before push or PR.
- `yeet` — DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name yeet; immediately route to gh-workflow in pr_prepare mode.

## Interview

- `architecture-interview` — Plan and review architecture decisions via a structured interview and ADR output. Use when choosing between system design alternatives.
- `bug-interview` — Analyze and review bug reports to capture repro, evidence, and the next smallest diagnostic step. Use when a bug report lacks clear reproduction.
- `deep-interview` — Deep, gap-filling interview that enhances an existing doc/spec (preferred) or explores a topic. Use when deepening PRDs, ADRs, tickets, notes, or draft specs; if given a doc path, update it in-place with Delta/Interview Insights and an approval gate.
- `interview-kernel` — Core interview engine enforcing strict discovery/decision gating with externalized state, decisions, assumptions, and an approval gate. Use when building interview wrapper skills.
- `interview-me` — Interactive, multiple-choice interview for requirements discovery and spec clarification; turns an underspecified idea (or draft spec) into an execution-ready spec with decisions, assumptions, acceptance criteria, and approval. Use when a user asks to 'interview me', clarify scope, or refine a draft spec.
- `pm-interview` — Plan and review product scope, value, metrics, and rollout via a structured interview. Use when product direction or scope must be clarified.

## Personas

- `benjitaylor-persona` — Generate @benjitaylor-inspired responses for interface craft, AI-assisted developer workflows, and React/TypeScript product execution. Use when users ask for @benjitaylor's perspective and need pragmatic, implementation-first guidance.
- `emilkowalski-persona` — Generate @emilkowalski-inspired responses for design-engineering decisions on UI feel, motion quality, performance, accessibility, and developer experience. Use when users explicitly ask for @emilkowalski's perspective.
- `jenny-wen-persona` — Generate @jenny_wen-inspired responses for AI product updates, collaboration tools, and team-facing communication with a friendly, practical, craft-forward, product-minded tone. Use when users ask for @jenny_wen's perspective.
- `jh3yy-persona` — Generate @jh3yy-inspired responses for modern web development, CSS animation, interaction design, and accessibility with a platform-first, example-driven teaching style. Use when users ask for @jh3yy's perspective.
- `kubadesign-persona` — Generate @kubadesign-inspired responses for web design, experimentation, and portfolio-driven product work with an enthusiastic but actionable tone. Use when users ask for @kubadesign's perspective.
- `steipete` — Generate @steipete-inspired guidance for agentic engineering, AI dev tooling, and open-source shipping. Use when users explicitly ask for @steipete’s perspective on shipping and tooling tradeoffs.

## Product — Content

- `youtube-hooks-scripts` — Create high-retention hooks and full scripts for technical YouTube videos tailored to topic, audience, and length. Use when the user asks for a hook, outline, or full script.
- `youtube-titles-thumbnails` — Generate multiple SEO/CTR-optimized YouTube title and thumbnail text options with variants and rationale. Use when the user wants packaging ideas, titles, or thumbnail copy.

## Product — Design

- `ui-ux-creative-coding` — Use when UI work needs polished motion + implementation artifacts in React/Tauri (Tailwind v4, Radix, optional Three.js); deliver brief, component/motion plans, and validation notes; do not use for brand-only identity or full 3D/game builds.

## Product — Docs

- `agents-md` — Refactor or create AGENTS.md using progressive disclosure: keep root minimal, split detailed instructions into linked docs, and flag contradictions/redundancy. Use when the user asks to create, update, or refactor AGENTS.md.
- `context7` — Extract current library documentation via Context7 when users need up-to-date API details, version checks, or dependency troubleshooting for external libraries.
- `docs-expert` — Co-author and QA GitHub repository documentation (README, docs, runbooks, community health files); use when auditing/upgrading repo docs and delivering a checklist + PR-ready edits; do not use for PRDs/specs.
- `openai-docs` — Use when the user asks how to build with OpenAI products or APIs and needs up-to-date official documentation with citations (for example: Codex, Responses API, Chat Completions, Apps SDK, Agents SDK, Realtime, model capabilities or limits); prioritize OpenAI docs MCP tools and restrict any fallback browsing to official OpenAI domains.

## Product — Domain

- `chatgpt-apps-production-checklist` — Turn ChatGPT Apps implementation work into a production-ready checklist with concrete tasks, tests, widget changes, and tool-result patterns mapped by priority (P0/P1/P2). Use when designing or hardening Apps SDK products for shipping; do not use for generic web-only apps, static code review, or non-ChatGPT integration planning.
- `cloudflare-deploy` — Deploy applications and infrastructure to Cloudflare using Workers, Pages, and related platform services. Use when the user asks to deploy, host, publish, or set up a project on Cloudflare.
- `oak-api` — Build or adapt Oak Curriculum API driven learning experiences, especially for child-facing, interactive ChatGPT Apps SDK workflows. Use when working with Oak API endpoints, curriculum data (subjects, units, lessons, quizzes, search), or when translating Oak content into adaptive learning activities with age-appropriate guardrails and compliance reminders.

## Product — Ops

- `decide-build-primitive` — Analyze and decide the right Codex primitive (Skill, Custom Prompt, or Agent automation) for a capability. Use this when you need to plan how to package or automate a workflow.
- `linear` — Manage Linear issues, projects, and docs through the Linear MCP workflow with consistent read/create/update operations. Use when a user asks to triage, create, update, or report on Linear work items.
- `release` — Create and publish a new project release (semver) when you need to cut a main-branch, clean-tree release via just release X.Y.Z for Cargo publish and git tag creation.

## Product — Review

- `codex-wrapped` — Generate a Codex/Claude Code usage recap from local logs, including last 30 days, last 7 days, and all-time stats. Use when the user asks for a usage summary, activity recap, or coding activity report.
- `llm-design-review` — Run a multidisciplinary design review for LLM-powered products and produce actionable risks, fixes, and evidence gaps across UX, architecture, safety, and ops. Use when a user asks for an AI product design review or pre-launch critique.
- `product-design-review` — Deliver a user-centered UX critique across the full experience. Use for heuristic reviews and journey analysis (not file:line guideline compliance). Use when the user requests this capability.

## Product — Security

- `security-best-practices` — Perform language and framework specific security best-practice reviews and suggest improvements. Trigger only when the user explicitly requests security best practices guidance, a security review/report, or secure-by-default coding help. Trigger only for supported languages (python, javascript/typescript, go). Do not trigger for general code review, debugging, or non-security tasks.
- `security-ownership-map` — Analyze git repositories to map security ownership (people-to-file), compute bus-factor and sensitive-code risk, and export CSV/JSON/graph artifacts for visualization. Use only when the user explicitly requests security-focused ownership analysis grounded in git history.
- `security-threat-model` — Repository-grounded threat modeling that enumerates trust boundaries, assets, attacker capabilities, abuse paths, and mitigations, and writes a concise Markdown threat model. Trigger only when the user explicitly asks to threat model a codebase or path, enumerate threats/abuse paths, or perform AppSec threat modeling. Do not trigger for general architecture summaries, code review, or non-security design work.

## Product — Specs

- `prd-clarifier` — DEPRECATED alias of product-spec. Convert legacy invocations when requests explicitly name prd-clarifier; immediately route to product-spec in clarify_prd mode.
- `prd-to-api` — DEPRECATED alias of product-spec. Convert legacy invocations when requests explicitly name prd-to-api; immediately route to product-spec in api_spec mode.
- `prd-to-arch` — DEPRECATED alias of product-spec. Convert legacy invocations when requests explicitly name prd-to-arch; immediately route to product-spec in arch_spec mode.
- `prd-to-testplan` — DEPRECATED alias of product-spec. Convert legacy invocations when requests explicitly name prd-to-testplan; immediately route to product-spec in testplan mode.
- `prd-to-ux` — DEPRECATED alias of product-spec. Convert legacy invocations when requests explicitly name prd-to-ux; immediately route to product-spec in ux_only mode.
- `product-spec` — Create or review implementation-ready product specifications from ideas or existing docs. Use when you need a full PRD+UX+build plan pipeline or a focused mode (clarify_prd, ux_only, api_spec, arch_spec, testplan).

## Product — Strategy

- `asymmetric-ideation-engine` — Generate 10 launchable asymmetric ideas by excavating a repository for hidden patterns. Use when users ask for radical non-incremental ideation from repo context; don't use for roadmap optimization, bug fixing, or routine prioritization. Outputs: structured idea set + artifact file. Success: all novelty constraints satisfied.
- `brainstorming` — This skill should be used before implementing features, building components, or making changes. It guides exploring user intent, approaches, and design decisions before planning. Triggers on "let's brainstorm", "help me think through", "what should we build", "explore approaches", ambiguous feature requests, or when the user's request has multiple valid interpretations that need clarification.
- `project-improvement-ideator` — Generate, score, and winnow project improvement ideas into a top 5 with impact/effort notes. Use when asked for roadmap ideas, prioritization, or improvement brainstorming.

## Product — Tech

- `agent-native-architecture` — Design or review agent-native application architecture for Codex-based workflows. Use when planning parity between UI and agent actions, primitive tool design, execution-loop completion signals, context injection, and safe rollout/rollback for agent-driven products.
- `tech-spec` — Create implementation-ready technical planning artifacts from an existing tech spec. Use when you need one focused mode: data_spec, migration_plan, ops_spec, or performance_plan.
- `tech-to-data` — DEPRECATED alias of tech-spec. Convert legacy invocations when requests explicitly name tech-to-data; immediately route to tech-spec in data_spec mode.
- `tech-to-migration` — DEPRECATED alias of tech-spec. Convert legacy invocations when requests explicitly name tech-to-migration; immediately route to tech-spec in migration_plan mode.
- `tech-to-ops` — DEPRECATED alias of tech-spec. Convert legacy invocations when requests explicitly name tech-to-ops; immediately route to tech-spec in ops_spec mode.
- `tech-to-performance` — DEPRECATED alias of tech-spec. Convert legacy invocations when requests explicitly name tech-to-performance; immediately route to tech-spec in performance_plan mode.

## Utilities

- `1password` — Plan, validate, and use 1Password CLI setup for secret injection and auth. Use when tasks need 1Password CLI usage, secret references, op run/read/inject, or provisioning secrets via env vars/.env files and scripts.
- `agent-browser` — Use this skill to extract page state and automate web interactions with the agent-browser CLI (navigate, snapshot, click, fill, screenshot). Use this when you need deterministic browser automation or scraping via ref-based elements.
- `alignment-checkpoint` — Intent-alignment gate for ambiguous/high-stakes requests. Use this when you want to extract goal/assumptions/criteria and require an explicit /proceed approval gate before any tool use.
- `atlas` — macOS-only AppleScript control for the ChatGPT Atlas desktop app. Use only when the user explicitly asks to control Atlas tabs/bookmarks/history on macOS and the \"ChatGPT Atlas\" app is installed; do not trigger for general browser tasks or non-macOS environments.
- `beautiful-mermaid` — Render Mermaid diagrams to SVG and PNG with Beautiful Mermaid. Use when the user asks to render or convert Mermaid diagrams into images.
- `bootstrap` — Bootstrap a local development environment from a GitHub repository URL. Use when the user asks to clone a repo, install toolchains/dependencies, and validate a working dev setup automatically.
- `codex-agent-creator` — Create and install Codex custom multi-agent roles when the user asks to add, update, or troubleshoot role entries under agents with a role config file.
- `codex-home-audit` — Audit and improve a Codex home directory (AGENTS.md, USER_PROFILE, instructions/, rules/, config.toml) when you want a dated report of risks, duplication, and recommended cleanups.
- `codex-sessions-skill-scan` — Daily skill health scan: analyze ~/.codex/sessions (default last 1 day) and summarize skill invocations + likely failures for personal skills in ~/dev/agent-skills (missing paths, tool failures). Use when you ask to scan recent Codex sessions for skill issues or when a skill keeps failing. Optional: include best-effort local OTel signals.
- `executing-plans` — Validate and execute written implementation plans in verified batches with checkpoints. Use when a plan already exists and work must proceed task-by-task.
- `fix-mise` — Diagnose and resolve mise trust/setup failures for local toolchains. Use when the user reports mise trust errors, missing runtimes, or broken mise-managed commands.
- `markdown-converter` — Convert source files into Markdown outputs using the bundled converter workflow. Use when a user asks to transform documents, notes, or technical files into clean Markdown format.
- `process-watch` — Analyze system processes and resource usage to diagnose runaway CPU/memory/IO, identify culprits, and propose next diagnostic steps. Use when investigating performance spikes or leaks.
- `prompt-creator` — Create or update reusable Codex skills under .agents/skills and optionally local ~/.codex/prompts shortcuts. Use when a user asks to build, revise, or package prompts and skills for repeatable workflows.
- `recent-code-bugfix` — Diagnose and fix a bug introduced by the current author within the last week. Use when a user asks for a proactive bugfix from their recent commits, asks to triage/fix issues caused by their own changes, or leaves the prompt empty. Don’t use when failures are unrelated to the author’s recent edits or there is no local git history. Outputs: root-cause summary, minimal fix, and targeted verification evidence. Success: root cause maps directly to the author’s own recent changes.
- `recon-workbench` — Run authorized, evidence-backed Recon Workbench (rwb) workflows (doctor/authorize/plan/run/summarize/manifest/validate/reconcile) and produce evidence-cited findings. Use when interrogating macOS/iOS, web/React, or OSS targets under explicit scope/permission.
- `remotion` — Best-practice guidance for Remotion (React video). Use when building or reviewing Remotion compositions, timing, assets, audio, captions, or rendering.
- `repoprompt` — Plan and guide Repo Prompt integration and usage in AI coding workflows. Use when integrating Repo Prompt with editors/agents or when needing MCP/CLI tool guidance.
- `run-tests-and-write-artifacts` — Run reproducible test suites in a checked-out repo and write evidence artifacts to /mnt/data (test_output.log, test_results.json, test_summary.md). Use when users ask to run tests, verify a branch, or reproduce CI failures; do not use for static-only review, deployment, or bug fixing before evidence is collected.
- `skill-creator` — Create, revise, and quality-gate Codex skills (SKILL.md + resources + evals + packaging) when asked to build or improve a skill.
- `skill-installer` — Plan and install skills into a Codex skills directory from a curated list or repo. Use when a user asks to list or install skills.
- `systematic-debugging` — Use this skill when encountering bugs, test failures, regressions, or unexpected behavior to run a root-cause-first debugging workflow before proposing fixes or code changes.
- `test-driven-development` — Create test-first Red-Green-Refactor delivery for behavior changes. Use when implementing a feature or bugfix before writing production code.
- `using-git-worktrees` — Create isolated git worktrees with baseline checks and cleanup safety. Use when starting feature work or plan execution in a dedicated worktree.
- `verification-before-completion` — Validate completion claims with fresh command evidence. Use when you are about to claim work is complete, fixed, or passing.
- `video-transcript-downloader` — Extract, summarize, and download video/audio/subtitles using yt-dlp/ffmpeg. Use when the user requests downloads or transcripts.
- `visual-explainer` — Generate beautiful, self-contained HTML pages that visually explain systems, code changes, plans, and data. Use when the user asks for a diagram, architecture overview, diff review, plan review, project recap, comparison table, or any visual explanation of technical concepts. Also use proactively when you are about to render a complex ASCII table (4+ rows or 3+ columns) — present it as a styled HTML page instead.
- `writing-plans` — Create execution-ready implementation plans with task sequencing and checks. Use when requirements are known but implementation is multi-step.

