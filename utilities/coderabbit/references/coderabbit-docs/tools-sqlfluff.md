---
source: https://docs.coderabbit.ai/tools/sqlfluff
---

# SQLFluff

## Files
SQLFluff will run on files with the following extensions:

- `.sql`

## Configuration
SQLFluff supports the following config files:

- User-defined config file set at `reviews.tools.sqlfluff.config_file` in your project’s `.coderabbit.yaml` file or setting the “Reviews → Tools → SQLFluff → Config File” field in CodeRabbit’s settings page.

- `setup.cfg`

- `tox.ini`

- `pep8.ini`

- `.sqlfluff`

- `pyproject.toml`

CodeRabbit will only run SQLFluff if your repository contains a SQLFluff config file. This config must use one of the default file names listed above, or you must define the path to this file in the `.coderabbit.yaml` or config UI.
## When we skip SQLFluff
CodeRabbit will skip running SQLFluff when:

- No config file is found (user-defined config file or one of the default file names).

- SQLFluff is already running in GitHub workflows.

## Links

- SQLFluff Configuration

- SQLFluff Rules Reference

smarty-lintStylelint
