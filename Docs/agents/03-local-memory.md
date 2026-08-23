# Local Memory Workflow

## Table of Contents
- [Workflow](#workflow)
- [Harness Memory Governance](#harness-memory-governance)
- [Store rules](#store-rules)
- [See Also](#see-also)

## Workflow
1. Bootstrap memory before durable notes.
2. Search for prior relevant notes.
3. Record durable facts only.

## Harness Memory Governance
When `.harness/memory/LEARNINGS.md` exists, treat it as a repo-specific append-only knowledge base for recurring fixes and repository-grounded operational context.

Purpose:
- Preserve durable, repo-local learnings that improve future troubleshooting and delivery quality.

Scope:
- Repo-only operational knowledge belongs in `.harness/memory/LEARNINGS.md`.
- Universal or cross-repo guidance belongs in `~/.codex/` memory instead.

Update policy:
- Append after confirmed bugs, tool failures, or repo-specific fixes.
- Do not rewrite historical entries in place; add a new dated entry when guidance evolves.

Format convention:
- `**YYYY-MM-DD [Agent]:** <problem> -> <fix>`

## Store rules
- Do not store secrets, tokens, keys, or PII.
- Keep observations short and stable.

## See Also
- [Root agent guidance](/AGENTS.md#further-guidance)
- [High-Signal Steering Feedback](/Docs/agents/19-high-signal-steering-feedback.md)
