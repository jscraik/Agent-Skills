---
source: https://docs.coderabbit.ai/tools/detekt
---

# Detekt

## Files
`detekt` will run on files with the following extensions:

- `.kt`

- `.kts`

## Configuration
`detekt` uses a YAML style configuration file.
`detekt` supports the following config files:

- User-defined config file set at `reviews.tools.detekt.config_file` in your project’s `.coderabbit.yaml` file or setting the “Reviews → Tools → `detekt` → Config File” field in CodeRabbit’s settings page.

If no user-defined config file is found, CodeRabbit will generate a `detekt-config.yaml` file based on the selected profile.
## When we skip detekt
CodeRabbit will skip running detekt when:

- No Kotlin files are found in the pull request.

- detekt is already running in GitHub workflows.

## Profile behavior
CodeRabbit generates different detekt configurations based on the review profile:

- **Chill Mode**: Uses a focused configuration with fewer rules enabled.

- **Assertive Mode**: Uses a more comprehensive configuration with additional rules enabled.

If you provide your own config file, it will be used instead of the generated one.
## Links

- `detekt` Configuration

CppcheckDotenv Linter
