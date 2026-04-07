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
- [Standards snapshot](#standards-snapshot-april-2026)
- [Required inputs](#required-inputs)
- [Discovery interview](#discovery-interview)
- [Response format](#response-format)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Philosophy](#philosophy)
- [Constraints](#constraints)
- [Procedure](#procedure)
- [Validation](#validation)
- [Project-tailored repo baseline](#project-tailored-repo-baseline)
- [Anti-patterns](#anti-patterns)
- [Variation](#variation)
- [AGENTS.md Template Guidance](#agentsmd-template-guidance)
- [Mandatory workflow snippet](#mandatory-workflow-snippet)
- [Examples](#examples)
- [Resource map](#resource-map)
- [Decision feedback protocol](#decision-quality-feedback)

## When to use

- Use this skill when the user asks to create or update `AGENTS.md`.
- Use this skill when AGENTS docs are too large, duplicated, or contradictory.
- Use this skill when instruction routing needs to be split into linked files.
- Use this skill when a repo needs AGENTS operating rules such as preflight, stack detection, tooling, required paths, Local Memory policy, Project Brain policy, or startup workflow tailored from real repo evidence.
- Use this skill when the user wants the project's instruction surface audited so required instruction files are present, current, correctly routed, and accurately disclosed.

## Standards snapshot (April 2026)

Use this section as an adaptation guideline for generated AGENTS.md files, not runtime policy.

- Keep root `AGENTS.md` minimal and route depth into linked docs.
- Start with 2-3 focused surfaces for a first pass: usually the root `AGENTS.md`, one linked-doc tree, and only one nested override if it is truly needed.
- Teach the canonical discovery chain: global `AGENTS.override.md` or `AGENTS.md`, then per-directory `AGENTS.override.md`, `AGENTS.md`, then configured fallback filenames.
- Treat only one auto-loaded instruction file per directory as canonical; linked docs are progressive-disclosure references, not implicitly discovered project instructions.
- Keep combined project guidance under the `project_doc_max_bytes` budget (32 KiB default) by splitting large guidance across nested scopes instead of bloating one root file.
- **Instruction budget:** frontier thinking models can reliably follow ~150–200 instructions. Every token in `AGENTS.md` loads on every request regardless of relevance, so every instruction must earn its place.
- **Minimum viable floor:** the root file needs only three things — a one-sentence project description, the package manager if not npm, and any non-standard build/typecheck commands. Everything else is a candidate for progressive disclosure.
- **Staleness is poison:** avoid documenting file paths in `AGENTS.md`; they change constantly and agents read stale paths confidently. Describe capabilities and where things *might* be rather than hardcoding structure.
- **Never auto-generate AGENTS.md files;** generated files flood the budget with generic instructions that hurt performance. Write them intentionally.
- When harmonizing `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, keep shared operational rules semantically aligned while respecting each tool's official instruction-file model and section conventions. For cross-tool coverage, a `ln -s AGENTS.md CLAUDE.md` symlink is a valid low-maintenance option when Claude Code is in scope.
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
- Project Brain expectations, including whether `instructions/project-brain.md` exists, whether a root-visible Project Brain section is expected, and whether a bootstrap helper such as `scripts/init-project-brain.sh` is part of the documented workflow.
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
- For out-of-scope responses, keep the compact structure expected by the evals: `## When to use`, `## Deliverables`, and `## Required inputs`.

## AGENTS.md Template Guidance

Reference guidance for AGENTS.md templates — adapt before emitting; not runtime/operational instructions.

Treat this as a template adaptation block. Runtime behavior is defined in:
- [AGENTS.md](../../../AGENTS.md)
- [CLAUDE.md](../../../CLAUDE.md)
- [GEMINI.md](../../../GEMINI.md)

Canonical shared guidance text lives in [Workflow and safety guidance](../../../docs/agents/13-workflow-and-safety-guidance.md). Keep this section as references, not duplicated runtime policy:
- Testing → [Workflow and safety guidance](../../../docs/agents/13-workflow-and-safety-guidance.md#testing)
- Git Workflow → [Workflow and safety guidance](../../../docs/agents/13-workflow-and-safety-guidance.md#git-workflow)
- Configuration Files → [Workflow and safety guidance](../../../docs/agents/13-workflow-and-safety-guidance.md#configuration-files)
- Code Review Fixes → [Workflow and safety guidance](../../../docs/agents/13-workflow-and-safety-guidance.md#code-review-fixes)
- Shell Scripting → [Workflow and safety guidance](../../../docs/agents/13-workflow-and-safety-guidance.md#shell-scripting)
- Refactoring → [Workflow and safety guidance](../../../docs/agents/13-workflow-and-safety-guidance.md#refactoring)
- Documentation → [Workflow and safety guidance](../../../docs/agents/13-workflow-and-safety-guidance.md#documentation)

## Deliverables

Use this section as an adaptation checklist for generated AGENTS.md outputs.

- Updated minimal root `AGENTS.md`.
- Updated scoped overrides when a nested directory truly needs different rules.
- Linked category docs for deeper instructions.
- Contradiction list and deletion candidates.
- Verification commands with expected discovery behavior.
- Evidence-backed command map and validation notes.
- Required-instruction coverage report showing which files were verified, created, strengthened, left unchanged, or intentionally omitted.
- If you return a machine-checkable split plan or JSON contract, include `schema_version`.

## Failure mode

If command truth, path ownership, or instruction precedence cannot be verified, stop at that contradiction, state the conflict clearly, and request a decision instead of writing speculative AGENTS guidance.

## Philosophy

- Prefer concise, verifiable guidance over comprehensive prose.
- Keep root AGENTS as an operator map, with depth in linked docs.
- Optimize for reader success in under two minutes.
- Every instruction not relevant to the current task wastes tokens and distracts the agent. Irrelevant instructions do not just occupy space; they reduce model attention on the actual work.
- Before adding anything to root AGENTS, apply these self-tests:
  - Is this relevant to **every single task** in this repo? If not, it belongs in a linked doc.
  - Why keep this instruction in root instead of a linked doc?
  - What evidence confirms this command/path is real?
  - Which tradeoff is best here: brevity or explicitness?
  - Would removing this line hurt a real workflow?

## Constraints

- Redact secrets, tokens, credentials, and PII by default.
- Do not invent commands, scripts, or paths.
- Keep ASCII by default unless repository conventions require otherwise.
- Avoid adding dependencies, legacy shims, or compatibility layers unless explicitly requested.

## Procedure

1. Discover repo facts, active instruction scopes, and any Codex config knobs that affect instruction discovery.
2. Detect command/style conventions from actual repo evidence.
3. Map the canonical instruction chain: global file, repo/root file, nested overrides, and linked docs.
4. Audit the current instruction surface for four conditions before writing:
   - required files present for the repo's actual instruction model,
   - guidance still accurate against current repo evidence,
   - guidance still up to date with current scripts, paths, and workflow entrypoints,
   - and guidance disclosed in the correct file instead of hidden in the wrong scope or duplicated across surfaces.
5. Identify contradictions, duplicate guidance, stale guidance, and places where linked docs are being mistaken for auto-loaded instructions.
6. Write minimal root AGENTS, reserve overrides for genuinely narrower scopes, and link deeper docs for progressive disclosure.
7. Create or update missing required instruction files when repo evidence shows they belong in the active instruction surface.
8. Add table of contents for generated docs.
9. Validate links, commands, discovery behavior, instruction consistency, and coverage of the required instruction surface.

## Validation

- Confirm commands exist in repo scripts/docs.
- Confirm file paths exist and links resolve.
- Confirm any prescribed preflight command and flags actually exist before inserting them.
- Confirm stack detection guidance matches observed root manifests or documented repo scripts.
- Confirm required-path guidance only names directories that exist or are explicit repo policy.
- Confirm Local Memory requirements are present only when requested or verified by repo policy.
- Confirm Project Brain guidance is present when requested or when `instructions/project-brain.md` exists in the target scope, and confirm linked paths/scripts resolve before insertion.
- Confirm discovery guidance matches official behavior: `AGENTS.override.md` wins within a directory, fallback names require config, empty files are ignored, and combined project docs are capped by `project_doc_max_bytes`.
- Confirm each required instruction file for the chosen surface is either:
  - present and current,
  - created as part of the change,
  - intentionally omitted with a repo-evidence reason,
  - or replaced by a clearly disclosed canonical alternative.
- Confirm no stale rule survives when the repo evidence has moved, such as renamed scripts, deleted folders, outdated quality checks, or retired fallback instruction files.
- Confirm the final instruction set clearly discloses where durable guidance lives, which files are canonical, which files are supplemental, and which files are legacy or migration candidates.
- Provide the official verification commands when applicable:
  - `codex "Summarize the current instructions."`
  - `codex --cd <subdir> "Show which instruction files are active."`
- Confirm no contradictory instructions remain unresolved.
- Fail fast: stop at first critical contradiction and request decision.

## Project-tailored repo baseline

- Use `references/project-tailored-agents-baseline.md` when a user wants a reusable AGENTS operating baseline adapted to each repository.
- Treat the baseline as a section menu, not a verbatim template. Verify each section before insertion.
- Keep `Repository rules` grounded in the actual repo preflight, supported flag set, and repo-root workflow.
- Keep `Stack detection` grounded in observed root manifests and documented override behavior.
- For Python-capable repos, include a concise `## Python Environment and Dependency Management` baseline section by default when absent, then tailor only paths/overrides to repo evidence.
- For repos that require preflight, include both the mandatory workflow snippet and `## Preflight Enforcement (REQUIRED)` block by default when absent, using repo-verified commands and supported flags.
- For coding-standards requests, include a `## Quality Checks` baseline section by default when absent, using repo-native formatter/lint/typecheck/test commands and a pass-before-complete rule.
- Keep `Required tooling` and `Required repo paths` limited to what the repo actually needs.
- Keep architecture-diagram paths repo-specific: mention `.diagram/`, `.diagrams/`, or another diagram directory only when that exact path is documented or verified in the repo.
- Keep `.harness/memory/LEARNINGS.md` opt-in at the repo level unless the repo has explicitly adopted the harness-memory convention.
- Keep `Local Memory policy` opt-in unless the repo or user explicitly makes it required.
- Keep `Project Brain` guidance opt-in unless the repo or user explicitly makes it part of the operating surface; when present, keep the root section concise and route detail to `instructions/project-brain.md`.
- Treat `FORJAMIE.md` as legacy or supplemental unless repo evidence shows it is still a live fallback instruction file.
- Keep `Startup workflow` and `Supplemental context` concise and operator-focused.

## Anti-patterns

Use this section as an anti-pattern check when adapting or generating AGENTS.md files.

- Do not dump full policy documents into root AGENTS.
- Never duplicate the same instruction across many files without need.
- Do not keep vague guidance that cannot be executed (e.g. "write clean code", "be careful").
- **Never auto-generate AGENTS.md** from init scripts or templates. They prioritize comprehensiveness over restraint and create bloated files that actively hurt agent performance.
- **Never document file system paths as source of truth.** Paths change; agents read stale paths confidently. Describe capabilities and surface hints instead.
- Do not paste the same `Repository rules` or `Local Memory policy` block into every repo without checking scripts, manifests, paths, and actual repo standards first.
- Do not keep stale `FORJAMIE.md` references around once the file is gone or the repo has moved to `AGENTS.md`.
- Do not imply that arbitrary linked Markdown files are auto-discovered by Codex; only scoped AGENTS files and configured fallback filenames participate in instruction discovery.
- Avoid repetitive, generic, cookie-cutter templates that ignore repo context.
- Warn on conflicting package manager instructions and unresolved hierarchy conflicts.
- Do not add instructions that are redundant with the agent's base knowledge (e.g. "use descriptive variable names").

## Variation

- Adapt structure for small repos versus multi-package monorepos.
- Use different category splits based on repo domains (frontend, backend, ops, docs).
- Customize guidance depth to team maturity and operational risk.
- Keep scope tight on the first pass; expand beyond the core 2-3 surfaces only when the repo evidence or user request clearly requires it.

### Monorepo scope table

| Level | Content |
|---|---|
| **Root** | Monorepo purpose, how to navigate packages, shared tools (e.g. pnpm workspaces) |
| **Package** | Package purpose, specific tech stack, package-specific conventions |

Do not overload either level. The agent sees all merged AGENTS files. Keep each level scoped to what is only relevant at that depth.

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
- User says: "Update our shared AGENTS, CLAUDE, and GEMINI guidance so validation findings that represent durable repo work create or update a Linear issue in the right `[[ project ]]` instead of being left only in chat."
- User says: "Add a reusable `## Policy Calibration (Dynamic)` section to our AGENTS, CLAUDE, and GEMINI docs so safe repeated command prefixes can be whitelisted without changing the default approval policy."
- User says: "Refactor our shared instruction files with agents-md and make sure the approval/sandbox calibration rules are part of the default governance baseline."
- User says: "Check this project's AGENTS, CLAUDE, and GEMINI files and make sure the required instruction files exist, are current, and disclose the right canonical docs."
- User says: "Use agents-md to audit our instruction surface, repair anything stale, and tell me which files are canonical versus legacy."
- User says: "Update our AGENTS template so repo rules, stack detection, required tooling, required paths, Local Memory policy, and startup workflow are tailored per project instead of copied blindly."

## Resource map

- References: `references/contract.yaml`, `references/discovery-interview.md`, `references/evals.yaml`, `references/folded-legacy-modes-core60.md`, `references/official-codex-agents-guidance.md`, `references/project-tailored-agents-baseline.md`, `references/shared-guidance-propagation.md`, `references/task-profile.json`

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

- Rebase conflict resolution can drop `###` subheadings in shared-guidance sections; after resolving conflicts, verify headings still exist and TOC anchors remain valid.
