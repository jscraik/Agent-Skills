---
name: plugin-builder
description: Harden, convert, and validate Codex plugin packages that bundle skills, hooks, agents, and MCP metadata. Use when the deliverable is clearly a plugin package and needs contract-grade safety checks, not when standalone skill lifecycle hardening is still unresolved.
metadata:
  skill-type: scaffolding_templates
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  review_cadence: quarterly
  last_reviewed: 2026-04-07
  metadata_source: frontmatter
---

# Plugin Builder
Build and harden safe, focused plugin packages for Codex workflows.

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Core philosophy](#core-philosophy)
- [Encouraging variation](#encouraging-variation)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints and safety](#constraints-and-safety)
- [Anti-patterns](#anti-patterns)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)
- [See Also](#see-also)

## When to use
Use this skill when the request is to:
- scaffold a new Codex plugin package;
- inspect and convert a third-party plugin source into Codex structure;
- harden an existing plugin package with contract and marketplace checks;
- package a contract-valid standalone skill as a plugin-owned deliverable.

Do not use this skill for:
- first-pass standalone skill authoring or hardening (`skill-creator`/`skill-builder`);
- pure plugin acquisition and installation from GitHub (`plugin-installer`);
- generic product feature implementation outside plugin packaging.

Handoffs:
- from `skill-builder` once standalone skill validity evidence is complete;
- to `plugin-installer` when the goal is distribution/install verification rather than package hardening.

## Required inputs
- plugin name and destination path (default `plugins/<plugin-name>`);
- requested plugin surfaces (`skills/`, `hooks.json`, `agents/`, `.mcp.json`, `.app.json`);
- source URL/path and pinned ref when converting third-party sources;
- validation depth (`none`, `smoke`, `full`).

## Deliverables
Produce only what the request needs:
- plugin package root with `.codex-plugin/plugin.json`;
- optional plugin-owned surfaces (`skills/`, `hooks.json`, `agents/`, `.mcp.json`, `.app.json`);
- `references/operational-spec.md` and `references/deconflict-report.md` when hardening/conversion is in scope;
- validator evidence summary and explicit blocker notes when checks fail.

## Core philosophy
Plugin hardening is a safety-first downstream operation:
- treat every source as untrusted until contract checks pass;
- keep plugin boundaries explicit so one package cannot silently override another;
- prefer deterministic validation evidence over assumptions.

Before finalizing any package, confirm:
- does the package stay within declared surfaces and paths?
- do marketplace entries reflect real on-disk state?
- do compatibility and rollback signals support safe activation?

## Encouraging variation
Adapt the hardening plan to source risk and package complexity:
- small local plugin updates can run `inspect-local` plus targeted validate/audit checks;
- third-party conversions should add deeper deconflict review and marketplace normalization;
- multi-surface plugins (skills + hooks + agents + MCP) should use staged checks with explicit blocker reporting.

No two plugin hardening runs should look identical when risk context differs.

## Workflow
1. Confirm plugin boundary and keep first pass to 2-3 focused surfaces.
2. Inspect external source before writing files.
3. Run local deconflict analysis against existing plugins.
4. Scaffold or convert package surfaces.
5. Validate plugin-owned skills with `skill-builder` validators.
6. Validate plugin contract and marketplace compatibility.
7. Report outcomes, risks, and next actions.

Core commands:

```bash
python3 utilities/plugin-builder/scripts/plugin_builder.py inspect-source <source-path-or-repo>
python3 utilities/plugin-builder/scripts/plugin_builder.py scaffold <plugin-name> --path plugins --with-marketplace
python3 utilities/plugin-builder/scripts/plugin_builder.py validate <path/to/plugin> --require-marketplace --marketplace-path .agents/plugins/marketplace.json
```

## Validation
Run checks in order and fail fast: stop at first failure, fix it, then rerun from that gate.

```bash
python3 utilities/plugin-builder/scripts/plugin_builder.py inspect-local <plugin-name> --path plugins
python3 utilities/plugin-builder/scripts/plugin_builder.py validate <path/to/plugin> --require-marketplace --marketplace-path .agents/plugins/marketplace.json
python3 utilities/plugin-builder/scripts/plugin_builder.py audit-compat <path/to/plugin> --marketplace-path .agents/plugins/marketplace.json
python3 utilities/plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins
python3 utilities/plugin-builder/scripts/plugin_builder.py normalize-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins --write
```

Family gate note:
- `scripts/validate_skill_authoring_family.sh` now enforces contract/eval/task-profile parity for `plugin-builder`.
- Live Codex smoke+release execution is trusted-lane only with `SKILL_FAMILY_LIVE_EVALS=1 SKILL_FAMILY_LIVE_EVALS_TRUSTED=1`.

## Constraints and safety
- never execute untrusted scripts from downloaded sources;
- redact secrets/tokens/PII in output and artifacts;
- keep destructive operations behind explicit user confirmation;
- keep path declarations plugin-relative (`./...`) and forbid `..` traversal.

## Anti-patterns
Avoid these failure patterns:
- validating only `plugin.json` while skipping marketplace consistency checks;
- treating conversion and installation as the same workflow owner;
- importing third-party plugin content without explicit source and ref evidence;
- hiding unresolved blockers instead of reporting a no-go result.

## Failure mode
If the request is out of scope, route clearly:
- `skill-builder` for standalone skill hardening;
- `plugin-installer` for installation/provenance workflows;
- `mcp-builder` for MCP servers not tied to plugin packaging.

## Gotchas
- Symptom: plugin conversion is treated as a straight install workflow.
- Cause: packaging and distribution boundaries were collapsed.
- Do instead: complete `plugin-builder` contract and compatibility checks before handing off install work.
- Check: `validate` and `audit-compat` evidence exists before any installer handoff.

## See Also

| Skill | When to use |
|---|---|
| [[plugin-installer]] | Install and verify third-party plugins from GitHub with provenance + rollback controls |
| [[skill-builder]] | Harden standalone skills before plugin packaging |
| [[plugin-creator]] | Start from a minimal plugin scaffold before hardening |

**Topic map:** [[agent-ops]]
