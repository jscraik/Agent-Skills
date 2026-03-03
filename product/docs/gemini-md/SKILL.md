---
name: gemini-md
description: "Use when a user asks to create, update, or review Gemini CLI context (`GEMINI.md`) and memory workflows; emit merge-safe edits that preserve existing guidance while adding what is missing for in-scope tasks."
knowledge_graph_profile: references/task-profile.json
---

# Gemini Md

## Table of Contents
- [Remember](#remember)
- [Compliance](#compliance)
- [Philosophy](#philosophy)
- [Mandatory snippet](#mandatory-snippet-include-verbatim-in-guidance)
- [Scope and triggers](#scope-and-triggers)
- [Response format (required)](#response-format-required)
- [Cognitive support / plain-language](#cognitive-support--plain-language)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Constraints](#constraints)
- [Git Operations](#git-operations)
- [Workflow](#workflow)
- [Planning and Design](#planning-and-design)
- [Debugging](#debugging)
- [Required sections (root GEMINI.md)](#required-sections-root-geminimd)
- [Flaky Test Artifact Capture (injectable block, conditional)](#flaky-test-artifact-capture-injectable-block-conditional)
- [Code Quality](#code-quality)
- [Code Quality Standards (injectable block, conditional)](#code-quality-standards-injectable-block-conditional)
- [Plan Review Guidelines (injectable block, conditional)](#plan-review-guidelines-injectable-block-conditional)
- [Shell Script Conventions (injectable block, conditional)](#shell-script-conventions-injectable-block-conditional)
- [Memory operations](#memory-operations)
- [Hierarchy and folder-scoped context](#hierarchy-and-folder-scoped-context)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Example prompts](#example-prompts)
- [Procedure](#procedure)

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/instructions/standards.md
- Use ~/.codex/AGENTS.md as the global index that links to current standards docs.

## Philosophy

Prefer concise, verifiable instructions over comprehensive prose. Every command and path must be real and sourced from the repo. Treat `GEMINI.md` and saved memory as persistent project context: short, direct, and actionable.

Guiding principles:
- Optimize for reader success in under 2 minutes.
- Favor deterministic steps over narrative.
- Keep scope tight; expand only when the repo requires it.
- Default to canonical-only guidance for unreleased/greenfield projects; do not add compatibility layers unless explicitly requested.

Mandatory snippet (include verbatim in guidance):
1. Explore project first, then invoke skill.
2. IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any React, Tauri, Apps-SDK-ui, Tailwind, Vite, Storybook + Chat Widget tasks.
3. Add a Table of Contents for docs.

## Scope and triggers

- The user asks to create or update `GEMINI.md` context files.
- The user asks to merge/merge-safe update instruction files for Gemini CLI context.
- The user asks for a Gemini-specific context hierarchy or memory workflow.
- The repo has `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, and the user asks to keep shared guidance synchronized.

## Response format (required)
- Always include all three sections in every response:
  - `## When to use` explaining the trigger or noting "in scope".
  - `## Outputs` describing delivered artifacts.
  - `## Inputs` listing missing info or noting "none".
- Use the exact heading text and casing shown above.
- For out-of-scope requests, start with `## When to use` and still include `## Outputs` and `## Inputs` below.
- Do not omit `## When to use` under any circumstance.
- For out-of-scope requests, do not write any text before `## When to use`.

### Response template (minimum)

```md
## When to use
- in scope

## Outputs
- ...

## Inputs
- ...
```

### Failure-mode template (out of scope)

```md
## When to use
- This skill applies when the user asks to create or refactor Gemini context (`GEMINI.md`) using progressive disclosure and merge-safe updates.

## Outputs
- None (out of scope).

## Inputs
- None (out of scope).
```

Use the failure-mode template verbatim for out-of-scope requests.

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (one task at a time, explicit steps).
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: assumptions and the next step.
- Ask one question at a time; prefer multiple-choice when possible.

### Response template (minimum)

```md
## When to use
- in scope

## Outputs
- ...

## Inputs
- ...
```

## Required inputs

- Target repo root path.
- Existing `GEMINI.md` file(s) (global, project, and nested) if present.
- Verified commands and paths from the repo (README, docs, config files).
- Package-manager signals from repo facts (`package.json#packageManager`, lockfiles, and existing command style in README/CI/docs).
- Any adjacent instruction files that may conflict (AGENTS.md, CLAUDE.md, local scripts, docs).
- Project-specific memory conventions (facts the agent should remember).
- Compatibility posture (default: canonical-only for unreleased/greenfield repos; replace only when explicitly requested).

## Deliverables

- A minimal root `GEMINI.md` or updated existing file set using merge-safe, deduplicated inserts.
- Optional directory-specific `GEMINI.md` files for subtrees that require stricter rules.
- A small context memory strategy (`save_memory` usage patterns and when not to persist facts).
- Idempotent guidance for existing file updates:
  - preserve existing sections,
  - append only missing content,
  - dedupe duplicate bullets/anchors,
  - create files/dirs only when absent.
- A detected package-manager command map (`install`, `run`, optional `exec`) derived from repo evidence and reused across generated guidance.
- Optional conflict list with one question per contradiction.
- Output contract schema_version: 1

## Constraints

- Do not invent commands, scripts, or paths.
- Use ASCII unless the repo already uses non-ASCII.
- Do not add dependencies or system-level settings.
- Do not add backwards-compatibility requirements or dual-write behavior unless explicitly requested.
- Do not replace existing `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` content; update by merging.
- Redact sensitive/PII/credential-like content by default and avoid adding secrets, tokens, keys, or private identifiers.
- Do not hardcode npm/pnpm/yarn/bun command examples without repo evidence.

## Git Operations
- Before reporting merge success, always verify state with:
  - `git status`
  - `git log --oneline -5`
  - Never report merged completion without confirmation from these commands.
- After any `git commit`, `git push`, or merge action, run:
  - `git log --oneline -3`
  - `git status`
  - and confirm repository state matches requested outcome.

## Workflow

1) Discover existing context topology
- Collect existing root/global and nested `GEMINI.md` files if present.
- Confirm which scope the user wants changed (repo-level only or nested replacements too).

2) Discover repository facts
- Read instruction files in precedence order: `~/.codex/AGENTS.md`, repo `AGENTS.md`, `~/.claude/CLAUDE.md`, repo `CLAUDE.md` (as constraints), then docs/code.
- Read README and `docs/` for real commands and structure.
- Detect package manager in this precedence: `package.json#packageManager` -> lockfiles (`pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`/`bun.lock`, `package-lock.json`, `npm-shrinkwrap.json`) -> existing command style in README/CI/docs.
- If package-manager signals conflict or are missing, state "not observed" and ask which command style should be used before emitting manager-specific commands.
- Build one package-manager command map from detected evidence and apply it consistently across generated GEMINI/AGENTS/CLAUDE updates.
- If commit or run conventions are absent, state "not observed."
- Canonical hierarchy rule: when `AGENTS.md` exists, treat it as canonical for repository-wide instruction overlap; keep `GEMINI.md` for Gemini-specific memory/loading conventions and only cite shared repo rules from AGENTS.

3) Merge instead of overwrite
- If `GEMINI.md` already exists, apply idempotent edits:
  - keep existing content,
  - insert only missing sections,
  - dedupe duplicated lines/anchors,
  - avoid recreating markers or metadata blocks.
- Never overwrite existing instruction files unless explicitly asked.

4) Define context essentials (root `GEMINI.md`)
- One-sentence project context.
- Repo-specific defaults that the agent cannot infer:
  - style/testing/build constraints,
  - non-obvious commands,
  - architecture preferences.

5) Add memory management operating rules
- Include when to persist facts and when to avoid.
- Include `/memory show` and `/memory refresh` usage guidance so users can inspect/load active context during sessions.

6) Build hierarchy for precision
- Prefer root file for universal rules.
- Use subdirectory `GEMINI.md` only for genuinely scoped instructions.
- Mention that if both project and deeper files exist, deeper files replace parent values as per Gemini CLI hierarchy.

7) Validate context
- Verify referenced files/commands exist before finalizing.
- Confirm that no secrets or private endpoints were added.
- Redact secrets/PII by default and avoid including tokens or credentials.
- If all three files exist and overlap is requested, verify `CLAUDE.md` and `AGENTS.md` references still align to shared canonical guidance and are not duplicated.

## Planning and Design
### Plan Decomposition
- For plans derived from technical review feedback (including DHH-style reviews), start with the minimal v1 version first, then add complexity.
- Ask: "What's the smallest version that delivers value?"

## Debugging
- For auth/key-related tasks (including Kimi, 1Password, etc.), start by checking environment variables:
  - `env | grep -i <key_name>`
  - `echo $<VAR>`
  - before assuming external key configuration is correct.

## Required sections (root GEMINI.md)

- Project summary (one sentence).
- Package/build/test defaults.
- Repo-native package-manager command map (`install`, `run`, optional `exec`) when Node tooling exists.
- Code quality standards (inject when requested or supported by repo evidence).
- Planning guidance (inject plan-review rules for complex implementation work).
- Shell script conventions when shell wrappers/scripts are present.
- Non-obvious command patterns.
- Explicit boundaries / forbidden patterns.
- Memory persistence guidance (`save_memory` prompts and retention logic).
- Project-specific facts that benefit from persistent memory.

## Flaky Test Artifact Capture (injectable block, conditional)

When repos have automated tests, include a flaky-artifact block in GEMINI.md (or reference canonical AGENTS section).

Injection rule:
- Inject if user asks for flaky detection/artifacts or automated test-history workflows.
- Inject if repo has test evidence (`test` scripts, `pytest`, `vitest`, `playwright`, `jest`, `cargo test`, `tests/`) **and** a verified artifact-capture script already exists (`scripts/test-with-artifacts.sh` or equivalent).
- Skip if no test evidence.

Required content:
- Verified script path (canonical default: `scripts/test-with-artifacts.sh`)
- Modes: `all`, `unit`, `integration`, `e2e`
- Artifact root: `artifacts/test`
- Stable outputs: `summary-*.json`, `test-output-*.log`, `junit-*.xml` (when supported), `*-results.json` (when supported), `artifact-manifest.json`
- If `package.json` exists and script keys are present, include `test:artifacts*` scripts.

Insert this section in GEMINI.md for test repos:

```md
## Flaky Test Artifact Capture
- Run the verified artifact-capture script in `all` mode (or the detected repo-native command for `test:artifacts`) to emit machine-readable flaky evidence under `artifacts/test`.
- Optional targeted modes: `unit`, `integration`, `e2e`.
- Keep artifact filenames stable (no timestamps in filenames) for cross-run comparison.
```

## Code Quality
### Bug Hunt Protocol
- When user says "find bugs" or "bug hunt", systematically analyze:
  1. calculation logic for edge cases,
  2. null/undefined handling,
  3. async/await patterns,
  4. resource cleanup.
- Report all findings with severity and file locations.

## Code Quality Standards (injectable block, conditional)

Injection rule:
- Inject when the user requests code-quality standards.
- Else inject when repo evidence shows tests, linting, or TypeScript workflows.
- Skip if no quality workflow evidence exists.

Insert this section in GEMINI.md when injected:

```md
## Code Quality Standards
- Run full test suite before committing: `npm test` or the detected repo-native equivalent.
- Fix TypeScript errors and lint issues before marking tasks complete.
- Ensure test isolation - tests should not depend on execution order.
```

## Plan Review Guidelines (injectable block, conditional)

Injection rule:
- Inject when the user asks for planning guardrails.
- Else inject for complex feature/refactor/architecture tasks.
- Skip for trivial edits unless explicitly requested.

Insert this section in GEMINI.md when injected:

```md
## Planning
### Plan Review Guidelines
- Before implementing complex features, create a minimal v1 scope.
- Avoid over-engineering - prefer simple solutions over comprehensive ones.
- Scale back ambition if initial plan feels too large.
```

## Shell Script Conventions (injectable block, conditional)

Injection rule:
- Inject when the user asks for shell script quality guidance.
- Else inject when repo evidence includes shell scripts or wrapper scripts.
- Skip if shell scripts are not part of the repo workflow.

Insert this section in GEMINI.md when injected:

```md
## Shell Script Conventions
- Always validate wrapper scripts with shellcheck before considering complete.
- Test script syntax with `bash -n script.sh` to catch errors early.
- Handle edge cases for function conflicts and environment variable loading.
```

## Memory operations

- To save a one-off fact, guide with natural phrasing (e.g. `Remember that...`, `Save the fact that...`) in conversation.
- Document that saved facts appear in session context automatically.
- Include `/memory show` command for debugging active context.
- Include `/memory refresh` for reloading updated context files in long-running sessions.
- Verify both commands are available in the current Gemini CLI version or note as missing/not observed.

## Hierarchy and folder-scoped context

Use this precedence when files exist:
1. `~/.gemini/GEMINI.md` (global)
2. `./GEMINI.md` (project root)
3. `./subdir/GEMINI.md` (folder-specific replacements)

When adding nested files, keep changes focused and non-overlapping with parent files.

## Reference map (skill internal)

- `references/contract.yaml`: Output contract and behavior definition for this skill.
- `references/evals.yaml`: Evaluation prompts for trigger, scope, and safety checks.

## Validation

- Fail fast: stop at the first validation gate, fix, then re-run.
- If validation tooling exists locally, run:
  - `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/quick_validate.py <skill>`
  - `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/skill_gate.py <skill>`
- If files are missing, state "not run (tooling not available)" and continue.

## Anti-patterns

- Full-file rewrites that erase existing project context.
- Dumping entire team manuals into `GEMINI.md` (keep concise, actionable guidance only).
- Adding volatile facts that age quickly without a refresh strategy.
- Omitting global/project/nested precedence when scoping instructions.
- Treating `GEMINI.md` as a place for secrets.
- Using memory facts for data that should be in code, config, or docs.
- Assuming hidden command support without verification from current Gemini CLI behavior.
- Mixing npm/pnpm/yarn/bun command examples in one output block or defaulting to npm without repository evidence.

## Example prompts

- "Draft a project `GEMINI.md` with style and testing rules."
- "Refactor our `GEMINI.md` so it works with existing `AGENTS.md` and `CLAUDE.md`."
- "Add a nested `GEMINI.md` for backend folder with stricter rules."

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
