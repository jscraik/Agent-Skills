---
source: https://docs.coderabbit.ai/knowledge-base/multi-repo-analysis
---

# Multi-Repo Analysis

Link related repositories so CodeRabbit can detect breaking changes, API mismatches, and dependency issues that cross repository boundaries during code review.

CodeRabbit can pull context from other repositories in the same organization when reviewing pull requests. When a code change touches a shared API, type definition, or database schema, CodeRabbit's research agent automatically explores linked repositories and surfaces downstream impact -- without you having to manually check each affected codebase.

## Use cases

Multi-repo analysis is most valuable when your codebase is split across several repositories that share contracts or dependencies:

- **Microservices architectures** -- A change to a service's REST API may break consumers in other repositories.
- **Shared libraries** -- Modifications to a shared utility or type definition can have ripple effects across multiple repositories.
- **API contracts** -- When a backend API changes, frontend or mobile repositories may need coordinated updates.
- **Database schemas** -- Schema changes can affect all services that query the same data model.

## How it works during reviews

When you submit a pull request, CodeRabbit inspects the changes and determines whether they may affect the linked repositories. If the research agent finds relevant cross-repository impact, it includes those findings in the review. If the changes are self-contained and have no cross-repo effect, the agent does not produce findings -- this is expected behavior and does not indicate a misconfiguration.

## Where findings appear

Cross-repository findings appear in the pull request review summary comment under **Review details** > **Additional context used**, grouped by linked repository name. Findings also surface in inline review comments and comment replies when relevant.

To see the **Review details** section, enable `review_details` in your configuration:

```yaml
reviews:
  review_details: true
```

## Setting it up

Linked repositories are configured through the CodeRabbit web interface or via your `.coderabbit.yaml` file.

In most cases, you want to configure this at the **repository level** -- for example, linking your frontend repository to your backend, or your client repository to your server. Configuring linked repositories at the organization level applies the same linked repository to _every_ repository in your organization, which is rarely what you want. If you need to share a default linked repository across repos while still allowing per-repo overrides, see configuration inheritance.

YAML Configuration:

Add a `linked_repositories` section under `knowledge_base` in your `.coderabbit.yaml` file inside the repository you want to configure (for example, your frontend repo):

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
knowledge_base:
  linked_repositories:
    - repository: "myorg/backend-api"
      instructions: "Contains REST API endpoints and database models"
```

### Configuration fields

| Field | Required | Description |
| --- | --- | --- |
| `repository` | Yes | Repository in `org/repo` format (GitHub) or `group/subgroup/repo` format (GitLab) |
| `instructions` | No | Description and guidance on what the repository contains (max 2,000 characters) |

## Platform requirements

The CodeRabbit bot must have read access to all linked repositories.

| Platform | Requirement |
| --- | --- |
| **GitHub** | The CodeRabbit GitHub App must be installed on all linked repositories. Inaccessible repositories are skipped, and a warning appears in the review summary. |
| **GitLab** | The bot token must have read access. Tokens are typically scoped to the group or instance. |
| **Bitbucket Cloud** | The bot token must have read access. Tokens are scoped to the workspace. |
| **Azure DevOps** | The PAT must have read access. Tokens are scoped to the organization. |

## Configuration inheritance

When configuration inheritance is enabled, organization-level and repository-level `linked_repositories` settings are merged. Repository-level entries take priority: if both levels define the same repository, the repository-level instructions are used.

After merging, the list is truncated to one entry, with the repository-level entry preserved. If any repositories are dropped during this process, a warning appears in the review summary showing which repositories were kept and which were skipped.

## Limitations

- **Same platform only**: All linked repositories must be on the same platform as the pull request under review. You cannot link a GitHub repository to a GitLab repository, because access tokens are platform-specific.

## Troubleshooting

If cross-repository context is not appearing in reviews, work through these checks in order.
