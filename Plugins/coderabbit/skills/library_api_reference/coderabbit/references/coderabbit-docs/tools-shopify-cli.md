---
source: https://docs.coderabbit.ai/tools/shopify-cli
---

# Shopify CLI

## Requirements
The tool only runs when the following conditions are met:
### File Types

- Only processes pull requests changing `*.liquid` files

### Configuration Files

- Requires either `.theme-check.yml` or `.theme-check.yaml` configuration file in the project root

### Directory Structure

- Requires the standard Shopify theme directory structure at the project root:

- `assets/`

- `Infrastructure/config/`

- `layout/`

- `locales/`

- `sections/`

- `snippets/`

- `Infrastructure/templates/`

If any of these requirements are not met, the tool will not run.
## When we skip Shopify Theme Check
CodeRabbit will skip running Shopify Theme Check when:

- No `.liquid` files are changed in the pull request.

- The repository does not have the required Shopify theme directory structure.

- No config file is found (`.theme-check.yml` or `.theme-check.yaml`).

- Shopify Theme Check is already running in GitHub workflows.

## Validation Rules
The tool checks for:
### Theme Validation

- Liquid syntax errors

- Theme requirements compliance

- Asset organization

- Performance best practices

- Accessibility standards

**Note**: The tool filters out `UndefinedObject` and `MissingTemplate` checks, reporting only errors and warnings for other issues.
## Common Issues
The tool helps identify and fix:

- Theme Issues:

- Invalid Liquid syntax

- Missing required templates

- Performance bottlenecks

- Accessibility violations

- App Issues:

- Invalid API usage

- Missing dependencies

- Configuration errors

- Security vulnerabilities

## Links

- Shopify CLI GitHub Repository

- Shopify CLI Theme Documentation

- Shopify CLI App Documentation

- Theme Development Requirements

ShellChecksmarty-lint
