---
source: https://docs.coderabbit.ai/tools/checkmake
---

# Checkmake

## Files
Checkmake will run checks against any `Makefile`.
## Configuration
Checkmake supports the following config files:

- `checkmake.yml`

- `checkmake.yaml`

CodeRabbit will use Checkmake’s default settings if no config file is found.
## When we skip checkmake
CodeRabbit will skip running checkmake when:

- No Makefiles are found in the pull request.

- checkmake is already running in GitHub workflows.

## Links

- Checkmake Configuration
