---
source: https://docs.coderabbit.ai/integrations/mcp-servers
---

# Integrate MCP servers

Connect CodeRabbit to external tools and data sources through the Model Context Protocol (MCP) integration. This allows CodeRabbit to serve as the MCP client and provides richer contextual understanding for enhanced code reviews.

## What MCP integration enables

## Supported integrations

Access your documentation, project management tools, knowledge bases, Figma designs, and more through MCP servers.

## Considerations

## Setup

## How it works

- During code reviews
- In chat interactions

CodeRabbit automatically calls relevant MCP tools during analysis to:

MCP integration enhances chat by providing access to:

## User guidance

The **User guidance** field is free-text instructions that CodeRabbit's AI agent reads before using your MCP server. Use it to tell the agent what information is available, what to look for, and why it matters for code reviews.
Some MCP servers need no additional guidance—the agent can figure out how to use their tools on its own. But many servers benefit from explicit context, especially when:

- The server stores a wide variety of content (for example, a Notion workspace covering engineering specs, meeting notes, HR policies, and runbooks)
- The server uses internal naming conventions or project keys that the agent can't guess
- The server is a custom in-house tool whose purpose isn't obvious from its tool names alone
- Resources are organized in non-standard hierarchies that the agent can't automatically navigate

### What to include in user guidance

Good user guidance answers three questions for the agent:

1. **What is stored here?** Describe the kind of information available on this MCP server.
2. **What should CodeRabbit look for?** Narrow the scope to what's relevant for code reviews.
3. **How is it organized?** Provide naming conventions, key formats, or URL patterns the agent needs to find the right resources.

### Example configurations

- Notion
- Custom in-house MCP server
- Jenkins
- SonarQube
- Azure DevOps

Notion workspaces can contain many different types of content. Tell the agent which pages or databases are relevant to code reviews:

```
This Notion workspace contains our engineering documentation.
For code reviews, look in the "Engineering" space—specifically:
- "Architecture Decisions" for design rationale
- "API Contracts" for interface specifications
- "Service Runbooks" for operational context

Do not pull content from HR, Finance, or Company-wide spaces.
```

For internal tools, explain what the server exposes and why it's useful for reviews:

```
This is our internal quality gate service. It provides:
- Static analysis results for each pull request
- Security scan findings from our custom ruleset
- Architecture compliance checks against our approved patterns

Always fetch the quality gate report for the current PR before commenting
on code quality or security issues. Results are indexed by repository name
and PR number.
```

If your Jenkins jobs are organized in folders that CodeRabbit can't automatically discover:

```
Jenkins builds are located at:
https://jenkins.company.com/job/{workspace}/job/{repo}/job/PR-{pr}/

Use getBuild or getBuildLog to fetch build results directly from this path.
```

If your SonarQube project keys follow a naming convention:

```
SonarQube project key format: {org}_{repo}
Dashboard: https://sonar.company.com/dashboard?id={org}_{repo}
```

For Azure DevOps pipelines using project-specific paths:

```
Pipeline runs: https://dev.azure.com/{org}/{project}/_build?definitionId=1&branchName=refs/pull/{pr}/merge
```

### URL template placeholders

When guidance includes URLs that change per pull request, use **placeholders** that CodeRabbit automatically expands with values from the current PR:

```
https://jenkins.company.com/job/{workspace}/job/{repo}/job/PR-{pr}/
```

#### Available placeholders

| Placeholder | Description | Example value |
| --- | --- | --- |
| `{repo}`, `{repo name}`, `{repository}` | Repository name | `my-backend` |
| `{pr}`, `{pr number}` | Pull request number | `42` |
| `{mr}`, `{mr number}` | Merge request number (GitLab) | `42` |
| `{workspace}`, `{owner}`, `{org}` | Organization or workspace | `acme-corp` |
| `{project}` | Project name (Azure DevOps) | `MyProject` |
