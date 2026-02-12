---
name: agents-md
description: 'Refactor or create AGENTS.md using progressive disclosure: keep root
  minimal, split detailed instructions into linked docs, and flag contradictions/redundancy.
  Use when the user asks to create, update, or refactor AGENTS.md.'
metadata:
  short-description: 'Refactor or create AGENTS.md using progressive disclosure: keep
    root minimal,...'
---

# Agents Md

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.


## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Philosophy

Prefer concise, verifiable instructions over comprehensive prose. Every command and path must be real and sourced from the repo. Treat AGENTS.md as an operator checklist: short, direct, and actionable. Use progressive disclosure: keep root minimal, link out for details.

Guiding principles:
- Optimize for reader success in under 2 minutes.
- Favor deterministic steps over narrative.
- Keep scope tight; expand only when the repo requires it.

Mandatory snippet (include verbatim in guidance):
1. Explore project first, then invoke skill.
2. IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any React, Tauri, Apps-SDK-ui, Tailwind, Vite, Storybook + Chat Widget tasks.
3. Add a Table of Contents for docs.

## Scope and triggers

- The user asks to create or update AGENTS.md.
- The user asks to refactor AGENTS.md for progressive disclosure or split instructions into multiple files.
- The repo needs a short contributor guide for agents or humans.
- The user requests “Repository Guidelines” content under 400 words.

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
- This skill applies when the user asks to create or refactor AGENTS.md using progressive disclosure.

## Outputs
- None (out of scope).

