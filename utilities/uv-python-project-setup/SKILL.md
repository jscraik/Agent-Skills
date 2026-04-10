---
name: uv-python-project-setup
description: "Python project initialization and dependency management with uv. Use when starting new CLI tools or libraries, configuring pyproject.toml, managing virtual environments, or setting up development workflows. Covers project types, dependency commands, and environment synchronization."
---

# uv Python Project Setup

Fast Python project initialization and dependency management with automatic environment handling.

## When to Apply

- Starting new Python CLI tools or libraries
- Migrating from pip/pipenv to modern project management
- Setting up reproducible development environments
- Managing complex dependency requirements

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

## See Also
| Skill | When to use together |
|---|---|
| [[test-driven-development]] | Establish test-first workflows for new Python projects once the uv scaffold is ready |
| [[systematic-debugging]] | Diagnose dependency conflicts, interpreter mismatch, or lockfile drift in uv-managed projects |

**Topic map:** [[utilities]]
