---
source: https://docs.coderabbit.ai/reference/tools-reference
---

# Tools Reference

CodeRabbit supports integration with 47 static analysis tools, linters, and security scanners. Each tool can be configured individually within your `.coderabbit.yaml` file.

## Actionlint

actionlint is a static checker for GitHub Actions workflow files. v1.7.10

**Configuration Options:**

- enabled: Defaults to true.

**Example Configuration:**

```yaml
reviews:
  tools:
    actionlint:
      enabled: true
```

## Ast-grep

ast-grep is a code analysis tool that helps you to find patterns in your codebase using abstract syntax trees patterns. v0.40.5

**Configuration Options:**

- rules_directories: List of rules directories. Defaults to [].
- utils_directories: List of utils directories. Defaults to [].
- essentials: Use ast-grep essentials package. Defaults to true.
- packages: Predefined packages to be used. Defaults to [].

**Example Configuration:**

```yaml
reviews:
  tools:
    ast-grep:
      enabled: true
```

## Biome

Biome is a fast formatter, linter, and analyzer for web projects. v2.3.14

**Configuration Options:**

- enabled: Enable Biome integration. Defaults to true.

**Example Configuration:**

```yaml
reviews:
  tools:
    biome:
      enabled: true
```

## Blinter

Blinter is a linter for Windows batch files. v1.0.112

**Example Configuration:**

```yaml
reviews:
  tools:
    blinter:
      enabled: true
```

## Brakeman

Brakeman is a static analysis security vulnerability scanner for Ruby on Rails applications. v8.0.2

**Example Configuration:**

```yaml
reviews:
  tools:
    brakeman:
      enabled: true
```

## Buf

Buf offers linting for Protobuf files. v1.65.0

**Example Configuration:**

```yaml
reviews:
  tools:
    buf:
      enabled: true
```

## Checkmake

checkmake is a linter for Makefiles. v0.2.2

**Example Configuration:**

```yaml
reviews:
  tools:
    checkmake:
      enabled: true
```

## Checkov

Checkov is a static code analysis tool for infrastructure-as-code files. v3.2.334

**Example Configuration:**

```yaml
reviews:
  tools:
    checkov:
      enabled: true
```

## Circleci

CircleCI tool is a static checker for CircleCI config files. v0.1.34283

**Example Configuration:**

```yaml
reviews:
  tools:
    circleci:
      enabled: true
```

## Clang

Configuration for Clang to perform static analysis on C and C++ code. v14.0.6

**Example Configuration:**

```yaml
reviews:
  tools:
    clang:
      enabled: true
```

## Clippy

Clippy is a collection of lints to catch common mistakes and improve your Rust code.

**Example Configuration:**

```yaml
reviews:
  tools:
    clippy:
      enabled: true
```

## Cppcheck

Cppcheck is a static code analysis tool for the C and C++ programming languages. v2.19.0

**Example Configuration:**

```yaml
reviews:
  tools:
    cppcheck:
      enabled: true
```

## Detekt

Detekt is a static code analysis tool for Kotlin files. v1.23.8

**Configuration Options:**

- config_file: Optional path to detekt configuration file relative to the repository.

**Example Configuration:**

```yaml
reviews:
  tools:
    detekt:
      enabled: true
      config_file: "detekt.yml"
```

## Dotenv Lint

dotenv-linter is a tool for checking and fixing .env files. v4.0.0

**Example Configuration:**

```yaml
reviews:
  tools:
    dotenvLint:
      enabled: true
```

## Eslint

ESLint is a static code analysis tool for JavaScript files.

**Example Configuration:**

```yaml
reviews:
  tools:
    eslint:
      enabled: true
```

## Flake8

Flake8 is a Python linter that wraps PyFlakes, pycodestyle and McCabe script. v7.3.0

**Example Configuration:**

```yaml
reviews:
  tools:
    flake8:
      enabled: true
```

## Fortitude Lint

Fortitude is a Fortran linter. v0.8.0

**Example Configuration:**

```yaml
reviews:
  tools:
    fortitudeLint:
      enabled: true
```

## Github-checks

GitHub Checks integration configuration.

**Configuration Options:**

- enabled: Enable GitHub Checks integration. Defaults to true.
- timeout: Time in ms to wait for all GitHub Checks to conclude. Default 90s, max 15 min (900000ms).

**Example Configuration:**

```yaml
reviews:
  tools:
    github-checks:
      enabled: true
```

## Gitleaks

Gitleaks is a secret scanner. v8.30.0

**Example Configuration:**

```yaml
reviews:
  tools:
    gitleaks:
      enabled: true
```

## Golangci-lint

golangci-lint is a fast linters runner for Go. v2.5.0

**Configuration Options:**

- config_file: Optional path to golangci-lint configuration file.

**Example Configuration:**

```yaml
reviews:
  tools:
    golangci-lint:
      enabled: true
      config_file: ".golangci.yml"
```

## Hadolint

Hadolint is a Dockerfile linter. v2.14.0

**Example Configuration:**

```yaml
reviews:
  tools:
    hadolint:
      enabled: true
```

## Htmlhint

HTMLHint is a static code analysis tool for HTML files. v1.9.0

**Example Configuration:**

```yaml
reviews:
  tools:
    htmlhint:
      enabled: true
```

## Languagetool

LanguageTool is a style and grammar checker for 30+ languages.

**Configuration Options:**

- enabled: Enable LanguageTool integration. Defaults to true.
- enabledRules: IDs of rules to enable. Defaults to [].
- disabledRules: IDs of rules to disable. EN_UNPAIRED_BRACKETS and EN_UNPAIRED_QUOTES always disabled. Defaults to [].
- enabledCategories: IDs of categories to enable. Defaults to [].
- disabledCategories: IDs of categories to disable. TYPOS, TYPOGRAPHY, and CASING always disabled. Defaults to [].
- onlyEnabled: Only use explicitly enabled rules/categories. Defaults to false.
- level: 'default' or 'picky'. Defaults to "default".

