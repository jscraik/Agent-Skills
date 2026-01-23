# Recon Workbench Skills

This repository defines a Codex-driven software interrogation toolkit spanning:

- Browser / React-style web apps (cloud-served SPAs)
- Open-source repos (architecture mapping, testing, static analysis)

The skills below implement evidence-first reverse engineering:
- Collect deterministic artifacts via a probe catalog (scripts/tools you control).
- Use Codex to plan, summarize, and decide next probes (closed-loop).
- Produce machine-readable findings (JSON) plus a human report.

## Non-goals / guardrails

- No DRM/TPM bypass, no decryption/circumvention steps, no credential exfiltration.
- No claims without evidence: every finding must reference an artifact path.
- "License purchased" does not automatically imply permission to circumvent protections or redistribute code; see docs/LEGAL_NOTES_UK_EU.md.

## Standard interrogation pattern (applies to all target types)

1) Doctor: verify toolchain and dependencies (baseline and worst-case).
2) Baseline run: minimal interaction; capture logs + network + file/process signals.
3) Stimulus run(s): scripted actions; capture the same signals.
4) Diff: baseline vs stimulus (new endpoints, files, modules, events).
5) Summarize: Codex converts artifacts into findings.json + report.md.
6) Escalate only if necessary using the worst-case ladder.

## Artifact contract (shared by all skills)

- Raw probe outputs: runs/<target_id>/<session_id>/<run_id>/raw/<probe_id>/...
- Derived outputs: runs/<target_id>/<session_id>/<run_id>/derived/
  - findings.json (schema-valid)
  - report.md (human, evidence-linked)
  - optional diff.json (schema-valid)

See docs/ARTIFACTS_AND_EVIDENCE.md.

## Skill index

Skills live under .codex/skills/<skill_name>/SKILL.md and can be invoked in Codex with $<skill_name>.
(Recommended: explicitly invoke during early setup; later you can let Codex auto-select.)

| Skill | When to use | Inputs | Outputs |
|---|---|---|---|
| interrogate | Main orchestrator (plan -> run -> summarize) | target kind + locator + goal | probe plan + findings + report |
| worst_case_interrogation | Escalation when targets are hardened/minified/opaque | target kind + goal | updated plan + high-signal evidence |
| macos_app_triage | Static + bundle mapping for .app / Mach-O | app path | inventory + derived capability map |
| web_app_interrogate | HAR/trace capture, endpoint inventory, runtime mapping | URL + scenario | endpoints + trace/har + findings |
| oss_repo_map | Architecture map, hotspots, dependency graph, SAST | repo path + goal | map + hotspots + SAST summary |
| report_compiler | Merge multi-run findings into a single understanding report | multiple run folders | consolidated report |
| dependency_doctor | Preflight installs/checks for worst-case toolchain | local machine | doctor output + install hints |

## Reference files

- docs/DEPENDENCIES.md -- baseline vs worst-case tool inventory and install/verify.
- docs/WORST_CASE_PLAYBOOKS.md -- per-target escalation ladder with safe fallbacks.
- docs/REFERENCES.md -- official docs and canonical references.
- docs/LEGAL_NOTES_UK_EU.md -- UK/EU legal notes + citations (not legal advice).
- docs/DATA_HANDLING.md -- redaction and retention guidance.
- docs/CI_CHECKS.md -- minimal CI verification suggestions.
- docs/AUTHORIZATION_CHECKLIST.md -- operator authorization checklist.
- AGENTS.md -- repo instructions for Codex.
- rules/recon.rules -- sample Codex execpolicy rules (Starlark).

## Codex integration notes

- Prefer non-interactive mode (codex exec) for repeatability and CI; use --output-schema and -o to write JSON to disk.
- Use AGENTS.md to define repo-wide and nested behavioral constraints.
- Use execpolicy rules to allow/prompt/block command prefixes outside sandbox.
- Use MCP when you want Codex to call high-level "probe tools" rather than shell commands.

See docs/REFERENCES.md for official Codex docs.
