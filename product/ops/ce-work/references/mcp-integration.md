# MCP Integration

## Table of Contents
- [Purpose](#purpose)
- [When to use MCP tools](#when-to-use-mcp-tools)
- [Tool mapping](#tool-mapping)
- [Execution guardrails](#execution-guardrails)

## Purpose
Capture deterministic MCP usage patterns for `ce-work` execution so tool calls support implementation quality without replacing repo-grounded evidence.

## When to use MCP tools
Use MCP only when it materially improves delivery confidence for the current slice.

Prefer local repo evidence first. Escalate to MCP when:
- framework/library behavior must be verified against current docs,
- issue tracking state must be created or updated,
- CI/CD diagnostics are needed for blocked validation,
- OpenAI product behavior depends on current official guidance.

## Tool mapping
| MCP capability | Use in ce-work |
|---|---|
| `Linear` | Create/update implementation follow-up issues, track deferred risks, attach handoff links |
| `Context7` | Resolve framework/library semantics when local evidence is insufficient |
| `OpenAI Docs` | Validate OpenAI API/model/platform behavior with official current docs |
| `CircleCI` | Investigate failing pipeline checks and required CI reruns |

## Execution guardrails
- Do not use MCP as a default substitute for reading local plan/spec/code context.
- Keep external retrieval bounded to claims that affect correctness, safety, or release confidence.
- When external evidence informs a decision, reflect that briefly in handoff notes.
- Never include secrets, tokens, or credentials in MCP queries or outputs.