**Example Configuration:**

```yaml
reviews:
  tools:
    languagetool:
      enabled: true
      level: "default"
```

## Luacheck

Luacheck helps maintain consistent and error-free Lua code. v1.2.0

**Example Configuration:**

```yaml
reviews:
  tools:
    luacheck:
      enabled: true
```

## Markdownlint

markdownlint-cli2 is a static analysis tool for Markdown files. v0.20.0

**Example Configuration:**

```yaml
reviews:
  tools:
    markdownlint:
      enabled: true
```

## Opengrep

OpenGrep is a high-performance static code analysis engine, compatible with Semgrep configurations. v1.16.0

**Example Configuration:**

```yaml
reviews:
  tools:
    opengrep:
      enabled: true
```

## Osv Scanner

OSV Scanner is a tool for vulnerability package scanning. v2.3.2

**Example Configuration:**

```yaml
reviews:
  tools:
    osvScanner:
      enabled: true
```

## Oxc

Oxlint is a JavaScript/TypeScript linter for OXC written in Rust. v1.46.0

**Example Configuration:**

```yaml
reviews:
  tools:
    oxc:
      enabled: true
```

## Phpcs

PHP CodeSniffer is a PHP linter and coding standard checker. v3.7.2

**Example Configuration:**

```yaml
reviews:
  tools:
    phpcs:
      enabled: true
```

## Phpmd

PHPMD is a tool to find potential problems in PHP code. v2.15.0

**Example Configuration:**

```yaml
reviews:
  tools:
    phpmd:
      enabled: true
```

## Phpstan

PHPStan is a tool to analyze PHP code. v2.1.38

**Configuration Options:**

- level: Rule level (default, 0-9, max). Ignored if config file already has level.

**Example Configuration:**

```yaml
reviews:
  tools:
    phpstan:
      enabled: true
      level: "default"
```

## Pmd

PMD is an extensible multilanguage static code analyzer. Mainly Java. v7.21.0

**Configuration Options:**

- config_file: Optional path to PMD configuration file.

**Example Configuration:**

```yaml
reviews:
  tools:
    pmd:
      enabled: true
      config_file: "ruleset.xml"
```

## Prisma Lint

Prisma Schema linting to ensure schema file quality. v0.13.1

**Example Configuration:**

```yaml
reviews:
  tools:
    prismaLint:
      enabled: true
```

## Pylint

Pylint is a Python static code analysis tool. v4.0.4

**Example Configuration:**

```yaml
reviews:
  tools:
    pylint:
      enabled: true
```

## Regal

Regal is a linter and language server for Rego. v0.38.1

**Example Configuration:**

```yaml
reviews:
  tools:
    regal:
      enabled: true
```

## Rubocop

RuboCop is a Ruby static code analyzer and code formatter. v1.84.1

**Example Configuration:**

```yaml
reviews:
  tools:
    rubocop:
      enabled: true
```

## Ruff

Ruff is a Python linter and code formatter. v0.15.0

**Example Configuration:**

```yaml
reviews:
  tools:
    ruff:
      enabled: true
```

## Semgrep

Semgrep is a static analysis tool for security vulnerabilities and code quality. v1.151.0

**Configuration Options:**

- config_file: Optional path to Semgrep configuration file.

**Example Configuration:**

```yaml
reviews:
  tools:
    semgrep:
      enabled: true
      config_file: ".semgrep.yml"
```

## Shellcheck

ShellCheck is a static analysis tool that finds bugs in shell scripts. v0.11.0

**Example Configuration:**

```yaml
reviews:
  tools:
    shellcheck:
      enabled: true
```

## Shopify Theme Check

A linter for Shopify themes. cli 3.90.0 | theme 3.58.2

**Example Configuration:**

```yaml
reviews:
  tools:
    shopifyThemeCheck:
      enabled: true
```

## Sqlfluff

SQLFluff is an open source, dialect-flexible and configurable SQL linter. v4.0.4

**Example Configuration:**

```yaml
reviews:
  tools:
    sqlfluff:
      enabled: true
```

## Stylelint

Stylelint is a linter for stylesheets (CSS, SCSS, Sass, Less, SugarSS, Stylus). v17.2.0

**Example Configuration:**

```yaml
reviews:
  tools:
    stylelint:
      enabled: true
```

## Swiftlint

SwiftLint is a Swift linter. v0.63.2

**Configuration Options:**

- config_file: Optional path to SwiftLint configuration file.

**Example Configuration:**

```yaml
reviews:
  tools:
    swiftlint:
      enabled: true
      config_file: ".swiftlint.yml"
```

## Tflint

TFLint is a Terraform linter for finding potential errors. v0.61.0

**Example Configuration:**

```yaml
reviews:
  tools:
    tflint:
      enabled: true
```

## Trivy

Trivy is a comprehensive security scanner for IaC files. v0.69.1

**Example Configuration:**

```yaml
reviews:
  tools:
    trivy:
      enabled: true
```

## Trufflehog

TruffleHog is a secret scanner with verification capabilities. v3.92.0

**Example Configuration:**

```yaml
reviews:
  tools:
    trufflehog:
      enabled: true
```

## Yamllint

YAMLlint is a linter for YAML files. v1.38.0

**Example Configuration:**

```yaml
reviews:
  tools:
    yamllint:
      enabled: true
```

## PSScriptAnalyzer

PSScriptAnalyzer is a static code checker for PowerShell scripts and modules. v1.24.0

**Example Configuration:**

```yaml
reviews:
  tools:
    psscriptanalyzer:
      enabled: true
```
