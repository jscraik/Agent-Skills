# Agent Skills

<!-- Skill count: 142 | Genome: active -->
**The source of truth for Codex and agent skills.**

If you are new here:

1. Start with `/SKILL.md` (skills index).
2. Then read `/docs/index.md` (contributor docs).

## What this repo is for

- Keep one canonical skill library.
- Generate a flat symlink view in `/.agents/skills` for tool loaders.
- Maintain clear documentation contracts for contributors.
- Run nightly skill improvement analysis via the Skill Genome Loop.

## Skill Genome Loop

The Skill Genome Loop analyzes skill usage patterns and identifies improvement candidates through a human-gated review process:

```bash
# Run the genome loop
python3 scripts/run_skill_genome_loop.py

# Review pending candidates
python3 scripts/review_candidates.py --list

# Approve a candidate
python3 scripts/review_candidates.py --approve <candidate_id>
```

**Key features:**

- Nightly cron job (4:00 AM UTC) for automated analysis
- Human review gate for all improvement candidates
- Fail-closed controls (kill-switch, rollback, rollout-mode)
- Confidence gating (composite_score >= 0.82, window count >= 2)

**See also:** [Skill Genome Loop Runbook](/docs/skill-graphs/runbooks/skill-genome-loop.md)

## Architecture Diagrams

Generate architecture diagrams using `@brainwav/diagram`:

```bash
# Install globally
npm i -g @brainwav/diagram

# Analyze codebase
diagram analyze .

# Generate diagram
diagram generate . --output diagram.mmd
```

Configuration file: `.diagramrc` (excludes `node_modules`, test files, build artifacts)

## Quickstart

Run these commands from the repository root:

```bash
# Show status overview
just status

# Run all validations
just validate

# Diagnose skills
just diagnose

# Run CI checks locally
just ci-local
```

### Using Just (Task Runner)

This project uses `just` for common tasks. Available commands:

```bash
just --list          # Show all commands
just status          # Quick status overview
just validate        # Run all validation
just diagnose        # Diagnose all skills
just genome-loop     # Run genome loop (dry-run)
just lint             # Run pre-commit hooks
```

### Creating New Skills

Use the skill template when creating new skills:

```bash
cp templates/SKILL.md.template <category>/<skill-name>/SKILL.md
```

### Validation

The consolidated validation script runs all checks:

```bash
bash scripts/validate_all.sh
```

This validates:

- Plan task graphs (dependency checking)
- Skill graph artifact compliance
- Documentation structure and links

## Verify your setup

You should see:

- `scripts/sync_skills.sh` completes without errors and updates `/SKILL.md`.
- `docs_lint.py` reports `errors=0` for docs structure and links.

If either check fails, use the troubleshooting section below.

## Repository layout

```text
~/dev/agent-skills/
├── auth/          # Authentication-focused skills
├── backend/       # Backend, architecture, and CLI skills
├── frontend/      # Frontend and UI skills
│   ├── graphics/  # Image/video generation (imagegen, sora, threejs, etc.)
│   ├── tools/     # Browser and design tooling (agentation, figma, stitch-*)
│   ├── ui/        # UI component and motion skills (baseline-ui, remotion, shadcn, etc.)
│   └── website/   # Web publishing skills (fixing-accessibility, fixing-metadata)
├── github/        # GitHub and DevOps workflow skills
├── interview/     # Interview workflows and kernels
├── ops/           # Operational and deployment skills
├── personas/      # Persona-style response skills
├── product/       # Product specs, docs, planning
│   ├── content/   # Content production skills
│   ├── docs/      # Documentation skills
│   ├── domain/    # Domain-specific skills
│   ├── ops/       # Product ops and decision skills
│   ├── security/  # Security and compliance skills
│   ├── specs/     # Specification skills
│   └── strategy/  # Strategy and ideation skills
├── utilities/     # General-purpose utilities and helpers
├── scripts/       # Repo-level helper scripts
├── references/    # Shared reference contracts
├── templates/     # Shared contract/eval templates
├── reports/       # Generated scan summaries and data snapshots
├── .agents/       # Repo-local Codex skills root
├── .agents/skills/ # Flat symlink directory (tooling entrypoint)
├── skills-antigravity/ # Antigravity-compatible flat symlink projection
├── skills -> .agents/skills  # Legacy compatibility symlink
├── skills-system/ # Bundled/system skills (kept out of flat view)
└── SKILL.md       # Human-readable skills index (auto-generated)
```

