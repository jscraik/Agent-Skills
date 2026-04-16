---
source: https://docs.coderabbit.ai/pr-reviews/pre-merge-checks
---

Agentic Pre-Merge Checks provide automated validation of pull requests against standard quality metrics and organization-specific requirements. Use **Built-in Checks** for common requirements and add your own **Custom Checks** with natural language instructions tailored to your team's policies. These AI-powered checks can be configured by an Admin user at the organization or repository level, and CodeRabbit automatically validates every pull request against these requirements.

## Why use Pre-Merge Checks?

- **Consistent standards:** Enforce naming, documentation, and change-management hygiene across every PR.
- **Safer merges:** Catch breaking API changes, security gaps, or policy violations before they land.
- **Team-specific guardrails:** Encode architectural patterns, compliance rules, or business logic as custom checks.
- **Faster reviews:** Surface blocking issues early in the PR **Walkthrough** so reviewers can act quickly.

## Built-in Checks

CodeRabbit includes four standard checks that address common organizational needs:

## Custom Checks

Go beyond built-in checks by defining your own validation logic using natural language instructions. Custom checks leverage AI to understand and validate complex requirements specific to your team's policies, such as:

- Detecting sensitive data in logs
- Enforcing documentation for breaking changes
- Validating database migration patterns
- Ensuring compliance with language migration policies

Custom checks run in a secure, read-only sandbox and can access the PR diff, linked issues, and external context via MCP tools. Learn more about writing custom checks, including limitations and examples.

## Configuring Pre-merge Checks

### Enforcement Modes

Each check can be configured with one of three enforcement modes:

- `off`: Check is disabled
- `warning`: Display warnings but don't block merges (default)
- `error`: When paired with Request Changes Workflow, block merges until resolved or manually overridden

### Configuration

Pre-Merge Checks can be configured via web interface or using `.coderabbit.yaml` file.

Configure Pre-Merge Checks through the CodeRabbit dashboard:

For version-controlled configuration, add checks to your `.coderabbit.yaml` file:

```
reviews:
  pre_merge_checks:
    docstrings:
      mode: "error"
      threshold: 85
    title:
      mode: "warning"
      requirements: "Start with an imperative verb; keep under 50 characters."
    description:
      mode: "error"
    issue_assessment:
      mode: "warning"
    custom_checks:
      - name: "Undocumented Breaking Changes"
        mode: "warning"
        instructions: "Pass/fail criteria: All breaking changes to public APIs, CLI flags, environment variables, configuration keys, database schemas, or HTTP/GraphQL endpoints must be documented in the Breaking Change section of the PR description and in CHANGELOG.md. Exclude purely internal or private changes (e.g., code not exported from package entry points or explicitly marked as internal)."
```

## Results in the Walkthrough

Pre-Merge Check results appear alongside CodeRabbit's analysis in the PR **Walkthrough** with clear visual organization for quick assessment.
Results are organized into two tables:

- **Failed checks** — prominently displayed to show errors and warnings requiring attention
- **Passed checks** — expandable to review checks that were validated successfully

Each check displays:

- **Objective** — the name of the check being evaluated
- **Status** — one of:
  - Error — failed and will block merge when **Request Changes** is enabled
  - Warning — failed but non-blocking
  - Passed — requirements met
  - Inconclusive — incomplete instructions or insufficient information to decide
- **Explanation** — why the check passed or failed
- **Resolution** — what the author can do to remediate

### Unblocking a PR

If **Request Changes Workflow** is enabled and a check in **Error** mode fails, the PR is blocked until the issue is resolved or you explicitly ignore it. To ignore, select the **Ignore failed checks** checkbox in the PR Walkthrough. The PR is then unblocked and the affected rows are tagged **[IGNORED]** for traceability.

## Manual commands

Trigger pre-merge checks manually using chat commands:

### Run All Checks

```
@coderabbitai run pre-merge checks
```

This reruns all configured checks and updates results in the walkthrough.

### Test Custom Check

```
@coderabbitai evaluate custom pre-merge check --name <check_name> --instructions <text> [--mode <error|warning>]
```

Tests custom check logic before saving to configuration.

### Ignore failures

```
@coderabbitai ignore pre-merge checks
```

Manually ignore failed checks and unblock the PR.
