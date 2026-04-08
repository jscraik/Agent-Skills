---
source: https://docs.coderabbit.ai/tools/phpstan
---

# PHPStan

## Files

PHPStan runs on files with extension:

- `.php`

## Configuration

Supported config files:

- `phpstan.neon`
- `phpstan.neon.dist`
- `phpstan.dist.neon`

CodeRabbit skips PHPStan if no supported config file exists.

## What CodeRabbit runs

PHPStan runs in a sandbox using the detected project config. CodeRabbit parses and validates config content before execution.

## Security policy and restrictions

To prevent unsafe bootstrap execution, CodeRabbit rejects configs that set:

- `bootstrapFile`
- `bootstrapFiles`

## When CodeRabbit skips PHPStan

CodeRabbit skips PHPStan when:

- No config file is found (`phpstan.neon`, `phpstan.neon.dist`, or `phpstan.dist.neon`).
- The config does not include `paths:`.
- The config contains `bootstrapFile` or `bootstrapFiles`.
- PHPStan is already running in GitHub workflows.
- Config parsing fails or is considered unsafe.

## Links

- [PHPStan Configuration](https://phpstan.org/config-reference)
