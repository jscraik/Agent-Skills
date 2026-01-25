# Recon Workbench Skills

Summary from `docs/guides/Skills.md`.

## Scope
- macOS apps, iOS Simulator apps, browser/React apps, OSS repos.

## Standard interrogation pattern
1) Doctor: verify toolchain
2) Baseline run: minimal interaction
3) Stimulus run(s): targeted actions
4) Diff: baseline vs stimulus
5) Summarize: findings.json + report.md
6) Escalate only if needed (worst-case ladder)

## Artifact contract
- Raw: `data/runs/<target>/<session>/<run>/raw/<probe_id>/...` (legacy `runs/...` supported)
- Derived: `data/runs/<target>/<session>/<run>/derived/` with findings/report

## Skill index (examples)
- `interrogate`: plan -> run -> summarize
- `worst-case-interrogation`: escalation for low-signal targets
- `macos-app-triage`: static bundle + Mach-O mapping
- `ios-sim-interrogate`: simulator runs, media capture
- `web-app-interrogate`: HAR/trace capture, endpoint mapping
- `oss-repo-map`: architecture map + SAST summary
- `report-compiler`: merge multi-run findings
- `dependency-doctor`: toolchain preflight

## References
- `docs/reference/DEPENDENCIES.md`
- `docs/reference/WORST_CASE_PLAYBOOKS.md`
- `docs/reference/REFERENCES.md`
- `docs/reference/LEGAL_NOTES_UK_EU.md`
- `docs/reference/DATA_HANDLING.md`
- `docs/reference/CI_CHECKS.md`
- `docs/reference/AUTHORIZATION_CHECKLIST.md`
- `docs/reference/THREAT_MITIGATIONS.md`
- `docs/reference/CLI_VS_MCP.md`
- `docs/reference/CLI_REFERENCE.md`
- `docs/reference/PROBE_CATALOG.md`
- `docs/reference/SCHEMAS.md`
- `AGENTS.md`
