---
name: skill-installer
description: "Plan and install skills into a Codex skills directory from a curated list or repo. Use when a user asks to list or install skills."
---

# Skill Installer

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Philosophy
- Prefer curated sources; verify before installing.
- Minimize changes and avoid overwriting without consent.
- Keep installs reproducible and auditable.

## Guiding questions
- What is the exact skill source (curated vs repo path)?
- Why is this skill needed (new capability vs update)?
- Is overwrite permitted if the skill exists?
- How will we verify installation success?

## When to use
- When the user asks to list installable skills.
- When the user asks to install a curated skill by name.
- When the user provides a GitHub repo/path for skill installation.

## Inputs
- Skill source (curated list, repo URL, or repo/path).
- Destination path or `AGENT_SKILLS_HOME`/`CODEX_HOME` override.
- User confirmation for overwrites or updates.

## Outputs
- Installed skill directory under a category folder (e.g., `~/dev/agent-skills/utilities/<skill-name>`) or an override path.
- A summary of what was installed and from where.
- A reminder to restart Codex to pick up new skills.

## Constraints / Safety
- Redact secrets/PII by default.
- Do not overwrite existing skills without explicit consent.
- Use network access only when required; request escalation in restricted sandboxes.
- Avoid installing from untrusted or ambiguous sources.

Helps install skills. By default these are from https://github.com/openai/skills/tree/main/skills/.curated, but users can also provide other locations.

Use the helper scripts based on the task:
- List curated skills when the user asks what is available, or if the user uses this skill without specifying what to do.
- Install from the curated list when the user provides a skill name.
- Install from another repo when the user provides a GitHub repo/path (including private repos).

Install skills with the helper scripts.

## Communication

When listing curated skills, output approximately as follows, depending on the context of the user's request:
"""
Skills from {repo}:
1. skill-1
2. skill-2 (already installed)
3. ...
Which ones would you like installed?
"""

After installing a skill, tell the user: "Restart Codex to pick up new skills."

## Variation rules
- Vary install method by auth context (download vs git).
- Vary output detail by user intent (listing vs install vs update).
- Prefer `--dry-run` or listing when intent is unclear.
- Use different verification depth for updates vs first installs.

## Empowerment principles
- Empower users to confirm overwrite decisions.
- Empower reviewers with a clear source + ref summary.
- Empower maintainers with a rollback note (remove installed folder).

## Anti-patterns to avoid
- Installing from an unverified or ambiguous source.
- Overwriting existing skills without explicit consent.
- Skipping the restart reminder after install.

## Scripts

All of these scripts use network, so when running in the sandbox, request escalation when running them.

- `scripts/list-curated-skills.py` (prints curated list with installed annotations)
- `scripts/list-curated-skills.py --format json`
- `scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...] --category <category>`
- `scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path> --category <category>`

## Behavior and Options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Requires a category when `--dest` is not provided.
- Installs into `~/dev/agent-skills/<category>/<skill-name>` by default.
- Overrides: `AGENT_SKILLS_HOME`, then `CODEX_HOME`, then `--dest`.
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--category <category>`, `--method auto|download|git`.

## Notes

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- The skills at https://github.com/openai/skills/tree/main/skills/.system are preinstalled, so no need to help users install those. If they ask, just explain this. If they insist, you can download and overwrite.
- Installed annotations come from the destination folder (category or overrides).

## Example prompts
- "List the curated skills I can install."
- "Install the `frontend-design` skill from the curated list."
- "Install a skill from this GitHub repo path."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
