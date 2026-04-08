---
source: https://docs.coderabbit.ai/tools/regal
---

# Regal

## Files
Regal will run on files with the following extensions:

- `.rego`

## Configuration
Regal uses a YAML configuration file located at `.regal/config.yaml`.
CodeRabbit will use the default settings based on the profile selected if no configuration file is found.
## When we skip Regal
CodeRabbit will skip running Regal when:

- No Rego files are found in the pull request.

- Regal is already running in GitHub workflows.

## Profile behavior
CodeRabbit generates different Regal configurations based on the review profile:

- **Chill Mode**: Uses a focused configuration with fewer rules enabled.

- **Assertive Mode**: Uses a more comprehensive configuration with additional rules enabled.

If you provide your own config file (`.regal/config.yaml`), it will be used instead of the generated one.
## Disabled categories
Regal automatically disables the following categories:

- `style` - style-related issues

- `testing` - testing-related issues

## Links

- Regal Configuration
