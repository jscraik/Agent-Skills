---
source: https://docs.coderabbit.ai/tools/sqlfluff
---

# SQLFluff

## Files

SQLFluff runs on:

- `.sql`

## Configuration

SQLFluff supports:

- User-defined file configured in `reviews.tools.sqlfluff.config_file` in `.coderabbit.yaml`
- `setup.cfg`
- `tox.ini`
- `pep8.ini`
- `.sqlfluff`
- `pyproject.toml`

CodeRabbit only runs SQLFluff when a recognized config file exists.

## When CodeRabbit skips SQLFluff

CodeRabbit skips SQLFluff when:

- No recognized SQLFluff config file exists.
- SQLFluff is already running in GitHub workflows.

## Links

- [SQLFluff Configuration](https://docs.sqlfluff.com/en/stable/configuration.html)
- [SQLFluff Rules Reference](https://docs.sqlfluff.com/en/stable/reference/rules.html)
