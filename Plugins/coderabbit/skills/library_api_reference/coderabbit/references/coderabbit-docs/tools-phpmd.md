---
source: https://docs.coderabbit.ai/tools/phpmd
---

# PHPMD

## Files
PHPMD will run on files with the following extensions:

- `.php`

## Features
PHPMD can detect various code quality issues including:

- **Clean Code Rules**: Detects code smells and violations of clean code principles

- **Controversial Rules**: Identifies potentially problematic code patterns

- **Design Rules**: Finds design-related issues and architectural problems

- **Naming Rules**: Checks for naming convention violations

- **Unused Code Rules**: Detects unused variables, parameters, methods, and classes

- **Size Rules**: Identifies overly complex methods and classes

## When we skip PHPMD
CodeRabbit will skip running PHPMD when:

- PHPMD is already running in GitHub workflows.

## Profile behavior
CodeRabbit’s review profile affects which PHPMD rules are applied:

- **Chill Mode**: Only checks for unused code (`unusedcode` rule set)

- **Assertive Mode**: Checks all rule sets including clean code, code size, controversial rules, design issues, naming conventions, and unused code (`cleancode,codesize,controversial,design,naming,unusedcode`)

## Links

- PHPMD Official Website

- PHPMD GitHub Repository

- PHPMD Documentation

- Available Rules
