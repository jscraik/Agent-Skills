# insight-report references

## Table of Contents
- [Canonical runtime scripts](#canonical-runtime-scripts)
- [Primary outputs](#primary-outputs)
- [Validation checklist](#validation-checklist)
- [Official docs baseline (retrieved 2026-03-31)](#official-docs-baseline-retrieved-2026-03-31)
- [Industry baseline](#industry-baseline)

## Canonical runtime scripts
- Skill wrapper (preferred): `/Users/jamiecraik/dev/agent-skills/utilities/insight-report/scripts/run_insight_report.py`
- Report generator: `/Users/jamiecraik/dev/config/codex/scripts/generate-insight-report.py`
- Project brief collector: `/Users/jamiecraik/dev/config/codex/scripts/collect-project-brief.py`
- Dynamic analyzer: `/Users/jamiecraik/dev/config/codex/scripts/dynamic_insights.py`

## Primary outputs
- Output root: `/Users/jamiecraik/dev/config/codex/usage-data`
- HTML report: `/Users/jamiecraik/dev/config/codex/usage-data/report.html`
- PDF report: `/Users/jamiecraik/dev/config/codex/usage-data/report.pdf`
- Facets: `/Users/jamiecraik/dev/config/codex/usage-data/facets/latest.json`
- Project brief: `/Users/jamiecraik/dev/config/codex/usage-data/project-brief.json`
- Fact snapshots:
  - `/Users/jamiecraik/dev/config/codex/usage-data/fact-snapshots/facts.json`
  - `/Users/jamiecraik/dev/config/codex/usage-data/fact-snapshots/sources.json`
  - `/Users/jamiecraik/dev/config/codex/usage-data/fact-snapshots/freshness.json`

## Validation checklist
- `project-brief.json` exists.
- `report.html` and `facets/latest.json` exist.
- `dynamic-insights.json` exists and was refreshed in this run.
- `report.html` includes `Project Brief` and `Data Sources & Accuracy`.
- If `--pdf` was requested, `report.pdf` exists.
- If launch is requested, native open succeeds or localhost fallback URL is emitted.
- If `--include-architecture` was requested, `diagrams/manifest.json` exists.
- If `--self-optimize` was requested, `Self-Optimizing Recommendation Loop (v1)` exists in HTML.

## Official docs baseline (retrieved 2026-03-31)
- Codex best practices: https://developers.openai.com/codex/learn/best-practices/
- Codex approvals and security: https://developers.openai.com/codex/agent-approvals-security/
- Codex advanced config: https://developers.openai.com/codex/config-advanced/
- Codex config reference: https://developers.openai.com/codex/config-reference/

## Industry baseline
- OpenTelemetry sensitive-data guidance: https://opentelemetry.io/docs/security/handling-sensitive-data/
