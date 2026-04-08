---
source: https://docs.coderabbit.ai/tools/buf
---

# Buf

## Files
Buf will run on files with the following extensions:

- `.proto`

## Configuration
Buf uses a YAML style configuration file. We look for the following file anywhere in the repository:

- `buf.yaml`

If no config file is found, CodeRabbit will consider the following categories of strictness based on the profile selected:
### Chill

- `MINIMAL`

### Assertive

- `BASIC`

## When we skip Buf
CodeRabbit will skip running Buf when:

- Buf is already running in GitHub workflows.

## Links

- Buf Configuration
