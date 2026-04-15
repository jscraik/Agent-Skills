---
source: https://docs.coderabbit.ai/tools/checkov
---

# Checkov

## Files

Checkov runs on these files and extensions:

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

CodeRabbit includes findings based on selected review profile:

### Chill

- `MEDIUM`
- `HIGH`
- `CRITICAL`

### Assertive

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

## When CodeRabbit skips Checkov

CodeRabbit skips Checkov when:

- Checkov is already running in GitHub workflows.
- Repository `.checkov.yml` or `.checkov.yaml` enables `external-checks-dir` or `external-checks-git`.

## Links

- [Checkov Scans Documentation](https://www.checkov.io/2.Basics/CLI%20Command%20Reference.html)
