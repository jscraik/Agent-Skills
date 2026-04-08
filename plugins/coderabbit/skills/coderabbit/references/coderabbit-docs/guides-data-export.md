---
source: https://docs.coderabbit.ai/guides/data-export
---

# Data Export Fields

CodeRabbit data exports include pull-request, author, repository, and review-comment metrics. Handle exported datasets using your organization's data-classification policy and retention requirements.

## Field reference

| Field | Type | Description |
| --- | --- | --- |
| `pr_url` | String | Full URL to the pull request. |
| `author_id` | String | Stable numeric identifier from your Git provider. |
| `author_username` | String | PR author username. |
| `organization_id` | String | Stable organization identifier from your Git provider. |
| `organization_name` | String | Organization name. |
| `repository_id` | String | Stable repository identifier from your Git provider. |
| `repository_name` | String | Repository name. |
| `created_at` | ISO 8601 | PR creation timestamp. |
| `first_human_review_at` | ISO 8601 | Timestamp of first human review (empty if none). |
| `last_commit_at` | ISO 8601 | Timestamp of last non-merge, non-rebase commit. |
| `merged_at` | ISO 8601 | Merge timestamp. |
| `estimated_complexity` | Integer | Complexity score (1-5). |
| `estimated_review_minutes` | Integer | Estimated review time in minutes. |
| `total_coderabbit_comments_posted` | Integer | Total CodeRabbit comments posted. |
| `total_coderabbit_comments_accepted` | Integer | Total CodeRabbit comments accepted. |
| `critical_comments_posted` | Integer | Critical comments posted. |
| `critical_comments_accepted` | Integer | Critical comments accepted. |
| `major_comments_posted` | Integer | Major comments posted. |
| `major_comments_accepted` | Integer | Major comments accepted. |
| `minor_comments_posted` | Integer | Minor comments posted. |
| `minor_comments_accepted` | Integer | Minor comments accepted. |
| `trivial_comments_posted` | Integer | Trivial comments posted. |
| `trivial_comments_accepted` | Integer | Trivial comments accepted. |
| `info_comments_posted` | Integer | Info comments posted. |
| `info_comments_accepted` | Integer | Info comments accepted. |
| `security_and_privacy_comments_posted` | Integer | Security and privacy comments posted. |
| `security_and_privacy_comments_accepted` | Integer | Security and privacy comments accepted. |
| `performance_and_scalability_comments_posted` | Integer | Performance/scalability comments posted. |
| `performance_and_scalability_comments_accepted` | Integer | Performance/scalability comments accepted. |
| `functional_correctness_comments_posted` | Integer | Functional-correctness comments posted. |
| `functional_correctness_comments_accepted` | Integer | Functional-correctness comments accepted. |
| `maintainability_and_code_quality_comments_posted` | Integer | Maintainability/code-quality comments posted. |
| `maintainability_and_code_quality_comments_accepted` | Integer | Maintainability/code-quality comments accepted. |
| `data_integrity_and_integration_comments_posted` | Integer | Data-integrity/integration comments posted. |
| `data_integrity_and_integration_comments_accepted` | Integer | Data-integrity/integration comments accepted. |
| `stability_and_availability_comments_posted` | Integer | Stability/availability comments posted. |
| `stability_and_availability_comments_accepted` | Integer | Stability/availability comments accepted. |

## Data governance notes

- Treat exported `author_id`, `organization_id`, and `repository_id` as operational identifiers that may still be sensitive in aggregated datasets.
- Apply least-privilege access controls to export storage locations.
- Follow internal retention and deletion policies for analytics exports.
