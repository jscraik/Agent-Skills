---
source: https://docs.coderabbit.ai/configuration/central-configuration
---

# Central configuration

Maintain CodeRabbit configuration for your entire organization in one dedicated repository. Create a `coderabbit` repository in your organization and add your `.coderabbit.yaml` file - CodeRabbit automatically applies these settings to any repository that doesn't have its own configuration.

## How configuration resolution works

CodeRabbit checks for configuration in this priority order:

| Priority | Source | Location |
| --- | --- | --- |
| 1 (Highest) | Repository file | `.coderabbit.yaml` in the repository |
| 2 | Central repository | `.coderabbit.yaml` in `coderabbit` repository |
| 3 | Repository settings | CodeRabbit UI - Repository Settings |
| 4 | Organization settings | CodeRabbit UI - Organization Settings |
| 5 (Lowest) | Default settings | CodeRabbit schema defaults |

The configuration source appears in the CodeRabbit comment on the pull request:

- **Repository file**: `Path: .coderabbit.yaml`
- **Central repository**: `Repository: coderabbit/.coderabbit.yaml`
- **UI settings**: `CodeRabbit UI`

## Setup

## GitLab hierarchical configuration

GitLab supports team-specific configurations through its nested group structure. CodeRabbit automatically finds the closest `coderabbit` repository in your group hierarchy, allowing different teams to have their own settings while maintaining organization-wide defaults.
**Configuration inheritance example**:

| Project path | Configuration used |
| --- | --- |
| `company/team-a/subteam/project1` | `company/team-a/subteam/coderabbit` |
| `company/team-a/project2` | `company/team-a/coderabbit` |
| `company/team-b/project3` | `company/coderabbit` |

This enables team-specific configurations with automatic fallback to parent group settings.

## Platform limitations

- **Azure DevOps**: Each project requires its own `coderabbit` repository - no cross-project configuration sharing
- **Bitbucket Server**: Central configuration not yet implemented - use individual repository settings

## Repository overrides

Individual repositories can override central configuration by adding their own `.coderabbit.yaml` file.

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
# Repository-specific config
reviews:
  profile: assertive
  high_level_summary: true
  poem: true
  review_status: true
  auto_review:
    enabled: true
    drafts: false
chat:
  art: true
```

When a repository has its own configuration file, CodeRabbit uses that instead of the central configuration. Repository settings take precedence over central settings.

- Configuration overview - Understanding CodeRabbit configuration options
- Organization settings - Managing organization-level settings
- Repository settings - Configuring individual repositories
- Configuration reference - Complete configuration reference
