---
source: https://docs.coderabbit.ai/tools/phpstan
---

# PHPStan

## Files
PHPStan will run on files with the following extensions:

- `.php`

## Configuration
PHPStan supports the following config files:

- `phpstan.neon`

- `phpstan.neon.dist`

- `phpstan.dist.neon`

CodeRabbit will not run PHPStan if no config file is found.
## What CodeRabbit runs
PHPStan runs in a sandbox with the project config if present; we parse and validate the config before execution.
## Security policy and restrictions

- We reject `phpstan.neon`/`phpstan.neon.dist` that declare `bootstrapFile` or `bootstrapFiles` to prevent executing arbitrary project bootstrap code.

- Blocked configuration keys include:

- `bootstrapFiles`

- `bootstrapFile`

## When we skip PHPStan
CodeRabbit will skip running PHPStan when:

- No config file is found (`phpstan.neon`, `phpstan.neon.dist`, or `phpstan.dist.neon`).

- The config file does not contain a `paths:` parameter.

- The config contains `bootstrapFile` or `bootstrapFiles`.

- PHPStan is already running in GitHub workflows.

- Config parsing fails or appears unsafe.

## Links

- PHPStan Configuration
