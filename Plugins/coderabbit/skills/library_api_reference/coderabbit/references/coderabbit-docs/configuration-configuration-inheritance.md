---
source: https://docs.coderabbit.ai/configuration/configuration-inheritance
---

# Configuration Inheritance

Configuration inheritance lets you share defaults across repositories while still customizing local behavior. When `inheritance: true` is enabled, CodeRabbit merges parent and child configuration instead of using only the highest-priority source.

## Enabling inheritance

Add `inheritance: true` at the root of `.coderabbit.yaml`:

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
inheritance: true
reviews:
  profile: chill
  auto_review:
    enabled: true
```

When inheritance is enabled:

1. CodeRabbit merges values from the parent level.
2. If the parent also enables inheritance, the merge continues upward.
3. The chain stops at the first level where `inheritance: false` (or unset).

## Configuration hierarchy

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

### Inheritance chain example

```text
Repository YAML (inheritance: true)
       ↓ merges with
Central YAML (inheritance: true)
       ↓ merges with
Organization UI (inheritance: false)
       ✗ chain stops here
```

- Each level with `inheritance: true` merges with its parent.
- The chain stops when `inheritance` is false or unset.
- Missing levels are skipped.

### Merge behavior by type

| Type | Behavior |
| --- | --- |
| Objects | Deep merge; child properties override parent properties at matching paths. |
| Arrays | Child-first; then unique parent items appended (dedupe by `path`, `label`, `name`, `id`, `key`). |
| Scalars | Child value overrides parent value when defined. |

## Example

### Repository configuration (`.coderabbit.yaml`)

```yaml
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

### Central configuration (`coderabbit/.coderabbit.yaml`)

```yaml
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
    - path: "Infrastructure/tests/**"
      instructions: "Ensure adequate test coverage"
chat:
  art: false
```

### Merged result

```yaml
language: "de-DE"
reviews:
  profile: assertive
  request_changes_workflow: true
  high_level_summary: true
  auto_review:
    enabled: true
    drafts: false
  path_instructions:
    - path: "src/**"
      instructions: "Use strict TypeScript settings"
    - path: "api/**"
      instructions: "Validate API contracts"
    - path: "docs/**"
      instructions: "Check for grammar and clarity"
    - path: "Infrastructure/tests/**"
      instructions: "Ensure adequate test coverage"
chat:
  art: false
```

## Common use cases

### Organization-wide defaults

Use a central `coderabbit` repository for defaults, then enable inheritance in individual repositories for targeted overrides.

### Team-specific configurations (GitLab)

GitLab nested groups can layer configuration naturally:

```text
company/coderabbit
company/backend/coderabbit
company/backend/payments/coderabbit
```

Each level can merge parent settings while adding team-specific rules.
