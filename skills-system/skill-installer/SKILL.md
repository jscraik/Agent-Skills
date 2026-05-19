---
name: skill-installer
description: Install Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos).
metadata:
  short-description: Install curated skills from openai/skills or other repos
---

# Skill Installer

Helps install skills. By default these are from https://github.com/openai/skills/tree/main/skills/.curated, but users can also provide other locations. Experimental skills live in https://github.com/openai/skills/tree/main/skills/.experimental and can be installed the same way.

## Agent Skills Kit Overlay

When running inside the Agent Skills Kit repository and `./bin/ask` exists, keep this upstream `.system` skill as the routing entrypoint but use the repo-native installer for writes:

```bash
./bin/ask skills install <github-url> --json --robot
```

- Before installing, inventory existing skills with `./bin/ask skills list --advanced --json` and targeted searches across `Skills/**`, `Plugins/**/skills/**`, and `skills-system/**`.
- Compare the candidate with likely local matches and choose one outcome: `install_new`, `blend_into_existing`, `keep_separate`, `reject_duplicate`, or `needs_human_choice`.
- Install only after the overlap decision is explicit. Blend into an existing canonical skill when the external package mostly adds a missing procedure, helper, example, or stop rule.
- Treat external skills as **External Skill Intake** source proposals, not installable packages. The repo command must return an **Intake Decision** at `data.intake_decision` before writing and must stop on `reject_duplicate` or `needs_human_choice`.
- Default canonical destination: `Skills/github/<skill-name>` under the git source tree.
- Use `--dest <Skills/category>` only for an explicit repo-owned category.
- Do not write directly to `$CODEX_HOME/skills` unless the user explicitly asks for a runtime-only Codex install.
- After canonical install, add or remediate local contract/eval/reference material before promotion, then run the relevant audit/sync/proof commands before claiming runtime visibility.
- Run full release evals before adding a command handle, routing as canonical, blending into an existing skill, or making a **Release-Readiness Claim**. If the candidate is a **Manifest-Backed Candidate**, include Snyk dependency screening; pure `SKILL.md`-first candidates without supported manifests are `not_applicable` for Snyk.
- Create a thin command handle only when direct invocation is justified; keep heavy references, contracts, and evals behind progressive disclosure.
- Read `references/skill-factory/install-flows.md` when you need the local install flow, output wording, or destination rules.

Use the helper scripts based on the task:
- List skills when the user asks what is available, or if the user uses this skill without specifying what to do. Default listing is `.curated`, but you can pass `--path skills/.experimental` when they ask about experimental skills.
- Install from the curated list when the user provides a skill name.
- Install from another repo when the user provides a GitHub repo/path (including private repos).

Outside Agent Skills Kit, install skills with the helper scripts.

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

## Behavior and Options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Installs into `$CODEX_HOME/skills/<skill-name>` (defaults to `~/.codex/skills`).
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--method auto|download|git`.

## Notes

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- The skills at https://github.com/openai/skills/tree/main/skills/.system are preinstalled, so no need to help users install those. If they ask, just explain this. If they insist, you can download and overwrite.
- Installed annotations come from `$CODEX_HOME/skills`.
