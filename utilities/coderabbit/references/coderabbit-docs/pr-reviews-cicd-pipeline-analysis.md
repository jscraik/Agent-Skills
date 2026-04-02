---
source: https://docs.coderabbit.ai/pr-reviews/cicd-pipeline-analysis
---

When a CI/CD pipeline fails on a pull request, CodeRabbit reads the failure output and posts inline comments with suggested fixes — directly on the lines of code that caused the failure.
This works across multiple CI/CD platforms: GitHub Actions, GitLab CI/CD, CircleCI, and Azure DevOps Pipelines.

## How it works

1. A pull request is opened or updated and your CI/CD pipelines run.
2. CodeRabbit waits for pipelines to finish (up to a configurable timeout).
3. CodeRabbit reads the failure logs and identifies the root cause.
4. Inline comments with suggested fixes are posted on the relevant lines of code.

## Supported platforms

| Platform | How CodeRabbit reads pipeline output |
| --- | --- |
| GitHub Actions | Via GitHub Checks — configure timeout under `reviews.tools.github-checks` |
| GitLab CI/CD | Via GitLab pipeline API, including GitLab Advanced Security SAST/DAST findings |
| CircleCI | Via CircleCI pipeline API (requires integration) |
| Azure DevOps Pipelines | Via Azure DevOps Checks API |

For GitHub Actions specifically, the timeout and enable/disable behavior is controlled by the `github-checks` tool configuration.

## What failures are analyzed

CI/CD pipeline analysis covers a broad range of failure types:

- **Build failures** — Docker, Node.js, Java, Python, Go module errors
- **Test failures** — unit, integration, and end-to-end test output
- **Security scan findings** — SAST and DAST output from tools like GitLab Advanced Security or custom pipeline steps
- **Infrastructure-as-code validation** — Terraform, Kubernetes, Ansible, and CloudFormation errors
- **Linter and code quality output** — any linter running as a pipeline step

## Configuration

For GitHub Actions, control how long CodeRabbit waits for checks to finish using `reviews.tools.github-checks.timeout_ms`.
If your pipelines take longer than 15 minutes, trigger a manual review once they finish:

For all other platforms (GitLab, CircleCI, Azure DevOps), CodeRabbit reads pipeline output automatically with no additional configuration required.

## What's next
