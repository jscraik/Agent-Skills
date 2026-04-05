---
name: plugin-creator
description: Scaffold local Codex plugins with a contract-valid `.codex-plugin/plugin.json`, optional companion folders, and marketplace entries with explicit policy defaults. Use when creating a plugin skeleton or updating local marketplace metadata, not for skill hardening or installation workflows.
metadata:
  short-description: Scaffold plugin skeletons and marketplace entries
---

# Plugin Creator

## When to use

Use this skill when the user asks to:
- create a new local plugin skeleton;
- generate `.codex-plugin/plugin.json` with valid baseline fields;
- add or update local marketplace entries in `.agents/plugins/marketplace.json`.

Do not use this skill as primary owner for:
- skill lifecycle hardening and eval upgrades;
- installing skills into Codex directories;
- full plugin packaging, release, or validation programs beyond scaffold scope.

Handoffs:
- to `skill-builder` when bundled skills need quality hardening;
- to `codex-plugin-builder` for full plugin package assembly and governance checks;
- to `skill-installer` when the user actually needs skill distribution/import.

## Inputs

Minimum inputs:
- plugin name (will be normalized to lowercase hyphen-case);
- target parent path (`plugins/` repo-local or home-local alternative);
- optional companion folder flags (`--with-<type>`): choose only the folder types needed for this plugin's first-pass scaffold; avoid adding every available type unless explicitly requested;
- marketplace intent (`--with-marketplace`, optional marketplace path override);
- overwrite intent (`--force` only when explicit replacement is requested).

If requirements are broad, start with 2-3 focused surfaces (manifest, folder scaffold, marketplace entry), then defer advanced packaging to handoff skills. Vary the companion folder selection to match what the plugin actually needs — unique scaffolds are better than generic kitchen-sink layouts that add noise without purpose.

Contract resources to reference during scaffold work:
- `references/plugin-json-spec.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`

## Outputs

Expected outputs:
- `<plugin-root>/<plugin-name>/.codex-plugin/plugin.json`;
- optional companion folders selected by flags;
- marketplace entry at `<root>/.agents/plugins/marketplace.json` when requested.

Output contract notes:
- generated JSON payloads should remain machine-checkable;
- include `schema_version` when introducing strict structured report contracts.

Marketplace entry contract must keep explicit:
- `policy.installation`
- `policy.authentication`
- `category`

## Philosophy

Plugin scaffolding should be deterministic and policy-forward:
- normalize names once and reuse consistently;
- keep defaults explicit so downstream automation is stable;
- preserve existing marketplace metadata unless user asks to replace it;
- separate scaffold creation from deeper packaging lifecycle decisions.

Adapt the scaffold layout to each plugin's unique purpose — avoid repetition of generic templates that don't match actual needs. Different plugin types require different companion structures; a capable scaffold enables rapid prototyping while keeping the first-pass scope narrow. Creative variation in the folder selection and marketplace policy is encouraged when the plugin's context differs from the default. Explore the available structure options and customize the baseline to what the plugin actually needs today, not what it might need tomorrow.

## Constraints

- Keep `.codex-plugin/plugin.json` present in every generated plugin.
- Keep plugin folder name and `plugin.json.name` aligned.
- Preserve marketplace root `interface.displayName` when already present.
- Never output secrets, tokens, or private credentials in generated manifests.
- Redact sensitive values in any shared logs or snippets by default.
- Add `policy.products` only when the user explicitly asks for product gating.
- Keep plugin branding assets under `assets/` and treat them as optional, not blocking scaffold validity.

## Procedure

1. Normalize plugin name and confirm parent path scope (repo-local vs home-local).
2. Run scaffold script for base plugin structure.
3. Add optional folders only when requested.
4. Generate or update marketplace entry with explicit policy defaults.
5. Apply `--force` only with explicit overwrite intent.
6. Validate generated outputs before handoff (`plugin.json` contract, marketplace policy defaults, and no implicit `policy.products` insertion).

Core commands:

```bash
# Minimal scaffold (manifest only)
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py <plugin-name>

# With marketplace entry
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py <plugin-name> --with-marketplace

# With selected companion folders (choose only what the plugin needs)
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py <plugin-name> --with-<type> [--with-<type>...] --with-marketplace
```

Home-local example:

```bash
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py <plugin-name> \
  --path ~/plugins \
  --marketplace-path ~/.agents/plugins/marketplace.json \
  --with-marketplace
```

## Anti-Patterns

Avoid these failures:
- mixing plugin scaffold scope with full package governance work;
- silently overwriting existing entries without explicit `--force` intent;
- omitting policy defaults (`installation`, `authentication`, `category`);
- writing absolute repo paths into marketplace `source.path` values;
- shipping manifest or marketplace examples that expose sensitive values.

## Examples

- When the user asks: "Can you create a repo-local plugin scaffold named `incident-tools` and add marketplace entry?"
- When the user says: "Help me set up a home-local plugin in `~/plugins` and update `~/.agents/plugins/marketplace.json`."
- When the user asks: "Please generate the plugin skeleton with companion structure folders (scripts, assets) but keep policy defaults unchanged."

## Validation

Run checks in order and fail fast: stop at first failure, fix it, then rerun from the failed gate.

```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py skills-system/plugin-creator
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py skills-system/plugin-creator --require-security-evals --pi-high-fail --require-fail-fast
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py skills-system/plugin-creator --mode both --format text
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/run_skill_evals.py skills-system/plugin-creator --list-cases --eval-mode smoke
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/run_skill_evals.py skills-system/plugin-creator --runner codex --eval-mode smoke
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/run_skill_evals.py skills-system/plugin-creator --runner codex --eval-mode release
```

Family gate note:
- `scripts/validate_skill_authoring_family.sh` defaults to structural contract/security checks (smoke+release case listing).
- Live Codex smoke+release execution is trusted-lane only with `SKILL_FAMILY_LIVE_EVALS=1 SKILL_FAMILY_LIVE_EVALS_TRUSTED=1`.

## See Also

| Skill | When to use together |
|---|---|
| [[codex-plugin-builder]] | Promote scaffold into a full plugin package with governance checks |
| [[skill-builder]] | Improve bundled skill quality before plugin release |
| [[codex-agent-creator]] | Add or refine agent roles inside the plugin |

**Topic map:** [[agent-ops]]
