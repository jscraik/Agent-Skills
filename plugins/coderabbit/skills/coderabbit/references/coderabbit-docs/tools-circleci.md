---
source: https://docs.coderabbit.ai/tools/circleci
---

# CircleCI

## Files
We look for `CircleCI Configuration` files specifically in the following directory:

- `.circleci/config.yml`

- `.circleci/config.yaml`

## Configuration
CodeRabbit will use the default configuration and runs `circleci config validate` to check for configuration errors.
## Notes

- CircleCI validates YAML syntax and workflow configuration errors.

- Errors are reported with line numbers when available.

## Links

- CircleCI Configuration
