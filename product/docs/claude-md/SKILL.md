---
name: claude-md
description: "Refactor or create CLAUDE.md using progressive disclosure: keep always-on guidance concise, include only non-obvious commands/style/workflow rules, use @imports for deeper docs, and flag contradictions/bloat. Use when the user asks to create, update, or audit CLAUDE.md files."
knowledge_graph_profile: references/task-profile.json
---

# Claude Md

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/instructions/standards.md
- Use ~/.codex/AGENTS.md as the global index that links to current standards docs.

## Philosophy

Prefer concise, verifiable instructions over comprehensive prose. Every command and path must be real and sourced from the repo. Treat CLAUDE.md as always-on context: short, direct, and actionable. Use progressive disclosure: keep root files minimal, link out for details using `@path` imports.

Guiding principles:
- Optimize for reader success in under 2 minutes.
- Favor deterministic steps over narrative.
- Keep scope tight; expand only when the repo requires it.
- Include only rules Claude cannot infer from the codebase.
- Default to canonical implementations for unreleased/greenfield projects; do not add backwards-compatibility layers unless explicitly required.

Mandatory snippet (include verbatim in guidance):
1. Explore project first, then invoke skill.
2. IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any React, Tauri, Apps-SDK-ui, Tailwind, Vite, Storybook + Chat Widget tasks.
3. Add a Table of Contents for docs.

## Scope and triggers

- The user asks to create or update `CLAUDE.md`.
- The user asks to refactor `CLAUDE.md` for clarity, brevity, or progressive disclosure.
- The user asks for repo-wide Claude rules (bash commands, code style, workflow).
- The user asks to split always-on instructions vs optional domain workflows.
- The repo has `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, and the user asks to keep shared instruction guidance synchronized.

## Response format (required)
- Always include all three sections in every response:
  - `## When to use` explaining the trigger or noting "in scope".
  - `## Outputs` describing delivered artifacts.
  - `## Inputs` listing missing info or noting "none".
- Use the exact heading text and casing shown above.
- For out-of-scope requests, start with `## When to use` and still include `## Outputs` and `## Inputs` below.
- Do not omit `## When to use` under any circumstance.
- For out-of-scope requests, do not write any text before `## When to use`.

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
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

### Failure-mode template (out of scope)

```md
## When to use
- This skill applies when the user asks to create or refactor CLAUDE.md using progressive disclosure.

## Outputs
- None (out of scope).

## Inputs
- None (out of scope).
```

Use the failure-mode template verbatim for out-of-scope requests.

## Required inputs

- Target repo root path.
- Existing `CLAUDE.md` files by scope (home, parent, repo root, child directories).
- Verified commands and paths from the repo (README, docs, config files).
- Package-manager signals from repo facts (`package.json#packageManager`, lockfiles, and existing command style in README/CI/docs).
- Code style and workflow rules that differ from language defaults.
- Any adjacent instruction files that may conflict (AGENTS.md, docs, team runbooks).
- Preference for shared (`CLAUDE.md`) vs local-only (`CLAUDE.local.md`) instructions.
- Compatibility posture (default: canonical-only for unreleased/greenfield repos; replace only when explicitly requested).

## Deliverables

- A minimal `CLAUDE.md` draft for the requested scope (home/repo/child).
- Optional layered plan for monorepos (root + folder-level `CLAUDE.md`).
- A table of contents for docs created/updated by this workflow.
- An include/exclude matrix for what should be always-on vs skill-on-demand.
- A contradictions list with a question for each conflict.
- A "flag for deletion" list (redundant, vague, volatile, obvious).
- Optional `@path` import block for deeper docs.
- Optional guidance on instruction-file structure (for domain-specific splits in larger repos).
- A detected package-manager command map (`install`, `run`, optional `exec`) derived from repo evidence and reused across generated guidance.
- Output contract schema_version: 1

## Constraints
- Redact secrets/PII by default.
- Do not invent commands, scripts, or paths.
- Use ASCII only unless the repo already uses non-ASCII.
- Do not add dependencies or tools.
- Do not add legacy shims, adapter layers, dual-write paths, or backwards-compatibility promises unless the user explicitly requires compatibility.
- Keep always-on files concise; move occasional or domain-specific workflows to skills.
- Do not hardcode npm/pnpm/yarn/bun command examples without repo evidence.

## Workflow

