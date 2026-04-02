---
source: https://docs.coderabbit.ai/guides/configuration-overview
---

# Configuration Overview

Configure CodeRabbit to fit your organization and repositories using multiple approaches with clear priority rules.

CodeRabbit works out of the box with sensible defaults, but configuration lets you customize reviews for your team's specific needs. Choose from multiple configuration approaches based on your workflow preferences.

## Configuration approaches

### File-based

### Web Interface-based

### Organization settings

Use organization settings when you want consistent CodeRabbit behavior across all your repositories. Configure once in the web UI and all repositories inherit the same settings.

Best for: Teams with standardized coding practices across projects.

See Organization preferences.

### Repository settings

Use repository settings when different projects need different CodeRabbit configurations. Configure each repository individually through the web UI or with a local `.coderabbit.yaml` file.

Best for: Organizations with diverse projects requiring specific review approaches.

See Repository preferences.

### YAML file (recommended)

Create a `.coderabbit.yaml` file in your repository root for version-controlled configuration. This approach gives you the benefits of infrastructure-as-code: configuration changes go through code review, maintain history, and deploy with your application.

Best for: Teams that prefer GitOps workflows and want configuration changes tracked in version control.

See the configuration reference for all available options and sample configurations for language-specific recommendations.

### Central configuration

Create a dedicated `coderabbit` repository in your organization with a `.coderabbit.yaml` file. This configuration automatically applies to any repository that doesn't have its own settings, giving you organization-wide defaults with the flexibility of repository-specific overrides.

Best for: Organizations wanting centralized configuration management without requiring individual repository setup.

See Central configuration for setup instructions and platform support.

## Understanding configuration priority

Configuration sources don't merge by default. When you use multiple configuration methods, CodeRabbit follows a strict priority hierarchy.

**Example:** If you set a custom timeout in organization settings and central configuration but have a local `.coderabbit.yaml` that doesn't mention timeouts and `configuration inheritance` is disabled, CodeRabbit uses the default timeout value, not your organization or central configuration settings.

## Adaptive configuration

Besides manual configuration, CodeRabbit automatically builds learnings about your team's review preferences based on your interactions with review comments over time. This creates a dynamic, self-improving configuration layer.

Learnings capture patterns like:

- Which types of suggestions your team typically accepts or rejects
- Coding standards specific to your repositories
- Review focus areas that matter most to your workflow
