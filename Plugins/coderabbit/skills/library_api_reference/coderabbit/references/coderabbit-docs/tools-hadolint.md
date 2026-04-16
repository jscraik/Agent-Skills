---
source: https://docs.coderabbit.ai/tools/hadolint
---

# Hadolint

## Files

Hadolint runs on:

- `Dockerfile`
- `*.dockerfile`
- `Dockerfile.*`

## Configuration

Hadolint supports:

- `.hadolint.yaml`

CodeRabbit filters findings by review profile severity:

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

## When CodeRabbit skips Hadolint

CodeRabbit skips Hadolint when:

- Hadolint is already running in GitHub workflows.

## Links

- [Hadolint Configuration](https://github.com/hadolint/hadolint#configure)
