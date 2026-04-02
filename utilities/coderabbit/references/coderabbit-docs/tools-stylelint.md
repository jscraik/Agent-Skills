---
source: https://docs.coderabbit.ai/tools/stylelint
---

# Stylelint

## Files
Stylelint runs on files with the following extensions:

- `.css`

- `.scss`

- `.sass`

- `.less`

- `.sss` (SugarSS)

- `.styl` (Stylus)

## Configuration

- **Allowed config files**: Only data-only config files are used. CodeRabbit looks for `.stylelintrc.json`, `.stylelintrc.yml`, or `.stylelintrc.yaml`. Executable configs (`.stylelintrc.js`, `stylelint.config.js`, `stylelint.config.mjs`) are **not** allowed.

- **No user config**: If no allowed config is found, CodeRabbit writes a default `.stylelintrc.json` that extends `stylelint-config-standard-scss` and disables some stylistic rules (e.g. `selector-class-pattern`, `color-hex-length`, `rule-empty-line-before`) to reduce noise. Plugin and `extends` resolution uses only packages we ship in the image.

## Links

- Stylelint Documentation

- Stylelint GitHub
