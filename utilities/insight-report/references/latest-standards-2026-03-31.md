# insight-report latest standards (2026-03-31)

## Table of Contents
- [Purpose](#purpose)
- [Codex official baseline](#codex-official-baseline)
- [Generator reality check](#generator-reality-check)
- [Industry baseline](#industry-baseline)
- [Adoption guidance](#adoption-guidance)

## Purpose
This note records the standards snapshot used to update `utilities/insight-report` on 2026-03-31.

## Codex official baseline
- Best practices: one coherent thread per unit of work, use bounded subagents for parallelizable side tasks.
- Security guidance: keep `log_user_prompt = false` unless policy explicitly allows prompt logging.
- Security guidance: treat telemetry content, tool args, and tool outputs as sensitive and apply redaction plus retention controls.
- Config guidance: `approval_policy = "on-failure"` is deprecated; use `untrusted`, `on-request`, `never`, or granular policy.
- Sandbox guidance: approval strictness and sandbox level must be explicit in `config.toml` and managed requirements.

## Generator reality check
Verified from local runtime behavior and source:
- CLI supports flags: `--open`, `--days`, `--pdf`, `--dynamic`, `--include-architecture`, `--self-optimize`, `--brief`, `--otel-root`.
- Project brief section renders when `--brief <path>` is provided.
- Dynamic mode writes `dynamic-insights.json`.
- Architecture mode writes diagrams plus `diagrams/manifest.json`.
- Provenance snapshots are written under `usage-data/fact-snapshots/`.
- Report supports `Data Sources & Accuracy` and `Self-Optimizing Recommendation Loop (v1)` sections.
- Wrapper path `utilities/insight-report/scripts/run_insight_report.py` now enforces:
  - project brief refresh per run,
  - dynamic refresh per run,
  - report generation with `--dynamic`,
  - launch fallback from native `file://` open to localhost URL.

## Industry baseline
OpenTelemetry baseline used for sensitive-data handling:
- Do not collect sensitive data unless required.
- Use collector processors (attributes, filter, redaction, transform) to hash/delete/filter sensitive fields before export.
- Maintain explicit responsibility for privacy compliance and review third-party instrumentation behavior.

## Adoption guidance
- Keep report claims bounded to observed evidence and freshness windows.
- Validate section presence and file outputs before claiming success.
- Declare evidence gaps instead of backfilling with speculation.
