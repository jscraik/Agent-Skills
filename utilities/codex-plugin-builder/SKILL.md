---
name: codex-plugin-builder
description: Create, convert, or validate Codex plugin packages that bundle skills, hooks, agents, and MCP metadata. Use when the user wants plugin packaging work, not standalone skill editing or generic app features.
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
- [Companion skills](#companion-skills)
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
- choose an archetype-informed scaffold shape based on real upstream plugin families;
- add plugin-owned surfaces such as `skills/`, `hooks.json`, `agents/`, `.app.json`, or `.mcp.json`;
- fold deprecated `commands/`, `slash-commands/`, or `prompts/` content into plugin-owned `skills/`;
- scaffold local package docs such as `README.md`, `LICENSE`, and `references/operational-spec.md` when helpful;
- validate plugin-owned skills with the `skill-builder` validator suite;
- audit marketplace coverage and normalize marketplace entries for local plugin catalogs;
- audit a plugin against curated upstream `openai/plugins` conventions without conflating that with minimal runtime validity.

Do not use this skill for:
- standalone app feature implementation;
- unrelated bugfix work;
- generic MCP server implementation that is not plugin packaging.

## Required inputs
- plugin name and destination path;
- default destination policy: if destination is not explicitly requested, write plugin packages to repo-root `plugins/<plugin-name>/`;
- requested surfaces for first pass:
  - runtime required: `.codex-plugin/plugin.json`;
  - common builder surfaces: `README.md`, `LICENSE`, `references/operational-spec.md`, `skills`, `hooks.json`, `agents`, `.app.json`, `.mcp.json`, `assets/`;
  - deprecated source signals to convert into `skills/`: `prompts`, `commands`, `slash-commands`;
- source of truth for conversion when applicable: GitHub URL, local path, and pinned ref or commit;
- validation depth: `none`, `smoke`, or `full`.

If key inputs are missing, ask only the smallest set of clarifying questions needed to scaffold safely.

## Deliverables
Produce only what the request needs:
- plugin package folder with `SKILL.md` or plugin-owned assets;
- archetype selection and suggested marketplace category when scaffold metadata or catalog positioning is in scope;
- plugin-owned skill bundles under `skills/<skill-name>/` created via `skill-builder` when `skills/` is requested;
- plugin-owned agent configs under `agents/<agent-name>.toml` created via `codex-agent-builder` when `agents/` is requested;
- `references/contract.yaml` and `references/evals.yaml` for non-trivial behavior;
- `references/plugin-contract.md` whenever packaging rules or manifest fields are in scope;
- `references/operational-spec.md` for locally scaffolded packages when the package needs an auditable runtime contract;
- `references/package-guide.md` and `README.md` created from shared `docs-expert` templates;
- `references/deconflict-report.md` when the builder compares the candidate against existing local plugins and merge-or-fold analysis is relevant;
- `references/hooks-contract.md` whenever `hooks/` is requested or converted;
- source-specific comparison docs when the source repo is generator-heavy, marketplace-style, or already ships Codex-native install lanes;
- source-backed operational-spec docs when comparison work needs a runtime model beyond the local package;
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
- Choose an archetype that matches the plugin family when possible:
  - `coding_tool`, `productivity_connector`, `design_tool`, `research_connector`, `communication_connector`, or `automation_orchestrator`.
- Use the archetype to drive curated manifest defaults and the suggested marketplace category, while still keeping surface creation capability-driven.
- Enforce the runtime-required surface first:
  - `.codex-plugin/plugin.json`.
- Add local scaffold conventions only when they help the package stay maintainable:
  - `README.md`,
  - `LICENSE`,
  - `references/operational-spec.md`.
- Emit `references/deconflict-report.md` so merge-vs-new-package reasoning stays auditable.
- Treat capability-linked surfaces as opt-in:
  - create `.mcp.json` only when the plugin will expose real MCP wiring, not merely recommend MCPs in prose;
  - create `.app.json` only when the plugin will expose a real app integration surface aligned with `chatgpt-apps`;
  - create `assets/` only when the package needs shared visuals or package assets;
  - do not emit manifest image fields until the referenced files exist.
- Delegate helper-owned surfaces instead of hand-rolling them:
  - `skill-builder` for `skills/<skill-name>/SKILL.md`, `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`;
  - `codex-agent-builder` for plugin-root `agents/<agent-name>.toml`;
  - `docs-expert` templates for `README.md`, `LICENSE`, and `references/package-guide.md`.
- Prefer script-backed scaffolding for deterministic output:
  - `python3 utilities/codex-plugin-builder/scripts/plugin_builder.py scaffold <plugin-name> --path plugins --with-marketplace`.
- If overlap exists and a fresh package is still intentional, require explicit continuation:
  - rerun with `--allow-overlap`.
- Create only needed optional directories/files:
  - `skills/`,
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
  - legacy command manifest keys, `commands/`, `slash-commands/`, and `prompts/` -> `skills/`
- Treat command mapping as semantic, not mechanical:
  - if the source artifact is actually a durable workflow skill, keep or convert it into `skills/`;
  - if it is entrypoint-only prompt content, fold the entry guidance into the most relevant `skills/<name>/SKILL.md`;
  - use `interface.defaultPrompt` only as optional entry text, not as a substitute for packaged workflow logic.
- Rewrite existing `commands/`, `slash-commands/`, and `prompts/` directories into `skills/` unless the user explicitly asks for a compatibility-only archival copy outside the runtime package.
- If a source command is explicitly deprecated and only redirects users to a skill, preserve the target skill and drop the deprecated wrapper from the runtime package.
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
- Audit curated compatibility and marketplace hygiene separately from pass/fail runtime checks:
  - `python3 utilities/codex-plugin-builder/scripts/plugin_builder.py audit-compat <path/to/plugin> --marketplace-path .agents/plugins/marketplace.json`
  - `python3 utilities/codex-plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins`
  - `python3 utilities/codex-plugin-builder/scripts/plugin_builder.py normalize-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins --write`
- Validate hook implementation shape when hooks are requested:
  - event buckets and handler type support,
  - supported vs provisional fields are clearly separated.
- Validate optional surfaces only when requested (`agents`, `.app.json`, `.mcp.json`).

## Companion skills
Use these helper skills instead of recreating their responsibilities inside this plugin skill:
- `skill-builder`: create and validate plugin-owned skill bundles, including `SKILL.md`, `references/`, `scripts/`, `assets/`, and skill eval wiring.
- `codex-agent-builder`: create plugin-owned root agent role configs when `agents/` is requested.
- `docs-expert`: supply shared templates for `README.md`, `LICENSE`, and package-facing reference docs.
- `openai-docs`: verify current Codex/OpenAI runtime behavior before changing contract rules.
- `mcp-builder` or `chatgpt-apps`: implement real MCP/app surfaces when `.mcp.json` or `.app.json` should point at working integrations rather than placeholders.
- `context7`: fetch current third-party library docs when the plugin depends on external SDKs or frameworks.
- `imagegen`: generate real plugin PNG assets only when `interface.composerIcon`, `interface.logo`, or screenshots are intentionally part of the package.

## Validation
Fail fast: stop at the first failed gate, fix it, then rerun before continuing.

Core checks for plugin-owned skills:
```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py <path/to/plugin>/skills/<skill-name>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py <path/to/plugin>/skills/<skill-name>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/analyze_skill.py <path/to/plugin>/skills/<skill-name>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py <path/to/plugin>/skills/<skill-name> --mode both
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py validate <path/to/plugin> --require-marketplace --marketplace-path .agents/plugins/marketplace.json
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py audit-compat <path/to/plugin> --marketplace-path .agents/plugins/marketplace.json
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py normalize-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins --write
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py inspect-local <plugin-name> --path plugins
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
- keep only `plugin.json` inside `.codex-plugin/`; keep `skills/`, `assets/`, `.mcp.json`, and `.app.json` at the plugin root;
- treat `.mcp.json` and `.app.json` as runtime integration files, not recommendation lists;
- enforce manifest path safety for `skills`, `mcpServers`, and `apps`: values must start with `./`, must not be `./`, and must not contain `..`;
- model runtime discovery correctly:
  - `skills` augments the default `./skills/` discovery when both exist;
  - `mcpServers` and `apps` select the declared path and replace default `./.mcp.json` and `./.app.json` discovery;
- if manifest image fields are declared, the referenced files must already exist; prefer `./assets/` for image storage;
- for scaffolded or normalized marketplace files in this repo, include marketplace `interface.displayName` plus plugin-entry `source.source = "local"`, a `./`-prefixed `source.path` relative to the marketplace root (for example `./plugins/<plugin-name>`), `policy.installation`, `policy.authentication`, and `category`;
- when the user does not specify a category, infer a suggested category from the chosen or inferred archetype, then allow deliberate overrides;
- validator compatibility note: accept legacy flat `installPolicy` and `authPolicy` while existing local marketplaces migrate, but emit the canonical nested `policy` object for all new scaffolds and overwrites;
- keep marketplace normalization separate from plugin runtime validation so curated-compatibility cleanup does not masquerade as runtime breakage;
- keep `agents` optional unless explicitly requested;
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
- fold deprecated prompt and command surfaces into `skills/`, rewrite docs to use skill wording instead of slash-command wording, and keep shared surfaces (`skills`, `hooks`, `agents`, `.mcp.json`, `.app.json`) in Codex-compatible structure;
- do not keep `commands/`, `slash-commands/`, or `prompts/` as runtime package surfaces in newly created or converted plugins.

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

## Failure mode
If the request is out of scope:
- explain the mismatch clearly and recommend the closest skill: `skill-builder` for standalone skill authoring, `chatgpt-apps` for full Apps SDK implementations, or `mcp-builder` for MCP server development without plugin packaging.

## Gotchas
- Keep marketplace hygiene (`audit-marketplace`, `normalize-marketplace`) separate from runtime validity (`validate`).
## See Also
| Skill | When to use |
|---|---|
| [[skill-builder]] | Author or upgrade a standalone skill before packaging it into a plugin |
| [[codex-agent-builder]] | Add agent roles to the plugin bundle alongside skills and hooks |
| [[decide-build-primitive]] | Decide whether the capability belongs in a plugin at all |
| [[skill-installer]] | Install a finished skill directly when full plugin packaging is unnecessary |

**Topic map:** [[agent-ops]]
