---
source: https://docs.coderabbit.ai/tools/phpcs
---

# PHPCS

## Files
PHPCS will run on files with the following extensions:

- `.php`

## Features
PHPCS can detect and fix various coding standard violations including:

- **PSR Standards**: Enforces PSR-1, PSR-2, PSR-12, and other coding standards

- **Custom Standards**: Supports custom coding standards and rules

- **Auto-fixing**: Can automatically fix many coding standard violations

- **Custom Rules**: Allows creation of custom sniff rules

- **Multiple Standards**: Can enforce multiple coding standards simultaneously

## Popular Standards
PHPCS supports many coding standards including:

- **PSR-1**: Basic Coding Standard

- **PSR-2**: Coding Style Guide

- **PSR-12**: Extended Coding Style

- **Squiz**: Squiz Labs coding standard

- **PEAR**: PEAR coding standard

- **Zend**: Zend Framework coding standard

## Configuration
PHPCS requires a configuration file to run. CodeRabbit will only run PHPCS if one of the following configuration files is found:

- `phpcs.xml` - XML configuration file

- `phpcs.xml.dist` - Distributed XML configuration file

CodeRabbit will not run PHPCS if no configuration file is found.
## When we skip PHPCS
CodeRabbit will skip running PHPCS when:

- PHPCS is disabled in the review profile (only runs in **Assertive** mode).

- No config file is found (`phpcs.xml` or `phpcs.xml.dist`).

- The config file does not appear to be a valid PHPCS ruleset (missing `<ruleset` or `<?xml` tags).

## Profile behavior
PHPCS only runs in **Assertive** mode. In **Chill** mode, PHPCS is skipped entirely.
## Links

- PHPCS GitHub Repository

- PHPCS Documentation

- Available Coding Standards

- Creating Custom Standards
