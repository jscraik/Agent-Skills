---
source: https://docs.coderabbit.ai/tools/markdownlint
---

# Markdownlint

## Files
Markdownlint will run on files with the following extensions:

- `.md`

- `.markdown`

## Configuration
`markdownlint-cli2` supports the following config files:

- `.markdownlint.jsonc`

- `.markdownlint.json`

- `.markdownlint.yaml`

- `.markdownlint.yml`

- `.markdownlint-cli2.json`

- `.markdownlint-cli2.yaml`

- `.markdownlint-cli2.js`

CodeRabbit will use the default settings based on the profile selected if no config file is found.
## When we skip markdownlint
CodeRabbit will skip running markdownlint when:

- markdownlint is already running in GitHub workflows.

## Ignored rules
The following markdownlint rules are automatically ignored:

- `MD004` - ul-style (disallows mixing of list markers)

- `MD012` - no-multiple-blanks (disallows multiple blank lines)

- `MD013` - line-length (enforces maximum line length)

- `MD025` - single-title, single-h1 (ensures only one H1 heading per file)

- `MD026` - no-trailing-punctuation (disallows trailing punctuation in headings)

- `MD032` - blanks-around-lists (disallows multiple blank lines around lists)

- `MD033` - no-inline-html (disallows inline HTML inside Markdown)

- `MD034` - no-bare-urls (disallows bare URLs)

- `MD036` - no-emphasis-as-heading (disallows emphasis instead of headings)

- `MD060` - table-column-count (table column count)

- `MD007` - ul-indent (unordered list indentation)

- `MD010` - no-hard-tabs (hard tabs)

## Links

- `markdownlint-cli2` Configuration

LuacheckOSV-Scanner
