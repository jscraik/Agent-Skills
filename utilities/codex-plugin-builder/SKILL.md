---
name: codex-plugin-builder
description: "Create, convert, and validate Codex plugin packages that include focused skills, prompts, hooks, agents, and MCP metadata. Use this skill when the user asks to scaffold plugin bundles, safely convert external plugin sources, or quality-gate plugin-owned skills; do not use it for unrelated app feature work."
---

# Codex Plugin Builder
Build safe, focused plugin packages for Codex workflows.

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Outputs](#outputs)
- [Core philosophy](#core-philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [Plugin contract](#plugin-contract)
- [Hook contract](#hook-contract)
- [Constraints and safety](#constraints-and-safety)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Failure mode](#failure-mode)

## Scope and triggers
Use this skill when the request is to:
- scaffold a new Codex plugin package;
- inspect an external plugin source before conversion;
- convert a Claude-oriented plugin shape into a Codex-compatible package;
- add plugin-owned surfaces such as `skills/`, `hooks/`, `prompts` (optional), `agents` (optional), `.app.json`, or `.mcp.json`;
- include package docs `README.md` and `LICENSE` in every plugin package;
- validate plugin-owned skills with the `skill-builder` validator suite.

Do not use this skill for:
- standalone app feature implementation;
- unrelated bugfix work;
- generic MCP server implementation that is not plugin packaging.

## Required inputs
- plugin name and destination path;
- default destination policy: if destination is not explicitly requested, write plugin packages to repo-root `plugins/<plugin-name>/`;
- requested surfaces for first pass:
  - required:
    - `.codex-plugin/plugin.json`,
    - `README.md`,
    - `LICENSE`,
  - `skills`,
  - `prompts`,
  - `hooks`,
  - `agents`,
  - `.app.json`,
  - `.mcp.json`;
- source of truth for conversion when applicable:
  - GitHub URL,
  - local path,
  - pinned ref or commit;
- validation depth:
  - `none`,
  - `smoke`,
  - `full`.

If key inputs are missing, ask only the smallest set of clarifying questions needed to scaffold safely.

## Outputs
Produce only what the request needs:
- plugin package folder with `SKILL.md` or plugin-owned assets;
- `references/contract.yaml` and `references/evals.yaml` for non-trivial behavior;
- `references/plugin-contract.md` whenever packaging rules or manifest fields are in scope;
- `references/hooks-contract.md` whenever `hooks/` is requested or converted;
- fixture examples under `fixtures/` for conversion templates and regression checks;
- optional helper docs in `references/` when conversion assumptions are non-obvious;
- validator and readiness summary for plugin-owned skills.

Keep the first pass small. Start with 2-3 focused surfaces unless the user asks for broader coverage.

## Core philosophy
Build the smallest viable plugin package boundary first, then expand by evidence.

Key principles:
- focused beats sprawling:
  - start with 2-3 high-value surfaces;
  - avoid claiming every capability in one draft;
- deterministic over aspirational:
  - verify with contracts, evals, and validator output;
  - do not rely on "looks good" judgment alone;
- safe conversion by default:
  - inspect before writing;
  - prefer dry-run preview for external sources;
  - only promote files after explicit confirmation when risk is unclear.

## Workflow
1. Confirm package boundary.
- Restate requested surfaces and what is out of scope for this pass.
- Prefer smallest package boundary wording when the request is broad.

2. Inspect source state.
- For external sources, capture:
  - URL/path,
  - selected ref or commit,
  - expected plugin subdirectory.
- Identify risky content before conversion:
  - hidden scripts,
  - unsafe command snippets,
  - ambiguous metadata.

3. Scaffold package layout.
- Default package root to repo-root `plugins/<plugin-name>/` unless the user explicitly requests another destination.
- Enforce required root surfaces first:
  - `.codex-plugin/plugin.json`,
  - `README.md`,
  - `LICENSE`.
- Create only needed optional directories/files:
  - `skills/`,
  - `prompts/` (optional),
  - `hooks/` or `hooks.json`,
  - `agents/` (optional),
  - `scripts/` (optional),
  - `assets/` (optional),
  - `.mcp.json` (optional),
  - `.app.json` (optional),
  - `references/`.
- Keep one-level-deep support files unless a validator requires deeper nesting.

4. Convert with explicit mapping.
- Map source concepts into Codex-friendly structure using documented assumptions.
- Keep placeholder-first metadata when parity is uncertain.
- Mark inferred fields clearly so follow-up hardening is easy.
- When `hooks/` is in scope, map against `references/hooks-contract.md` and separate:
  - verified behavior backed by Codex sources,
  - provisional behavior that still needs runtime confirmation.

5. Validate plugin-owned skills.
- Run the same skill-builder validators against each plugin-owned skill under `skills/`.
- Report pass, warn, fail status by validator and path.

6. Validate plugin contract.
- Validate `.codex-plugin/plugin.json` exists and includes required metadata from `references/plugin-contract.md`.
- Validate hook implementation shape when hooks are requested:
  - event buckets and handler type support,
  - supported vs provisional fields are clearly separated.
- Validate optional surfaces only when requested (`prompts`, `agents`, `.app.json`, `.mcp.json`).

7. Summarize plus next step.
- Return what changed, what was validated, and one next action.

## Validation
Fail fast: stop at the first failed gate, fix it, then rerun before continuing.

Core checks for plugin-owned skills:
```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py <path/to/plugin>/skills/<skill-name>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py <path/to/plugin>/skills/<skill-name>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/analyze_skill.py <path/to/plugin>/skills/<skill-name>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py <path/to/plugin>/skills/<skill-name> --mode both
```

Optional eval depth:
```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/run_skill_evals.py <path/to/plugin>/skills/<skill-name>
```

Repo hygiene before completion:
```bash
bash scripts/sync_skills.sh
python3 scripts/docs_lint.py --mode warn --config docs-policy.json
just validate
```

If full `just validate` fails due to known unrelated baseline issues, report them as pre-existing blockers rather than new regressions.

## Plugin contract
When packaging plugins, treat `references/plugin-contract.md` as mandatory.

Required behavior:
- always emit `.codex-plugin/plugin.json`;
- always emit `README.md` and `LICENSE`;
- include required manifest metadata:
  - `name`,
  - `version`,
  - `description`,
  - `license`,
  - `surfaces`;
- include integration metadata when present:
  - `.mcp.json` wiring details,
  - `.app.json` app-level details;
- keep `prompts` and `agents` optional unless explicitly requested.

## Hook contract
When plugin work includes `hooks/`, treat `references/hooks-contract.md` as mandatory grounding.

Required behavior:
- use the codified event and handler model from the official Codex hooks runtime;
- align examples to currently supported handler types;
- mark unsupported or provisional fields explicitly instead of presenting them as stable;
- keep hook conversion notes auditable with source file links and short evidence notes.

## Constraints and safety
- store generated plugin packages under repo-root `plugins/` by default;
- default to offline-safe behavior for conversion workflows;
- never execute untrusted downloaded scripts during inspection;
- redact secrets, tokens, credentials, and personal data by default;
- avoid absolute paths in skill docs when relative paths are sufficient;
- keep destructive file operations behind explicit user intent;
- do not claim schema parity you cannot verify from source docs;
- for schema-bound outputs, include a `schema_version` field in the emitted summary contract.

## Anti-patterns
- do not build a mega-plugin first and rationalize later;
- do not skip source inspection for external repositories;
- do not mix conversion assumptions with verified facts;
- do not circumvent validator failures with prose-only explanations;
- do not overfit eval prompts by naming the skill in every trigger case.

## Encouraging variation
- adapt package shape to the request context rather than defaulting to one template;
- vary examples and mappings based on the source ecosystem;
- keep deterministic gates constant while allowing structure choices to differ by plugin goal.

## Empowering execution style
Treat this skill as a precision tool, not a rigid script. Use judgment, explain tradeoffs, and choose the smallest safe path that still delivers momentum.

## Examples
- "Create a `codex-plugin-builder` package skeleton for a repo-local plugin with `skills` and `prompts` only."
- "Inspect this GitHub plugin at a pinned commit, dry-run conversion, then show the files you would write."
- "Convert this Claude plugin into a Codex package and validate plugin-owned skills with `skill_gate.py`."
- "Add `hooks` and `.mcp.json` to this existing plugin but keep scope narrow and rerun validators."

## Failure mode
If the request is out of scope:
- explain the mismatch clearly;
- recommend the closest skill:
  - `skill-builder` for standalone skill authoring,
  - `chatgpt-apps` for full Apps SDK implementations,
  - `mcp-builder` for MCP server development without plugin packaging.
