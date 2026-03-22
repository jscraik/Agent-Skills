---
name: codex-plugin-builder
description: "Create, convert, and validate Codex plugin packages that include focused skills, prompts, hooks, agents, and MCP metadata. Use this skill when the user asks to scaffold plugin bundles, safely convert external plugin sources, or quality-gate plugin-owned skills; do not use it for unrelated app feature work."
metadata:
  skill-type: scaffolding_templates
---

# Codex Plugin Builder
Build safe, focused plugin packages for Codex workflows.

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Core philosophy](#core-philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [Plugin contract](#plugin-contract)
- [Hook contract](#hook-contract)
- [Terminology mapping](#terminology-mapping)
- [Constraints and safety](#constraints-and-safety)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Failure mode](#failure-mode)

## When to use
Use this skill when the request is to:
- scaffold a new Codex plugin package;
- inspect an external plugin source before conversion;
- convert a Claude-oriented plugin shape into a Codex-compatible package;
- compare a proposed plugin against existing local plugins before deciding whether to merge, fold, improve, or create;
- add plugin-owned surfaces such as `skills/`, `hooks.json`, `commands/`, `prompts/`, `agents/`, `.app.json`, or `.mcp.json`;
- scaffold local package docs such as `README.md`, `LICENSE`, and `references/operational-spec.md` when helpful;
- validate plugin-owned skills with the `skill-builder` validator suite.

Do not use this skill for:
- standalone app feature implementation;
- unrelated bugfix work;
- generic MCP server implementation that is not plugin packaging.

## Required inputs
- plugin name and destination path;
- default destination policy: if destination is not explicitly requested, write plugin packages to repo-root `plugins/<plugin-name>/`;
- requested surfaces for first pass:
  - runtime required:
    - `.codex-plugin/plugin.json`,
  - builder conventions:
    - `README.md`,
    - `LICENSE`,
    - `references/operational-spec.md`,
  - `skills`,
  - `prompts`,
  - `commands`,
  - `hooks.json`,
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

## Deliverables
Produce only what the request needs:
- plugin package folder with `SKILL.md` or plugin-owned assets;
- `references/contract.yaml` and `references/evals.yaml` for non-trivial behavior;
- `references/plugin-contract.md` whenever packaging rules or manifest fields are in scope;
- `references/operational-spec.md` for locally scaffolded packages when the package needs an auditable runtime contract;
- `references/deconflict-report.md` when the builder compares the candidate against existing local plugins and merge-or-fold analysis is relevant;
- `references/hooks-contract.md` whenever `hooks/` is requested or converted;
- `references/arscontexta-conversion-map.md` when the source plugin is Ars Contexta or similarly mixes package assets, generated runtime outputs, and migration-only platform files;
- `references/compound-engineering-comparison.md` when the source repo is marketplace-style, contains multiple plugins, or ships provider-conversion tooling and provider-specific manifests;
- `references/superpowers-comparison.md` when the source repo already ships Codex-native install docs, deprecated command shims, or provider-multiplexed hook wrappers;
- `references/arscontexta-operational-spec.md`, `references/compound-engineering-operational-spec.md`, or source-specific equivalents when comparison work needs a source-backed runtime model;
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
- improve before duplicate:
  - check the local plugin directory for exact or similar packages first;
  - prefer merge, fold, or capability expansion when an existing plugin already covers the job;
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
- Determine whether the source is:
  - a single plugin package,
  - a marketplace repo containing multiple plugins,
  - or a converter repo that also ships plugin payloads.
- Resolve the real plugin root before inventorying surfaces.
- Inspect manifest-declared custom paths before assuming defaults for `commands`, `skills`, `agents`, `hooks`, or `mcp`.
- Inspect sibling provider metadata such as `.cursor-plugin/` as migration references, not as Codex runtime surfaces.
- Identify risky content before conversion:
  - hidden scripts,
  - unsafe command snippets,
  - ambiguous metadata,
  - inline MCP definitions that diverge from `.mcp.json`,
  - repo-maintainer command surfaces that are not actually part of the plugin payload,
  - deprecated command shims that should not become fresh Codex prompts,
  - native Codex install docs that already describe a non-plugin skill-discovery lane,
  - provider-specific hook wrappers or env vars that should not be copied verbatim into Codex hooks.

3. Run local deconflict review before creating a new package.
- Inspect the target plugin directory for exact or similar local plugins.
- Treat this as the plugin equivalent of `skill-builder` install-distribute deconflict analysis.
- Prefer script-backed inspection:
  - `python3 utilities/codex-plugin-builder/scripts/plugin_builder.py inspect-local <plugin-name> --path plugins`
- If overlap is detected, prefer:
  - updating the existing plugin,
  - folding the new capability into the existing plugin,
  - or documenting why a distinct package is still justified.

4. Scaffold package layout.
- Default package root to repo-root `plugins/<plugin-name>/` unless the user explicitly requests another destination.
- Enforce the runtime-required surface first:
  - `.codex-plugin/plugin.json`.
- Add local scaffold conventions only when they help the package stay maintainable:
  - `README.md`,
  - `LICENSE`,
  - `references/operational-spec.md`.
- Emit `references/deconflict-report.md` so merge-vs-new-package reasoning stays auditable.
- Prefer script-backed scaffolding for deterministic output:
  - `python3 utilities/codex-plugin-builder/scripts/plugin_builder.py scaffold <plugin-name> --path plugins --with-marketplace`.
- If overlap exists and a fresh package is still intentional, require explicit continuation:
  - rerun with `--allow-overlap`.
- Create only needed optional directories/files:
  - `skills/`,
  - `prompts/` (optional),
  - `commands/` when preserving a curated Codex command surface,
  - `hooks/` or `hooks.json`,
  - `agents/` (optional),
  - `scripts/` (optional),
  - `assets/` (optional),
  - `.mcp.json` (optional),
  - `.app.json` (optional),
  - `references/`.
- Keep one-level-deep support files unless a validator requires deeper nesting.

5. Convert with explicit mapping.
- Map source concepts into Codex-friendly structure using documented assumptions.
- Apply terminology mapping from `references/terminology-map.md`:
  - `.claude-plugin/plugin.json` -> `.codex-plugin/plugin.json`
  - legacy command manifest keys and slash-command language -> `prompts/`
- Treat command mapping as semantic, not mechanical:
  - if the source artifact is actually a durable workflow skill, keep or convert it into `skills/`;
  - if it is entrypoint-only prompt content, convert it into `prompts/`;
  - if the target UX benefits from both, document the fan-out explicitly.
- Do not rewrite an existing curated Codex `commands/` directory away unless the user is explicitly converting that surface into prompts or skills.
- If a source command is explicitly deprecated and only redirects users to a skill, do not preserve it as a first-class Codex prompt unless the user asks for backward-compatibility shims.
- When the source looks like Ars Contexta or another generator-heavy plugin, explicitly separate:
  - package-owned plugin surfaces,
  - generated runtime outputs,
  - migration-only or provisional behavior.
- When the source already ships `.codex/INSTALL.md` or `docs/README.codex.md`, record whether the repo already supports Codex via native skill discovery and whether conversion to a plugin package is additive or redundant.
- Keep placeholder-first metadata when parity is uncertain.
- Mark inferred fields clearly so follow-up hardening is easy.
- When `hooks/` is in scope, map against `references/hooks-contract.md` and separate:
  - verified behavior backed by Codex sources,
  - provisional behavior that still needs runtime confirmation.
- Preserve hook intent, not provider glue:
  - rewrite provider-specific output multiplexing into the Codex hook contract;
  - do not carry `CLAUDE_PLUGIN_ROOT`, Cursor-only payload fields, or cross-platform `.cmd` wrappers into Codex without a clear Codex runtime need.

6. Validate plugin-owned skills.
- Run the same skill-builder validators against each plugin-owned skill under `skills/`.
- Report pass, warn, fail status by validator and path.

7. Validate plugin contract.
- Validate `.codex-plugin/plugin.json` exists and satisfies the runtime contract from `references/plugin-contract.md`.
- Treat richer metadata such as `version`, `author`, `license`, `homepage`, `repository`, `keywords`, and `hooks` as optional curated fields unless the user explicitly asks for marketplace-ready polish.
- Validate `references/operational-spec.md` exists and matches the compact runtime-spec contract:
  - transition table is the source of truth,
  - Mermaid diagram is derived from the same transitions,
  - failures terminate in explicit fail states.
- Validate deconflict posture:
  - when an exact or similar local plugin exists, require `references/deconflict-report.md`;
  - treat unexplained duplicate-intent packages as a blocker until merge/fold/improve reasoning is explicit.
- Validate plugin and marketplace JSON contract with script-backed checks:
  - `python3 utilities/codex-plugin-builder/scripts/plugin_builder.py validate <path/to/plugin> --require-marketplace --marketplace-path .agents/plugins/marketplace.json`
- Validate hook implementation shape when hooks are requested:
  - event buckets and handler type support,
  - supported vs provisional fields are clearly separated.
- Validate optional surfaces only when requested (`prompts`, `agents`, `.app.json`, `.mcp.json`).

8. Summarize plus next step.
- Return what changed, what was validated, and one next action.

## Validation
Fail fast: stop at the first failed gate, fix it, then rerun before continuing.

Core checks for plugin-owned skills:
```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py <path/to/plugin>/skills/<skill-name>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py <path/to/plugin>/skills/<skill-name>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/analyze_skill.py <path/to/plugin>/skills/<skill-name>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py <path/to/plugin>/skills/<skill-name> --mode both
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py validate <path/to/plugin> --require-marketplace --marketplace-path .agents/plugins/marketplace.json
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py inspect-local <plugin-name> --path plugins
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
- validate the runtime-required manifest shape first;
- run local deconflict review before shipping a new plugin package;
- emit `references/deconflict-report.md` when overlap review is relevant;
- include integration metadata when present:
  - `.mcp.json` wiring details,
  - `.app.json` app-level details;
- marketplace entries must include marketplace `interface.displayName`, `source.source = "local"`, `source.path = "./plugins/<plugin-name>"`, `policy.installation`, `policy.authentication`, and `category`;
- validator compatibility note: accept legacy flat `installPolicy` and `authPolicy` while existing local marketplaces migrate, but emit the canonical nested `policy` object for all new scaffolds and overwrites;
- keep `prompts` and `agents` optional unless explicitly requested;
- remember that `README.md`, `LICENSE`, `references/operational-spec.md`, and richer manifest metadata are builder conventions or curated-plugin niceties, not minimal runtime requirements.

## Hook contract
When plugin work includes `hooks/`, treat `references/hooks-contract.md` as mandatory grounding.

Required behavior:
- use the codified event and handler model from the official Codex hooks runtime;
- align examples to currently supported handler types;
- mark unsupported or provisional fields explicitly instead of presenting them as stable;
- keep hook conversion notes auditable with source file links and short evidence notes.

## Terminology mapping
When converting Claude-oriented plugins, use `references/terminology-map.md` as a required check.

Required behavior:
- do not ship converted plugins with Claude package markers such as `.claude-plugin`;
- ensure codex prompts use `prompts/` and plugin docs use prompt wording, not slash-command wording;
- keep shared surfaces (`skills`, `hooks`, `agents`, `.mcp.json`, `.app.json`) in Codex-compatible structure;
- allow curated Codex-native `commands/` directories to remain when they are already part of the official plugin shape.

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

## Failure mode
If the request is out of scope:
- explain the mismatch clearly;
- recommend the closest skill:
  - `skill-builder` for standalone skill authoring,
  - `chatgpt-apps` for full Apps SDK implementations,
  - `mcp-builder` for MCP server development without plugin packaging.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
