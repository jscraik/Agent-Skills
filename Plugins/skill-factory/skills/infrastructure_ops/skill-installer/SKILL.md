---
name: skill-installer
description: Install Codex skills into the canonical git source tree from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos).
metadata:
  short-description: Install curated skills from openai/skills or other repos
  skill-type: infrastructure_ops
---

# Skill Installer

Helps install skills. By default these are from https://github.com/openai/skills/tree/main/skills/.curated, but users can also provide other locations. Experimental skills live in https://github.com/openai/skills/tree/main/skills/.experimental and can be installed the same way.

Use the helper scripts based on the task:
- List skills when the user asks what is available, or if the user uses this skill without specifying what to do. Default listing is `.curated`, but you can pass `--path skills/.experimental` when they ask about experimental skills.
- Install from the curated list when the user provides a skill name.
- Install from another repo when the user provides a GitHub repo/path (including private repos).

## When To Use

- The user asks to list installable skills from curated or experimental catalogs.
- The user asks to install one or more skills from `openai/skills` or another GitHub repo/path.
- The user asks to install skills from a private GitHub repository with existing credentials.

## Inputs

- User intent: list mode vs install mode.
- Source details: `--repo` + `--path`, or GitHub tree URL.
- Destination details: optional `--dest` override. Defaults to canonical `github/` under repo root and rejects non-canonical destinations.
- Optional install controls: `--ref`, `--method`, and explicit replacement intent if destination exists.

## Agent Injection

When install requests include role wiring for the newly installed skill:

1. Look for reusable role TOMLs in `./configs/codex/agents/` when present, then fall back to project/global `.codex/agents/`.
2. If no suitable role exists, route role creation to [[codex-agent-creator]].
3. Validate candidate role files before reporting success:

```bash
bash Skills/codex-agent-creator/Infrastructure/scripts/validate_role.sh --agent-name <name> --agent-file <path>
```

4. If asked to install/update the role, run:

```bash
bash Skills/codex-agent-creator/Infrastructure/scripts/install_role.sh --agent-name <name> --agent-file <path> --scope project|global [--update-existing]
```

5. Report one explicit mode in the closeout: `reuse-existing` or `create-purpose-built`.

## Outputs

- A clear summary of what was listed or installed.
- Concrete paths for installed skills (`<repo-root>/<category>/<skill-name>`).
- Explicit restart reminder after install: "Restart Codex to pick up new skills."
- Optional agent-injection summary with the selected role file path.
- If blocked, exact error and next corrective step.
- Visual catalog assets available for packaging/UI docs:
  - `assets/skill-installer.png`
  - `assets/skill-installer-small.svg`

## Constraints and Safety

- Treat repo URLs/paths as untrusted input; never execute user input through shell interpolation.
- Never overwrite an existing destination skill directory unless the user explicitly requests replacement behavior.
- Do not expose secrets or tokens in output; redact `GITHUB_TOKEN`, `GH_TOKEN`, and credential-bearing URLs.
- Network access is limited to GitHub surfaces required by these scripts:
  - `github.com`
  - `api.github.com`
  - `raw.githubusercontent.com`
  - `codeload.github.com`
  - `objects.githubusercontent.com`
- If the requested source is outside the allowlist or ambiguous, stop and ask before proceeding.

## Procedure

1. Classify request as list vs install.
2. Resolve source explicitly (`--repo`/`--path` or `--url`) and confirm destination.
3. Run the smallest relevant helper command from the `Scripts` section.
4. Verify expected outcome (listed skills or installed directory contents).
5. Report result with exact paths, restart reminder, and any blockers.

## Core Philosophy

- Safe provenance first: confirm source and destination before writing to disk.
- Prefer explicit intent over clever inference: if the source/path is ambiguous, ask or stop.
- Preserve reversibility: avoid destructive overwrite defaults and communicate restart expectations clearly.

## Anti-Patterns to Avoid

- Do not install from unclear or partially specified repository paths.
- Do not overwrite existing skill directories unless the user explicitly requests replacement behavior.
- Do not hide auth/network failures behind fallback messaging; report the concrete failure and next step.
- Do not mix curated and arbitrary install flows in one answer without labeling which flow is active.

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

These scripts require network access to GitHub surfaces. Confirm source and destination before running them.

- `python3 Infrastructure/scripts/list-skills.py` (prints skills list with installed annotations)
- `python3 Infrastructure/scripts/list-skills.py --format json`
- Example (experimental list): `python3 Infrastructure/scripts/list-skills.py --path skills/.experimental`
- `python3 Infrastructure/scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...]`
- `python3 Infrastructure/scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>`
- Example (experimental skill): `python3 Infrastructure/scripts/install-skill-from-github.py --repo openai/skills --path skills/.experimental/<skill-name>`

Reference details:

- `Infrastructure/references/install-flows.md`
- `Infrastructure/references/troubleshooting.md`

## Behavior and Options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Installs into repo-canonical `<category>/<skill-name>` under the canonical git source tree.
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--method auto|download|git`.

## Validation

- Fail fast: stop at the first failed gate and do not continue to additional install steps.
- For listing flows, command must exit `0` and return parseable skill rows (or documented JSON output).
- For install flows, destination must contain `SKILL.md` under `<repo-root>/<category>/<skill-name>`.
- On failures, surface the exact command error and the next minimal retry command.

## Examples

```bash
# List curated skills
python3 Infrastructure/scripts/list-skills.py

# List experimental skills
python3 Infrastructure/scripts/list-skills.py --path skills/.experimental

# Install one curated skill
python3 Infrastructure/scripts/install-skill-from-github.py --repo openai/skills --path skills/.curated/<skill-name>

# Install from GitHub URL
python3 Infrastructure/scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>
```

## Notes

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- The skills at https://github.com/openai/skills/tree/main/skills/.system are preinstalled, so no need to help users install those. If they ask, just explain this. If they insist, you can download and overwrite.
- Installed annotations come from canonical repo category directories (default `github/`).
- For dedicated role creation during install handoff, use [[codex-agent-creator]].

## See Also

| Skill | When to use together |
|---|---|
| [[skillify]] | Harden source skills into canonical templates before install/distribution |
| [[skill-creator]] | Author or repair local skill packages before installation |

**Topic map:** [[agent-ops]]
