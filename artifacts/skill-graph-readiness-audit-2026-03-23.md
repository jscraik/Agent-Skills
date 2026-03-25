# Skill Graph Readiness Audit

Date: 2026-03-23
Scope: canonical skills only
Excluded: generated projections under `skills-antigravity/` and plugin copies under `plugins/`

## Table of Contents
- [Purpose](#purpose)
- [Method](#method)
- [Headline Findings](#headline-findings)
- [New Skills](#new-skills)
- [Strongest Skills](#strongest-skills)
- [Weakest Skills](#weakest-skills)
- [What Matters Most](#what-matters-most)
- [Recommended Next Sweeps](#recommended-next-sweeps)

## Purpose

Audit whether skill structure is helping the repository's skill graph, not just whether each skill exists and routes.

This pass focuses on three graph-relevant dimensions:
- routing quality
- cross-link quality
- structured scaffold completeness

## Method

Each canonical `SKILL.md` was scored heuristically across:

1. Routing quality
- frontmatter `description`
- `metadata.skill-type`
- reasonable description length
- explicit trigger phrasing like `Use when`
- explicit exclusion boundary like `not ...` or `do not ...`

2. Cross-link quality
- `## See Also`
- number of `[[wiki-links]]`
- explicit topic-map link

3. Structured scaffold completeness
- `references/`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- either `agents/openai.yaml` or `scripts/`

This is a graph-readiness heuristic, not a correctness judgment. A low score does not mean a skill is bad. It means the skill contributes less structure to routing, traversal, or future graph tooling.

## Headline Findings

- Canonical skills scanned: `120`
- Strong graph-readiness: `88`
- Medium graph-readiness: `22`
- Weak graph-readiness: `10`

This is a repo-wide issue, not just a new-skills issue.

The biggest graph-health gaps are:
- missing `## See Also`
- missing `[[wiki-links]]`
- missing topic-map pointers
- for some skills, missing structured reference scaffolding

The repository already has many strong graph contributors, so the next gains should come from targeted connective-tissue passes, not wholesale rewrites.

## New Skills

Scores shown as `total = routing + cross-links + scaffold`.

| Skill | Score | Read |
| --- | --- | --- |
| `greploop` | `30 = 10 + 10 + 10` | Fully graph-ready; strongest new addition |
| `rclone` | `18 = 10 + 0 + 8` | Structurally solid, but lacks graph links |
| `every-style-editor` | `16 = 10 + 0 + 6` | Good routing, weak graph linkage |
| `resolve-todo-parallel` | `16 = 10 + 0 + 6` | Good routing, weak graph linkage |
| `changelog` | `16 = 8 + 0 + 8` | Good scaffold, but no cross-links |
| `reproduce-bug` | `14 = 8 + 0 + 6` | Adequate, but still sparse for graph use |
| `agent-native-architecture` | `10 = 8 + 0 + 2` | Valuable doctrine, weakest graph scaffold among new skills |

The key pattern: most of the new skills are routeable and indexed, but only `greploop` is already contributing real graph density.

## Strongest Skills

These scored highest because they combine strong routing, explicit cross-linking, and structured scaffolding:

- `atlas` — `30`
- `brainstorming` — `30`
- `check-pr` — `30`
- `compound-engineering-router` — `30`
- `design-system` — `30`
- `diagram-cli` — `30`
- `frontend-ui-design` — `30`
- `gh-fix-ci` — `30`
- `gh-workflow` — `30`
- `greploop` — `30`

These are good models for future graph-hardening work because they expose:
- clear ownership in frontmatter
- explicit exclusions
- `See Also`
- `[[wiki-links]]`
- structured references and support files

## Weakest Skills

These are the lowest graph-readiness outliers from this audit:

| Skill | Score | Primary gaps |
| --- | --- | --- |
| `skill-installer` | `8` | no `skill-type`, no cross-links, no scaffold beyond core wrapper |
| `openai-docs` | `10` | no `skill-type`, no graph links, limited scaffold |
| `agent-native-architecture` | `10` | no `See Also`, no wiki-links, no contract/evals/task-profile |
| `test-xcode` | `11` | weak scaffold, sparse graph links |
| `skill-creator` | `12` | no `skill-type`, no graph links |
| `test-browser` | `13` | sparse graph links, partial scaffold only |
| `frontend-design` | `14` | router logic is fine, but graph linkage is thin |
| `feature-video` | `14` | preserved doctrine exists, graph surface is still thin |
| `agent-native-audit` | `14` | strong content, weak graph scaffold |
| `reproduce-bug` | `14` | new skill with weak cross-linking and partial scaffold |

Not all of these need heavy scaffolding. But they are the highest-leverage candidates if the goal is improving graph traversal and cluster cohesion.

## What Matters Most

The graph-health docs already point to the main fix:
- add explicit `[[related-skill]]` links inside `SKILL.md`
- use `## See Also` consistently

In practice, the highest-value improvements are:

1. Add `## See Also` plus 3-5 meaningful `[[wiki-links]]` to skills that already have strong routing.
2. Add `task-profile.json` to medium-strength skills that already have `contract.yaml` and `evals.yaml`.
3. Bring a few doctrine-heavy but structurally thin skills up to parity with stronger owners.

This matters more than endlessly tuning description wording. Frontmatter helps routing, but graph density comes from explicit relationships.

## Recommended Next Sweeps

### Sweep 1: Cross-link uplift

Add `## See Also` and `[[wiki-links]]` to:
- `agent-native-architecture`
- `changelog`
- `every-style-editor`
- `rclone`
- `reproduce-bug`
- `resolve-todo-parallel`
- `feature-video`
- `test-browser`
- `frontend-design`

### Sweep 2: Structured scaffold parity

Add `task-profile.json` where it is conspicuously missing but the skill is already non-trivial:
- `every-style-editor`
- `rclone`
- `reproduce-bug`
- `resolve-todo-parallel`

Add full `contract.yaml` + `evals.yaml` + `task-profile.json` to:
- `agent-native-architecture`

### Sweep 3: System-skill governance cleanup

Audit the graph outliers among system-owned skills:
- `skill-installer`
- `skill-creator`
- `openai-docs`

These are not necessarily weak operationally, but they are weak graph citizens by the current heuristic.
