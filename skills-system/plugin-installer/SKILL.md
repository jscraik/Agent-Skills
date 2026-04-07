---
name: plugin-installer
description: Install contract-valid Codex plugins from curated registries or GitHub sources into `${CODEX_HOME:-$HOME/.codex}/plugins` with provenance, quarantine validation, and rollback safeguards. Use when distribution and visibility repair are the primary goals after package hardening is already complete.
metadata:
  short-description: Install validated plugins with provenance and rollback safety
---

# Plugin Installer

## When to use

Use this skill when the user asks to:
- list installable third-party plugins from curated or explicit sources;
- install a contract-valid plugin from GitHub path or repository ref;
- verify plugin integrity and restore missing plugin visibility.

Do not use this skill as primary owner for:
- plugin package authoring or conversion hardening;
- standalone skill lifecycle hardening;
- marketplace curation beyond install-scoped updates.

Handoffs:
- to `plugin-builder` for package hardening and conversion;
- to `plugin-creator` for first-pass local scaffold creation;
- to `skill-installer` when installed skills need lifecycle hardening or contract/eval upgrades.

## Inputs

Minimum inputs:
- install source (`--repo` or `--url`, plus `--path` plugin root);
- destination root (default `${CODEX_HOME:-$HOME/.codex}/plugins`);
- trust policy (trusted repo allowlist or explicit override);
- provenance pin (`--ref` commit SHA unless explicit override);
- validation policy (`--validation-level strict|compat`).

## Outputs

Expected outputs from a successful run:
- installed plugin directory at `<dest>/<plugin-name>`;
- quarantine promotion evidence and validation result;
- rollback journal at `<dest>/.install-journal/plugin-installer/<run-id>.jsonl`;
- provenance manifest at `<dest>/.provenance/plugin-installer/<run-id>.json`.

User-facing closeout:
- list installed plugin and source ref/commit;
- include any trust override used;
- remind user to restart Codex to refresh plugin discovery.

## Philosophy

Installation is downstream execution, not package design judgment:
- trust boundaries must be explicit before activation;
- provenance must be durable and machine-checkable;
- activation should be transactional so failures roll back cleanly;
- installer behavior should remain predictable under pressure.

## Constraints

- prefer curated or explicitly trusted sources by default;
- require pinned commit refs unless explicit override is approved;
- stage in quarantine before promotion; never activate unvalidated plugin content directly;
- network access is required only for GitHub install paths;
- never print secrets, access tokens, or credentials in output.

## Procedure

1. Resolve source and requested plugin path.
2. Validate trust allowlist and ref pinning policy.
3. Fetch source and stage plugin in quarantine.
4. Run staged validation (`plugin-builder validate`) for strict mode.
5. Promote plugin atomically into destination.
6. Write rollback journal and provenance manifest.
7. Report install summary and restart guidance.

Core commands:

```bash
bin/ask plugins install https://github.com/<owner>/<repo> --path plugins/<plugin-name>
python3 skills-system/plugin-installer/scripts/install-plugin-from-github.py --url https://github.com/<owner>/<repo> --path plugins/<plugin-name>
```

## Anti-Patterns

Avoid these failures:
- installing from floating refs without explicit approval;
- bypassing quarantine validation in strict environments;
- treating installer flow as package design or conversion hardening;
- omitting provenance or rollback evidence from closeout.

## Examples

- "Install this third-party plugin from GitHub and verify it is contract-valid before activation."
- "Reinstall this known-good plugin because it disappeared from my Codex plugin list."
- "Import a plugin at a pinned commit and keep a provenance audit trail."

## Validation

Run checks in order and fail fast: stop at first failure, fix it, then rerun from the failed gate.

```bash
python3 skills-system/plugin-installer/scripts/install-plugin-from-github.py --url https://github.com/<owner>/<repo> --path plugins/<plugin-name> --validation-level strict
python3 utilities/plugin-builder/scripts/plugin_builder.py validate <installed-plugin-path>
./bin/ask repo validate --ephemeral
```

Family gate note:
- `scripts/validate_skill_authoring_family.sh` now enforces structural contract/security checks for `plugin-installer`.
- Live Codex smoke+release execution is trusted-lane only with `SKILL_FAMILY_LIVE_EVALS=1 SKILL_FAMILY_LIVE_EVALS_TRUSTED=1`.

## See Also

| Skill | When to use together |
|---|---|
| [[plugin-builder]] | Harden/convert plugin packages before distribution install |
| [[plugin-creator]] | Scaffold a local plugin package before hardening or install |
| [[skill-installer]] | Install standalone skills when plugin packaging is unnecessary |

**Topic map:** [[agent-ops]]
