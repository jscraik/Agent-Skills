---
name: agents-md
description: "Refactor or create AGENTS.md using progressive disclosure: keep root minimal, split detailed instructions into linked docs, and flag contradictions/redundancy. Use when the user asks to create, update, or refactor AGENTS.md."
---

# Agents Md

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Philosophy

Prefer concise, verifiable instructions over comprehensive prose. Every command and path must be real and sourced from the repo. Treat AGENTS.md as an operator checklist: short, direct, and actionable. Use progressive disclosure: keep root minimal, link out for details.

Guiding principles:
- Optimize for reader success in under 2 minutes.
- Favor deterministic steps over narrative.
- Keep scope tight; expand only when the repo requires it.

## When to use

- The user asks to create or update AGENTS.md.
- The user asks to refactor AGENTS.md for progressive disclosure or split instructions into multiple files.
- The repo needs a short contributor guide for agents or humans.
- The user requests “Repository Guidelines” content under 400 words.

## Response format (required)
- Always include all three sections in every response:
  - `## Outputs` describing delivered artifacts.
  - `## Inputs` listing missing info or noting "none".
  - `## When to use` explaining the correct trigger or noting "in scope".
- Use the exact heading text and casing shown above.
- For out-of-scope requests, start with `## When to use` and still include `## Outputs` and `## Inputs` below.
- Do not omit `## When to use` under any circumstance.
- For out-of-scope requests, do not write any text before `## When to use`.

### Response template (minimum)

```md
## Outputs
- ...

## Inputs
- ...

## When to use
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

## Inputs

- Target repo root path.
- Existing AGENTS.md content (if present).
- Verified commands and paths from the repo (README, docs, config files).
- Any adjacent instruction files that may conflict (global or per-directory).

## Outputs

- A minimal root `AGENTS.md` that links to separate instruction files.
- One file per instruction category (e.g., `docs/agents/typescript.md`, `docs/agents/testing.md`).
- A suggested `docs/` folder structure.
- A contradictions list with a question for each conflict.
- A “flag for deletion” list (redundant, vague, overly obvious).
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

## Required sections (root AGENTS.md)

- One-sentence project description
- Tooling essentials (package manager if not npm)
- Non-standard build/typecheck commands
- References or imports (global protocol pointers; no duplication)
- Global instructions discovery order (brief, link to full doc)
- Links to category files

## Variation

- Vary examples and commands to match the target repo’s stack (Python vs Node vs Swift).
- Use repo-specific paths and filenames; avoid repeating generic defaults across repos.

## Empowerment

- Offer two to three clear next-step options after drafting (accept, revise, or add missing info).
- Call out unknowns explicitly and ask for confirmation before finalizing.
- Encourage the user to prioritize sections when the scope is broad.
- Empower the user to choose between a minimal or detailed guideline set.
- Ask whether to proceed with inserts when the global protocol is detected but optional.
- Provide a one-sentence rationale for each recommended insert or deletion.

## Validation

- Fail fast: stop at the first failed validation gate, fix it, then re-run.
- Run `python scripts/quick_validate.py <skill>` if available.
- Run `python scripts/skill_gate.py <skill>` and fix any missing sections.
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

## Example prompts that should trigger this skill

- "Draft an AGENTS.md for this repo."
- "Create a Repository Guidelines AGENTS.md under 400 words."
- "Standardize our AGENTS.md using actual repo commands."
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
