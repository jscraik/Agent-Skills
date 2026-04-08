---
source: https://docs.coderabbit.ai/getting-started/yaml-configuration
---

# YAML Configuration

In this guide, we cover configuring CodeRabbit with a `.coderabbit.yaml` file. For the full option list, see the [Configuration Reference](/reference/configuration). For framework-specific templates, see [Configuration Examples](/configuration/example).

## Export existing UI configuration

If you already configured settings in the UI, use the `@coderabbitai configuration` command on any PR to export the current settings as YAML. Copy that output into a `.coderabbit.yaml` file at repository root.

## Configure CodeRabbit using a YAML file

The `.coderabbit.yaml` file must be located at repository root. CodeRabbit uses the version from the feature branch under review.

### Example configuration

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: "en-US"
early_access: false
reviews:
  profile: "chill"
  request_changes_workflow: false
  high_level_summary: true
  poem: true
  review_status: true
  review_details: false
  auto_review:
    enabled: true
    drafts: false
chat:
  auto_reply: true
```

## Configuration options

The configuration file supports many options for customizing CodeRabbit behavior. For complete option descriptions, see the [Configuration Reference](/reference/configuration#reference).

## Shared configuration

Shared configuration is generally not recommended because it can expose sensitive settings. Prefer [Central Configuration](/configuration/central-configuration) for multi-repository management and [Configuration Inheritance](/configuration/configuration-inheritance) for layered reuse.

If you are self-hosting CodeRabbit in an air-gapped environment, shared configuration can still be used. In that case:

1. Host your shared `.coderabbit.yaml` at an internal URL that is reachable by your repositories.
2. Reference it from each repository-level `.coderabbit.yaml`:

```yaml
remote_config:
  url: "https://your-config-location/.coderabbit.yaml"
```

## Need help?

Code reviews begin on new pull requests or incremental commits after app installation. If you need help, visit the [support page](/support).
