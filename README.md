# Agent Skills

This repository is the source of truth for Codex and agent skills.

If you are new here:

1. Start with `/SKILL.md` (skills index).
2. Then read `/docs/index.md` (contributor docs).

## What this repo is for

- Keep one canonical skill library.
- Generate a flat symlink view in `/skills` for tool loaders.
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
# Sync skills and regenerate index
bash scripts/sync_skills.sh

# Run all validations (plans, skill graphs, docs)
bash scripts/validate_all.sh

# Generate architecture diagrams
diagram generate . --output artifacts/diagram.mmd
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

## Skill Genome Loop

Nightly batch process for skill improvement candidates:

```bash
# Run genome loop manually
python3 scripts/run_skill_genome_loop.py

# Review pending candidates
python3 scripts/review_candidates.py --list

# Approve/reject candidates
python3 scripts/review_candidates.py --approve <id>
python3 scripts/review_candidates.py --reject <id>
```

**Controls:**
- `artifacts/skill-graphs/controls/rollout-mode.txt` — `off | observe_only | active`
- `artifacts/skill-graphs/controls/kill-switch.txt` — Emergency stop (file exists = stop)

**Outputs:**
- `artifacts/skill-graphs/telemetry/pending-candidates.jsonl` — Awaiting review
- `artifacts/skill-graphs/telemetry/candidates.jsonl` — Approved candidates
- `logs/genome-loop.log` — Execution logs

**Documentation:** [Skill Genome Loop Runbook](/docs/skill-graphs/runbooks/skill-genome-loop.md)

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
  - `~/.agents/skills`
  - `~/.codex/skills`
  - `~/.gemini/antigravity/skills`
  - `~/.antigravity/skills`

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
python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md
```

3. Run canonical verification:

```bash
bash ~/.codex/scripts/verify-work.sh
```

4. Follow scaffold policy:

- `~/.codex/instructions/agent-first-scaffold-spec.md`
<!-- AGENT-FIRST-WORKFLOW:END -->
