---
source: https://docs.coderabbit.ai/tools/hadolint
---

# Hadolint

## Files
Hadolint will run on files with the following file names:

- `Dockerfile`

- `*.dockerfile`

- `Dockerfile.*`

## Configuration
Hadolint supports the following config files:

- `.hadolint.yaml`

CodeRabbit filters the following severity levels based on the selected review profile:
### Chill

- `none`

- `ignore`

- `style`

- `info`

- `warning`

### Assertive

- `none`

- `ignore`

- `style`

## When we skip Hadolint
CodeRabbit will skip running Hadolint when:

- Hadolint is already running in GitHub workflows.

## Links

- Hadolint Configuration

golangci-lintHTMLHint
