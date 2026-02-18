# Agent Skills

This repository is the source of truth for Codex/agent skills.

If you are new here: start with the skills index in `/SKILL.md`, then use `/docs/index.md` for contributor docs.

## Quick commands

- Sync symlinks and regenerate the skills index:

```bash
bash scripts/sync_skills.sh
```

- Lint docs links and docs structure (warn mode):

```bash
python3 scripts/docs_lint.py --mode warn --config docs-policy.json
```

## Repository Layout

```
~/dev/agent-skills/
├── github/       # GitHub/DevOps workflows
├── frontend/     # Frontend/UI patterns
├── backend/      # Backend/Architecture/CLI
├── interview/    # Interview workflows and kernels
├── product/      # Product specs, docs, planning
├── design/       # PRD/spec templates and design-oriented references
├── utilities/    # Utilities and helpers
├── skills/       # Flat symlink directory (tooling entrypoint)
├── skills-system/ # Bundled/system skills (kept out of flat view)
└── SKILL.md      # Human-readable skills index
```

## How It Works

- Each skill lives in a category folder and includes its own `SKILL.md` (with YAML frontmatter).
- The `skills/` directory contains symlinks so tools can load a flat list.
- `skills-system/` stores bundled/system skills and is excluded from the flat view.
- `scripts/sync_skills.sh` updates symlinks and regenerates `/SKILL.md` (it prefers `metadata.short-description` when present).
- The sync script also links `skills/` into `~/.claude/skills`, `~/.agents/skills`, `~/.gemini/antigravity/skills`, and `~/.gemini/skills`.

## Deprecations (Wave 1)

Canonical skills for the first consolidation wave:

- `product-spec` now includes focused modes: `full_pipeline`, `clarify_prd`, `ux_only`, `api_spec`, `arch_spec`, `testplan`.
- `tech-spec` is the canonical technical transformation skill with modes: `data_spec`, `migration_plan`, `ops_spec`, `performance_plan`.
- `figma` is the canonical Figma skill with modes: `setup`, `extract_context`, `implement_design`, `troubleshoot`.

Backward-compatible aliases remain active during deprecation window (target review date: **2026-04-12**):

- PRD aliases: `prd-clarifier`, `prd-to-api`, `prd-to-arch`, `prd-to-testplan`, `prd-to-ux`
- Tech aliases: `tech-to-data`, `tech-to-migration`, `tech-to-ops`, `tech-to-performance`
- Figma alias: `figma-implement-design`

## Categories and Skills

See `SKILL.md` for the full index with descriptions.

## Docs governance

- Contributor docs contract: `CONTRIBUTING.md`
- Policy config: `docs-policy.json`
- Local lint command:

```bash
python3 scripts/docs_lint.py --mode warn --config docs-policy.json
```

- CI workflow: `.github/workflows/docs-governance.yml`

<!-- AGENT-FIRST-WORKFLOW:START -->
## Agent-first workflow

1. Create/update implementation plan using `.agent/PLANS.md` contract.
2. Validate plan graph:

```bash
python3 /Users/jamiecraik/.codex/scripts/plan-graph-lint.py .agent/PLANS.md
```

3. Run canonical verification:

```bash
/Users/jamiecraik/.codex/scripts/verify-work.sh
```

4. Follow global scaffold policy:

- `/Users/jamiecraik/.codex/instructions/agent-first-scaffold-spec.md`
<!-- AGENT-FIRST-WORKFLOW:END -->
