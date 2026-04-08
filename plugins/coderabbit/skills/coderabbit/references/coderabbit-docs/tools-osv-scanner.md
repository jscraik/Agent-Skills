---
source: https://docs.coderabbit.ai/tools/osv-scanner
---

# OSV-Scanner

## Files
OSV-Scanner scans the following manifest and lock files:

- `bun.lock`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`

- `requirements.txt`, `Pipfile.lock`, `poetry.lock`, `pdm.lock`, `pylock.toml`, `uv.lock`

- `go.mod`

- `pom.xml`, `buildscript-gradle.lockfile`, `gradle.lockfile`, `gradle/verification-metadata.xml`

- `Gemfile.lock`, `gems.locked`

- `composer.lock`

- `Cargo.lock`

- `pubspec.lock`

- `mix.lock`

- `renv.lock`

- `cabal.project.freeze`, `stack.yaml.lock`

- `conan.lock`

- `deps.json`

- `packages.lock.json`, `packages.config`

## Configuration
You can customize OSV-Scanner by adding an optional `osv-scanner.toml` configuration file to your repository.

OSV-Scanner runs without a config file. If your repository contains an `osv-scanner.toml` file, CodeRabbit uses it when running OSV-Scanner.
## Notes

- OSV-Scanner scans dependency manifest and lock files to identify known vulnerabilities.

- Findings include vulnerability severity scores and details from the OSV.dev database.

## Profile behavior

- In **Chill** mode, CodeRabbit keeps only `high` and `critical` findings.

- In **Assertive** mode, CodeRabbit reports findings across all severities.

## Links

- OSV-Scanner GitHub Repository

- OSV-Scanner Documentation

- OSV.dev Database

markdownlintOpenGrep
