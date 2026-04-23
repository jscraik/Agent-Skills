# Scripts Index

Index for repository automation, validation, and maintenance scripts.

## Table of Contents
- [Core workflows](#core-workflows)
- [Validation and quality](#validation-and-quality)
- [Sync and projection](#sync-and-projection)
- [Skill graph and recursive loop](#skill-graph-and-recursive-loop)
- [Setup and environment](#setup-and-environment)

## Core workflows
- `verify-work.sh` - canonical local verification entrypoint
- `codex-preflight.sh` - required preflight checks for path-sensitive work
- `validate_all.sh` - validation bundle with output modes
- `status.sh` - quick repository status helper

## Validation and quality
- `docs_lint.py`
- `lint_openai_skill_format.sh`
- `lint_progressive_disclosure.sh`
- `lint_skill_types.sh`
- `validate_skill_authoring_family.sh`
- `validate_skill_authoring_family_benchmarks.py`
- `validate_projection_integrity.sh`
- `check_path_ownership_boundaries.sh`
  - Guardrails:
    - default local scope checks staged diff only;
    - blocks direct edits to derived runtime/projection surfaces (`.agents/**`, `.agents/skills/**`, `Plugins/cache/**`, `runtime/**`);
    - set `PATH_OWNERSHIP_GUARD_SCOPE=working` for full working-tree checks;
    - set `PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1` only for explicit projection-refresh lanes.
- `projection_integrity.py`
- `check_plugin_skill_shadowing.sh`
- `check_codex_home_skill_overlap.sh`
  - Audits overlap between flat runtime skills (`<codex-home>/skills`) and plugin-cache skills (`<codex-home>/Plugins/cache/...`).
  - Default target: `~/.codex`; use `--codex-home ~/.codex-red` for alternate profiles.
  - Add `--strict --show-overlap` for CI-style fail-fast behavior with explicit overlap names.
  - Use `--remediate-cache-skills` to repair cache plugin-root layout when plugin caches are nested under `local/` or version/hash directories.
- `verify_skill_catalog_freshness.py`
- `verify_recursive_skill_graph_artifacts.py`
- `wiki_lint.py`

## Sync and projection
- `sync_skills.sh`
  - Projects repaired plugin caches into Codex profile homes and, for non-symlinked `~/.codex-*` profiles, creates `Plugins/<plugin>` source mirrors so profile `marketplace.json` entries with `./Plugins/<name>` remain resolvable.
- `sync_skills_sandbox_safe.sh`
- `sync_plugin_factory_family.sh`
- `sync_projection_trees.sh`
- `sync_mcp.py`
- `skill_catalog.py`
- `skill_scan.py`

## Skill graph and recursive loop
- `run_skill_genome_loop.py`
- `bootstrap_recursive_skill_graph_artifacts.py`
- `review_candidates.py`
- `run_recursive_skill_shadow_cycle.sh`
- `human_promote_recursive_run.sh`

## Setup and environment
- `check-environment.sh`
- `setup-git-hooks.js`
- `prepare-worktree.sh`
- `ensure-gh-cli.sh`
- `install_cron.sh`
