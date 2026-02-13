# Plan: chatgpt-apps-production-checklist

## Summary
Build a reusable Codex skill that operationalizes 15 ChatGPT Apps lessons into a production-readiness checklist with explicit mappings for tasks, tests, widget changes, and tool-output patterns.

## Task graph
```yaml
tasks:
  - id: T1
    title: Scaffold skill folder and baseline files
    depends_on: []
  - id: T2
    title: Author SKILL.md with routing boundaries and workflow
    depends_on: [T1]
  - id: T3
    title: Author contract and eval references
    depends_on: [T2]
  - id: T4
    title: Add lesson matrix and checklist template assets
    depends_on: [T2, T3]
  - id: T5
    title: Run validation gates and fix findings
    depends_on: [T2, T3, T4]
```
