---
source: https://docs.coderabbit.ai/tools/htmlhint
---

# HTMLHint

## Files
HTMLHint will run checks against `*.html` files.
## Configuration
HTMLHint supports the following config files:

- `.htmlhintrc`

- `.htmlhintrc.json`

- `htmlhintrc.json`

CodeRabbit will use the default settings based on the profile selected if no config file is found.
## When we skip HTMLHint
CodeRabbit will skip running HTMLHint when:

- HTMLHint is already running in GitHub workflows.

## Profile behavior
CodeRabbit filters out the following categories and does not report them:

- `attr-lowercase` - attribute names must be lowercase

- `attr-value-double-quotes` - attribute values must use double quotes

In **Assertive** mode, all findings are reported.
## Links

- HTMLHint Configuration
