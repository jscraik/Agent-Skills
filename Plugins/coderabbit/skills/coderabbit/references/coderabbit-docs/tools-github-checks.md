---
source: https://docs.coderabbit.ai/tools/github-checks
---

# GitHub Checks

## How it works
When a pull request is opened or updated, CodeRabbit waits for GitHub Checks to finish and then reads their output. Any failures are analyzed and surfaced as inline review comments on the relevant lines of code, alongside suggested fixes.
This integration covers a broad range of check types including:

- Build failures (Docker, Node.js, Java, Python, Go, etc.)

- Test failures (unit, integration, end-to-end)

- Security scan findings (SAST, DAST, container scanning)

- Infrastructure-as-code validation (Terraform, Kubernetes, Ansible)

- Linter output from tools running in your CI pipeline

## Configuration
GitHub Checks integration is enabled by default. You can configure it — including the timeout CodeRabbit waits for checks to finish — using your `.coderabbit.yaml` file or the CodeRabbit web UI.
- .coderabbit.yaml
- Web UI
.coderabbit.yaml

`reviews:
 tools:
 github-checks:
 enabled: true
 timeout_ms: 90000
`Go to **Reviews → Tools → GitHub Checks** in your organization or repository settings to toggle the integration on or off and adjust the timeout.
### Options
OptionTypeDefaultDescription`enabled`boolean`true`Enable or disable the GitHub Checks integration.`timeout_ms`number`90000`Milliseconds CodeRabbit waits for all checks to finish before proceeding with the review. Minimum: `0`. Maximum: `900000` (15 minutes).
## Adjusting the timeout
By default, CodeRabbit waits 90 seconds (90,000 ms) for GitHub Checks to complete. If your pipelines regularly take longer, increase `timeout_ms` up to the 15-minute maximum:
.coderabbit.yaml

`reviews:
 tools:
 github-checks:
 timeout_ms: 900000
`
If your pipelines exceed 15 minutes, trigger a manual review once they finish so CodeRabbit can incorporate the results:

`@coderabbitai review
`
## When CodeRabbit skips GitHub Checks
CodeRabbit skips the GitHub Checks integration when:

- `enabled` is set to `false`.

- The repository is not hosted on GitHub.

- No checks have run within the configured `timeout_ms` window.

## What’s next

## CI/CD pipeline analysisLearn how CodeRabbit reads CI/CD pipeline failures and posts inline remediation suggestions across GitHub Actions, GitLab, CircleCI, and Azure DevOps.

## All supported toolsBrowse the complete list of linters, security analyzers, and CI/CD integrations available in CodeRabbit.

## Configuration referenceFull reference for all available options, including how to enable, disable, and tune individual tools.
