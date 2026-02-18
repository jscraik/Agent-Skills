# Agent Skills

This repository is the source of truth for Codex and agent skills.

If you are new here:

1. Start with `/SKILL.md` (skills index).
2. Then read `/docs/index.md` (contributor docs).

## What this repo is for

- Keep one canonical skill library.
- Generate a flat symlink view in `/skills` for tool loaders.
- Maintain clear documentation contracts for contributors.

## Quickstart

Run these commands from the repository root:

```bash
bash scripts/sync_skills.sh
python3 scripts/docs_lint.py --mode warn --config docs-policy.json
```

## Verify your setup

You should see:

- `scripts/sync_skills.sh` completes without errors and updates `/SKILL.md`.
- `docs_lint.py` reports `errors=0` for docs structure and links.

If either check fails, use the troubleshooting section below.

## Repository layout

```text
~/dev/agent-skills/
├── auth/          # Authentication-focused skills
├── personas/      # Persona-style response skills
├── github/        # GitHub/DevOps workflows
├── frontend/      # Frontend/UI patterns
├── backend/       # Backend/Architecture/CLI
├── interview/     # Interview workflows and kernels
├── product/       # Product specs, docs, planning
├── design/        # PRD/spec templates and design references
├── utilities/     # Utilities and helpers
├── scripts/       # Repo-level helper scripts
├── references/    # Shared reference contracts
├── templates/     # Shared contract/eval templates
├── reports/       # Generated scan summaries and data snapshots
├── skills/        # Flat symlink directory (tooling entrypoint)
├── skills-system/ # Bundled/system skills (kept out of flat view)
└── SKILL.md       # Human-readable skills index
```

### Categorization rule of thumb

- Put each active skill under the closest domain folder above.
- Keep `scripts/` and `references/` inside each skill folder when they are skill-specific.
- Keep root `scripts/`, `references/`, and `templates/` for shared repo-wide tooling only.

## How skills are loaded

- Each skill lives in a category folder and includes a `SKILL.md` file.
- `/skills` contains symlinks so tools can load one flat list.
- `skills-system/` stores bundled/system skills and is excluded from the flat view.
- `scripts/sync_skills.sh` refreshes symlinks and regenerates `/SKILL.md`.
- The sync script links `/skills` into:
  - `~/.claude/skills`
  - `~/.agents/skills`
  - `~/.gemini/antigravity/skills`

## Deprecations (Wave 1)

Canonical skills for the first consolidation wave:

- `product-spec` with modes: `full_pipeline`, `clarify_prd`, `ux_only`, `api_spec`, `arch_spec`, `testplan`
- `tech-spec` with modes: `data_spec`, `migration_plan`, `ops_spec`, `performance_plan`
- `figma` with modes: `setup`, `extract_context`, `implement_design`, `troubleshoot`

Backward-compatible aliases remain active during the deprecation window (target review date: **2026-04-12**):

- PRD aliases: `prd-clarifier`, `prd-to-api`, `prd-to-arch`, `prd-to-testplan`, `prd-to-ux`
- Tech aliases: `tech-to-data`, `tech-to-migration`, `tech-to-ops`, `tech-to-performance`
- Figma alias: `figma-implement-design`

## Docs governance

- Contributor contract: `/CONTRIBUTING.md`
- Docs policy config: `/docs-policy.json`
- CI workflow: `/.github/workflows/docs-governance.yml`

Local check:

```bash
python3 scripts/docs_lint.py --mode warn --config docs-policy.json
```

## Troubleshooting

### `docs_lint.py` reports link errors

- Ensure internal docs links start with `/` (for example, `/docs/deployment`).
- Remove trailing slashes from internal docs links.
- Re-run `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`.

### `SKILL.md` did not update

- Re-run `bash scripts/sync_skills.sh`.
- Confirm the target skill folder contains `SKILL.md`.

### Symlink targets are missing

- Re-run `bash scripts/sync_skills.sh`.
- Check write permissions for `~/.claude/skills`, `~/.agents/skills`, and `~/.gemini/antigravity/skills`.

## Support and security

- Questions and usage help: `/SUPPORT.md`
- Security vulnerability reporting: `/SECURITY.md`
- Contribution process: `/CONTRIBUTING.md`
- Code of conduct: `/CODE_OF_CONDUCT.md`

## Documentation requirements

- Audience: contributors maintaining or adding skills.
- Scope: repo structure, skill lifecycle, docs governance, and contributor workflows.
- Non-scope: product-level feature specs and runtime API design docs.
- Owner: repository maintainers (`@jscraik`).
- Review cadence: every 90 days or after major workflow changes.
- Last updated: 2026-02-18.

## Community health files

- `/README.md`
- `/LICENSE`
- `/CONTRIBUTING.md`
- `/CODE_OF_CONDUCT.md`
- `/SECURITY.md`
- `/SUPPORT.md`
- `/.github/ISSUE_TEMPLATE`
- `/.github/PULL_REQUEST_TEMPLATE.md`
- `/CODEOWNERS`

Release notes policy:

- This repository is not currently published with semantic version tags.
- Use pull requests and commit history as the source of change tracking.

## License

See `/LICENSE`.

<!-- AGENT-FIRST-WORKFLOW:START -->
## Agent-first workflow

1. Create or update an implementation plan using `.agent/PLANS.md`.
2. Validate the plan graph:

```bash
python3 /Users/jamiecraik/.codex/scripts/plan-graph-lint.py .agent/PLANS.md
```

3. Run canonical verification:

```bash
/Users/jamiecraik/.codex/scripts/verify-work.sh
```

4. Follow scaffold policy:

- `/Users/jamiecraik/.codex/instructions/agent-first-scaffold-spec.md`
<!-- AGENT-FIRST-WORKFLOW:END -->
