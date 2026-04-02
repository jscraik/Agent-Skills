---
source: https://docs.coderabbit.ai/guides/data-export
---

|  |  |  |
| --- | --- | --- |
| `pr_url` | String | Full URL to the pull request |
| `author_id` | String | Unique numeric identifier assigned by your Git provider (GitHub, GitLab, etc.). Unlike usernames, this ID remains constant even if the user changes their username. |
| `author_username` | String | Username of the PR author |
| `organization_id` | String | Unique identifier for the organization assigned by your Git provider. Unlike organization names, this ID remains constant even if the organization is renamed. |
| `organization_name` | String | Organization name |
| `repository_id` | String | Unique numeric identifier assigned by your Git provider. Unlike repository names, this ID remains constant even if the repository is renamed or transferred to a different owner. |
| `repository_name` | String | Repository name |
| `created_at` | ISO 8601 | When the PR was created |
| `first_human_review_at` | ISO 8601 | When the first human review was submitted (empty if no human reviewers) |
| `last_commit_at` | ISO 8601 | When the last non-merge, non-rebased commit was pushed (empty if no new commits) |
| `merged_at` | ISO 8601 | When the PR was merged |
| `estimated_complexity` | Integer | Complexity score (1-5) |
| `estimated_review_minutes` | Integer | Estimated time to review in minutes |
| `total_coderabbit_comments_posted` | Integer | Total review comments posted by CodeRabbit |
| `total_coderabbit_comments_accepted` | Integer | Total CodeRabbit review comments accepted |
| `critical_comments_posted` | Integer | Critical severity comments posted |
| `critical_comments_accepted` | Integer | Critical severity comments accepted |
| `major_comments_posted` | Integer | Major severity comments posted |
| `major_comments_accepted` | Integer | Major severity comments accepted |
| `minor_comments_posted` | Integer | Minor severity comments posted |
| `minor_comments_accepted` | Integer | Minor severity comments accepted |
| `trivial_comments_posted` | Integer | Trivial severity comments posted |
| `trivial_comments_accepted` | Integer | Trivial severity comments accepted |
| `info_comments_posted` | Integer | Info severity comments posted |
| `info_comments_accepted` | Integer | Info severity comments accepted |
| `security_and_privacy_comments_posted` | Integer | Security & Privacy category comments posted |
| `security_and_privacy_comments_accepted` | Integer | Security & Privacy category comments accepted |
| `performance_and_scalability_comments_posted` | Integer | Performance & Scalability category comments posted |
| `performance_and_scalability_comments_accepted` | Integer | Performance & Scalability category comments accepted |
| `functional_correctness_comments_posted` | Integer | Functional Correctness category comments posted |
| `functional_correctness_comments_accepted` | Integer | Functional Correctness category comments accepted |
| `maintainability_and_code_quality_comments_posted` | Integer | Maintainability & Code Quality category comments posted |
| `maintainability_and_code_quality_comments_accepted` | Integer | Maintainability & Code Quality category comments accepted |
| `data_integrity_and_integration_comments_posted` | Integer | Data Integrity & Integration category comments posted |
| `data_integrity_and_integration_comments_accepted` | Integer | Data Integrity & Integration category comments accepted |
| `stability_and_availability_comments_posted` | Integer | Stability & Availability category comments posted |
| `stability_and_availability_comments_accepted` | Integer | Stability & Availability category comments accepted |
