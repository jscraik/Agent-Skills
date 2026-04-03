---
name: insight-report
description: Generate an evidence-backed Codex usage insights report (HTML and optional PDF) from local sessions, OTEL signals, and a project brief. Use when the user asks for insights, usage analytics, or repeatable retrospective reporting.
metadata:
  skill-type: data_fetch_analysis
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  review_cadence: quarterly
  last_reviewed: 2026-03-31
  metadata_source: frontmatter
---

# Insight Report

Generate reproducible Codex insights artifacts from local evidence, with explicit provenance and confidence boundaries.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [Philosophy](#philosophy)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Variations](#variations)
- [Workflow](#workflow)
- [Required checks](#required-checks)
- [Output contract](#output-contract)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Validation](#validation)
- [Examples](#examples)
- [References](#references)
- [See Also](#see-also)
- [Gotchas](#gotchas)

## Standards snapshot
- Verified against official Codex docs and local generator behavior on 2026-03-31.
- Prefer one coherent reporting thread per analysis cycle; fork only when the report goal diverges materially.
- Treat telemetry, prompts, tool arguments, and tool outputs as sensitive data and avoid exposing secrets in report artifacts.
- Keep `log_user_prompt` disabled unless explicit policy permits prompt storage.
- Use explicit confidence boundaries whenever data coverage is partial, stale, or noisy.
- `approval_policy = "on-failure"` is deprecated in current docs; use `untrusted`, `on-request`, `never`, or granular policy.

## Philosophy
- Reports are decision-support artifacts, not vanity dashboards.
- Evidence-first approach: every non-trivial claim should map to a source, timestamp, and freshness window.
- Safety by default: protect sensitive telemetry and prompt/tool content even when users ask for speed.
- Practicality over perfection: ship the smallest complete report that is valid for the requested scope.
- Use explicit principles and a clear mental model: explain the why, call out tradeoffs, and help operators understand uncertainty boundaries.
- This workflow should empower capable operators, enable creative follow-up analysis, and unlock innovative improvements they can explore safely.
- Guiding question: "Would another operator be able to verify this claim from artifacts without re-running the full analysis?"

## When to use
- The user asks for a Codex insights report, usage report, or session-health retrospective.
- The request needs a durable artifact (`report.html` and optionally `report.pdf`) instead of a chat-only summary.
- The request needs a cross-project brief plus data-backed recommendations.

## Required inputs
- Optional time window (`days=N`) and flags (`dynamic`, `architecture`, `pdf`, `self-optimize`).
- Expected output location defaults to `$HOME/dev/config/codex/usage-data` unless the user requests override paths.
- OTEL root path defaults to `$HOME/.agents/otel-collector` unless unavailable.

## Deliverables
- Project brief JSON: `$HOME/dev/config/codex/usage-data/project-brief.json`.
- HTML report: `$HOME/dev/config/codex/usage-data/report.html`.
- Optional PDF report: `$HOME/dev/config/codex/usage-data/report.pdf`.
- Facets JSON: `$HOME/dev/config/codex/usage-data/facets/latest.json`.
- Optional dynamic insights JSON: `$HOME/dev/config/codex/usage-data/dynamic-insights.json`.
- Optional architecture outputs under `$HOME/dev/config/codex/usage-data/diagrams/`.
- Fact provenance snapshots under `$HOME/dev/config/codex/usage-data/fact-snapshots/`.
- Launch fallback URL when native open fails: `http://127.0.0.1:<port>/report.html`.

## Variations
- Quick health pass: `days=3` with base report only.
- Operational deep dive: `days=14 dynamic` for stronger strengths and weakness signals.
- Portfolio review: `days=30 dynamic architecture pdf` for cross-project narrative and export-ready output.
- Controlled improvement run: `self-optimize` with explicit delta validation and timeout guard.
- Keep variation context-specific: adapt and customize report depth for different audiences, maintain diverse evidence slices, and avoid repetition or cookie-cutter outputs.
- Prefer unique framing per objective (operator triage vs leadership summary) while keeping the same verification backbone.

## Workflow
1. Keep scope narrow for skill maintenance work.
   - Default edit scope: `utilities/insight-report/SKILL.md`, `references/contract.yaml`, `references/evals.yaml`, and one dated standards note.
   - Start with the smallest package boundary, keep scope tight, and limit first-pass changes to 2-3 focused surfaces unless the user asks for broader work.
   - Expand scope only when the user explicitly asks for runtime/report-generator code changes.
2. Start from the canonical wrapper command (preferred):
   - `python3 $HOME/dev/agent-skills/utilities/insight-report/scripts/run_insight_report.py --otel-root $HOME/.agents/otel-collector`.
   - Wrapper invariants:
     - Always refresh `project-brief.json` before generation.
     - Always refresh `dynamic-insights.json` before generation.
     - Always pass `--dynamic` to the report generator so output is usable and current.
     - Attempt native launch first, then fallback to localhost serving when native launch fails.
3. Apply argument mapping:
   - `days=N` -> append `--days N`.
   - `open` or `launch` -> no-op because wrapper opens by default.
   - `no-open` -> append `--no-open`.
   - `pdf` -> append `--pdf`.
   - `dynamic` -> no-op because dynamic mode is already enforced by wrapper.
   - `architecture` -> append `--include-architecture`.
   - `self-optimize` -> append `--self-optimize` and keep timeout explicit when needed.
4. If wrapper script is unavailable, run fallback sequence manually:
   - `python3 $HOME/dev/config/codex/scripts/collect-project-brief.py --output $HOME/dev/config/codex/usage-data/project-brief.json`
   - `python3 $HOME/dev/config/codex/scripts/dynamic_insights.py --json --output $HOME/dev/config/codex/usage-data/dynamic-insights.json`
   - `python3 $HOME/dev/config/codex/scripts/generate-insight-report.py --dynamic --brief $HOME/dev/config/codex/usage-data/project-brief.json --otel-root $HOME/.agents/otel-collector`
5. Run generation once per requested variant and capture any failures verbatim.
6. Run required checks before final output.

## Required checks
- Fail fast: stop at first failed gate in this section and do not proceed to subsequent checks until the blocker is resolved.
- Confirm `project-brief.json` exists in `usage-data`.
- Confirm `report.html` and `facets/latest.json` exist.
- Confirm `dynamic-insights.json` exists and was refreshed in the current run (not stale carry-over).
- Confirm `report.html` includes `Project Brief` and `Data Sources & Accuracy`.
- If `pdf` was requested, confirm `report.pdf` exists.
- If `dynamic` was requested, confirm `dynamic-insights.json` exists (already required by default wrapper flow).
- If `architecture` was requested:
  - confirm `diagrams/manifest.json` exists;
  - confirm at least one diagram source such as `architecture.mmd` exists.
- If `self-optimize` was requested, confirm the report includes `Self-Optimizing Recommendation Loop (v1)`.
- If open/launch behavior was requested, confirm either:
  - native open succeeded, or
  - localhost fallback URL was emitted.
- Confirm fact snapshots exist:
  - `fact-snapshots/facts.json`
  - `fact-snapshots/sources.json`
  - `fact-snapshots/freshness.json`

## Output contract
For automation callers that require a typed envelope, use:

```yaml
schema_version: "1.0"
status: "ready|failed"
artifacts:
  - "file://$HOME/dev/config/codex/usage-data/report.html"
  - "file://$HOME/dev/config/codex/usage-data/report.pdf"
```

After successful generation, output this block exactly:

Your shareable insights report is ready:
file://$HOME/dev/config/codex/usage-data/report.html
file://$HOME/dev/config/codex/usage-data/report.pdf (if requested)

Want to dig into any section or try one of the suggestions?

If launch fallback was used, append exactly one additional line:
- `Launch URL: http://127.0.0.1:<port>/report.html`

## Failure mode
- If required source data is unavailable, stop and report the exact missing source and smallest safe fix.
- If command execution fails, report the exact failing command and stderr snippet without fabricating report conclusions.
- If requested flags exceed available evidence quality, downshift to the closest safe variant and declare the downgrade.

## Constraints
- Do not run destructive operations unless explicitly requested.
- Do not expose secrets, credentials, tokens, API keys, or private personal data.
- Do not claim causal insights without evidence; separate observed metrics from interpretation.

## Anti-patterns
- Skipping project brief collection and still claiming cross-project coverage.
- Publishing polished charts without freshness/provenance checks.
- Hiding stale data or invariant violations from the final report summary.
- Treating self-optimization output as validated when no before-vs-after delta is shown.
- NEVER ship a report that hides stale or missing evidence.
- DO NOT present interpretation as fact when the data only supports directional inference.
- DON'T ignore warning signs that indicate pitfall, mistake, or incorrect metric attribution.

## Validation
- Fail fast: stop at first failed gate, then surface the exact failing artifact or section.
- Validate key files and section markers before finalizing.
- If a check fails, report the exact failure and smallest safe remediation.
- Keep confidence statements explicit when any source category is stale.

## Examples
- "When the user asks for sprint risk review: `Can you inspect /insights days=7 dynamic and validate which tool calls dropped below a 95% success rate in dynamic-insights.json?`"
- "User says: `Please generate /insights days=30 architecture pdf, then validate diagrams/manifest.json, report.html, and report.pdf for leadership review.`"
- "For recommendation tuning: `Can you run /insight self-optimize and inspect before/after recommendation changes to decide whether we should migrate this into automation?`"

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Runtime + doc source notes: `references/latest-standards-2026-03-31.md`
- Integration notes: `references/README.md`

## See Also

| Skill | When to use together |
|---|---|
| [[codex-sessions-skill-scan]] | Build a session quality baseline before generating the report |
| [[codex-automation-architect]] | Convert repeated recommendations into scheduled automations |
| [[codex-home-audit]] | Follow up on report-detected local environment drift |
| [[visual-explainer]] | Convert report outcomes into an executive visual explainer |

**Topic map:** [[agent-ops]]

## Gotchas
- `approval_policy = "on-failure"` is deprecated in current docs -> switch to `untrusted`, `on-request`, `never`, or granular policy.
- On some macOS setups, LaunchServices can fail to open `file://` reports (`kLSExecutableIncorrectFormat`) -> use localhost fallback from `scripts/run_insight_report.py`.
