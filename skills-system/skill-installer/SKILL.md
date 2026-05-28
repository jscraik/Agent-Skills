---
name: skill-installer
description: "Use when listing or installing Codex skills from curated sources, GitHub repo paths, private repos, or local package locations."
metadata:
  short-description: Install curated skills from openai/skills or other repos
---

# Skill Installer

Install the smallest requested skill set, prove where it landed, and keep
source, destination, and runtime visibility separate. By default these are from
https://github.com/openai/skills/tree/main/skills/.curated, but users can also
provide other locations. Experimental skills live in
https://github.com/openai/skills/tree/main/skills/.experimental and can be
installed the same way.

## Philosophy

Treat installation as a provenance and visibility workflow, not a file copy.
List before installing when the user has not named a skill, install only the
named package, and report validation as pass, fail, or blocked with the exact
source and destination.

Adapt the route to the source: curated names, experimental names, public GitHub
paths, and private repo paths need different commands and blocker language.
Keep the install surface narrow even when the user mentions several catalogs.

## When To Use

- The user asks what curated or experimental skills are available.
- The user names a curated skill to install.
- The user provides a GitHub repo, tree URL, or repo path for a skill package.
- The user asks whether an installed skill is already present locally.

Use the helper scripts based on the task:
- List skills when the user asks what is available, or if the user uses this skill without specifying what to do. Default listing is `.curated`, but you can pass `--path skills/.experimental` when they ask about experimental skills.
- Install from the curated list when the user provides a skill name.
- Install from another repo when the user provides a GitHub repo/path (including private repos).

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

## Examples

User: "What skills can I install from the curated catalog?"
Action: run `scripts/list-skills.py --format json`, then summarize available
skills and installed annotations.

User: "Install the GitHub skill at this repo path."
Action: run `scripts/install-skill-from-github.py --url <url>`, then report
source, destination, validation, and restart guidance.

## Behavior and Options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Installs into `$CODEX_HOME/skills/<skill-name>` (defaults to `~/.codex/skills`).
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--method auto|download|git`.

## SDK Package Checks

When installing into an SDK-aware repository, preserve and validate the skill
package contract after download:

1. Confirm the package has `SKILL.md` with `name` and `description`.
2. Preserve `agents/openai.yaml` when present; do not move SDK contract fields
   into it.
3. Preserve `references/contract.yaml` when present. If the repo enforces
   strict SDK readiness and this file is missing, classify the install as
   `blocked_validation` rather than silently accepting the package.
4. Run `./bin/ask skills package <installed-path-or-handle> --json --robot`
   when available.
5. Treat `package_contract.sdk_contract.required_fields.missing` as blocking
   for strict SDK installation. Required SDK fields are purpose, inputs,
   outputs, permission profile, evals, and evidence policy.
6. Report local `~/.agents/` OTEL, session, or observability providers only as
   evidence enrichment. They do not replace install artifacts, evals, or
   package validators.

## Notes

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- The skills at https://github.com/openai/skills/tree/main/skills/.system are preinstalled, so no need to help users install those. If they ask, just explain this. If they insist, you can download and overwrite.
- Installed annotations come from `$CODEX_HOME/skills`.

## References

- Base contract: `references/contract.yaml`
- Eval cases: `references/evals.yaml`
- Skill Factory install flows: `references/skill-factory/install-flows.md`
- Skill Factory troubleshooting: `references/skill-factory/troubleshooting.md`

## Anti-Patterns

- Do not install over an existing destination without explicit approval.
- Do not treat a skill source edit, sync, or publish request as installation.
- Do not print credential-bearing URLs, tokens, or private repo contents in output.
- Do not claim runtime availability without checking the installed destination.
