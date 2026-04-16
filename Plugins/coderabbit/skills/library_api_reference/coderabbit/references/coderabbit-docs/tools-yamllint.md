---
source: https://docs.coderabbit.ai/tools/yamllint
---

# YAMLlint

## Files
YAMLlint will run on files with the following extensions:

- `.yaml`

- `.yml`

## Configuration
### Enable YAMLlint
- Web UI
- .coderabbit.yaml
Reviews → Tools → Enable YAMLlinttrue`reviews.tools.yamllint.enabled`booleantrue
YAMLlint is a linter for YAML files.
## Features
YAMLlint performs several checks:
### Syntax checks

- YAML validity

- Document structure

### Cosmetic checks

- Line length limits

- Trailing whitespace

- Indentation consistency

- Empty lines

- Comments formatting

## Configuration File
CodeRabbit loads repository `.yamllint.yml` or `.yamllint.yaml` files for this integration if they exist. If not, it passes inline configuration data to yamllint based on the selected review profile.
## When we skip YAMLlint
CodeRabbit will skip running YAMLlint when:

- YAMLlint is already running in GitHub workflows.

## Ignored rules
The following YAMLlint rules are automatically ignored (noisy whitespace/indentation-only rules):

- `trailing-spaces` - extra spaces at end of line

- `indentation` - spaces don’t line up

- `new-line-at-end-of-file` - new line at end of file

- `commas` - commas in lists

- `line-length` - line length limits

- `document-start` - document start requirements

## Profile behavior
CodeRabbit uses different YAMLlint rule sets based on the review profile:

- **Chill Mode**: Uses the `relaxed` rule set

- **Assertive Mode**: Uses the `default` rule set

## Links

- YAMLlint Documentation

- Configuration Reference

TruffleHogConfiguration reference
