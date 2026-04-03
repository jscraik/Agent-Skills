---
source: https://docs.coderabbit.ai/tools/ember-template-lint
---

# ember-template-lint

## Files
ember-template-lint runs on files with the following extensions:

- `.hbs`

## Configuration
ember-template-lint reads its configuration from your repository automatically. Supported config files include:

- `.template-lintrc.js`

- `.template-lintrc.cjs`

- `.template-lintrc.mjs`

- `.template-lintrc.json`

- `.template-lintrc.yaml`

- `.template-lintrc.yml`

If no config file is found, ember-template-lint runs with its default rule set.
To enable or disable ember-template-lint, use your `.coderabbit.yaml` file or the CodeRabbit web UI:
- .coderabbit.yaml
- Web UI
.coderabbit.yaml

`reviews:
 tools:
 emberTemplateLint:
 enabled: true
`Go to **Reviews → Tools → ember-template-lint** in your organization or repository settings and toggle ember-template-lint `on` or `off`.
## When CodeRabbit skips ember-template-lint
CodeRabbit skips ember-template-lint when:

- No `.hbs` files are present in the pull request diff.

- ember-template-lint is already running as a step in your CI pipeline (detected via GitHub Checks).

## What’s next

## All supported toolsBrowse the complete list of linters, security analyzers, and CI/CD integrations available in CodeRabbit.

## Tools referenceExplore detailed specifications and capabilities of all available CodeRabbit tools.

## Configuration referenceFull reference for all available options, including how to enable, disable, and tune individual tools.

Dotenv LinterESLint
