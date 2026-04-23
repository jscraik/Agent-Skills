# Agent-First Status

Last reviewed: 2026-04-16

## Summary

Agent-Skills is a governed repository of canonical skills for AI coding agents (Codex, Codex, OpenAI). The project is in active maintenance with a topic-cluster skill layout and automated quality gates.

## Current State

| Surface | Status | Notes |
|---------|--------|-------|
| Skill discovery | ✅ operational | 120 canonical skills across 7 topic clusters + .system lane |
| CLI (`ask`) | ✅ operational | Fuzzy matching, JSON output, trace IDs |
| Validation | ✅ operational | 28 automated checks via `ask repo validate` |
| CI pipeline | ✅ operational | GitHub Actions + CircleCI dual-provider |
| Harness | ✅ operational | v0.12.0, contract-governed |
| Graph navigation | ✅ operational | Skill relationship mapping with topic clusters |
| Plugin system | ✅ operational | 27 plugin skills across 5 plugin packages |

## Key Metrics

- Total skills: 120 (88 Skills/ + 5 .system/ + 27 Plugins/)
- Topic clusters: 7 (agent-ops, frontend-ui, backend-platform, product-strategy, security-ops, content-publishing, mobile-native)
- Validation checks: 28
- Plugin packages: 5 (coderabbit, skill-factory, plugin-factory, harness-engineering, compound-engineering-router)

## Next Milestones

- [ ] Complete Docs/ skill migration (27 skills still under Docs/ from legacy structure)
- [ ] Wire githubCheckName into ci-required-checks.json for branch protection alignment
