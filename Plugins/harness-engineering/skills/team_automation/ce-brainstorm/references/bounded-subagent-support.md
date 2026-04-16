# Bounded Subagent Support for ce-brainstorm

## Table of Contents

- [Approval gate](#approval-gate)
- [Research roles](#research-roles)
- [Fallback](#fallback)
- [Constraints](#constraints)

Read when: spawning internal research subagents during Phase 1.1 (Standard or Deep scope)

## Policy
This operational quick-reference defines the enforceable delegation rules inline. In brief:
- **Approval required**: Blocking user confirmation before spawning subagents
- **Research roles**: repo-research-analyst, learnings-researcher (bounded scope)
- **Fallback**: Serial grounding when tools unavailable
- **Constraints**: No unapproved delegation; synthesize before proceeding

## Quick Reference

### repo-research-analyst

```text
"Find similar features, conventions, or patterns relevant to: <topic>
- Max 20 files, max 4 MB total read
- Return a <=400 word summary with file:line refs"
```

### learnings-researcher

```text
"Find prior learnings relevant to: <topic>
- Check .harness/memory/LEARNINGS.md first when it exists (see Docs/agents/03-local-memory.md for governance)
- Then docs/solutions/ for directly relevant entries
- Return only directly relevant findings, <=200 words total"
```
