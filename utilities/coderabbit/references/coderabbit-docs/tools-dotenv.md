---
source: https://docs.coderabbit.ai/tools/dotenv
---

# Dotenv Linter

## Files
Dotenv Linter will run on files with the following patterns:

- `**/.env`

- `**/.env.*`

We will not run against files that do not start with `.env` (e.g., `test.env`). However `.env.dev` or `.env.local` is fine.

Dotenv Linter does not require configuration to run and automatically anlysises `.env` files. If no configuration file is found, it will use default settings.
## When we skip dotenv-linter
CodeRabbit will skip running dotenv-linter when:

- No `.env` files are found in the pull request.

- dotenv-linter is already running in GitHub workflows.

## Notes

- All dotenv-linter issues are treated as warnings (dotenv-linter does not distinguish severity levels).

## Features
Dotenv Linter can detect:

- Key duplication

- Missing values

- Incorrect formatting

- Invalid characters

- And many more issues

## Links

- Dotenv Linter GitHub Repository

detektember-template-lint
