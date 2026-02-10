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

- `figma-implement-design` — Translate Figma nodes into production-ready code with 1:1 visual fidelity using the Figma MCP workflow (design context, screenshots, assets, and project-convention translation). Trigger when the user provides Figma URLs or node IDs, or asks to implement designs or components that must match Figma specs. Requires a working Figma MCP server connection.
- `figma` — Use the Figma MCP server to fetch design context, screenshots, variables, and assets from Figma, and to translate Figma nodes into production code. Trigger when a task involves Figma URLs, node IDs, design-to-code implementation, or Figma MCP setup and troubleshooting.
- `frontend-ui-design` — Create and review production-ready UI systems/components with tokens
- `react-best-practices` — React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements.
- `react-ui-patterns` — Provide concrete, example-driven guidance for React UI composition, state,
- `ui-visual-regression` — Run a minimal, repeatable UI visual regression pipeline (Storybook build
- `web-design-guidelines` — Review UI code against Web Interface Guidelines with file:line findings.

## Github

- `gh-actions-fix` — Use gh to locate failing PR checks, fetch GitHub Actions logs for actionable
- `gh-address-comments` — The agent is capable of extraordinary work in this domain. These guidelines
- `gh-issue-fix` — Analyze and resolve a GitHub issue from intake through fix, validation,
- `gh-pr-local` — Fetch, preview, test, and merge GitHub PRs locally using the primary
- `yeet` — Use only when the user explicitly asks to stage, commit, push, and open a GitHub pull request in one flow using the GitHub CLI (`gh`).

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

## Product — Domain

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
- `security-ownership-map` — Analyze git repositories to build a security ownership topology (people-to-file), compute bus factor and sensitive-code ownership, and export CSV/JSON for graph databases and visualization. Trigger only when the user explicitly wants a security-oriented ownership or bus-factor analysis grounded in git history (for example: orphaned sensitive code, security maintainers, CODEOWNERS reality checks for risk, sensitive hotspots, or ownership clusters). Do not trigger for general maintainer lists or non-security ownership questions.
- `security-threat-model` — Repository-grounded threat modeling that enumerates trust boundaries, assets, attacker capabilities, abuse paths, and mitigations, and writes a concise Markdown threat model. Trigger only when the user explicitly asks to threat model a codebase or path, enumerate threats/abuse paths, or perform AppSec threat modeling. Do not trigger for general architecture summaries, code review, or non-security design work.

## Product — Specs

- `prd-clarifier` — Clarify an existing PRD via structured AskUserQuestion sessions (fill gaps, acceptance criteria). Use when a PRD is ambiguous/missing detail; use product-spec to draft from scratch.
- `prd-to-api` — Generate a full API specification from an existing PRD/tech spec (endpoints, schemas, errors, auth). Use when a production-grade contract is required; use product-spec to draft end-to-end.
- `prd-to-arch` — Generate a full architecture specification from an existing PRD/tech spec. Use when boundaries/diagrams must be locked before build; use product-spec to draft end-to-end.
- `prd-to-testplan` — Generate a test plan from an existing PRD (map acceptance criteria to tests + quality gates). Use when verification must be explicit before build; use product-spec to draft end-to-end.
- `prd-to-ux` — Generate a UX specification from an existing PRD/Foundation Spec (Stage 2). Use when you need UX clarity before build planning; use product-spec for end-to-end PRD+UX+plan.
- `product-spec` — Create or review end-to-end product specs (PRD + UX spec + build plan) from an idea or existing docs. Use when you want implementation-ready documentation without writing code.

## Product — Strategy

- `project-improvement-ideator` — Generate, score, and winnow project improvement ideas into a top 5 with

## Product — Tech

- `tech-to-data` — Generate a data specification from a tech spec covering schemas, lifecycle,
- `tech-to-migration` — Generate a migration plan from a tech spec with phased rollout, rollback,
- `tech-to-ops` — Generate an ops/runbook spec from a tech spec with SLOs, alerts, dashboards,
- `tech-to-performance` — Generate a performance plan from a tech spec with budgets, load tests,

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
- `skill-creator` — Create, revise, and quality-gate Codex skills (SKILL.md + resources +
- `skill-installer` — Plan and install skills into a Codex skills directory from a curated
- `video-transcript-downloader` — Extract, summarize, and download video/audio/subtitles using yt-dlp/ffmpeg.