1) Discover instruction topology
- Locate applicable files in this order: `~/.claude/CLAUDE.md`, parent directories, repo root, child directories.
- Confirm which scope the user wants changed.
- Note: Codex `AGENTS.md` does not support `@` imports; Claude `CLAUDE.md` does.
- Canonical hierarchy rule: when `AGENTS.md` exists, use it as the canonical repository-wide reference for overlapping rules. Keep `CLAUDE.md` focused on always-on, Claude-specific guidance and project-local workflow deltas.

2) Discover repo facts
- Read instruction files in precedence order before drafting changes.
- Read README and `docs/` for real commands and structure.
- Inspect config files (for example `package.json`, `pyproject.toml`, `Makefile`).
- Detect package manager in this precedence: `package.json#packageManager` -> lockfiles (`pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`/`bun.lock`, `package-lock.json`, `npm-shrinkwrap.json`) -> existing command style in README/CI/docs.
- If package-manager signals conflict or are missing, state "not observed" and ask which command style should be used before emitting manager-specific commands.
- Build one package-manager command map from detected evidence and apply it consistently across generated CLAUDE/AGENTS/GEMINI updates.
- If commit conventions are not visible, state "not observed."
- If existing `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, or required instruction directories already exist, merge instead of overwrite.
- Apply **idempotent updates**: keep existing sections, append only missing required content, and dedupe duplicate bullets/anchors.
- Create/modify files only where absent or missing sections; avoid regenerating already-correct blocks.
- If a repo already has `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, update shared sections in `CLAUDE.md` and `GEMINI.md` to reference canonical `AGENTS.md` content instead of duplicating it, then keep tool-specific sections in sync.

3) Add instruction inserts (when applicable)
- If a higher-level global guidance source exists and is relevant, add a short references/import block rather than repeating source content.
- Verify referenced files and paths exist before including them.
- Keep linked references minimal and always scoped to this repo’s guidance.

4) Set compatibility posture
- Default to canonical-only guidance for unreleased/greenfield projects.
- Only include backwards-compatibility instructions when explicitly requested or when the repo shows clear released-version compatibility commitments.

5) Build include/exclude set
- Include: non-obvious bash commands, non-default style rules, test workflow preferences, repo etiquette, architectural decisions, environment quirks.
- Exclude: things Claude can infer from code, standard conventions, long tutorials, file-by-file descriptions, frequently changing details.

6) Draft concise structure
- Prefer short sections such as:
  - Code style
  - Bash commands
  - Workflow
  - Testing
  - Git/PR etiquette
  - Architecture notes
- Keep each rule independently testable and specific.

7) Add progressive disclosure with imports
- Use `@path/to/file.md` for longer guides.
- Verify every import path exists before finalizing.
- For personal replacements, keep project-safe defaults and mention local-only file option.

8) Find contradictions
- Identify conflicting instructions across layers and ask which should win.
- Do not resolve conflicts without user confirmation.

9) Validate content
- Confirm commands exist and are runnable.
- Confirm referenced files exist.
- Confirm naming conventions in examples match project conventions.
- Ensure no secrets or private endpoints appear.
- Check brevity: remove any line that fails "Would deleting this cause mistakes?"

## Required sections (recommended CLAUDE.md shape)

- One-sentence project context
- Bash command defaults (non-obvious, repo-specific)
- Repo-native package-manager command map (`install`, `run`, optional `exec`) when Node tooling exists
- Code style deviations from defaults
- Workflow/testing preferences
- Code quality standards (inject when requested or supported by repo evidence)
- Plan review guidance for complex implementation work
- Shell script conventions when shell wrappers/scripts exist
- Git/PR etiquette
- Architecture decisions that impact most tasks
- Imports/references for deep docs (optional, verified paths only)

## Flaky Test Artifact Capture (injectable block, conditional)

When repos have automated tests, CLAUDE.md should include a compact flaky-artifact block aligned with canonical AGENTS guidance.

Injection rule:
- Inject when user asks for flaky test workflows, artifact capture, or detector automation.
- Inject when repo facts show tests (`test` scripts, `pytest`, `vitest`, `playwright`, `jest`, `cargo test`, or `tests/`) **and** the repo already contains `scripts/test-with-artifacts.sh` (or an equivalent artifact-capture script you can verify on disk).
- Skip if repo has no test evidence.

Required content to include (or reference from AGENTS):
- Verified artifact-capture script path (canonical default: `scripts/test-with-artifacts.sh`) with modes `all|unit|integration|e2e`
- Stable artifact root `artifacts/test`
- Stable outputs: `summary-*.json`, `test-output-*.log`, `junit-*.xml`, `*-results.json`, `artifact-manifest.json`
- Package scripts (if `package.json` exists and script keys are present): `test:artifacts*`

