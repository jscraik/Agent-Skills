---
source: https://docs.coderabbit.ai/reference/configuration
---

# Configuration Reference

CodeRabbit's behavior can be customized using a `.coderabbit.yaml` file in your repository root. This reference covers all available configuration options with clear property names and examples.

## Configuration Sections

## General settings

### Reference

Set the language for reviews by using the corresponding ISO language code. Defaults to "en-US".

Set the tone of reviews and chat. Example: 'You must talk like Mr. T. I pity the fool who doesn't!' Defaults to "".

Enable early-access features. Defaults to false.

Enable free tier features for users not on a paid plan. Defaults to true.

## Reviews

Settings related to reviews.

### Reference

- **review_status**: Set the review profile: `chill` for lighter feedback, `assertive` for more feedback. Defaults to "chill".
- **auto_approve**: Automatically approve once CodeRabbit's comments are resolved and no pre-merge checks are failing. Defaults to false.
- **high_level_summary**: Generate a high-level summary of the changes in the PR description or walkthrough. Defaults to true.
- **high_level_summary_instructions**: Customize the summary content and format. Defaults to "".
- **high_level_summary_placeholder**: Placeholder in the PR description that CodeRabbit replaces with the summary. Defaults to "@coderabbitai summary".
- **high_level_summary_in_walkthrough**: Include the high-level summary in the walkthrough comment. Defaults to false.
- **auto_title_placeholder**: Add this keyword to the PR title to auto-generate a title. Defaults to "@coderabbitai".
- **review_status**: Post review status messages in the walkthrough summary comment. Defaults to true.
- **review_details**: Post review details (ignored files, extra context used, suppressed comments, etc.). Defaults to false.
- **commit_status**: Set the commit status to 'pending' when review is in progress and 'success' when complete. Defaults to true.
- **commit_status_fail**: Set commit status to 'failure' when the PR cannot be reviewed. Defaults to false.
- **walkthrough_collapsible**: Wrap the walkthrough in a Markdown collapsible section. Defaults to true.
- **changed_files_summary**: Include a summary of the changed files in the walkthrough. Defaults to true.
- **sequence_diagrams**: Include sequence diagrams in the walkthrough. Defaults to true.
- **estimate_code_review_effort**: Include estimated code review effort in the walkthrough. Defaults to true.
- **issue_assessment**: Include assessment of how well changes address linked issues. Defaults to true.
- **related_issues**: Include potentially related issues in the walkthrough. Defaults to true.
- **related_prs**: Include potentially related PRs in the walkthrough. Defaults to true.
- **suggest_labels**: Suggest labels based on the changes. Defaults to true.
- **labeling_instructions**: Define allowed labels and when to suggest them. Defaults to [].
- **auto_apply_labels**: Automatically apply suggested labels to the PR. Defaults to false.
- **suggest_reviewers**: Suggest reviewers based on the changes. Defaults to true.
- **auto_assign_reviewers**: Automatically assign suggested reviewers. Defaults to false.
- **poem**: Generate a poem in the walkthrough comment. Defaults to true.
- **fortune**: Post a fortune message while review is running. Defaults to true.
- **enable_prompt_for_ai_agents**: Include the 'Prompt for AI Agents' section in inline review comments. Defaults to true.
- **path_filters**: Specify file patterns to include or exclude using glob patterns. Defaults to [].
- **path_instructions**: Add path-specific guidance for code review. Defaults to [].
- **abort_on_close**: Abort in-progress review if PR is closed or merged. Defaults to true.
- **disable_cache**: Disable caching of code and dependencies. Defaults to false.

### Auto review

- **enabled**: Review PRs automatically. Defaults to true.
- **keyword**: Keyword in PR description that triggers a review when automatic reviews are disabled. Defaults to "".
- **incremental**: Re-run the review on each push. Defaults to true.
- **auto_pause_after_reviewed_commits**: Pause automatic reviews after this many reviewed commits. Set to 0 to disable. Defaults to 5.
- **skip_titles_keywords**: Skip reviews when PR title contains any of these keywords. Defaults to [].
- **review_labels**: Labels that control which PRs are reviewed. Labels starting with '!' are negative matches. Defaults to [].
- **drafts**: Include draft PRs. Defaults to false.
- **base_branches**: Base branches (other than default) to review. Accepts regex patterns. Defaults to [].
- **ignored_reviewer_usernames**: Skip reviews for PRs authored by these usernames. Defaults to [].

### Finishing touches

- **docstrings**: Enable docstring generation. Defaults to true.
- **unit_tests**: Generate unit tests for changes in PRs. Defaults to true.
- **custom_recipes**: Define up to 5 custom finishing touch recipes. Trigger with `@coderabbitai run <recipe name>`. Defaults to [].

### Pre merge checks

- **docstring_coverage**: Check docstring coverage meets threshold. Mode: off/warning/error. Defaults to warning with 80% threshold.
- **title_check**: Validate PR title against requirements. Mode: off/warning/error.
- **description_check**: Check PR description follows best practices. Mode: off/warning/error.
- **linked_issue_assessment**: Assess how well PR addresses linked issues. Mode: off/warning/error.
- **custom_checks**: Define up to 5 custom pre-merge checks. Each needs unique name (<=50 chars) and deterministic instructions (<=10,000 chars).

