---
name: skill-installer
description: Install contract-valid Codex skills from curated registries or GitHub sources into `$CODEX_HOME/skills` with provenance, quarantine validation, and rollback safeguards. Use when distribution and visibility repair are the primary goals after authoring quality is already established.
metadata:
  short-description: Install validated skills with provenance and rollback safety
---

# Skill Installer

## When to use

Use this skill when the user asks to:
- list installable skills from curated or experimental registries;
- install a contract-valid skill from curated sources or GitHub path;
- restore missing skill visibility by reinstalling into a clean destination path.

Do not use this skill as primary owner for:
- creating new skills from scratch;
- lifecycle hardening, eval tuning, or routing optimization;
- plugin packaging workflows.

Handoffs:
- to `skill-creator` for first-pass authoring;
- to `skill-builder` for lifecycle hardening and contract/eval upgrades;
- to `codex-plugin-builder` when the deliverable must ship as a plugin package.

## Inputs

Minimum inputs:
- install source (`--repo`/`--url`, and one or more `--path` values);
- destination root (default `${CODEX_HOME:-$HOME/.codex}/skills`);
- trust policy (trusted repo allowlist or explicit override);
- provenance pin (`--ref` commit SHA unless explicit override);
- validation policy (`--validation-level strict|compat`).

If scope expands beyond install/distribution, narrow to install-only and hand off adjacent work.

Contract resources to read before risky installs:
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`

## Outputs

Expected outputs from a successful run:
- installed skill directory at `<dest>/<skill-name>`;
- quarantine promotion evidence;
- rollback journal at `<dest>/.install-journal/skill-installer/<run-id>.jsonl`;
- provenance manifest at `<dest>/.provenance/skill-installer/<run-id>.json`.

Structured output contract:
- provenance manifests include `schema_version` and run metadata;
- staged validator results are recorded per skill for auditability.

User-facing closeout:
- list what was installed and source ref;
- include any trust override used;
- remind user to restart Codex to refresh skill discovery.

## Philosophy

Installation is downstream execution, not authoring judgment:
- trust boundaries must be explicit before activation;
- provenance must be durable and machine-checkable;
- activation should be transactional so failures roll back cleanly;
- installer behavior should remain predictable under pressure.

## Constraints

- Prefer curated or explicitly trusted sources by default.
- Require pinned commit refs unless an explicit override is approved.
- Stage in quarantine before promotion; never activate unvalidated content directly.
- Network access is required only for GitHub install paths; keep an explicit host allowlist of `github.com`, `api.github.com`, and `codeload.github.com`.
- Keep transport boundaries explicit: SSH fallback is opt-in (`--allow-ssh-fallback`) and only allowed with `--method git`; call it out in closeout when used.
- Never print secrets, access tokens, or private credentials in output.
- Redact sensitive values in logs/manifests before sharing snippets.
- Keep installation scope focused; do not drift into authoring or plugin packaging work.
- If icon or UX assets are bundled for installer docs, keep them under `assets/` and reference them explicitly in change notes.

## Procedure

1. Resolve install source and requested skill paths.
2. Validate trust allowlist and ref pinning policy.
3. Validate path/ref tokens (`--path` and `--ref`) before any Git command execution.
4. Fetch source via download and use git fallback only when failure class and transport policy allow it.
5. Stage each skill in quarantine.
6. Run staged validators (`quick_validate`, `skill_gate`, `openclaw`) when validation level is strict.
7. Promote staged skills atomically.
8. Write rollback journal and provenance manifest.
9. Report installed skills and restart guidance.

Primary commands:

```bash
scripts/list-skills.py
scripts/list-skills.py --path skills/.experimental
scripts/install-skill-from-github.py --repo <owner>/<repo> --ref <40-char-sha> --path <path/to/skill>
scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<sha>/<path>
```

Key options:
- `--trusted-repo <owner/repo>`
- `--allow-untrusted-source`
- `--allow-unpinned-ref`
- `--allow-ssh-fallback` (requires `--method git`)
- `--validation-level strict|compat`
- `--provenance-dir <path>`
- `--journal-dir <path>`

## Anti-Patterns

Avoid these failures:
- installing from floating branch refs without explicit approval;
- bypassing quarantine validation in strict environments;
- treating installer as a place to redesign skill behavior;
- continuing after failed validation or failed promotion;
- omitting provenance and rollback evidence from closeout.

## Examples

- When the user asks: "Can you list curated skills and install one for PR triage?"
- When the user says: "Help me install this GitHub skill at a pinned commit and keep provenance logs."
- When the user asks: "Please reinstall this known-good skill because it disappeared from my list."

## Validation

Run these checks and fail fast: if any gate fails, stop immediately, fix, then rerun from that gate.

```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py skills-system/skill-installer --mode compat
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py skills-system/skill-installer --require-security-evals --pi-high-fail --require-fail-fast
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py skills-system/skill-installer --mode both --format text
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/run_skill_evals.py skills-system/skill-installer --list-cases --eval-mode smoke
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/run_skill_evals.py skills-system/skill-installer --runner codex --eval-mode smoke
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/run_skill_evals.py skills-system/skill-installer --runner codex --eval-mode release
python3 scripts/test_skill_installer_security.py
```

Family gate note:
- `scripts/validate_skill_authoring_family.sh` runs structural contract/security checks by default (lists smoke+release cases).
- Live Codex smoke+release execution is trusted-lane only with `SKILL_FAMILY_LIVE_EVALS=1 SKILL_FAMILY_LIVE_EVALS_TRUSTED=1`.

## See Also

| Skill | When to use together |
|---|---|
| [[skill-creator]] | Author or complete a starter skill before installation |
| [[skill-builder]] | Harden and validate an existing skill before install/distribution |
| [[codex-plugin-builder]] | Package a validated skill as a plugin deliverable |

**Topic map:** [[agent-ops]]