### Categorization rule of thumb

- Put each active skill under the closest domain folder above.
- Keep `scripts/` and `references/` inside each skill folder when they are skill-specific.
- Keep root `scripts/`, `references/`, and `templates/` for shared repo-wide tooling only.

## How skills are loaded

- Each skill lives in a category folder and includes a `SKILL.md` file.
- `/.agents/skills` contains symlinks so tools can load one flat list.
- `skills-system/` stores bundled/system skills and is excluded from the flat view.
- `scripts/sync_skills.sh` refreshes symlinks and regenerates `/SKILL.md`.
- The sync script links `/.agents/skills` into:
  - `~/.agents/skills`
  - `~/.codex/skills`
  - `~/.gemini/antigravity/skills`
  - `~/.gemini/skills`
  - `~/.antigravity/skills`

Run this command to verify all skill entrypoints at once:

```bash
bash scripts/sync_skills.sh
for d in ~/.agents/skills ~/.claude/skills ~/.gemini/antigravity/skills ~/.gemini/skills; do
  echo "== $d =="
  fd --max-depth 1 --type l . "$d" | wc -l
done
python3 scripts/diagnose_skill.py --all
```

## Deprecations (Wave 1)

Wave 1 deprecated aliases were retired early and removed from the repository on **2026-02-24**.

Canonical replacements:

- `product-spec` with modes: `full_pipeline`, `clarify_prd`, `ux_only`, `api_spec`, `arch_spec`, `testplan`
- `tech-spec` with modes: `data_spec`, `migration_plan`, `ops_spec`, `performance_plan`
- `figma` with modes: `setup`, `extract_context`, `implement_design`, `troubleshoot`

## Docs governance

- Contributor contract: `/CONTRIBUTING.md`
- Docs policy config: `/docs-policy.json`
- CI workflow: `/.github/workflows/docs-governance.yml`

Local check:

```bash
python3 scripts/docs_lint.py --mode warn --config docs-policy.json
```

## Troubleshooting

### Skill not loading in Codex or Claude Code

Run the diagnostic tool:

```bash
python3 scripts/diagnose_skill.py <skill-name>
# Or check all skills:
python3 scripts/diagnose_skill.py --all
```

Common causes:

- **Nested `.git` directory**: Skills with their own `.git` folder break discovery. Remove it: `rm -rf .agents/skills/<name>/.git`
- **Missing symlink**: Re-run `bash scripts/sync_skills.sh`
- **Invalid SKILL.md**: Ensure YAML frontmatter has `name:` and `description:`

### `docs_lint.py` reports link errors

- Ensure internal docs links start with `/` (for example, `/docs/deployment`).
- Remove trailing slashes from internal docs links.
- Re-run `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`.

### `SKILL.md` did not update

- Re-run `bash scripts/sync_skills.sh`.
- Confirm the target skill folder contains `SKILL.md`.

### Symlink targets are missing

- Re-run `bash scripts/sync_skills.sh`.
- Check write permissions for `~/.agents/skills`.

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
- Last updated: 2026-03-07.

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
python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md
```

1. Run canonical verification:

```bash
bash ~/.codex/scripts/verify-work.sh
```

1. Follow scaffold policy:

- `~/.codex/instructions/agent-first-scaffold-spec.md`
<!-- AGENT-FIRST-WORKFLOW:END -->
