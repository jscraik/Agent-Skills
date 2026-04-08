---
source: https://docs.coderabbit.ai/configuration/configuration-inheritance
---

Configuration inheritance allows you to share common settings across repositories while still allowing individual repositories to customize specific values. When enabled, CodeRabbit merges configuration from parent levels instead of using only the highest-priority source.

## Enabling inheritance

Add `inheritance: true` at the root level of your `.coderabbit.yaml` file:

```
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
inheritance: true
reviews:
  profile: chill
  auto_review:
    enabled: true
```

When inheritance is enabled:

1. CodeRabbit merges values from the parent configuration level
2. If the parent also has `inheritance: true`, the chain continues to the grandparent level
3. The chain stops at the first level where `inheritance:false` or not set

## Configuration hierarchy

CodeRabbit resolves configuration from multiple levels. Without inheritance, only the highest-priority source is used. With inheritance enabled, values merge across levels.

### Cloud/SaaS deployment

| Priority | Source | Location |
| --- | --- | --- |
| 1 (Highest) | Repository YAML | `.coderabbit.yaml` in the repository |
| 2 | Central YAML | `.coderabbit.yaml` in `coderabbit` repository |
| 3 | Repository UI | CodeRabbit UI - Repository Settings |
| 4 | Organization UI | CodeRabbit UI - Organization Settings |
| 5 (Lowest) | Defaults | CodeRabbit schema defaults |

### Self-hosted deployment

| Priority | Source | Location |
| --- | --- | --- |
| 1 (Highest) | Repository YAML | `.coderabbit.yaml` in the repository |
| 2 | Central YAML | `.coderabbit.yaml` in `coderabbit` repository |
| 3 | Environment YAML | `YAML_CONFIG` environment variable |
| 4 (Lowest) | Defaults | CodeRabbit schema defaults |

## How inheritance works

When you enable inheritance, CodeRabbit walks up the configuration hierarchy and merges values. The merge behavior depends on the data type.

### How the inheritance chain works

```
Repository YAML (inheritance: true)
       ↓ merges with
Central YAML (inheritance: true)
       ↓ merges with
Organization UI (inheritance: false)
       ✗ chain stops here
```

- Each level with `inheritance: true` merges with its parent
- The chain stops at the first level where `inheritance:false` or unset
- Missing configuration levels are skipped automatically

### Merge behavior by type

| Type | Behavior |
| --- | --- |
| __Objects__ | Deep merge - child properties override parent properties at each nesting level |
| __Arrays__ | Child items first, then unique parent items appended (deduplicated by `path`, `label`, `name`, `id`, or `key`) |
| __Scalars__ | Simple override - child value wins when defined |

### Example

This example demonstrates all three merge behaviors.
__Repository configuration__ (`.coderabbit.yaml`):

```
inheritance: true
language: "de-DE"
reviews:
  profile: assertive
  auto_review:
    drafts: false
  path_instructions:
    - path: "src/**"
      instructions: "Use strict TypeScript settings"
    - path: "api/**"
      instructions: "Validate API contracts"
```

__Central configuration__ (`coderabbit/.coderabbit.yaml`):

```
inheritance: true
language: "en-US"
reviews:
  profile: chill
  request_changes_workflow: true
  high_level_summary: true
  auto_review:
    enabled: true
    drafts: true
  path_instructions:
    - path: "src/**"
      instructions: "Follow our coding standards"
    - path: "docs/**"
      instructions: "Check for grammar and clarity"
    - path: "tests/**"
      instructions: "Ensure adequate test coverage"
chat:
  art: false
```

__Merged result__:

```
language: "de-DE" # scalar: child wins
reviews:
  profile: assertive # scalar: child wins
  request_changes_workflow: true # object: inherited from central
  high_level_summary: true # object: inherited from central
  auto_review:
    enabled: true # object: inherited from central
    drafts: false # scalar: child wins
  path_instructions: # array: child-first, then unique parent items
    - path: "src/**"
      instructions: "Use strict TypeScript settings" # from repo
    - path: "api/**"
      instructions: "Validate API contracts" # from repo
    - path: "docs/**"
      instructions: "Check for grammar and clarity" # from central (unique)
    - path: "tests/**"
      instructions: "Ensure adequate test coverage" # from central (unique)
chat:
  art: false # object: inherited from central
```

## Common use cases

### Organization-wide defaults

Set up common settings in your central `coderabbit` repository, then enable inheritance in individual repositories to use those defaults while customizing specific values.
__Central configuration__ (`organization/coderabbit/.coderabbit.yaml`):

```
inheritance: true
reviews:
  profile: chill
  request_changes_workflow: true
  high_level_summary: true
  path_instructions:
    - path: "**/*.test.*"
      instructions: "Verify test coverage and edge cases"
chat:
  art: false
```

__Repository configuration__ (`organization/my-repo/.coderabbit.yaml`):

```
inheritance: true
reviews:
  profile: assertive # This repo needs stricter reviews
  path_instructions:
    - path: "src/api/**"
      instructions: "Ensure backward compatibility"
```

The repository inherits all central settings but uses an assertive review profile and adds API-specific instructions.

### Team-specific configurations (GitLab)

GitLab's nested group structure allows team-specific configurations. Each team can have their own `coderabbit` repository with settings that inherit from parent groups.

```
company/coderabbit                     # Organization defaults
company/backend/coderabbit             # Backend team settings (inherits from company)
company/backend/payments/coderabbit    # Payments team settings (inherits from backend)
```

Each level can enable inheritance to merge with its parent while adding team-specific customizations.
