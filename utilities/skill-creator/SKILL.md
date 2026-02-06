---
name: skill-creator
description: Create, revise, and quality-gate Codex skills (SKILL.md + resources +
  evals + packaging). Use when asked to build or improve a skill.
metadata:
  short-description: Create, revise, and quality-gate Codex skills (SKILL.md + resources
    + evals +...
---

# Skill Creator

This skill helps you design, author, validate, and package high-quality skills.

**Version**: 1.4.0  
**Last updated**: 2026-01-22

## Scope and triggers

- Create a new skill (instruction-only or router-style skill folder).
- Revise an existing skill for better triggering, portability, or reliability.
- Audit/upgrade a skill to meet “gold standard” structure, progressive disclosure, and validation.
- Package a skill into a distributable `.skill` archive.

## Required inputs

- Desired skill goal (what users want to accomplish).
- 3–10 example user prompts (happy-path + edge-cases + out-of-scope prompts).
- Target environment(s): Codex, Claude Code, or portable subset.
- Any required assets, schemas, APIs, CLIs, or “house style” constraints.

If any of the above are missing, ask only the minimum questions required to proceed safely.

## Deliverables

Depending on the request, produce one or more of:

- A skill folder containing:
  - `SKILL.md` (required)
  - `agents/openai.yaml` (recommended when targeting Codex/OpenAI/Agents) - appearance + MCP dependencies configuration
  - `scripts/` (optional)
  - `references/` (optional)
  - `assets/` (optional)
- `references/contract.yaml` (output contract) and `references/evals.yaml` (eval cases) when the skill is non-trivial. Include `schema_version` in the contract.
- `references/plan.md` (plan artifact) for non-trivial skill builds; store the `$create-plan` output here when available.
- A validation report (what passed/failed and what to fix).
- A packaged `.skill` file created via `scripts/package_skill.py`.

## Response format (required)

Always start responses with these headings (no text before them):

## Scope and triggers
- 1–3 bullets on when this skill applies (confirm scope).

## Required inputs
- List required inputs and ask targeted questions if needed.

## Deliverables
- List deliverables you will produce.

## Failure mode (required)

If the request is out of scope:
- Use the headings above.
- Under **Inputs**, explain what’s missing or why it’s out of scope.
- Under **Outputs**, propose the closest appropriate next step or skill.

## Constraints

- Redact secrets/credentials/PII by default. Never print raw tokens or env var values.
- Do not invent file contents, commands, or external facts. If you must rely on time-sensitive details, ask to verify or propose a verification step.
- Keep YAML frontmatter valid:
  - `name` and `description` must be single-line YAML scalars.
  - Quote values if they contain `:` or could be parsed as YAML syntax.
- Prefer progressive disclosure:
  - Keep `SKILL.md` short (aim ~200–300 lines; hard cap ~400).
  - Push depth into `references/` and executable helpers into `scripts/`.
- Prefer instruction-only skills by default; add scripts only when determinism/repeatability matters.

## What to not include

- No extra YAML frontmatter fields beyond `name` and `description`.
- Do not add “When to use / Inputs / Outputs / Failure mode” headings inside `SKILL.md`.
- Do not embed long API docs, policies, or large examples; move them to `references/`.
- Do not include eval outputs, logs, or run artifacts in `SKILL.md`.
- Do not put step-by-step workflows in the `description`; keep workflows in the body/references.

## Script-backed security rules (required)

When a skill includes executable code (`scripts/` or containers), apply these rules:

- No network assumptions: default to offline behavior. If network access is required, make it explicit and gate it behind an `--allow-network` flag.
- Never echo secrets or environment variables. Do not print `os.environ`, `process.env`, or token values.
- Require explicit confirmation for destructive actions (delete/overwrite/remote writes). Prefer `--dry-run` by default and require `--confirm` / `--force` to execute.

See `references/security-hardening.md` for patterns and a Codex `.rules` template.

## Principles

- **Concise is key**: keep `SKILL.md` short (aim ~200–300 lines; hard cap ~400) and push depth into `references/`/`scripts/`.
- **Trigger-first design**: discovery depends on `name` + `description`. Put trigger keywords and “use when …” contexts in the description.
- **Progressive disclosure**: keep the core workflow in `SKILL.md`; link out to `references/` for deep docs and `scripts/` for automation.
- **Eval-driven iteration (RED → GREEN → REFACTOR)**:
  1. Write eval cases that fail without the skill (or against the old skill).
  2. Implement the smallest change that passes.
  3. Add pressure tests to prevent backsliding and rationalization.
- **Least privilege**: scripts should be minimal, explicit, and safe; avoid network assumptions unless explicitly enabled.
- **Set degrees of freedom** (choose one):
  - **Low**: strict steps, fixed templates, minimal variation.
  - **Medium**: clear steps with bounded options or branches.
  - **High**: high-level guidance, creative latitude.

### Progressive disclosure patterns (quick list)

- Keep the core workflow in `SKILL.md`; move depth to `references/`.
- Put deterministic or repetitive steps into `scripts/` with safe flags.
- Keep examples short in `SKILL.md`; link to full examples in `references/`.
- Use `assets/` for templates, boilerplate, or fixtures.

## Reference Map

Use these files when needed:

- `references/about-skills.md`: background on skills, intent, and structure.
- `references/portable-skills.md`: strict subset for cross-platform portability.
- `references/skill-structure.md`: router vs single-file skill patterns.
- `references/progressive-disclosure-patterns.md`: how to split SKILL.md into references/scripts.
- `references/quality-tools.md`: how to run validators/evals and interpret output.
- `references/iteration-and-testing.md`: eval-driven iteration patterns, pressure tests, and rationalization hardening.
- `references/planning.md`: how to use `$create-plan` and store plan artifacts.
- `references/security-hardening.md`: script-backed safety patterns (no-network defaults, redaction, destructive action confirmations, Codex rules).
- `references/destructive-commands.rules`: example Codex rules file to prompt/block risky commands.
- `references/examples.md`: calibrated examples for phrasing and structure.
- `references/anti-patterns.md`: common failure modes + remediation patterns.

## Anatomy of a Skill (quick schematic)

- **Frontmatter**: `name` + `description` with trigger keywords.
- **Core workflow**: principles + minimal reliable procedure.
- **References**: deep docs, schemas, evals, contracts.
- **Scripts/assets**: optional helpers/templates for determinism.
- **Agents metadata**: `agents/openai.yaml` when targeting Codex/OpenAI/Agents.

## Skill Creation Process

Follow this workflow, skipping steps only with a clear reason.

### 0) Confirm scope and target

- Identify where the skill will live:
  - Repo scope: `.agents/skills/<skill-name>/`
  - User scope: `~/.agents/skills/<skill-name>/`
- Admin scope: `/etc/codex/skills/<skill-name>/` (system-wide)
  - (Claude Code uses `~/.claude/skills/`)

Reload note:
- Restart Codex/Agents after adding/updating skills so the index refreshes.
- You can enable/disable skills in `~/.codex/config.toml` under `[skills]` (for example, a `disabled = [...]` list).
- Decide target: `portable` (strict subset), `codex`, or `claude`.

### 0.5) Planning phase (Codex-native `$create-plan`)

If the task is non-trivial (multiple files, scripts, contracts/evals, or safety gates):

1. If the `$create-plan` skill is installed, invoke it first.
2. Store the resulting plan artifact in the target skill folder as:
   - `references/plan.md` (preferred)
3. Then execute the plan (RED → GREEN → REFACTOR).

If `$create-plan` is not installed, write a compact plan yourself and store it in the same place.

### 1) Lock down triggers (with examples)

- Collect 3–10 prompts:
  - 2–5 happy-path prompts
  - 1–3 edge-cases
  - 1–3 “should NOT trigger” prompts
- Use these prompts to write `references/evals.yaml` early (at least 3 cases).

### 2) Pick the skill structure

- **Single-file**: one intent, one workflow, < ~200 lines.
- **Router style**: multiple intents/workflows, or heavy domain knowledge.

Router layout:
```
skill-name/
  SKILL.md
  workflows/
  references/
  scripts/
  assets/
```

### 3) Scaffold the folder

Use the initializer:

```bash
python scripts/init_skill.py <skill-name> --target codex --run-type instruction --path <output-dir>
```

**Resource auto-creation:** The initializer intelligently creates directories based on skill needs:
- `scripts/` — always created for `--run-type python` or `--run-type container`
- `references/` — always created for complex skills (external APIs, multiple workflows)
- `assets/` — created when templates/static files would help
- `agents/openai.yaml` — always created for OpenAI/Codex compatibility

To override auto-creation, use `--resources scripts,references,assets` or `--minimal` for just `SKILL.md`.

Tip: for script-backed skills, use `--run-type python` (creates `scripts/run.py`) or `--run-type container` (adds `Dockerfile` + `scripts/run.py`).
Security note: for any executable code, follow `references/security-hardening.md` (offline defaults, no secret/env echo, `--dry-run` + `--confirm` for destructive actions).

Then delete any unused resource folders and example files.

### 4) Author SKILL.md (core)

**Frontmatter**
- `name`: kebab-case, matches folder name.
- `description`: single-line; includes WHAT + WHEN (trigger contexts + keywords).
- Avoid workflow summaries in `description` (no steps / procedures). Keep workflows in the body / references.
- Keep frontmatter minimal by default.

**Body**
- Include a short Principles section before detailed steps.
- Write the minimal reliable Procedure.
- Put deep docs in `references/` and reference them explicitly (“Read X when you need Y”).

### 5) Add reusable resources (as needed)

- `scripts/`: executable helpers for deterministic operations and token efficiency.
- `references/`: schemas, API docs, policies, style guides, large examples.
- `assets/`: templates, boilerplate folders, brand files, fixtures.

Prefer relative paths (`scripts/foo.py`, `references/bar.md`) so the skill works in different locations.

### 6) Validate and iterate (fail-fast)

Run the lightweight checks first:

```bash
~/.venvs/pyyaml/bin/python scripts/quick_validate.py <path/to/skill-folder>
~/.venvs/pyyaml/bin/python scripts/skill_gate.py <path/to/skill-folder>
```

If available, run deeper validation:

```bash
skills-ref validate <path/to/skill-folder>
```

Then run evals:

```bash
~/.venvs/pyyaml/bin/python scripts/run_skill_evals.py <path/to/skill-folder>
```

Codex runner (optional):

```bash
~/.venvs/pyyaml/bin/python scripts/run_skill_evals.py <path/to/skill-folder> --runner codex
```

Fix the first failure, re-run, then proceed.

### 7) Package (optional)

```bash
python scripts/package_skill.py <path/to/skill-folder> dist/
```

Packaging should exclude dev artifacts via `.skillignore`.

## Validation

- Fail fast: stop at the first failed validation gate, fix it, and re-run before proceeding.
For any non-trivial skill, ensure:

- Frontmatter passes `quick_validate.py`.
- Prompt-injection warnings from `skill_gate.py` are reviewed and resolved (or explicitly justified).
- Prompt-injection patterns are configurable via `references/prompt-injection-patterns.json` (supports `severity`).
- Local allow/block config (not in repo) can override matches: `~/.codex/skill-security/allow-block.json` or `CODEX_SKILL_SECURITY_CONFIG`.
- `SKILL.md` stays under the line budget and references external files instead of bloating.
- At least 3 eval cases exist (happy / edge / failure).
- Scripts run successfully in the intended environment.
- Trigger prompts reliably select the skill over nearby alternatives.

## Trigger Testing (Quick Check)

Before shipping, confirm the description selects the skill:

- Write 3–5 prompts and sanity check that they match the description keywords.
- Add 1–2 negative prompts (should not select this skill).


## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Extended guidance
See `references/extended.md` for additional examples, workflows, and appendices.
