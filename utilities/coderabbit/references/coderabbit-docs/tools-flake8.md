---
source: https://docs.coderabbit.ai/tools/flake8
---

# Flake8

## Supported Files
Flake8 will run on files with the following extensions:

- `*.py`

- `*.ipynb` (using nbQA)

## Configuration
Flake8 supports the following config files:

- `.flake8`

CodeRabbit will not run Flake8 if no config file is found.
## When we skip Flake8
CodeRabbit will skip running Flake8 when:

- No config file is found (`.flake8`).

- Flake8 is already running in GitHub workflows.

## Excluded codes
The following Flake8 codes are automatically excluded (style and whitespace issues that won’t cause runtime errors):

- `E501` - line too long

- `E302`, `E303`, `E305` - blank line issues

- `W291`, `W292`, `W293`, `W391` - whitespace issues

- `E201`, `E202`, `E203`, `E211` - whitespace around brackets

- `E221`, `E222`, `E225`, `E226`, `E227`, `E228` - whitespace around operators

- `E231`, `E241`, `E242`, `E251` - whitespace around commas

- `E261`, `E262` - inline comment spacing

- `E271`, `E272`, `E273`, `E274`, `E275` - whitespace around keywords

- `E301`, `E304`, `E306` - blank line issues

- `E401`, `E402`, `E411` - import grouping issues

- `E502` - redundant backslash

- `W191` - indentation contains tabs

- `E266` - too many leading ’#’ for block comment

## Profile behavior
In **Chill** mode, Flake8 filters out warnings and conventions, reporting only errors.
In **Assertive** mode, all findings (errors, warnings, and conventions) are reported.
## Features
Flake8 can detect many issues such as:

- Style violations (PEP 8)

- Logical errors and unused imports

- Code complexity issues

- Syntax errors

- And many more

## Links

- Flake8 Official Website

- Flake8 GitHub Repository

- Flake8 Documentation

- Flake8 Configuration

- nbQA Documentation