### Tools

Tools that provide additional context to code reviews. Each tool can be enabled/disabled individually. All default to `true`.

Supported tools include:
- **ast-grep**: Code analysis using AST patterns (v0.40.5)
- **shellcheck**: Static analysis for shell scripts (v0.11.0)
- **ruff**: Python linter and formatter (v0.15.1)
- **markdownlint**: Markdown linting (v0.21.0)
- **github-checks**: GitHub Checks integration (90s default timeout)
- **languagetool**: Style and grammar checker for 30+ languages
- **biome**: Formatter, linter, and analyzer for web projects (v2.4.2)
- **hadolint**: Dockerfile linter (v2.14.0)
- **swiftlint**: Swift linter (v0.63.2)
- **phpstan**: PHP static analysis (v2.1.39)
- **phpmd**: PHP mess detector (v2.15.0)
- **phpcs**: PHP CodeSniffer (v3.7.2)
- **golangci-lint**: Go linters runner (v2.5.0)
- **yamllint**: YAML linter (v1.38.0)
- **gitleaks**: Secret scanner (v8.30.0)
- **trufflehog**: Secret scanner with verification (v3.93.3)
- **checkov**: IaC static analysis (v3.2.334)
- **tflint**: Terraform linter (v0.61.0)
- **detekt**: Kotlin static analysis (v1.23.8)
- **eslint**: JavaScript linting
- **flake8**: Python linter (v7.3.0)
- **fortitudeLint**: Fortran linter (v0.8.0)
- **rubocop**: Ruby linter/formatter (v1.84.2)
- **buf**: Protobuf linting (v1.65.0)
- **regal**: Rego linter (v0.38.1)
- **actionlint**: GitHub Actions checker (v1.7.11)
- **pmd**: Java static analyzer (v7.21.0)
- **clang**: C/C++ static analysis (v14.0.6)
- **cppcheck**: C/C++ static analysis (v2.19.0)
- **opengrep**: High-performance static analysis (v1.16.0)
- **semgrep**: Security and quality scanning (v1.151.0)
- **circleci**: CircleCI config checker (v0.1.34422)
- **clippy**: Rust lints
- **sqlfluff**: SQL linter (v4.0.4)
- **trivy**: IaC security scanner (v0.69.1)
- **prismaLint**: Prisma Schema linting (v0.13.1)
- **pylint**: Python static analysis (v4.0.4)
- **oxc**: JavaScript/TypeScript linter (v1.48.0)
- **shopifyThemeCheck**: Shopify theme linter
- **luacheck**: Lua linting (v1.2.0)
- **brakeman**: Ruby on Rails security scanner (v8.0.2)
- **dotenvLint**: .env file linter (v4.0.0)
- **htmlhint**: HTML linting (v1.9.1)
- **stylelint**: Stylesheet linting (v17.3.0)
- **checkmake**: Makefile linter (v0.2.2)
- **osvScanner**: Vulnerability package scanner (v2.3.3)
- **blinter**: Windows batch file linter (v1.0.112)
- **psscriptanalyzer**: PowerShell static checker (v1.24.0)

## Chat

Configuration for chat.

- **art**: Generate art in chat responses (ASCII or emoji). Defaults to true.
- **auto_reply**: Let CodeRabbit reply automatically without requiring a mention/tag. Defaults to true.

### Integrations

- **jira**: Allow creating Jira issues from chat. 'auto' disables for public repos. Options: auto/enabled/disabled. Defaults to "auto".
- **linear**: Allow creating Linear issues from chat. 'auto' disables for public repos. Options: auto/enabled/disabled. Defaults to "auto".

## Knowledge base

Configuration for knowledge base.

- **opt_out**: Disable knowledge base features that require data retention. Defaults to false.
- **web_search**: Use web search to gather additional context. Defaults to true.
- **code_guidelines**: Use coding guideline documents as review criteria. File patterns include .cursorrules, .github/copilot-instructions.md, CLAUDE.md, GEMINI.md, AGENTS.md, etc.
- **learnings**: Scope for learnings: local/global/auto. Defaults to "auto".
- **issues**: Scope for GitHub/GitLab issues: local/global/auto. Defaults to "auto".
- **jira**: Use Jira as knowledge source. Options: auto/enabled/disabled.
- **linear**: Use Linear as knowledge source. Options: auto/enabled/disabled.
- **pull_requests**: Scope for PRs: local/global/auto. Defaults to "auto".
- **mcp**: Use MCP servers as knowledge source. Options: auto/enabled/disabled. Defaults to "auto".
- **linked_repositories**: Repositories that CodeRabbit should consider when reviewing PRs. Defaults to [].

## Code generation

Configuration for code generation.

- **docstrings**: Settings for generating docstrings. Includes language and path_instructions.
- **unit_tests**: Settings for generating unit tests. Includes path_instructions.

## Issue enrichment

Configuration for issue enrichment.

- **auto_enrich**: Analyze and enrich issues with additional context. Defaults to false.
- **planning**: Generate implementation plan for issues. Defaults to true.
- **auto_planning**: Trigger issue planning based on labels. Defaults to true.
- **labeling**: Define issue labels to suggest. Includes auto_apply option. Defaults to false.
