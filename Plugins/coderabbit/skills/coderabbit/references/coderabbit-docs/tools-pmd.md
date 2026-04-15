---
source: https://docs.coderabbit.ai/tools/pmd
---

# PMD

## Files
PMD will run on files with the following extensions:

- `.java`

- `.jsp`

- `.kt` (Kotlin)

- `.apex` (Salesforce Apex)

- `pom.xml` (Maven)

## Configuration
PMD uses an XML configuration file.
PMD supports the following config files:

- User-defined config file set at `reviews.tools.pmd.config_file` in your project’s `.coderabbit.yaml` file or setting the “Reviews → Tools → PMD → Config File” field in CodeRabbit’s settings page.

- If no user-defined config file is found, we look for the following config file in the repo:

- `ruleset.xml`

CodeRabbit will not run PMD if no config file is found.
## When we skip PMD
CodeRabbit will skip running PMD when:

- No config file is found (user-defined config file or `ruleset.xml`).

- PMD is already running in GitHub workflows.

## Links

- PMD Configuring rules

PHPStanPrisma Lint
