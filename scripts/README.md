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
- `verify_skill_catalog_freshness.py`
- `verify_recursive_skill_graph_artifacts.py`

## Sync and projection
- `sync_skills.sh`
- `sync_skills_sandbox_safe.sh`
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
