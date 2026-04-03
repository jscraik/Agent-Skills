---
source: https://docs.coderabbit.ai/tools/prisma-lint
---

# Prisma Lint

## Files
Prisma Lint will run on files with the following extensions:

- `.prisma`

## Configuration
Prisma Lint supports the following config files:

- `.prismalintrc.json`

- `.prismalintrc`

- `.prismalintrc.js`

- `.prismalintrc.yaml`

- `.prismalintrc.yml`

- `prismalint.config.js`

CodeRabbit runs Prisma Lint against changed `.prisma` files in the pull request.
## When we skip Prisma Lint
CodeRabbit will skip running Prisma Lint when:

- No Prisma schema files are found in the pull request.

- No config file is found.

- Prisma Lint is already running in GitHub workflows.

## Rule Configuration
Rules can be configured in your `.prismalintrc.json` file. See the Prisma Lint Rules Documentation for more information on the available rules and their configuration options.
## Links

- Prisma Lint GitHub Repository

- Prisma Lint Rules Documentation
