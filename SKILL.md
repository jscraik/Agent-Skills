# Agent Skills Index

Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/skills`.

## Auth

- `best-practices` — Review Better Auth setups and highlight secure integration best practices. Use for audits, config guidance, or debugging flows (not full implementation).
- `create-auth` — Build Better Auth integrations for TS/JS apps with secure defaults. Use for implementation or migration work (not just review).

## Backend

- `backend-design` — Produce a complete, review-ready backend design spec with explicit tradeoffs, compliance checks, and a fixed output contract.. Use when Use this skill when the task matches its description and triggers..
- `cli-spec` — Plan and draft CLI UX and surface area (commands, flags, help, output). Use when specifying or refactoring a command-line interface.
- `mcp-builder` — Create general-purpose MCP servers and tool schemas for standard integrations. Use when building MCP services without OAuth/billing/Apps UI requirements.
- `mkit-builder` — Create MCP servers with OAuth, billing/licensing, and Apps SDK UI integration. Use when you need enterprise-grade MCP patterns beyond the standard MCP builder.
- `workers-mcp` — Create production-ready MCP servers on Cloudflare Workers with:. Use when Use this skill when the task matches its description and triggers..

## Design

- `better-icons` — Use this skill to search and extract SVG icons via the better-icons CLI or MCP. Use this when you need icons from Iconify collections for UI/UX work, product mocks, or codebases.

## Frontend — Graphics

- `favicon-generator` — Generate complete favicon/app icon suites with templates and assets. Use when the user needs favicons or app icons for a web/app project.
- `og-image-creator` — Generate authentic, brand-aligned Open Graph images by understanding your codebase first, then creating contextually appropriate images for each route using Playwright and your existing components.. Use when Use this skill when the task matches its description and triggers..
- `threejs-builder` — Build and validate simple, performant Three.js web apps using modern ES module patterns. Use this when you need a minimal Three.js scene, interaction, or animation for a web UI or demo.

## Frontend — Seo

- `seo-optimizer` — Transform your web application from invisible to discoverable. This skill analyzes your codebase and implements comprehensive SEO optimizations that help search engines and social platforms understand, index, and surface your content.. Use when Use this skill when the task matches its description and triggers..

## Frontend — Tools

- `codex-ui-kit-installer` — Scaffold and install codex-ui-kit assets and optional prompts in a repo. Use when adding codex-ui-kit to a project.
- `nano-banana-builder` — Build production-ready web applications powered by Google's Nano Banana image generation APIs—creating everything from simple text-to-image generators to sophisticated iterative editors with multi-turn conversation.. Use when Use this skill when the task matches its description and triggers..

## Frontend — Ui

- `frontend-ui-design` — Create and review production-ready UI systems/components with tokens and accessibility. Use for standard UI implementation or redesign (not creative-coding polish).
- `react-best-practices` — React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements.
- `react-ui-patterns` — Provide concrete, example-driven guidance for React UI composition, state, routing, and component patterns in a TypeScript + Tailwind + Radix stack.. Use when Building or refactoring React screens and components..
- `ui-design-system` — Create or update a governed UI design system (tokens, components, governance). Use when establishing or revising a multi-platform design system.
- `ui-visual-regression` — Run a minimal, repeatable UI visual regression pipeline (Storybook build + Playwright capture + Argos diff) and iterate on targeted UI fixes until visual diffs pass. If design-system guidance, tokens, or component standards are needed, consult the skill.. Use when Investigating visual diffs in Storybook/Argos pipelines..
- `web-design-guidelines` — Review UI code against Web Interface Guidelines with file:line findings. Use for rule-based compliance checks (not experiential critiques).

## Github

- `gh-actions-fix` — Use gh to locate failing PR checks, fetch GitHub Actions logs for actionable failures, summarize the failure snippet, then propose a fix plan and implement after explicit approval.. Use when When a user asks to debug or fix failing GitHub Actions checks on a PR..
- `gh-address-comments` — The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it. Use judgment, adapt to context, and push boundaries when appropriate.. Use when When the user asks to address review comments on an open GitHub PR..
- `gh-issue-fix` — Analyze and resolve a GitHub issue from intake through fix, validation, and push using gh, local edits, and git. Use this skill when you need to analyze and fix a GitHub issue end-to-end using gh and local changes.
- `gh-pr-local` — Fetch, preview, test, and merge GitHub PRs locally using the primary PR workflow. Use when you want a local evaluation before merge.
- `github-pr` — Compatibility alias for the gh-pr-local workflow. Use only when a user explicitly requests github-pr.

## Interview

- `architecture-interview` — Plan and review architecture decisions via a structured interview and ADR output. Use when choosing between system design alternatives.
- `bug-interview` — Analyze and review bug reports to capture repro, evidence, and the next smallest diagnostic step. Use when a bug report lacks clear reproduction.
- `deep-interview` — Deep, gap-filling interview that enhances an existing doc/spec (preferred) or explores a topic. Use when deepening PRDs, ADRs, tickets, notes, or draft specs; if given a doc path, update it in-place with Delta/Interview Insights and an approval gate.
- `interview-kernel` — Core interview engine enforcing strict discovery/decision gating with externalized state, decisions, assumptions, and an approval gate. Use when building interview wrapper skills.
- `interview-me` — Interactive, multiple-choice interview for requirements discovery and spec clarification; turns an underspecified idea (or draft spec) into an execution-ready spec with decisions, assumptions, acceptance criteria, and approval. Use when a user asks to 'interview me', clarify scope, or refine a draft spec.
- `pm-interview` — Plan and review product scope, value, metrics, and rollout via a structured interview. Use when product direction or scope must be clarified.

## Personas

- `steipete` — Generate @steipete-style persona responses for agentic engineering, AI dev tooling, and open-source shipping. Use when users ask for @steipete’s voice or approach." 

## Product — Content

- `app-store-release-notes` — Generate a comprehensive, user-facing changelog from git history since the last tag, then translate commits into clear App Store release notes.. Use when Creating App Store “What’s New” text from git history..
- `youtube-hooks-scripts` — Create hooks and full scripts for technical YouTube videos. Use when drafting video hooks or scripts.
- `youtube-titles-thumbnails` — Generate YouTube titles and thumbnail text optimized for CTR. Use when crafting or optimizing titles/thumbnails.

## Product — Design

- `ui-ux-creative-coding` — Creative-coding UI polish for Tauri+React (Tailwind v4, Radix, Three.js). Use when you need expressive motion craft or WebGL accents—not baseline UI system work.

## Product — Docs

- `agents-md` — Refactor or create AGENTS.md using progressive disclosure: keep root minimal, split detailed instructions into linked docs, and flag contradictions/redundancy. Use when the user asks to create, update, or refactor AGENTS.md.
- `context7` — Extract current library documentation via Context7 when users need up-to-date API details, version checks, or dependency troubleshooting for external libraries.
- `docs-expert` — Co-author and QA documentation such as READMEs, guides, and runbooks. Use when writing or auditing docs (not PRDs/specs).

## Product — Domain

- `oak-api` — Build or adapt Oak Curriculum API driven learning experiences, especially
- `oracle` — Use the @steipete/oracle CLI to bundle a prompt plus the right files and get a peer-model review (API or browser) for debugging, refactors, design checks, or cross-validation. Use this when you need a peer-model review with real repo context, multi-model comparisons, or browser-mode verification.

## Product — Ops

- `decide-build-primitive` — Analyze and decide the right Codex primitive (Skill, Custom Prompt, or Agent automation) for a capability. Use this when you need to plan how to package or automate a workflow.
- `linear` — This skill provides a structured workflow for managing issues, projects & team workflows in Linear. It ensures consistent integration with the Linear MCP server, which offers natural-language project management for issues, projects, documentation, and team collaboration.. Use when When the user wants to read, create, or update Linear issues or projects..
- `release` — Create and publish a new project release (semver) when you need to cut a main-branch, clean-tree release via just release X.Y.Z for Cargo publish and git tag creation.

## Product — Review

- `llm-design-review` — Structure a multidisciplinary design review for LLM-powered products, producing actionable risks, fixes, and evidence gaps across UX, architecture, AI safety, and operations.. Use when Use this skill when the task matches its description and triggers..
- `product-design-review` — Deliver a user-centered UX critique across the full experience. Use for heuristic reviews and journey analysis (not file:line guideline compliance).

## Product — Specs

- `prd-clarifier` — Refine and clarify PRDs via structured AskUserQuestion sessions. Use when a PRD is ambiguous, missing acceptance criteria, or needs scoped clarification before planning.
- `prd-to-accessibility` — Generate accessibility requirements and checks from a PRD, aligned to WCAG targets and key journeys. Use when accessibility expectations must be explicit and testable.
- `prd-to-api-lite` — Generate a minimal API outline from a PRD (endpoints + example requests/responses). Use for demos or early alignment, not full contracts.
- `prd-to-api` — Generate a full API specification from a PRD or tech spec (endpoints, schemas, errors, auth). Use when a production-grade contract is required.
- `prd-to-arch-lite` — Generate a lite architecture snapshot from a PRD (minimal components + primary flow). Use for demo-grade guidance, not full governance.
- `prd-to-arch` — Generate a full architecture specification from a PRD or tech spec. Use when system boundaries and diagrams must be locked before build.
- `prd-to-qa-cases` — Generate QA test cases from PRD acceptance criteria using Given/When/Then and expected results. Use when QA coverage needs explicit, auditable cases.
- `prd-to-risk` — Generate a risk register and mitigation plan from a PRD, covering product, security, delivery, and dependency risks. Use when risks must be explicitly enumerated and owned.
- `prd-to-roadmap` — Generate a phased roadmap from a PRD with goals, dependencies, and validation gates. Use when sequencing and milestone logic must be explicit without dates.
- `prd-to-security-review` — Generate a security review from a PRD. Use when security requirements, threats, and mitigations must be explicit before build.
- `prd-to-testplan` — Generate a test plan and validation matrix from a PRD, mapping acceptance criteria to test types and quality gates. Use when verification strategy must be explicit before build.
- `prd-to-ui-spec` — Generate UI specifications from PRDs or UX specs using the aStudio design system. Use when a UI spec is needed before build or mockups.
- `prd-to-ux` — Generate UX specifications from PRDs, feature specs, or product requirements for mockup tools. Use when preparing UX foundations before visual design.
- `product-spec` — Create or review PRDs/tech specs for product ideas; use when you need structured requirements, UX spec, and build plan, especially for high-risk scopes.
- `ui-spec-to-prompts` — Translate a UI spec into build-order prompts for UI generator tools (v0, Bolt, Claude). Use when a UI spec already exists (not UX‑only).
- `ux-spec-to-prompts` — Translate UX specifications into build-order prompts for UI generator tools. Use when you have UX flows/PRDs and need sequenced prompts (not a full UI spec).

## Product — Strategy

- `code-plan` — Turn a user prompt into a **single, actionable plan** delivered in the final assistant message.. Use when When a user explicitly asks for a plan or roadmap..
- `project-improvement-ideator` — Generate and winnow project improvement ideas to a top 5. Use when asked for roadmap/improvement ideas.

## Product — Tech

- `tech-to-data` — Generate a data specification from a tech spec covering schemas, lifecycle, retention, and access controls. Use when data contracts must be explicit before implementation.
- `tech-to-migration` — Generate a migration plan from a tech spec with phased rollout, rollback, and validation. Use when schema or data changes require controlled execution.
- `tech-to-ops` — Generate an ops/runbook spec from a tech spec with SLOs, alerts, dashboards, and rollback steps. Use when operational readiness must be defined.
- `tech-to-performance` — Generate a performance plan from a tech spec with budgets, load tests, thresholds, and monitoring. Use when performance targets must be explicit and verifiable.

## Utilities

- `1password` — Plan, validate, and use 1Password CLI setup for secret injection and auth. Use when tasks need 1Password CLI usage, secret references, op run/read/inject, or provisioning secrets via env vars/.env files and scripts.
- `agent-browser` — Use this skill to extract page state and automate web interactions with the agent-browser CLI (navigate, snapshot, click, fill, screenshot). Use this when you need deterministic browser automation or scraping via ref-based elements.
- `beautiful-mermaid` — Render Mermaid diagrams to SVG and PNG with Beautiful Mermaid. Use when the user asks to render or convert Mermaid diagrams into images.
- `codeception` — Extract reusable, non-obvious learnings from a completed task into new Codex agent skills (SKILL.md). Use when the user asks to run codeception, do a retrospective, save/extract a skill, or turn a workaround into a reusable skill.
- `markdown-converter` — Convert files to Markdown using — no installation required.. Use when Use this skill when the task matches its description and triggers..
- `process-watch` — Analyze system processes and resource usage to diagnose runaway processes. Use when investigating CPU/memory/IO spikes.
- `recon-workbench` — Analyze and report authorized evidence using Recon Workbench (rwb) workflows. Use when you need authorize/plan/run/summarize flows and evidence-backed reporting for web apps or OSS repos.
- `remotion` — Best-practice guidance for Remotion (React video). Use when building or reviewing Remotion compositions, timing, assets, audio, captions, or rendering.
- `repoprompt` — Plan and guide Repo Prompt integration and usage in AI coding workflows. Use when integrating Repo Prompt with editors/agents or when needing MCP/CLI tool guidance.
- `skill-creator` — Create, revise, and quality-gate Codex skills (SKILL.md + resources + evals + packaging). Use when asked to build or improve a skill.
- `skill-installer` — Plan and install skills into a Codex skills directory from a curated list or repo. Use when a user asks to list or install skills.
- `video-transcript-downloader` — Extract, summarize, and download video/audio/subtitles using yt-dlp/ffmpeg. Use when the user requests downloads or transcripts.

