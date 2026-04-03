---
source: https://docs.coderabbit.ai/tools/checkov
---

# Checkov

## Files
Checkov will run on files with the following files and extensions:

- `.tf`

- `.yml`

- `.yaml`

- `.json`

- `.template`

- `.bicep`

- `.hcl`

- `bower.json`

- `build.gradle`

- `build.gradle.kts`

- `go.sum`

- `gradle.properties`

- `METADATA`

- `npm-shrinkwrap.json`

- `package.json`

- `package-lock.json`

- `pom.xml`

- `requirements.txt`

- `Dockerfile`

- `.dockerfile`

- `Dockerfile.*`

- `.csproj`

- `yarn.lock`

- `Gemfile`

- `Gemfile.lock`

- `go.mod`

- `paket.dependencies`

- `paket.lock`

- `packages.config`

- `composer.json`

- `composer.lock`

## Configuration
CodeRabbit will include on the following severity levels based on the profile selected:
### Chill

- `MEDIUM`

- `HIGH`

- `CRITICAL`

### Assertive

- `LOW`

- `MEDIUM`

- `HIGH`

- `CRITICAL`

## When we skip Checkov
CodeRabbit will skip running Checkov when:

- Checkov is already running in GitHub workflows.

- The repository’s `.checkov.yml` or `.checkov.yaml` config enables `external-checks-dir` or `external-checks-git`.

## Links

- Checkov All Resource Scans
