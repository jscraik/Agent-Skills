---
source: https://docs.coderabbit.ai/knowledge-base/mcp-context
---

# MCP Servers

MCP (Model Context Protocol) servers are a knowledge source that CodeRabbit can query during reviews and chat. By connecting MCP servers to CodeRabbit, you give it access to context from your external tools — such as documentation systems, design files, and project management platforms — so that review comments and chat responses reflect your organization's full context.

## What MCP servers add to reviews

When MCP servers are connected, CodeRabbit can draw on external context beyond the code itself. Supported integrations include:

- **Documentation and knowledge bases** — Internal docs, wikis, and reference material
- **Project management tools** — Issues, tickets, and project specs
- **Design tools** — Figma designs and related design assets
- **Any tool with an MCP server** — If a tool publishes an MCP server, CodeRabbit can connect to it without waiting for a formal integration

This makes review comments more relevant to your team's standards and project context.

## How CodeRabbit uses MCP during analysis

CodeRabbit acts as the MCP **client** — it ingests data from your connected MCP servers, not the other way around. During a code review or chat interaction, CodeRabbit:

CodeRabbit searches your connected MCP tools automatically, but some tools organize their resources in ways that hard to be discovered without a hint—for example, Jenkins Organization Folders or SonarQube projects with custom key formats. In those cases you can supply **user guidance**: URL patterns with placeholders like `{repo}` or `{pr}` that tell CodeRabbit exactly where to look for each pull request. See User guidance for the full reference and examples.

## Examples of MCP server types

Based on the integrations described in the CodeRabbit documentation, common categories of MCP servers you can connect include:

| Category | Examples |
| --- | --- |
| Documentation systems | Internal wikis, Confluence spaces, Context7 |
| Design tools | Figma files and design assets |
| Project management | Issue trackers, project boards |
| Knowledge bases | Team knowledge bases and reference documentation |

## Configuration

Once an MCP server is connected, control its usage with the `knowledge_base.mcp` section of your `.coderabbit.yaml` file:

```
knowledge_base:
  mcp:
    usage: auto
    disabled_servers:
      - my-disabled-server
```

- The `usage` field (`auto` | `enabled` | `disabled`) Controls whether MCP servers are used as a knowledge source. `auto` disables MCP for public repositories. Use `enabled` to activate for all repositories, or `disabled` to turn off entirely.
- The `disabled_servers` field allows you to selectively disable specific servers by name.

For instructions on connecting and configuring MCP servers in the CodeRabbit app, see Integrate MCP servers.

## What's next
