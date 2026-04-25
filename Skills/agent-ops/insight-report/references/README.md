# insight-report references

## Table of Contents

- [Canonical runtime script](#canonical-runtime-script)
- [Primary outputs](#primary-outputs)
- [Validation checklist](#validation-checklist)
- [Codex Browser](#codex-browser)

## Canonical runtime script

- Report generator: `/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/insight-report/scripts/run_insight_report.py`

## Primary outputs

- Output root: `/Users/jamiecraik/dev/configs/codex/usage-data`
- Evidence bundle: `/Users/jamiecraik/dev/configs/codex/usage-data/insight-evidence.json`
- Codex prompt: `/Users/jamiecraik/dev/configs/codex/usage-data/INSIGHT_PROMPT.md`
- Codex-written insights: `/Users/jamiecraik/dev/configs/codex/usage-data/insights.generated.json`
- HTML report: `/Users/jamiecraik/dev/configs/codex/usage-data/report.html`

## Validation checklist

- `insight-evidence.json` exists and is valid JSON.
- `INSIGHT_PROMPT.md` exists and is non-empty.
- `insights.generated.json` exists and includes required top-level sections.
- `report.html` exists.
- Runner output includes `REPORT_URL=file://.../report.html`.
- The final report URL is opened in the Codex in-app browser when Browser tooling is available.

## Codex Browser

Use the Browser plugin with the in-app browser backend to open the final `REPORT_URL=`. If the Browser plugin is unavailable, disclose that and provide the URL.
