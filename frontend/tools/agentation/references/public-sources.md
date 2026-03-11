# Agentation public sources and trust ranking

Status: dated public-source memo for the canonical `frontend/tools/agentation` skill.
Verified: 2026-03-11.

## Purpose

Use this document when we need to decide which public Agentation sources are trustworthy enough to guide the skill's install, MCP, webhook, output, and compatibility claims.

## Trust ranking

### 1. Official product docs

Primary authoritative docs, verified live on 2026-03-11:
- [agentation.com](https://www.agentation.com)
- [agentation.com/install](https://www.agentation.com/install)
- [agentation.com/mcp](https://www.agentation.com/mcp)
- [agentation.com/webhooks](https://www.agentation.com/webhooks)
- [agentation.com/output](https://www.agentation.com/output)
- [agentation.com/annotation-format](https://www.agentation.com/annotation-format)

Use these pages first for:
- current install and setup guidance;
- MCP and webhook workflow claims;
- output-format and annotation-format wording;
- the public product contract.

### 2. User-supplied stable compatibility anchors

Treat these as compatibility anchors that must remain visible in the skill when the user explicitly asks for the original Agentation workflow:
- `npx skills add benjitaylor/agentation`
- `ln -s "$(pwd)/skills/agentation-self-driving" ~/.claude/skills/agentation-self-driving`

These are important because they describe the historical upstream skill-install path and self-driving compatibility surface, even if newer public docs emphasize different packaging routes.

### 3. Public product article

Primary verified public reference:
- [benji.org/agentation](https://benji.org/agentation)

Use this page for:
- structured output behavior;
- source detection expectations;
- annotation-focused workflow framing;
- high-level install and product positioning.

### 4. Public skill pages

Verified public pages on 2026-03-11:
- [skills.sh/playbooks/agentation](https://skills.sh/playbooks/agentation)
- [skills.sh/agentskills/agentation-self-driving](https://skills.sh/agentskills/agentation-self-driving)

Use these pages for:
- current public install/distribution hints;
- self-driving packaging expectations;
- compatibility wording for the published skill path.

### 5. Temporary fallback rule

If the official product docs become unavailable in a future run, mark that outage explicitly and fall back to the verified article + skill pages + local reference docs instead of silently inventing a replacement authority.

## How to use this reference

### For SKILL.md

Use this file when changing:
- install commands;
- MCP setup wording;
- webhook or self-driving workflow claims;
- compatibility notes about the original published skill.

### For evals

Use this file when adding cases about:
- original-skill compatibility;
- self-driving wording;
- public workflow expectations.

### For plan updates

Use this file to justify why Agentation changes must track both:
- public workflow/install sources;
- local AFS/schema references in `references/annotation-format.md`.

## Change-control rule

When the public sources drift:
1. update this memo with date and URL changes;
2. decide whether the drift affects install flow, MCP flow, or compatibility language;
3. only then update `SKILL.md`, `contract.yaml`, and `evals.yaml`.
