---
source: https://docs.coderabbit.ai/tools/ember-template-lint
---

# ember-template-lint

## Files

ember-template-lint runs on:

- `.hbs`

## Configuration

Supported config files:

- `.template-lintrc.js`
- `.template-lintrc.cjs`
- `.template-lintrc.mjs`
- `.template-lintrc.json`
- `.template-lintrc.yaml`
- `.template-lintrc.yml`

If no config file is found, ember-template-lint uses default rules.

To enable/disable ember-template-lint, use `.coderabbit.yaml` or the CodeRabbit UI.

### `.coderabbit.yaml`

```yaml
reviews:
  tools:
    emberTemplateLint:
      enabled: true
```

### Web UI

Go to **Reviews → Tools → ember-template-lint** and toggle it on or off.

## When CodeRabbit skips ember-template-lint

CodeRabbit skips this tool when:

- No `.hbs` files are present in the pull request diff.
- ember-template-lint is already running in CI (detected via GitHub Checks).

## What's next

- [All supported tools](/tools/list)
- [Tools reference](/reference/tools)
- [Configuration reference](/reference/configuration)
