---
name: uv-python-project-setup
description: Create and configure Python projects with uv for dependency management, virtual environments, and reproducible workflows. Use when initializing or repairing uv-based Python project setup.
metadata:
  skill-type: runbook
---

# uv Python Project Setup

Fast Python project initialization and dependency management with automatic environment handling.

## When to use

- Starting new Python CLI tools or libraries.
- Migrating from pip/pipenv to modern project management.
- Setting up reproducible development environments.
- Managing complex dependency requirements.

## Required inputs

- Intended project type (`app` or distributable `library`).
- Target Python runtime contract (default repo policy uses Python 3.12 commands).
- Dependency policy (runtime vs development dependencies).
- Execution context (`local dev`, `CI`, or release verification).

## Critical Rules

**Project Type Selection**: Use `--lib` flag for distributable packages

```bash
# WRONG - Library needs src layout
uv init my-package

# RIGHT - Library with proper structure  
uv init --lib my-package
```

**Environment Sync**: Always use `uv run --python 3.12` instead of manual activation

```bash
# WRONG - Manual activation breaks reproducibility
source .venv/bin/activate
python main.py

# RIGHT - Automatic sync and execution
uv run --python 3.12 main.py
```

## Deliverables

- A valid `pyproject.toml` aligned to project type and dependency intent.
- A synchronized `uv.lock` checked into source control.
- Reproducible command set based on `uv run --python 3.12 ...`.
- Explicit validation commands for lint/test/build entrypoints.

## Key Patterns

### Project Initialization

```bash
# CLI tool (default)
uv init my-cli
cd my-cli

# Library with src layout
uv init --lib my-library

# Initialize in existing directory
mkdir existing-project && cd existing-project
uv init
```

### Dependency Management

```bash
# Add with automatic lockfile update
uv add requests
uv add 'flask>=2.0,<3.0'

# Development dependencies
uv add --dev pytest ruff

# Remove and cleanup
uv remove requests

# Upgrade specific package
uv lock --upgrade-package requests
```

### Project Configuration

```toml
# CLI tool pyproject.toml
[project]
name = "my-cli"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["click", "rich"]

[dependency-groups]
dev = ["pytest", "ruff", "mypy"]

# Library pyproject.toml
[project] 
name = "my-lib"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["uv_build>=0.11.3,<0.12"]
build-backend = "uv_build"
```

### Running Commands

```bash
# Execute scripts with auto-sync
uv run --python 3.12 main.py --help
uv run --python 3.12 python -m my_package

# CLI commands from dependencies
uv run --python 3.12 ruff check
uv run --python 3.12 pytest

# Ad-hoc dependencies
uv run --python 3.12 --with rich debug_script.py
```

## Common Mistakes

- **Manual venv activation** — Use `uv run --python 3.12` to ensure environment consistency
- **Skipping lockfile** — Always commit `uv.lock` for reproducible builds  
- **Wrong project type** — Use `--lib` for packages that will be distributed
- **Direct pyproject.toml edits** — Use `uv add/remove` to maintain lockfile sync

## Failure mode

- If project type (`app` vs `library`) is unclear, pause and request explicit confirmation before scaffolding.
- If required Python version differs from repo policy, return partial with the exact mismatch and impact.

## Gotchas

- `uv init` defaults to app-style layout; use `--lib` for package distributions.
- Running tools from manually activated virtualenvs can bypass lockfile sync guarantees.

## See Also

| Skill | When to use |
|---|---|
| [[he-tdd]] | Pair uv-managed environments with behavior-first testing workflows |
| [[verification-before-completion]] | Enforce final verification before declaring setup complete |

**Topic map:** [[agent-ops]]

## Philosophy

- Optimize for clear, verifiable outcomes with the minimum necessary changes.
- Keep guidance deterministic so repeated runs produce consistent decisions.

## Procedure

1. Confirm scope, constraints, and required inputs before edits.
2. Apply focused changes tied directly to the requested outcome.
3. Re-run the highest-signal validations and capture concrete evidence.

## Validation

- Run the relevant local checks for touched files and workflow contracts.
- Fail fast: stop at the first blocking validation failure and report exact evidence.
- Re-run checks after fixes and record residual risk if any remains.

## Constraints

- Redact secrets, tokens, credentials, and sensitive data by default.
- Do not expand scope beyond the request unless explicitly asked.
- Prefer safe, reversible edits over broad refactors.

## Anti-patterns

- Skipping validation after making changes.
- Applying broad refactors to solve narrow issues.
- Assuming behavior without evidence from current checks.
