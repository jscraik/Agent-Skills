---
source: https://docs.coderabbit.ai/tools/dotenv
---

# Dotenv Linter

## Files

Dotenv Linter runs on these file patterns:

- `**/.env`
- `**/.env.*`

Files that do not start with `.env` (for example `test.env`) are ignored.

## Configuration

Dotenv Linter does not require a configuration file. It analyzes supported `.env` files with default rules.

## When CodeRabbit skips dotenv-linter

CodeRabbit skips dotenv-linter when:

- No `.env` files are present in the pull request.
- dotenv-linter is already running in GitHub workflows.

## Notes

- All dotenv-linter findings are treated as warnings (dotenv-linter does not expose severity levels).

## Features

Dotenv Linter can detect:

- Duplicate keys
- Missing values
- Formatting issues
- Invalid characters

## Links

- [Dotenv Linter GitHub Repository](https://github.com/dotenv-linter/dotenv-linter)
