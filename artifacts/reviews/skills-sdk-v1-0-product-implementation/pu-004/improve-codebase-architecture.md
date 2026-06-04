# PU-004 Improve Codebase Architecture Review

Status: pass

Reviewed question: Does PU-004 introduce risk-tier and sensor placement in the right architectural boundary without prematurely wiring heavy gates?

Findings: None requiring changes.

Evidence:
- `Infrastructure/scripts/lib/ask/skills_sdk/risk.py` owns the static source-shape classifier instead of embedding tier rules directly into the command handler.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py` only reads already selected skill source text and emits the classification in `skills doctor` output.
- `Infrastructure/config/schemas/skills-sdk/risk-classification.v1.schema.json` captures sensor placement, blocking behavior, and receipt requirements as contract data.
- The classifier is read-only. It does not invoke scanners, sandboxes, external adapters, package managers, projections, trust-store writes, or global roots.

Residual risk: PU-003 and PU-004 are intentionally parallel after PU-002. PU-005 must wait for both PRs to merge and be pulled into main so install preview can consume the command facade and risk classifier from a single base.
