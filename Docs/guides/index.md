# Guides

Task-oriented "how to" docs belong here. Keep each page focused on one job to be done.

Guides should list prerequisites up front, show the exact command(s) to run, and say what "success" looks like (expected output or files changed).

Prefer numbered steps, and add a short Troubleshooting section for the most common failure modes.

Good guide topics for this repo:

- Add a new canonical skill under `Skills/<topic>/<skill>/SKILL.md` or `Plugins/<plugin>/skills/**/SKILL.md`
- Run `python3 bin/ask skills sync --scope workspace --projection rooted` and confirm generated projection surfaces update
- Validate generated command handles with `python3 bin/ask skills handles --check --json`
- Validate a skill before you open a PR
- Apply governance scope defaults: [hook-governance-scope-defaults.md](/Docs/guides/hook-governance-scope-defaults.md)
- Run the recursive skill loop MVP: [recursive-skill-loop.md](/Docs/guides/recursive-skill-loop.md)
- Run the human promotion gate: [recursive-promotion-gate.md](/Docs/guides/recursive-promotion-gate.md)
- Cut a release (if/when the repo starts versioning skills)

- Back to [Docs index](/Docs)
