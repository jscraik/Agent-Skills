---
type: moc
name: skill-graph-index
description: "Master index of the Agent-Skills topic maps and cross-topic execution flows."
covers:
  - all-skills
  - topic-maps
  - skill-graph
---

# Skill Graph Index

> Master navigator for the Agent-Skills knowledge graph topic maps.

## Table of Contents
- [Topic Maps](#topic-maps)
- [Cross-topic Skills](#cross-topic-skills)
- [Cross-topic Pipelines](#cross-topic-pipelines)
- [Graph Health](#graph-health)

---

## Topic Maps

| Topic Map | Domain |
|-----------|--------|
| [[frontend-ui]] | UI design, components, browser testing, media assets |
| [[agent-ops]] | Skill authoring, codex tooling, verification, orchestration |
| [[backend-platform]] | APIs, MCP, deployment, CI/CD, auth, secrets |
| [[product-strategy]] | Ideation, interviews, architecture decisions, product planning |
| [[security-ops]] | Threat modeling, ownership analysis, auth and security hardening |
| [[content-publishing]] | Video, YouTube, slides, transcript and markdown conversion |
| [[mobile-native]] | macOS/iOS native workflows and Atlas automation |

---

## Cross-topic Skills

- [[context7]] — Live library documentation across product, backend, and agent-ops work.
- [[technical-writer]] — Documentation quality and repo-truth alignment across all domains.
- [[create-auth]] — Auth implementation bridging backend-platform and security-ops.
- [[best-practices]] — Security hardening and Better Auth review.
- [[1password]] — Secret and env-injection workflows across delivery lanes.
- [[process-watch]] — Runtime diagnostics shared by agent-ops and mobile-native.

---

## Cross-topic Pipelines

### Full-stack feature delivery
```
[[he-brainstorm]] (agent-ops/product-strategy)
  → [[interview-me]] (product-strategy)
  → [[architecture-interview]] (product-strategy)
  → [[he-plan]] (harness-engineering)
  → [[backend-engineer]] (backend-platform) + [[frontend-ui-design]] (frontend-ui)
  → [[verification-before-completion]] (agent-ops)
  → [[gh-workflow]] (agent-ops)
```

### Security hardening
```
[[security-threat-model]] (security-ops)
  → [[security-best-practices]] (security-ops)
  → [[security-ownership-map]] (security-ops)
  → [[gh-workflow]] (agent-ops)
```

### Content production
```
[[youtube-hooks-scripts]] (content-publishing)
  → [[youtube-titles-thumbnails]] (content-publishing)
  → [[imagegen]] (skills-system)
  → [[slides]] (content-publishing)
```

### iOS/macOS app delivery
```
Build iOS Apps plugin workflow (mobile-native)
  → [[he-tdd]] (harness-engineering)
  → [[create-auth]] (security-ops/backend-platform)
  → [[verification-before-completion]] (agent-ops)
```

---

## Graph Health

- Rebuild adjacency after See Also edits:
  - `python3 Infrastructure/scripts/skill-graph/build-adjacency-yaml.py .`
- Validate graph drift:
  - `python3 Infrastructure/scripts/skill-graph/validate-adjacency.py .`