## Inputs
- None (out of scope).
```

Use the failure-mode template verbatim for out-of-scope requests.

## Required inputs

- Target repo root path.
- Existing AGENTS.md content (if present).
- Verified commands and paths from the repo (README, docs, config files).
- Any adjacent instruction files that may conflict (global or per-directory).
- Whether Jamie's agent-first scaffold standard is requested (`/Users/jamiecraik/.codex/instructions/agent-first-scaffold-spec.md`).

## Deliverables

- A minimal root `AGENTS.md` that links to separate instruction files.
- One file per instruction category (e.g., `docs/agents/typescript.md`, `docs/agents/testing.md`).
- A suggested `docs/` folder structure.
- A table of contents for docs that are created or updated.
- A contradictions list with a question for each conflict.
- A “flag for deletion” list (redundant, vague, overly obvious).
- When requested: idempotent scaffold blocks for `AGENTS.md`, `.agent/PLANS.md`, and `README.md`.
- Output contract schema_version: 1

## Constraints
- Redact secrets/PII by default.

- Do not invent commands, scripts, or paths.
- Redact secrets and sensitive data by default.
- Use ASCII only unless the repo already uses non-ASCII.
- Do not add dependencies or tools.

## Workflow

1) Discover repo facts
- Read README and `docs/` for real commands and structure.
- Inspect config files (for example `pyproject.toml`, package scripts).
- If commit conventions are not visible, state “not observed.”
- Read global instructions from `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md` if present.
- Also check `~/.codex/instructions/` for applicable global standards and guidance.
- Then read project instructions from repo root down to the working directory and treat them as canonical.
- Note: Codex `AGENTS.md` does not support `@` imports; Claude `CLAUDE.md` and `~/.claude/rules/*.md` do.

2) Find contradictions
- Identify conflicting instructions and ask which one should win.
- Do not resolve conflicts without user confirmation.

3) Identify the essentials (root AGENTS.md)
- One-sentence project description.
- Package manager (if not npm).
- Non-standard build/typecheck commands.
- Anything truly relevant to every single task.

4) Add inserts (global references)
- If a canonical global protocol exists (for example `~/.codex/instructions/rvcp-common.md`), add a short "References" or "Imports" section at the top of the root `AGENTS.md` that points to it.
- Never duplicate the full protocol content in repo files; link only.
- If `CODEX_HOME` is set, prefer `$CODEX_HOME/...` for global references; otherwise use `~/.codex/...`.
- Only insert references that exist on disk; if not found, state "not observed" and do not invent paths.
- If the repo uses a different global protocol, add the same style of reference block.
- When scaffold mode is requested, include references to the scaffold spec and governance docs listed above.
  - Example (root `AGENTS.md` block):
    ```md
    ## References (informational)
    - Global protocol: ~/.codex/instructions/rvcp-common.md
    - Global override: ~/.codex/AGENTS.override.md
    ```

5) Group the rest
- Organize remaining instructions into logical categories (TypeScript, testing, deployment, accessibility, etc.).
- Keep each category file focused and scoped.

6) Create the file structure
- Output a minimal root `AGENTS.md` with Markdown links to category files.
- Output each category file with its relevant instructions.
- Provide a suggested `docs/` folder structure.

7) Flag for deletion
- Identify redundant, vague, or overly obvious instructions.

8) Validate content
- Confirm commands exist and are runnable.
- Confirm naming conventions match the codebase.
- Ensure no secrets or private endpoints appear.
- For scaffold mode: verify marker blocks are present and not duplicated.
- For scaffold mode: run `python3 /Users/jamiecraik/.codex/scripts/plan-graph-lint.py <repo>/.agent/PLANS.md`.
- For scaffold mode: run link-integrity checks with `rg -n` for required global references.

## Required sections (root AGENTS.md)

- One-sentence project description
- Tooling essentials (package manager if not npm)
- Non-standard build/typecheck commands
- References or imports (global protocol pointers; no duplication)
- Global instructions discovery order (brief, link to full doc)
- Links to category files

## Agent-first scaffold integration (Jamie standard)

Apply this when the user asks for agent-first rollout/scaffold across repos (especially under `/Users/jamiecraik/dev`).

Required global references (verify they exist before insertion):
- `/Users/jamiecraik/.codex/instructions/openai-agent-workflow-playbook.md`
- `/Users/jamiecraik/.codex/instructions/README.checklist.md`
- `/Users/jamiecraik/.codex/instructions/validator-contracts.md`
- `/Users/jamiecraik/.codex/instructions/strict-toggle-governance.md`
- `/Users/jamiecraik/.codex/instructions/agent-first-scaffold-spec.md`

Use idempotent marker blocks:
- `AGENTS.md`: `<!-- AGENT-FIRST-SCAFFOLD:START --> ... <!-- AGENT-FIRST-SCAFFOLD:END -->`
- `.agent/PLANS.md`: `<!-- AGENT-FIRST-PLANS:START --> ... <!-- AGENT-FIRST-PLANS:END -->`
- `README.md`: `<!-- AGENT-FIRST-WORKFLOW:START --> ... <!-- AGENT-FIRST-WORKFLOW:END -->`

`.agent/PLANS.md` contract requirements:
- `tasks[]`, each task has `id`, `title`, `depends_on`
- `id` format `^T[1-9][0-9]*$`
- IDs unique within plan
- `depends_on` references in-plan IDs only
- no self-dependency; DAG required; single connected component
- validation command: `python3 /Users/jamiecraik/.codex/scripts/plan-graph-lint.py <plan-file>`

Canonical verification command:
- `/Users/jamiecraik/.codex/scripts/verify-work.sh`

Rollout policy:
- Link to 3-gate warn->block model in `/Users/jamiecraik/.codex/instructions/agent-first-scaffold-spec.md`.

## Variation

- Vary examples and commands to match the target repo’s stack (Python vs Node).
- Use repo-specific paths and filenames; avoid repeating generic defaults across repos.

## Empowerment

- Offer two to three clear next-step options after drafting (accept, revise, or add missing info).
- Call out unknowns explicitly and ask for confirmation before finalizing.
- Encourage the user to prioritize sections when the scope is broad.
- Empower the user to choose between a minimal or detailed guideline set.
- Empower the user with explicit **choice and control** over scope, depth, and inserts before expanding.
- Explicitly empower the user to defer optional inserts until core guidance is approved.
- Ask whether to proceed with inserts when the global protocol is detected but optional.
- Provide a one-sentence rationale for each recommended insert or deletion.

## Validation

- Fail fast: stop at the first failed validation gate, fix it, then re-run.
- Run `~/.venvs/pyyaml/bin/python scripts/quick_validate.py <skill>` if available.
- Run `~/.venvs/pyyaml/bin/python scripts/skill_gate.py <skill>` and fix any missing sections.
- If needed, consult `references/contract.yaml` and `references/evals.yaml`.
- If validation scripts or paths are missing, state "not run (tooling not available)" and continue.

## Anti-patterns

- Generic boilerplate that ignores repo specifics.
- Fabricated commands or paths.
- Omitting contradictions or failing to ask which instruction wins.
- Burying risks or assumptions in long prose.
- Using vague headings like “Misc” or “Notes.”
- Presenting unverified commands as facts.
- Mixing unrelated policies into the same section.
- Adding global protocol content directly into repo `AGENTS.md` instead of linking.
- Stating paths that do not exist under the current `$CODEX_HOME` or repo.
- Treating imports as supported in Codex `AGENTS.md` (they are not).
- Hiding conflicts in linked docs instead of calling them out in the root file.
- Expanding root `AGENTS.md` beyond 400 words without explicit user approval.
- Skipping project exploration before applying or invoking the skill.
- Adding a Table of Contents that does not match actual document headings.
- Never proceed with contradictory instructions without asking which one wins.
- Do not introduce new sections without confirming they are required for every task.
- Avoid “one‑size‑fits‑all” templates that erase repo‑specific commands.
- In scaffold mode, writing non-idempotent edits without marker blocks.
- Omitting `/Users/jamiecraik/.codex/instructions/agent-first-scaffold-spec.md` when Jamie standard is requested.

## Example prompts that should trigger this skill

- "Draft an AGENTS.md for this repo."
- "Create a Repository Guidelines AGENTS.md under 400 words."
- "Standardize our AGENTS.md using actual repo commands."
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

