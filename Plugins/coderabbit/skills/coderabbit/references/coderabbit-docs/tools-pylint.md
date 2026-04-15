---
source: https://docs.coderabbit.ai/tools/pylint
---

# Pylint

## Supported Files
Pylint will run on files with the following extensions:

- `*.py`

- `.ipynb` (using nbQA)

## Configuration
Pylint supports the following config files:

- `.pylintrc`

- `pylintrc`

- `.pylintrc.toml`

- `pylintrc.toml`

CodeRabbit will not run Pylint if no config file is found.
## What CodeRabbit runs
Pylint runs per-file in a sandbox. We validate the config before execution.
## Security policy and restrictions

- We skip if the config declares `init-hook`, which can execute arbitrary Python code at startup.

## When we skip Pylint
CodeRabbit will skip running Pylint when:

- No config file is found.

- The config contains `init-hook`.

- Pylint is already running in GitHub workflows.

- Config parsing fails or appears unsafe.

## Profile behavior
In **Chill** mode, Pylint filters out:

- Warnings and conventions

- `E0401` (Unable to import)

- `C0301` (Line too long)

In **Assertive** mode, all findings are reported.
## Features
Pylint can detect many issues such as:

- Coding standard violations (PEP8)

- Unused variables and imports

- Undefined variables

- Code smells and refactoring suggestions

- Error-prone constructs

- And many more

## Links

- Pylint Official Website

- Pylint GitHub Repository

- Pylint Documentation

- Message Control

- nbQA Documentation
