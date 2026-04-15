---
type: moc
name: skill-graph-index
description: "Master index of the Agent-Skills knowledge graph. Top-level navigator for all 92 skills organized into 7 functional topic maps."
covers:
  - all-skills
  - topic-maps
  - skill-graph
---

# Skill Graph Index

> Master navigator for the Agent-Skills knowledge graph (92 skills, 7 topic maps).
> Generated: 2026-03-16 | Last reviewed: 2026-03-16

## Table of Contents
- [Topic Maps](#topic-maps)
- [Unclustered Skills](#unclustered-skills)
- [Cross-topic Pipelines](#cross-topic-pipelines)
- [Graph Health](#graph-health)

---

## Topic Maps

The 92 skills are organized into 7 functional topic maps. Each topic map serves as a navigable cluster with explicit cross-links and pipeline patterns.

| Topic Map | Skills | Domain |
|-----------|--------|--------|
| [[frontend-ui]] | 25 | UI design, components, browser automation, graphics, accessibility |
| [[agent-ops]] | 22 | Skill authoring, Codex tooling, debugging, planning, routing |
| [[backend-platform]] | 17 | APIs, MCP, cloud deployment, CI/CD, auth, secrets |
| [[product-strategy]] | 11 | Ideation, specs, interviews, research, project analysis |
| [[security-ops]] | 7 | Threat modeling, security reviews, auth, ownership analysis |
| [[content-publishing]] | 9 | Video, YouTube, slides, transcripts, written content |
| [[mobile-native]] | 3 | iOS/macOS, Build iOS Apps plugin workflows, Apple platform automation |

---

## Unclustered Skills

The following skills appear in multiple topic maps or serve cross-cutting concerns:

- [[brainstorming]] — Pre-planning exploration (in [[agent-ops]] and [[product-strategy]])
- [[context7]] — Live library documentation (in [[agent-ops]] and [[product-strategy]])
- [[docs-expert]] — Repository documentation (in [[agent-ops]] and [[product-strategy]])
- [[create-auth]] — Auth implementation (in [[backend-platform]] and [[security-ops]])
- [[best-practices]] — Auth review (in [[backend-platform]] and [[security-ops]])
- [[1password]] — Secrets (in [[backend-platform]] and [[security-ops]])
- [[fix-mise]] — Toolchain repair (in [[backend-platform]] and [[agent-ops]])
- [[process-watch]] — System diagnostics (in [[agent-ops]] and [[mobile-native]])
- [[recon-workbench]] — Authorized investigation (in [[security-ops]] and [[agent-ops]])

---

## Cross-topic Pipelines

### Full-stack feature delivery
```
[[brainstorming]] (product-strategy)
  → [[product-spec]] (product-strategy)
  → [[ce-plan]] (agent-ops)
  → [[backend-engineer]] (backend-platform) + [[frontend-ui-design]] (frontend-ui)
  → [[test-driven-development]] (agent-ops)
  → [[verification-before-completion]] (agent-ops)
  → [[gh-workflow]] (backend-platform)
```

### Security audit
```
[[security-threat-model]] (security-ops)
  → [[security-best-practices]] (security-ops)
  → [[security-ownership-map]] (security-ops)
  → [[gh-workflow]] (backend-platform)
```

### New skill authoring
```
[[decide-build-primitive]] (agent-ops)
  → [[skill-builder]] (agent-ops)
  → [[plugin-builder]] (agent-ops)
  → [[verification-before-completion]] (agent-ops)
```

### Content production
```
[[youtube-hooks-scripts]] (content-publishing)
  → [[youtube-titles-thumbnails]] (content-publishing)
  → [[imagegen]] (frontend-ui)
  → [[slides]] (content-publishing)
```

### iOS app launch
```
Build iOS Apps plugin workflow (mobile-native)
  → [[test-driven-development]] (agent-ops)
  → [[create-auth]] (security-ops / backend-platform)
  → [[production-deployment]] (backend-platform)
```

---

## Graph Health

**Last `/graph health` run:** 2026-03-16  
**Graph state:** FRAGMENTED → in progress of being connected  
**Current density:** 0.00 (no explicit [[wiki-links]] within SKILL.md files yet)  
**Topic maps created:** 7 of 7  

### Next steps to improve density:
1. Add `[[related-skill]]` references within individual SKILL.md cross-section blocks.
2. Run `feedback-loop.sh` after 3+ new skills are added to track community drift.
3. When a topic map exceeds 30 skills, consider splitting it.

**Feedback log:** `Infrastructure/ops/metrics/graph/feedback/decision-feedback.jsonl`  
**Graph snapshots:** `Infrastructure/ops/metrics/graph/snapshots/`
