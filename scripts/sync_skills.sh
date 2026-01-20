#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

categories=(github frontend apple backend product utilities)
excluded_names=(skill-creator skill-installer)
skills_dir="$repo_root/skills"
system_skills_dir="$repo_root/skills-system"

mkdir -p "$skills_dir"

# Ensure system skills are not in the flat symlink view (prevents duplicates).
if [ -d "$skills_dir/.system" ]; then
  mkdir -p "$system_skills_dir"
  # Use rsync to handle existing directories, then remove source
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$skills_dir/.system/" "$system_skills_dir/"
    rm -rf "$skills_dir/.system"
  elif command -v zsh >/dev/null 2>&1; then
    zsh -c "setopt globdots; rm -rf \"$system_skills_dir\"/*; mv \"$skills_dir/.system\"/* \"$system_skills_dir\"/; rmdir \"$skills_dir/.system\""
  else
    # Fallback: remove target first, then move
    rm -rf "$system_skills_dir"/*
    mv "$skills_dir"/.[!.]* "$system_skills_dir"/ 2>/dev/null || true
    mv "$skills_dir"/..?* "$system_skills_dir"/ 2>/dev/null || true
    mv "$skills_dir"/* "$system_skills_dir"/ 2>/dev/null || true
    rmdir "$skills_dir/.system" 2>/dev/null || true
  fi
fi

# Remove stale symlinks only (keep any real files that might be intentional).
find "$skills_dir" -maxdepth 1 -type l -exec rm -f {} +

# Recreate symlinks for each category's SKILL.md directories.
for category in "${categories[@]}"; do
  while IFS= read -r skill_path; do
    skill_dir="$(dirname "$skill_path")"
    skill_name="$(basename "$skill_dir")"
    skill_dir_abs="$repo_root/$skill_dir"
    for excluded in "${excluded_names[@]}"; do
      if [ "$skill_name" = "$excluded" ]; then
        continue 2
      fi
    done
    ln -s "$skill_dir_abs" "$skills_dir/$skill_name"
  done < <(rg --files -g 'SKILL.md' "$category")
done

# Regenerate root SKILL.md index.
cat > "$repo_root/SKILL.md" <<'INDEX_EOF'
# Agent Skills Index

Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/skills`.

## GitHub/DevOps
- `gh-actions-fix` — Inspect failing GitHub Actions checks, summarize failures, and implement fixes after approval. Not for external CI or PR merge/testing; use gh-pr-local for PR workflows.
- `gh-address-comments` — Address GitHub PR review or issue comments with gh CLI. Not for CI failures or full issue workflows; use gh-actions-fix or gh-issue-fix.
- `gh-issue-fix` — End-to-end GitHub issue fix workflow with gh, local changes, tests, commit, and push. Not for comment triage or CI-only fixes; use gh-address-comments or gh-actions-fix.
- `gh-pr-local` — Fetch, preview, merge, and test GitHub PRs locally. Not for issue workflows or CI debugging; use gh-issue-fix or gh-actions-fix.
- `github-pr` — Fetch, preview, merge, and test GitHub PRs locally. Great for trying upstream PRs before they're merged.

## Frontend/UI
- `codex-ui-kit-installer` — Install or update codex-ui-kit in a repo and optional Codex UI prompts. Not for general skill installation; use skill-installer or clawdhub.
- `favicon-generator` — Generate professional-quality favicons that rival the best app icons. Uses a multi-layer effects engine with drop shadows, inner glows, highlights, gradients, and noise textures. Includes 8 curated design templates and 18 Lucide icons. Produces complete favicon suites with proper ICO, SVG, PNG formats and framework integration. Trigger when users need favicons, app icons, or browser tab icons.
- `frontend-ui-design` — Design or implement frontend UI/UX components across web, Apple, and Tauri desktop surfaces with tokens and accessibility. Not for design-system governance or visual regression; use ui-design-system or ui-visual-regression.
- `nano-banana-builder` — Build full-stack web applications powered by Google Gemini's Nano Banana & Nano Banana Pro image generation APIs. Use when creating Next.js image generators, editors, galleries, or any web app that integrates gemini-2.5-flash-image or gemini-3-pro-image-preview models. Covers React components, server actions, API routes, storage, rate limiting, and production deployment patterns.
- `og-image-creator` — Smart OG image generation that studies your codebase, understands routes and brand identity, then creates contextually appropriate Open Graph images using Playwright and React components. Triggers: "create og images", "generate social cards", "add open graph images".
- `react-ui-patterns` — Provide React UI patterns and examples with TypeScript, Tailwind, and Radix. Not for design-system governance or visual regression; use ui-design-system or ui-visual-regression.
- `seo-optimizer` — Comprehensive SEO optimization for web applications. Use when asked to improve search rankings, add meta tags, create structured data, generate sitemaps, optimize for Core Web Vitals, or analyze SEO issues. Works with Next.js, Astro, React, and static HTML sites.
- `threejs-builder` — Creates simple Three.js web apps with scene setup, lighting, geometries, materials, animations, and responsive rendering. Use for: "Create a threejs scene/app/showcase" or when user wants 3D web content. Supports ES modules, modern Three.js r150+ APIs.
- `ui-design-system` — Create or update governed UI design systems across SwiftUI and React stacks. Not for app-specific UI implementation or visual regression; use frontend-ui-design or ui-visual-regression.
- `ui-visual-regression` — Run and interpret UI visual regression workflows (Storybook, Playwright, Argos). Not for UI implementation or design-system governance; use frontend-ui-design or ui-design-system.

## Apple/Swift
- `apple-mail-search` — Search, triage, and organize Apple Mail on macOS. Not for Gmail, Outlook, or webmail workflows.
- `instruments-profiling` — Use when profiling native macOS or iOS apps with Instruments/xctrace. Covers correct binary selection, CLI arguments, exports, and common gotchas.
- `ios-sim-debug` — Use XcodeBuildMCP to build, run, launch, and debug the current iOS project on a booted simulator. Trigger when asked to run an iOS app, interact with the simulator UI, inspect on-screen state, capture logs/console output, or diagnose runtime behavior using XcodeBuildMCP tools.
- `macos-spm-packager` — Scaffold, build, and package SwiftPM-based macOS apps without an Xcode project. Use when you need a from-scratch macOS app layout, SwiftPM targets/resources, a custom .app bundle assembly script, or signing/notarization/appcast steps outside Xcode.
- `swift-concurrency-expert` — Review and remediate Swift concurrency (async/await, actors, Sendable, isolation) and performance issues. Not for SwiftUI layout or visual design.
- `swiftui-liquid-glass` — Adopt or review iOS 26+ Liquid Glass in SwiftUI. Not for general SwiftUI patterns or refactors; use swiftui-ui-patterns or swiftui-view-refactor.
- `swiftui-ui-patterns` — SwiftUI UI patterns and example structures for building screens and components. Not for refactors or Liquid Glass adoption; use swiftui-view-refactor or swiftui-liquid-glass.
- `swiftui-view-refactor` — Refactor SwiftUI views for structure, dependency injection, and Observation usage. Not for general UI patterns or Liquid Glass; use swiftui-ui-patterns or swiftui-liquid-glass.
- `xcode-build` — Build and manage iOS/macOS apps via XcodeBuildMCP and Xcode CLI tools. Not for interactive simulator debugging; use ios-sim-debug.

## Backend/Arch
- `backend-design` — Design backend architecture, data models, API contracts, auth, reliability, observability, and integrations. Trigger when user asks for backend design/specs or system architecture; not for frontend UI or product requirements (use frontend-ui-design or product-spec).
- `cli-spec` — Design command-line interface parameters and UX: arguments, flags, subcommands, help text, output formats, error messages, exit codes, prompts, config/env precedence, and safe/dry-run behavior. Use when you're designing a CLI spec (before implementation) or refactoring an existing CLI's surface area for consistency, composability, and discoverability.
- `mcp-builder` — Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
- `mkit-builder` — Build MCP servers integrating external APIs and services, including OAuth, billing, and Apps SDK UI. Not for general backend architecture; use backend-design.
- `workers-mcp` — Create production-ready Cloudflare Workers MCP servers with OAuth 2.1 authentication (Auth0), feature-based licensing (Stripe), D1 database, Durable Objects, Workers KV, and Vectorize vector search. Use when Codex needs to: (1) Scaffold a new Workers MCP project, (2) Add MCP tools with proper schemas and licensing, (3) Configure D1 database with migrations, (4) Set up Auth0 OAuth 2.1 authentication, (5) Implement Stripe subscription licensing, (6) Add Vectorize semantic search, (7) Deploy to Cloudflare Workers.

## Product/Docs
- `agents-md` — Create or update a repository-level AGENTS.md contributor guide with clear sections, commands, and repo-specific conventions. Use when asked to draft, improve, or standardize AGENTS.md files or when a repo needs concise contributor instructions.
- `app-store-release-notes` — Create user-facing App Store release notes by collecting and summarizing all user-impacting changes since the last git tag (or a specified ref). Use when asked to generate a comprehensive release changelog, App Store "What's New" text, or release notes based on git history or tags.
- `code-plan` — Create concise, actionable plans for coding tasks. Use when users ask for a plan, roadmap, or steps to implement a feature, fix, refactor, or investigation.
- `decide-build-primitive` — Decide whether a capability should be a Skill, custom prompt, or automation agent. Not for creating or installing skills; use skill-creator or skill-installer.
- `docs-expert` — Co-author, improve, and QA documentation (specs, READMEs, guides, runbooks). Trigger when user asks to create, revise, audit, or QA docs; not for implementation plans or PRDs (use code-plan or product-spec).
- `linear` — Manage Linear issues and projects (read, create, update). Not for GitHub issue flows; use gh-issue-fix.
- `llm-design-review` — Run design reviews and audits for LLM features across UX, architecture, model/prompt, safety, evaluation, and governance. Not for product PRDs; use product-spec.
- `product-design-review` — Review end-to-end user experience and UI for products or flows; produce a user-perspective critique with usability, accessibility, content, and interaction issues plus fixes. Use for UX/UI audits, product design reviews, onboarding or checkout critiques, heuristic evaluations, accessibility-first reviews, or when asked to find issues in a user journey from the user's point of view. Target web, iOS, and macOS products, including React apps and open-source software.
- `product-manager` — Lead users through every software design step—from idea to production-ready PRD or technical spec—via interview, drafting, adversarial debate, diagrams, and gold-standard validation; use whenever the user asks for PRD/tech specs, software design steps, or taking an idea to production.
- `product-spec` — Create PRDs and tech specs and critique UX flows. Not for documentation QA or implementation plans; use docs-expert or code-plan.
- `project-improvement-ideator` — Generate 30 pragmatic improvement ideas for the current project, weigh feasibility/impact/user perception, then winnow to the best 5 with rationale. Use when asked for “best ideas”, “improvements”, “roadmap”, or “top 5”/“winnow” prioritization. Not for full product specs or LLM design reviews; use product-spec or llm-design-review.
- `youtube-hooks-scripts` — Create compelling hooks and full scripts for technical YouTube videos about coding and AI. Use when given a video idea, braindump, source code, or rough notes to develop into engaging long-form content. Helps transform raw material into conversational scripts that grab attention and maintain engagement throughout.
- `youtube-titles-thumbnails` — Create high-performing YouTube titles and thumbnail text that maximize CTR and virality while maintaining authenticity. Use when analyzing video transcripts to generate title and thumbnail suggestions, optimizing existing titles/thumbnails, or when users request help with YouTube content strategy for click-through rate optimization.

## Utilities
- `1password` — Set up and use 1Password CLI (op) for install, desktop integration, sign-in, and secret injection. Not for non-1Password secret tooling.
- `markdown-converter` — Convert documents and files to Markdown using markitdown. Use when converting PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx, .xls), HTML, CSV, JSON, XML, images (with EXIF/OCR), audio (with transcription), ZIP archives, YouTube URLs, or EPubs to Markdown format for LLM processing or text analysis.
- `process-watch` — Monitor system processes and resources (CPU, memory, I/O, network) and manage runaway processes. Not for app-level profiling or code tuning.
- `recon-workbench` — Production-grade forensic evidence collection for software interrogation across macOS/iOS, web/React, and OSS repos. Use when running rwb CLI commands (doctor, authorize, plan, run, manifest, summarize, validate), designing probe catalogs or schemas, generating evidence-backed findings, inspecting targets under authorization guardrails, or configuring scope and compliance policies.
- `skill-creator` — Create, update, validate, or package skills and their resources. Use when a user asks to create or revise a skill, improve routing/portability, or package a skill; not for installing skills or choosing the right build primitive (use skill-installer or decide-build-primitive).
- `skill-installer` — Install skills into $CODEX_HOME/skills from curated lists or GitHub paths. Not for clawdhub.com installs or skill creation.
- `video-transcript-downloader` — Download videos, audio, subtitles, and clean paragraph-style transcripts from YouTube and any other yt-dlp supported site. Use when asked to “download this video”, “save this clip”, “rip audio”, “get subtitles”, “get transcript”, or to troubleshoot yt-dlp/ffmpeg and formats/playlists.
INDEX_EOF

chmod +x "$repo_root/scripts/sync_skills.sh"

echo "Synced symlinks and regenerated SKILL.md."
