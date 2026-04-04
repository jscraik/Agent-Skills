---
name: skill-installer
description: Install contract-valid Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list, import, install, or repair visibility for an already-valid skill backed by ContractValidityEvidence, not to author, harden, or package a plugin.
metadata:
  short-description: Install contract-valid skills from curated or repo sources
---

# Skill Installer

Helps install already-valid skills. By default these are from https://github.com/openai/skills/tree/main/skills/.curated, but users can also provide other locations. Experimental skills live in https://github.com/openai/skills/tree/main/skills/.experimental and can be installed the same way.

Treat installation as the execution stage after lifecycle judgment is settled:
- prefer curated or explicitly trusted sources;
- when importing remote content, pin the ref or commit and record provenance before activation;
- validate imported skills in quarantine or another staged location before moving them into `$CODEX_HOME/skills`;
- roll back atomically if validation or activation fails;
- consume `ContractValidityEvidence` from `skill-builder` before treating a skill as install-ready;
- hand off to `skill-builder` if the skill still needs routing, validator, eval, or packaging judgment;
- hand off to `codex-plugin-builder` when the requested deliverable is a plugin package instead of a standalone installed skill.

Use the helper scripts based on the task:
- List skills when the user asks what is available, or if the user uses this skill without specifying what to do. Default listing is `.curated`, but you can pass `--path skills/.experimental` when they ask about experimental skills.
- Install from the curated list when the user provides a skill name.
- Install from another repo when the user provides a GitHub repo/path (including private repos).
- For production-trust installs, require a pinned commit ref, provenance manifest output, and rollback journal output.

Install skills with the helper scripts.

## Communication

When listing skills, output approximately as follows, depending on the context of the user's request. If they ask about experimental skills, list from `.experimental` instead of `.curated` and label the source accordingly:
"""
Skills from {repo}:
1. skill-1
2. skill-2 (already installed)
3. ...
Which ones would you like installed?
"""

After installing a skill, tell the user: "Restart Codex to pick up new skills."

## Scripts

All of these scripts use network, so when running in the sandbox, request escalation when running them.

- `scripts/list-skills.py` (prints skills list with installed annotations)
- `scripts/list-skills.py --format json`
- Example (experimental list): `scripts/list-skills.py --path skills/.experimental`
- `scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...]`
- `scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>`
- Example (experimental skill): `scripts/install-skill-from-github.py --repo openai/skills --path skills/.experimental/<skill-name>`
- Recommended trusted-source install:
  `scripts/install-skill-from-github.py --repo <owner>/<repo> --ref <40-char-commit-sha> --path <path/to/skill>`

## Behavior and Options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Installs into `$CODEX_HOME/skills/<skill-name>` (defaults to `~/.codex/skills`).
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Enforces pinned refs by default (`--ref` must be a 40-char commit SHA). Use `--allow-unpinned-ref` only when explicitly approved.
- Stages every install in `<dest>/.quarantine/skill-install-<run-id>` before atomic promotion.
- Writes a rollback journal at `<dest>/.install-journal/skill-installer/<run-id>.jsonl`.
- Writes a provenance manifest at `<dest>/.provenance/skill-installer/<run-id>.json`.
- Options: `--ref <ref>`, `--dest <path>`, `--method auto|download|git`, `--allow-unpinned-ref`, `--provenance-dir <path>`, `--journal-dir <path>`.

## Notes

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- The skills at https://github.com/openai/skills/tree/main/skills/.system are preinstalled, so no need to help users install those. If they ask, just explain this. If they insist, you can download and overwrite.
- Installed annotations come from `$CODEX_HOME/skills`.

## Contract Artifacts

- `references/contract.yaml` defines install-stage ownership, trusted-source requirements, and rollback expectations.
- `references/evals.yaml` defines happy/edge/negative/pressure cases, including prompt-injection and risky-command guard coverage.

## See Also

| Skill | When to use together |
|---|---|
| [[skill-creator]] | Author or revise a skill before attempting to distribute it |
| [[skill-builder]] | Run quality gates and packaging checks on a skill before installation |
| [[codex-plugin-builder]] | Package a contract-valid standalone skill when the deliverable should ship as a plugin instead of a bare install |

**Topic map:** [[agent-ops]]
