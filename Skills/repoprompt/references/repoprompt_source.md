# Repo Prompt Source Notes (Provided)

Use this as source material for summaries and explanations. Prefer concise paraphrase over long quotes. Avoid inventing pricing or feature availability; use what is here or ask.

## Overview

Repo Prompt helps build token-efficient, context-rich prompts so AI models understand code better. It targets the common problem of too little context (hallucinations) vs too much (token waste). Typical pain points:
- Manual copy/paste of files
- Blind agent discovery that burns tokens
- Paying per-token API costs for discovery

### Solution summary
1) Token-efficient context building
- Full content for active files
- Slices for targeted ranges
- Codemaps for signatures only

2) Use existing AI subscriptions via CLI providers
- Claude MAX / ChatGPT Plus or Pro / Google AI

3) MCP server integration
- Repo Prompt as a backend for Claude Code, Cursor, etc.

## Key Features
- Codemaps (tree-sitter signatures)
- Multi-root workspaces
- Context Builder
- CLI providers
- MCP server
- XML Edit / Pro Edit

## Free vs Pro (from provided text)
| Feature | Free | Pro |
|---|---|---|
| Token Limit | 32K | Unlimited |
| File Selection & Workspaces | Yes | Yes |
| Own API Keys | Yes | Yes |
| CLI Providers | Yes | Yes |
| Codemaps | No | Yes |
| MCP Server | No | Yes |
| Context Builder | No | Yes |
| Custom API Providers | No | Yes |

## Who Repo Prompt Is For
- Developers using AI for coding who want better context
- Teams with large codebases
- Power users of AI agents (Claude Code / Cursor)
- Anyone analyzing file-based projects

## Two Main Workflows

### Compose Mode
- Build context and copy into external AI (ChatGPT, Claude, etc.)
- Pro Edit: paste XML response back to apply changes

### Chat Mode
- Integrated AI conversation
- Pro Edit handles XML internally
- Delegate agents for parallel editing

## Repo Prompt vs AI Editors

Repo Prompt complements AI editors rather than replacing them. Via MCP, it acts as a context server that supercharges external tools.

### Repo Prompt + Cursor/Claude Code
- Keep editor workflows, add Repo Prompt context building
- Multi-repo context, codemaps, slices
- Context Builder for discovery
- MCP tools for selection, search, file ops, planning

### MCP Server Summary
- 14 specialized tools (selection, search, structure, edits, workspaces)
- Selection modes: full, slices, codemap_only
- Secure local integration (user-approved)
- One-click setup for Cursor; manual for others

### Unique Capabilities
- Cross-repository intelligence
- Token-efficient context with codemaps
- AI-powered discovery (Context Builder)
- Optimized for large reasoning models

### Complementary Strengths
- Use Cursor/Claude Code for daily coding
- Use Repo Prompt for deep context building, multi-repo analysis

## Getting Started (desktop)

### Installation
- Download installer from repoprompt.com
- Follow the installer prompts for your OS

### First Launch
- Open Repo Prompt, grant folder access
- Open workspace via File -> Open or drag folder

### Updates
- Automatic update checks; manual via Settings -> License & Updates

## Interface Overview

### Main Views
- Compose: build context and prompts
- Chat: AI conversation with context
- Apply: paste XML edits and review
- Review: inspect diffs and apply

### Compose View
- File tree (left)
- Selected files panel
- Instructions area
- Bottom bar with presets + token count

## Context Building Concepts

- Full: complete file content
- Slices: line ranges
- Codemap: signatures only

### Git Integration
- Include diffs for uncommitted changes

## Token Management

- Large contexts degrade reasoning beyond effective limits
- Use codemaps/slices to reduce token usage
- Leave room for responses

## Presets & Prompts

- Presets configure prompt format, tree, diffs, codemap settings
- Built-in presets: Standard, XML Edit, Plan, Diff Follow-up
- MCP presets: MCP Pair, MCP Discover, MCP Agent

## Workflows: Discovery -> Plan -> Implement

- Context Builder discovers files and creates a handoff prompt
- Architectural planning recommended for large tasks
- Then implement in agent/editor

## MCP Tool Categories (examples)

Selection & context:
- manage_selection
- workspace_context
- prompt
- context_builder

File ops:
- get_file_tree
- file_search
- read_file
- get_code_structure
- file_actions
- apply_edits

Chat & models:
- chat_send
- chats
- list_models

Workspaces:
- manage_workspaces

## rp-cli (Repo Prompt CLI)

- Acts as a proxy MCP client via local sockets
- Supports exec mode, interactive mode, and scripting
- Useful for agents that cannot use MCP directly

## Notes on Claims

- Some claims are time-sensitive (model names, pricing). If asked for the latest, ask user to confirm or verify via official Repo Prompt docs.
