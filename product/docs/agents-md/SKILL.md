---
name: agents-md
description: Create or refactor AGENTS.md and linked instruction docs using progressive disclosure. Use when the user wants repo-specific agent guidance organized, deduplicated, or routed cleanly, not ordinary product documentation edits.
metadata:
  skill-type: code_quality_review

---

# Agents Md

Create and maintain concise, high-signal AGENTS guidance with progressive disclosure.

## Table of Contents
- [When to use](#when-to-use)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Inputs](#inputs)
- [Discovery interview](#discovery-interview)
- [Response format](#response-format)
- [Outputs](#outputs)
- [Failure mode](#failure-mode)
- [Philosophy](#philosophy)
- [Constraints](#constraints)
- [Procedure](#procedure)
- [Validation](#validation)
- [Shared guidance propagation](#shared-guidance-propagation)
- [Project-tailored repo baseline](#project-tailored-repo-baseline)
- [Anti-patterns](#anti-patterns)
- [Variation](#variation)
- [Mandatory workflow snippet](#mandatory-workflow-snippet)
- [Examples](#examples)
- [Resource map](#resource-map)
- [Decision feedback protocol](#decision-quality-feedback)

## When to use
- Use this skill when the user asks to create or update `AGENTS.md`.
- Use this skill when AGENTS docs are too large, duplicated, or contradictory.
- Use this skill when instruction routing needs to be split into linked files.
- Use this skill when a repo needs AGENTS operating rules such as preflight, stack detection, tooling, required paths, Local Memory policy, or startup workflow tailored from real repo evidence.

## Standards snapshot (March 2026)
- Keep root `AGENTS.md` minimal and route depth into linked docs.
- Start with 2-3 focused surfaces for a first pass: usually the root `AGENTS.md`, one linked-doc tree, and only one nested override if it is truly needed.
- Teach the canonical discovery chain: global `AGENTS.override.md` or `AGENTS.md`, then per-directory `AGENTS.override.md`, `AGENTS.md`, then configured fallback filenames.
- Treat only one auto-loaded instruction file per directory as canonical; linked docs are progressive-disclosure references, not implicitly discovered project instructions.
- Keep combined project guidance under the `project_doc_max_bytes` budget (32 KiB default) by splitting large guidance across nested scopes instead of bloating one root file.
- When harmonizing `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, keep shared operational rules semantically aligned while respecting each tool's official instruction-file model and section conventions.
- Base commands, paths, and conventions on verified repo evidence only.
- Treat contradiction detection and instruction precedence as first-class outputs.
- Prefer progressive disclosure over megadoc accumulation.

## Required inputs
- Target repository root path.
- Existing `AGENTS.md`, `AGENTS.override.md`, fallback-named instruction files, and related linked docs.
- Verified commands/paths from repository sources.
- Active Codex config knobs when present: `project_doc_fallback_filenames`, `project_doc_max_bytes`, and any custom `CODEX_HOME` expectations.
- Preferred linked-doc tree (`instructions/agents` or `docs/agents`) based on repo convention.
- Repo preflight command state, including whether `./scripts/codex-preflight.sh --stack auto --mode required` exists and which flags are supported, such as `--repo-fragment`, `--bins`, and `--paths`.
- Root manifest signals for stack detection, such as `package.json`, `pyproject.toml`, or `Cargo.toml`.
- Required repo paths and whether they are present, especially `docs/`, `docs/plans/`, and any repo-specific operating folders.
- Whether the repo has explicitly adopted the harness-memory convention and, if so, whether `.harness/memory/LEARNINGS.md` is part of the required operating surface.
- Local Memory policy expectations and whether required-mode checks are genuinely part of the repo standard.
- Optional supplemental context files, such as `Learning.md` or `Learnings.md`, only when they exist and are intended for operators.

## Discovery interview
Run discovery for underspecified AGENTS creation or refactor requests.
- For discovery-only prompts that do not provide a concrete repo path or editable files yet, do not explore the filesystem or run tools first. Ask the compact scope question immediately.
- Ask one round at a time and wait before moving forward.
- Start each round with one plain-language question and explain why the round matters in a short `Why this matters:` line.
- Avoid dumping the whole interview plan at once; keep the first turn to the current round only.
- Skip already-answered rounds.
- Stop when repo scope, instruction chain, contradiction risks, and preferred linked-doc layout are clear enough to write safely.
- Before implementation, summarize confirmed facts, assumptions, and the approval checkpoint.
- Use `references/discovery-interview.md` for reusable round templates.

## Response format
- For the first discovery response, start with `## Scope and triggers`, then `## Required inputs`.
- In that first discovery response, include one short `Why this matters:` line and ask only one intuitive scope question before waiting.
- Keep discovery-round responses minimal and immediate: no repo walkthrough, no extra sections, no tool calls, no examples, and no optional next-step menu before the question.
- Prefer one of these exact discovery questions in round one:
  - `Which instruction scope are we changing here?`
  - `What AGENTS scope are we changing?`
  - `What should this skill help you do?`
- For the confirmation round, start with `## Skill Summary:`.
- In the confirmation round, include `Assumptions:` when any remain and end with one simple confirmation question such as `Does this capture it well enough for me to build?`.
- Keep the confirmation round compact as well: summarize only the current AGENTS update shape, list assumptions only when needed, and end with the single confirmation question.
- For out-of-scope responses, keep the compact structure expected by the evals: `## When to use`, `## Outputs`, and `## Inputs`.

## Deliverables
- Updated minimal root `AGENTS.md`.
- Updated scoped overrides when a nested directory truly needs different rules.
- Linked category docs for deeper instructions.
- Contradiction list and deletion candidates.
- Verification commands with expected discovery behavior.
- Evidence-backed command map and validation notes.
- If you return a machine-checkable split plan or JSON contract, include `schema_version`.

## Failure mode
If command truth, path ownership, or instruction precedence cannot be verified, stop at that contradiction, state the conflict clearly, and request a decision instead of writing speculative AGENTS guidance.

## Philosophy
- Prefer concise, verifiable guidance over comprehensive prose.
- Keep root AGENTS as an operator map, with depth in linked docs.
- Optimize for reader success in under two minutes.
- Why keep this instruction in root instead of a linked doc?
- What evidence confirms this command/path is real?
- Which tradeoff is best here: brevity or explicitness?

## Constraints
- Redact secrets, tokens, credentials, and PII by default.
- Do not invent commands, scripts, or paths.
- Keep ASCII by default unless repository conventions require otherwise.
- Avoid adding dependencies, legacy shims, or compatibility layers unless explicitly requested.

## Procedure
1. Discover repo facts, active instruction scopes, and any Codex config knobs that affect instruction discovery.
2. Detect command/style conventions from actual repo evidence.
3. Map the canonical instruction chain: global file, repo/root file, nested overrides, and linked docs.
4. Identify contradictions, duplicate guidance, and places where linked docs are being mistaken for auto-loaded instructions.
5. Write minimal root AGENTS, reserve overrides for genuinely narrower scopes, and link deeper docs for progressive disclosure.
6. Add table of contents for generated docs.
7. Validate links, commands, discovery behavior, and instruction consistency.

## Validation
- Confirm commands exist in repo scripts/docs.
- Confirm file paths exist and links resolve.
- Confirm any prescribed preflight command and flags actually exist before inserting them.
- Confirm stack detection guidance matches observed root manifests or documented repo scripts.
- Confirm required-path guidance only names directories that exist or are explicit repo policy.
- Confirm Local Memory requirements are present only when requested or verified by repo policy.
- Confirm discovery guidance matches official behavior: `AGENTS.override.md` wins within a directory, fallback names require config, empty files are ignored, and combined project docs are capped by `project_doc_max_bytes`.
- Provide the official verification commands when applicable:
  - `codex --ask-for-approval never "Summarize the current instructions."`
  - `codex --cd <subdir> --ask-for-approval never "Show which instruction files are active."`
- Confirm no contradictory instructions remain unresolved.
- Fail fast: stop at first critical contradiction and request decision.

## Shared guidance propagation
- When a user asks to add guidance under named AGENTS sections, place it in the canonical AGENTS file for that repo scope and update that file's Table of Contents.
- If the named section does not exist, create it with concise, action-oriented bullets instead of scattering equivalent guidance across multiple unrelated files.
- Keep cross-repo guidance consistent by mirroring durable section-level rules in this skill when they affect how AGENTS refactors should be performed.
- When a user wants the same operating rule reflected across `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, keep the rule semantically consistent across all three files but preserve target-specific wording and file structure instead of forcing one identical block everywhere.
- When a repo uses `CLAUDE.md`, prefer Anthropic's official style guidance: concise, specific, verifiable instructions, structured headings, and stronger wording over duplicate bullets when a weaker rule already exists.
- When a repo uses `GEMINI.md`, preserve Gemini CLI's configured context-file behavior and avoid assuming the filename is always the default when the repo or tool config sets `context.fileName` differently.
- For TypeScript validation guidance in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, place repo-native test and lint instructions under `## Quality Checks`. If that section does not exist, create it. In npm-based repos, require `npm run lint` and `npm run test` after TypeScript changes and require both to pass before the session is marked complete. If equivalent guidance already exists, strengthen it instead of duplicating it.
- For CI guidance in `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`, place the rule under `## CI/CD Workflow` when present or create that section when it is missing. Require confirmation of the final authoritative pipeline or workflow-run status before ending CI/CD work, not just a local fix or partial rerun.
- For pull-request coordination guidance in `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`, place the rule under `## GitHub Workflow` or `## PR Management`. Require checking merge-conflict state up front for multi-repo PR work, flagging blocked PRs early, and calling out blockers before spending effort on downstream merge prep.
- When repo operating rules are requested, tailor sections like `Repository rules`, `Stack detection`, `Required tooling`, `Required repo paths`, `Local Memory policy`, `Startup workflow`, and `Supplemental context` from verified repo evidence instead of copying a fixed block unchanged.
- For section-level additions touching operational safety, preserve explicit checks for:
  - quality validation after config/CI/dependency edits,
  - external tool authentication readiness (including 1Password/env cache checks),
  - git-history risk escalation before complex rebase/conflict workflows,
  - tool/skill existence verification before fallback assumptions,
  - exact path verification against documented locations before commit.
- When preflight guidance is requested, prefer `./scripts/codex-preflight.sh --stack auto --mode required` only if the repo really ships that script and supports its documented flags. Preserve supported overrides like `--repo-fragment`, `--bins`, and `--paths` only when they are part of the repo's actual script.
- When stack detection guidance is requested, derive it from root manifests such as `package.json`, `pyproject.toml`, and `Cargo.toml`, and mention override flags only when the repo's scripts or docs support them.
- When required path guidance is requested, mention `docs/` and `docs/plans/` only if they are present or explicitly standardized by the repo.
- When architecture-context guidance is requested, treat the repo's documented architecture-diagram surface as valuable quick-start context when it exists, because diagrams often help agents form a correct system model faster than prose alone.
- Never silently normalize between diagram-path variants such as `.diagram/`, `.diagrams/`, or `AI/diagrams/`. Verify the repo's documented path first and then use that exact location consistently in AGENTS guidance.
- When project learnings guidance is requested, require `.harness/memory/LEARNINGS.md` only for repos that explicitly adopt the harness-memory convention. Otherwise, treat it as `not observed` rather than promoting it into a universal required path.
- When a repo uses legacy guidance files like `FORJAMIE.md`, do not present them as canonical by default. Either migrate durable guidance into `AGENTS.md`, register the file through `project_doc_fallback_filenames`, or mention it only as supplemental context when the file actually exists.
- When external integration guidance is requested, preserve a strict preflight order:
  1. env vars resolved,
  2. `op account list` succeeds,
  3. simple MCP/API connectivity check,
  4. then full operations.
  If auth fails, require auth-layer debugging before operation retries.
- When Local Memory guidance is requested, preserve the script's explicit mode handling (`off`, `optional`, `required`) and required-mode checks for installation, daemon health, config path resolution (`LOCAL_MEMORY_CONFIG_PATH` or `~/.local-memory/config.yaml`), `host: 127.0.0.1`, `auto_port: false`, numeric `rest_api_port`, REST health, smoke cycle (`observe`, `relate`, `search`), malformed payload rejection, duplicate-observe snapshot capture, daemon-log migration signal check when available, and stop-on-failure behavior in required mode.
- When git safety guidance is requested, require explicit pre-operation briefing for rebasing 5+ commits, merge conflict resolution, and force-pushes, including branch state, strategy with risks, alternatives, and user confirmation.
- When validation guidance is requested for config-sensitive files (for example `package.json`, CI workflows, `settings.json`, config files), require running applicable validation commands and reporting pass status before commit.
- When command preflight guidance is requested, preserve explicit `exec_command` preflight rules: run shell via `zsh -lc`, use `which` before `mise` installs, and verify destructive-operation paths with `fd` before execution.
- When policy guidance is requested, include sandbox tuning rules that review rejected patterns, whitelist safe frequent commands, and keep strict controls for destructive operations.
- When MCP workflow guidance is requested, require `codex mcp list` before implementation and require fixing missing server setup first.
- When delivery workflow guidance is requested, require separate implementation and verification `codex exec` workflows, and require `codex review --uncommitted` before merge.
- When startup workflow guidance is requested, preserve the operator sequence: read `AGENTS.md` and task-relevant docs, run the required preflight, summarize repo structure and blockers before editing, make the smallest change that satisfies the task, and run the narrowest validation that proves the change works.
- When supplemental context guidance is requested, mention organization-level `instructions/Learning.md` or `instructions/Learnings.md` only if those files exist and the repo wants them as extra context. Keep them supplemental, not a replacement for repo-local instructions.

## Project-tailored repo baseline
- Use `references/project-tailored-agents-baseline.md` when a user wants a reusable AGENTS operating baseline adapted to each repository.
- Treat the baseline as a section menu, not a verbatim template. Verify each section before insertion.
- Keep `Repository rules` grounded in the actual repo preflight, supported flag set, and repo-root workflow.
- Keep `Stack detection` grounded in observed root manifests and documented override behavior.
- Keep `Required tooling` and `Required repo paths` limited to what the repo actually needs.
- Keep architecture-diagram paths repo-specific: mention `.diagram/`, `.diagrams/`, or another diagram directory only when that exact path is documented or verified in the repo.
- Keep `.harness/memory/LEARNINGS.md` opt-in at the repo level unless the repo has explicitly adopted the harness-memory convention.
- Keep `Local Memory policy` opt-in unless the repo or user explicitly makes it required.
- Treat `FORJAMIE.md` as legacy or supplemental unless repo evidence shows it is still a live fallback instruction file.
- Keep `Startup workflow` and `Supplemental context` concise and operator-focused.

## Anti-patterns
- Do not dump full policy documents into root AGENTS.
- Never duplicate the same instruction across many files without need.
- Do not keep vague guidance that cannot be executed.
- Do not paste the same `Repository rules` or `Local Memory policy` block into every repo without checking scripts, manifests, paths, and actual repo standards first.
- Do not keep stale `FORJAMIE.md` references around once the file is gone or the repo has moved to `AGENTS.md`.
- Do not imply that arbitrary linked Markdown files are auto-discovered by Codex; only scoped AGENTS files and configured fallback filenames participate in instruction discovery.
- Avoid repetitive, generic, cookie-cutter templates that ignore repo context.
- Warn on conflicting package manager instructions and unresolved hierarchy conflicts.

## Variation
- Adapt structure for small repos versus multi-package monorepos.
- Use different category splits based on repo domains (frontend, backend, ops, docs).
- Customize guidance depth to team maturity and operational risk.
- Keep scope tight on the first pass; expand beyond the core 2-3 surfaces only when the repo evidence or user request clearly requires it.

## Mandatory workflow snippet
1. Explore project first, then invoke skill.
2. IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any React, Tauri, Apps-SDK-ui, Tailwind, Vite, Storybook + Chat Widget tasks.
3. Add a Table of Contents for docs.

## Examples
- User says: "Can you help me trim this giant root `AGENTS.md` and move the detailed policy into linked docs without breaking Codex discovery?"
- User says: "Please inspect our repo instructions and explain whether `services/payments/AGENTS.override.md` should replace the broader root rule."
- User says: "Validate this `TEAM_GUIDE.md` setup and tell me whether I should migrate it or register it with `project_doc_fallback_filenames`."
- User says: "Help me merge AGENTS, CLAUDE, and GEMINI guidance into one progressive-disclosure instruction tree."
- User says: "Update our shared AGENTS, CLAUDE, and GEMINI guidance so all three get a `## Quality Checks` section with `npm run lint` and `npm run test`, CI work always ends by confirming final pipeline status, and multi-repo PRs check merge conflicts up front."
- User says: "Inspect these conflicting instructions and return a clear conflict-decision list before you edit anything."
- User says: "Update our AGENTS template so repo rules, stack detection, required tooling, required paths, Local Memory policy, and startup workflow are tailored per project instead of copied blindly."
- User says: "We used to have a `FORJAMIE.md` file. Please update the AGENTS guidance so it handles that legacy file correctly."
- User says: "Our repo keeps architecture drawings in `.diagrams/`. Update the AGENTS guidance so agents use that as quick project context without guessing the wrong diagram path in other repos."

## Resource map
- References: `references/contract.yaml`, `references/discovery-interview.md`, `references/evals.yaml`, `references/folded-legacy-modes-core60.md`, `references/official-codex-agents-guidance.md`, `references/project-tailored-agents-baseline.md`, `references/task-profile.json`

## See Also

| Skill | When to use together |
|---|---|
| [[skill-builder]] | Build new skills that will be registered in AGENTS.md |
| [[codex-home-audit]] | Audit the full Codex home dir after AGENTS.md refactors |
| [[codex-agent-creator]] | Create agent roles that AGENTS.md will reference |
| [[docs-expert]] | Apply docs polish and community-health guidance to AGENTS.md |
| [[compound-engineering-router]] | Route compound workflows referenced in AGENTS.md |

**Topic map:** [[agent-ops]]

<!-- decision-feedback-protocol:v2 -->
## Decision Quality Feedback
- If post-run feedback capture is enabled, emit non-blocking `post_run_feedback` after result delivery.
- Capture `decision`, `outcome`, and `confidence`.
- Persist with `python3 utilities/skill-builder/scripts/record_skill_feedback.py`.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