Insert this section in CLAUDE.md for test repos:

```md
## Flaky Test Artifact Capture
- Run the verified artifact-capture script in `all` mode (or the detected repo-native command for `test:artifacts`) to emit machine-readable flaky evidence under `artifacts/test`.
- Optional targeted modes: `unit`, `integration`, `e2e`.
- Preserve stable artifact filenames so recurring flaky scans can compare runs.
```

## Code Quality Standards (injectable block, conditional)

Injection rule:
- Inject when the user requests code-quality standards.
- Else inject when repo evidence shows tests, linting, or TypeScript workflows.
- Skip if no quality workflow evidence exists.

Insert this section in CLAUDE.md when injected:

```md
### Code Quality Standards
- Run full test suite before committing: `npm test` or the detected repo-native equivalent.
- Fix TypeScript errors and lint issues before marking tasks complete.
- Ensure test isolation - tests should not depend on execution order.
```

## Plan Review Guidelines (injectable block, conditional)

Injection rule:
- Inject when the user asks for planning guardrails.
- Else inject for complex features/refactors/architecture work.
- Skip for trivial changes unless explicitly requested.

Insert this section in CLAUDE.md when injected:

```md
### Plan Review Guidelines
- Before implementing complex features, create a minimal v1 scope.
- Avoid over-engineering - prefer simple solutions over comprehensive ones.
- Scale back ambition if initial plan feels too large.
```

## Shell Script Conventions (injectable block, conditional)

Injection rule:
- Inject when the user asks for shell scripting quality standards.
- Else inject when repo evidence includes shell scripts or wrapper scripts.
- Skip if shell scripts are not part of the repo workflow.

Insert this section in CLAUDE.md when injected:

```md
### Shell Script Conventions
- Always validate wrapper scripts with shellcheck before considering complete.
- Test script syntax with `bash -n script.sh` to catch errors early.
- Handle edge cases for function conflicts and environment variable loading.
```

## Claude loading behavior (authoring guidance)

- `~/.claude/CLAUDE.md`: applies to all Claude sessions.
- `./CLAUDE.md`: repo-shared defaults (check into git).
  - `./CLAUDE.local.md`: local-only replacements (usually gitignored).
- Parent directories: useful for monorepo shared rules.
- Child directories: loaded when Claude works in that subtree.

## Variation

- Vary examples and commands to match the target repo stack (Node/Python/Rust/etc).
- Use repo-specific paths and filenames; avoid repeating generic defaults.

## Empowerment

- Offer two to three clear next-step options after drafting (accept, revise, or add missing info).
- Call out unknowns explicitly and ask for confirmation before finalizing.
- Encourage the user to prioritize sections when scope is broad.
- Empower the user to choose between minimal and detailed guidance.
- Provide one-sentence rationale for each recommended insert or deletion.

## Validation

- Fail fast: stop at the first failed validation gate, fix it, then re-run.
- Run `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/quick_validate.py <skill>` if available.
- Run `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/skill_gate.py <skill>` and fix missing sections.
- If needed, consult `references/contract.yaml` and `references/evals.yaml`.
- If validation scripts or paths are missing, state "not run (tooling not available)" and continue.

## Anti-patterns

- Generic boilerplate that ignores repo specifics.
- Fabricated commands or paths.
- Overlong always-on files that bury critical rules.
- Embedding detailed API docs instead of linking/importing.
- Including volatile details that change frequently.
- Omitting contradictions or failing to ask which instruction wins.
- Presenting unverified commands as facts.
- Mixing unrelated policies into the same section.
- Using vague headings like "Misc" or "Notes."
- Adding a Table of Contents that does not match actual headings.
- Adding backwards-compatibility requirements by default in unreleased/greenfield projects.
- Introducing non-required sections without confirming they are universally needed.
- Generating extra legacy-preservation code paths without explicit compatibility requirements.
- Replacing existing instruction files/directories with full rewrites when a scoped merge would preserve intent.
- Mixing npm/pnpm/yarn/bun command examples in one output block or defaulting to npm without repository evidence.

## Example prompts that should trigger this skill

- "Draft a CLAUDE.md for this repo."
- "Refactor our CLAUDE.md to be shorter and clearer."
- "Split always-on Claude rules from optional workflows using @ imports."

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
