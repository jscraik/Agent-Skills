---
source: https://docs.coderabbit.ai/tools/smarty-lint
---

# smarty-lint

## Files
smarty-lint runs on files with the following extension:

- `.tpl`

## Configuration
You can enable or disable smarty-lint in your CodeRabbit configuration (see Tools reference and Configuration reference).
CodeRabbit supports `smartylint.json`. If no config file is present, CodeRabbit creates a temporary `smartylint.json` that scans `**/*.tpl`.
If `smartylint.js` is present, CodeRabbit skips smarty-lint rather than executing a JavaScript config file.
## When we skip smarty-lint
CodeRabbit will skip running smarty-lint when:

- No `.tpl` files are found in the pull request.

- smarty-lint is already running in GitHub workflows.

- `smartylint.js` is present in the repository.

## Links

- smarty-lint on GitHub

Shopify CLISQLFluff
