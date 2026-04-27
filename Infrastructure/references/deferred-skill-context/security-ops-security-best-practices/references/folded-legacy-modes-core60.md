# Folded Legacy Modes (Core60)

Destination skill: `product/security/security-best-practices`

This file captures legacy capabilities migrated from retired skills.

## `ownership-risk-map`
- Source skill: `product/security/security-ownership-map`
- Legacy description: Analyze git repositories to map security ownership (people-to-file), compute bus-factor and sensitive-code risk, and export CSV/JSON/graph artifacts for visualization. Use only when the user explicitly requests security-focused ownership analysis grounded in git history.
- Fold rationale: Ownership risk analysis complements security recommendation outputs.
- Legacy section map:
  - Overview
  - Requirements
  - Philosophy
  - Workflow
  - Quick start
  - Sensitivity rules

## `threat-model`
- Source skill: `product/security/security-threat-model`
- Legacy description: Repository-grounded threat modeling that enumerates trust boundaries, assets, attacker capabilities, abuse paths, and mitigations, and writes a concise Markdown threat model. Trigger only when the user explicitly asks to threat model a codebase or path, enumerate threats/abuse paths, or perform AppSec threat modeling. Do not trigger for general architecture summaries, code review, or non-security design work.
- Fold rationale: Threat-modeling can be embedded as advanced stage in security review workflow.
- Legacy section map:
  - Quick start
  - Philosophy
  - Workflow
  - Risk prioritization guidance (illustrative, not exhaustive)
  - References
  - Anti-patterns
