---
source: https://docs.coderabbit.ai/tools/blinter
---

# Blinter

Blinter is a linter for Windows batch files that provides comprehensive static analysis to identify syntax errors, security vulnerabilities, performance issues, and style problems.

## Files

Blinter will run on files with the following extensions:

- `.bat`
- `.cmd`

## Configuration

Blinter supports the following config files:

- `blinter.ini`

CodeRabbit will use the default settings if no config file is found.

## When we skip Blinter

CodeRabbit will skip running Blinter when:

- No batch files are found in the pull request.
- Blinter is already running in GitHub workflows.

## Features

Blinter provides comprehensive static analysis with:

- **159 Built-in Rules** across 5 severity levels:
  - **Error Level (E001-E999)**: Critical syntax errors that prevent execution
  - **Warning Level (W001-W999)**: Potential runtime issues and bad practices
  - **Style Level (S001-S999)**: Code formatting and readability improvements
  - **Security Level (SEC001+)**: Security vulnerabilities and dangerous operations
  - **Performance Level (P001-P999)**: Optimization opportunities and efficiency improvements

## Profile behavior

- Style findings are suppressed in all profiles.
- In non-assertive profiles, warning-level findings are also suppressed.

## Links

- Blinter GitHub Repository
