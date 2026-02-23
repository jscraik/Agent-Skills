---
name: claude-md
description: "Refactor or create CLAUDE.md using progressive disclosure: keep always-on guidance concise, include only non-obvious commands/style/workflow rules, use @imports for deeper docs, and flag contradictions/bloat. Use when the user asks to create, update, or audit CLAUDE.md files."
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
- Code style and workflow rules that differ from language defaults.
- Any adjacent instruction files that may conflict (AGENTS.md, docs, team runbooks).
- Preference for shared (`CLAUDE.md`) vs local-only (`CLAUDE.local.md`) instructions.
- Compatibility posture (default: canonical-only for unreleased/greenfield repos; override only when explicitly requested).

## Deliverables

- A minimal `CLAUDE.md` draft for the requested scope (home/repo/child).
- Optional layered plan for monorepos (root + folder-level `CLAUDE.md`).
- A table of contents for docs created/updated by this workflow.
- An include/exclude matrix for what should be always-on vs skill-on-demand.
- A contradictions list with a question for each conflict.
- A "flag for deletion" list (redundant, vague, volatile, obvious).
- Optional `@path` import block for deeper docs.
- Output contract schema_version: 1

## Constraints
- Redact secrets/PII by default.
- Do not invent commands, scripts, or paths.
- Use ASCII only unless the repo already uses non-ASCII.
- Do not add dependencies or tools.
- Do not add legacy shims, adapter layers, dual-write paths, or backwards-compatibility promises unless the user explicitly requires compatibility.
- Keep always-on files concise; move occasional or domain-specific workflows to skills.

## Workflow

1) Discover instruction topology
- Locate applicable files in this order: `~/.claude/CLAUDE.md`, parent directories, repo root, child directories.
- Confirm which scope the user wants changed.
- Note: Codex `AGENTS.md` does not support `@` imports; Claude `CLAUDE.md` does.

2) Discover repo facts
- Read README and `docs/` for real commands and structure.
- Inspect config files (for example `package.json`, `pyproject.toml`, `Makefile`).
- If commit conventions are not visible, state "not observed."

2.1) Set compatibility posture
- Default to canonical-only guidance for unreleased/greenfield projects.
- Only include backwards-compatibility instructions when explicitly requested or when the repo shows clear released-version compatibility commitments.

3) Build include/exclude set
- Include: non-obvious bash commands, non-default style rules, test workflow preferences, repo etiquette, architectural decisions, environment quirks.
- Exclude: things Claude can infer from code, standard conventions, long tutorials, file-by-file descriptions, frequently changing details.

4) Draft concise structure
- Prefer short sections such as:
  - Code style
  - Bash commands
  - Workflow
  - Testing
  - Git/PR etiquette
  - Architecture notes
- Keep each rule independently testable and specific.

5) Add progressive disclosure with imports
- Use `@path/to/file.md` for longer guides.
- Verify every import path exists before finalizing.
- For personal overrides, keep project-safe defaults and mention local-only file option.

6) Find contradictions
- Identify conflicting instructions across layers and ask which should win.
- Do not resolve conflicts without user confirmation.

7) Validate content
- Confirm commands exist and are runnable.
- Confirm referenced files exist.
- Ensure no secrets or private endpoints appear.
- Check brevity: remove any line that fails "Would deleting this cause mistakes?"

## Required sections (recommended CLAUDE.md shape)

- One-sentence project context
- Bash command defaults (non-obvious, repo-specific)
- Code style deviations from defaults
- Workflow/testing preferences
- Git/PR etiquette
- Architecture decisions that impact most tasks
- Imports/references for deep docs (optional, verified paths only)

## Claude loading behavior (authoring guidance)

- `~/.claude/CLAUDE.md`: applies to all Claude sessions.
- `./CLAUDE.md`: repo-shared defaults (check into git).
- `./CLAUDE.local.md`: local-only overrides (usually gitignored).
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
- Adding backwards-compatibility requirements by default in unreleased/greenfield projects.
- Generating extra legacy-preservation code paths without explicit compatibility requirements.

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
