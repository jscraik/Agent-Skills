# Agent Skills Index

Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/skills`.

## Auth

- `best-practices` — Review Better Auth setups and highlight secure integration best practices.
- `create-auth` — Build Better Auth integrations for TS/JS apps with secure defaults. Use

## Backend

- `backend-engineer` — Plan and review safe backend extensions for existing services (Cloudflare Workers + Hono primary). Use this skill when patching or adding backend features in an existing codebase.
- `cli-spec` — Plan and draft CLI UX and surface area (commands, flags, help, output).
- `mcp-builder` — Create general-purpose MCP servers and tool schemas for standard integrations.
- `mkit-builder` — Create MCP servers with OAuth, billing/licensing, and Apps SDK UI integration.
- `workers-mcp` — Create production-ready MCP servers on Cloudflare Workers with:. Use

## Design

- `better-icons` — Use this skill to search and extract SVG icons via the better-icons CLI or MCP. Use this when you need icons from Iconify collections for UI/UX work, product mocks, or codebases.

## Frontend — Graphics

- `favicon-generator` — Generate complete favicon/app icon suites with templates and assets.
- `imagegen` — Use when the user asks to generate or edit images via the OpenAI Image API (for example: generate image, edit/inpaint/mask, background removal or replacement, transparent background, product shots, concept art, covers, or batch variants); run the bundled CLI (`scripts/image_gen.py`) and require `OPENAI_API_KEY` for live calls.
- `og-image-creator` — Generate authentic, brand-aligned Open Graph images by understanding
- `sora` — Use when the user asks to generate, remix, poll, list, download, or delete Sora videos via OpenAI\u2019s video API using the bundled CLI (`scripts/sora.py`), including requests like \u201cgenerate AI video,\u201d \u201cSora,\u201d \u201cvideo remix,\u201d \u201cdownload video/thumbnail/spritesheet,\u201d and batch video generation; requires `OPENAI_API_KEY` and Sora API access.
- `threejs-builder` — Build and validate simple, performant Three.js web apps using modern

## Frontend — Seo

- `seo-optimizer` — Transform your web application from invisible to discoverable. This skill

## Frontend — Tools

- `agent-trace-debug` — Analyze Agent Trace data flow when AIAttributionPanel shows empty/incorrect trace by tracing expected vs actual shapes across agentTraceStore and API.
- `codex-ui-kit-installer` — Scaffold and install codex-ui-kit assets, prompts, and optional config
- `nano-banana-builder` — Build production-ready web applications powered by Google's Nano Banana

## Frontend — Ui

- `figma-implement-design` — DEPRECATED alias of figma. Convert legacy invocations when requests explicitly name figma-implement-design; immediately route to figma in implement_design mode.
- `figma` — Use this canonical Figma skill to extract design context/screenshots/assets with Figma MCP and build production-ready UI guidance. Use when requests include Figma URLs/node IDs, design-to-code implementation, or Figma MCP setup/troubleshooting.
- `frontend-ui-design` — Create and review production-ready UI systems/components with tokens
- `interface-craft` — Interface Craft by Josh Puckett helps build polished, animated React interfaces using Storyboard Animation, DialKit tuning panels, and Design Critique. Use when requests involve motion design, animation sequencing, live tuning controls, or structured UI critique and polish.
- `react-best-practices` — React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements.
- `react-ui-patterns` — Provide concrete, example-driven guidance for React UI composition, state,
- `ui-visual-regression` — Run a minimal, repeatable UI visual regression pipeline (Storybook build
- `web-design-guidelines` — Review UI code against Web Interface Guidelines with file:line findings.

## Github

- `gh-actions-fix` — DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name gh-actions-fix; immediately route to gh-workflow in ci_diagnose mode.
- `gh-address-comments` — DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name gh-address-comments; immediately route to gh-workflow in pr_review_comments mode.
- `gh-fix-ci` — Use when a user asks to debug or fix failing GitHub PR checks that run in GitHub Actions; use `gh` to inspect checks and logs, summarize failure context, draft a fix plan, and implement only after explicit approval. Treat external providers (for example Buildkite) as out of scope and report only the details URL.
- `gh-issue-fix` — DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name gh-issue-fix; immediately route to gh-workflow in issue_fix mode.
- `gh-pr-local` — DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name gh-pr-local; immediately route to gh-workflow in pr_prepare mode.
- `gh-workflow` — Consolidated GitHub lifecycle skill for agents and users: intake, issue fixing, PR prep, review comment handling, CI diagnosis, and server-side merge via gh. Use when requests involve GitHub issues/PRs/checks/merge operations.
- `yeet` — DEPRECATED alias of gh-workflow. Convert legacy invocations when requests explicitly name yeet; immediately route to gh-workflow in pr_prepare mode.

## Interview

- `architecture-interview` — Plan and review architecture decisions via a structured interview and ADR output. Use when choosing between system design alternatives.
- `bug-interview` — Analyze and review bug reports to capture repro, evidence, and the next smallest diagnostic step. Use when a bug report lacks clear reproduction.
- `deep-interview` — Deep, gap-filling interview that enhances an existing doc/spec (preferred) or explores a topic. Use when deepening PRDs, ADRs, tickets, notes, or draft specs; if given a doc path, update it in-place with Delta/Interview Insights and an approval gate.
- `interview-kernel` — Core interview engine enforcing strict discovery/decision gating with
- `interview-me` — Interactive, multiple-choice interview for requirements discovery and spec clarification; turns an underspecified idea (or draft spec) into an execution-ready spec with decisions, assumptions, acceptance criteria, and approval. Use when a user asks to 'interview me', clarify scope, or refine a draft spec.
- `pm-interview` — Plan and review product scope, value, metrics, and rollout via a structured interview. Use when product direction or scope must be clarified.

## Personas

- `steipete` — Generate @steipete-style persona responses for agentic engineering, AI dev tooling, and open-source shipping. Use when users ask for @steipete’s voice or approach." 

## Product — Content

- `youtube-hooks-scripts` — Create high-retention hooks and full scripts for technical YouTube videos
- `youtube-titles-thumbnails` — Generate multiple SEO/CTR-optimized YouTube title and thumbnail text

## Product — Design

- `ui-ux-creative-coding` — Creative-coding UI polish for Tauri+React (Tailwind v4, Radix, Three.js).

## Product — Docs

- `agents-md` — 'Refactor or create AGENTS.md using progressive disclosure: keep root
- `context7` — Extract current library documentation via Context7 when users need up-to-date
- `docs-expert` — Co-author and QA documentation such as READMEs, guides, and runbooks.
- `openai-docs` — Use when the user asks how to build with OpenAI products or APIs and needs up-to-date official documentation with citations (for example: Codex, Responses API, Chat Completions, Apps SDK, Agents SDK, Realtime, model capabilities or limits); prioritize OpenAI docs MCP tools and restrict any fallback browsing to official OpenAI domains.

## Product — Domain

- `chatgpt-apps-production-checklist` — Turn ChatGPT Apps implementation work into a production-ready checklist with concrete tasks, tests, widget changes, and tool-result patterns mapped by priority (P0/P1/P2). Use when designing or hardening Apps SDK products for shipping; do not use for generic web-only apps, static code review, or non-ChatGPT integration planning.
- `cloudflare-deploy` — Deploy applications and infrastructure to Cloudflare using Workers, Pages, and related platform services. Use when the user asks to deploy, host, publish, or set up a project on Cloudflare.
- `oak-api` — Build or adapt Oak Curriculum API driven learning experiences, especially

## Product — Ops

- `decide-build-primitive` — Analyze and decide the right Codex primitive (Skill, Custom Prompt, or
- `linear` — This skill provides a structured workflow for managing issues, projects
- `release` — Create and publish a new project release (semver) when you need to cut

## Product — Review

- `codex-wrapped` — Generate a Codex/Claude Code usage recap from local logs, including last
- `llm-design-review` — Structure a multidisciplinary design review for LLM-powered products,
- `product-design-review` — Deliver a user-centered UX critique across the full experience. Use for

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

- `project-improvement-ideator` — Generate, score, and winnow project improvement ideas into a top 5 with

## Product — Tech

- `agent-native-architecture` — Design or review agent-native application architecture for Codex-based workflows. Use when planning parity between UI and agent actions, primitive tool design, execution-loop completion signals, context injection, and safe rollout/rollback for agent-driven products.
- `tech-spec` — Create implementation-ready technical planning artifacts from an existing tech spec. Use when you need one focused mode: data_spec, migration_plan, ops_spec, or performance_plan.
- `tech-to-data` — DEPRECATED alias of tech-spec. Convert legacy invocations when requests explicitly name tech-to-data; immediately route to tech-spec in data_spec mode.
- `tech-to-migration` — DEPRECATED alias of tech-spec. Convert legacy invocations when requests explicitly name tech-to-migration; immediately route to tech-spec in migration_plan mode.
- `tech-to-ops` — DEPRECATED alias of tech-spec. Convert legacy invocations when requests explicitly name tech-to-ops; immediately route to tech-spec in ops_spec mode.
- `tech-to-performance` — DEPRECATED alias of tech-spec. Convert legacy invocations when requests explicitly name tech-to-performance; immediately route to tech-spec in performance_plan mode.

## Utilities

- `1password` — Plan, validate, and use 1Password CLI setup for secret injection and
- `agent-browser` — Use this skill to extract page state and automate web interactions with
- `alignment-checkpoint` — Intent-alignment gate for ambiguous/high-stakes requests. Use this when you want to extract goal/assumptions/criteria and require an explicit /proceed approval gate before any tool use.
- `atlas` — macOS-only AppleScript control for the ChatGPT Atlas desktop app. Use only when the user explicitly asks to control Atlas tabs/bookmarks/history on macOS and the \"ChatGPT Atlas\" app is installed; do not trigger for general browser tasks or non-macOS environments.
- `beautiful-mermaid` — Render Mermaid diagrams to SVG and PNG with Beautiful Mermaid. Use when
- `codex-home-audit` — Audit and improve a Codex home directory (AGENTS.md, USER_PROFILE, instructions/, rules/, config.toml) when you want a dated report of risks, duplication, and recommended cleanups.
- `codex-sessions-skill-scan` — Daily skill health scan: analyze ~/.codex/sessions (default last 1 day) and summarize skill invocations + likely failures for personal skills in ~/dev/agent-skills (missing paths, tool failures). Use when you ask to scan recent Codex sessions for skill issues or when a skill keeps failing. Optional: include best-effort local OTel signals.
- `markdown-converter` — Convert files to Markdown using — no installation required.. Use when
- `process-watch` — Analyze system processes and resource usage to diagnose runaway CPU/memory/IO,
- `prompt-creator` — Create or update Codex skills (shareable, can be invoked implicitly) under .agents/skills when you want reusable team workflows; optionally create local custom prompts in ~/.codex/prompts when you explicitly want /prompts:... slash commands (deprecated).
- `recon-workbench` — Run authorized, evidence-backed Recon Workbench (rwb) workflows (doctor/authorize/plan/run/summarize/manifest/validate/reconcile) and produce evidence-cited findings. Use when interrogating macOS/iOS, web/React, or OSS targets under explicit scope/permission.
- `remotion` — Best-practice guidance for Remotion (React video). Use when building or reviewing Remotion compositions, timing, assets, audio, captions, or rendering.
- `repoprompt` — Plan and guide Repo Prompt integration and usage in AI coding workflows.
- `run-tests-and-write-artifacts` — Run reproducible test suites in a checked-out repo and write evidence artifacts to /mnt/data (test_output.log, test_results.json, test_summary.md). Use when users ask to run tests, verify a branch, or reproduce CI failures; do not use for static-only review, deployment, or bug fixing before evidence is collected.
- `skill-creator` — Create, revise, and quality-gate Codex skills (SKILL.md + resources + evals + packaging) when asked to build or improve a skill.
- `skill-installer` — Plan and install skills into a Codex skills directory from a curated
- `systematic-debugging` — Use this skill when encountering bugs, test failures, regressions, or unexpected behavior to run a root-cause-first debugging workflow before proposing fixes or code changes.
- `video-transcript-downloader` — Extract, summarize, and download video/audio/subtitles using yt-dlp/ffmpeg.

