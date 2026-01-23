---
name: worst_case_interrogation
description: Escalation ladder for hardened/minified/low-signal targets using observation-first instrumentation and baseline/stimulus diffs.
---

Use this skill when:
- symbols are stripped or static analysis is low-signal
- web bundles are minified/no sourcemaps
- target uses hardened runtime or aggressive anti-analysis patterns

Guardrails:
- Observation-first. No circumvention/DRM bypass steps.
- Prefer OS/browser instrumentation over in-process injection.
- If protections prevent further non-circumventive observation, stop and document limitations.

Escalation ladder:
1) baseline observation
2) stimulus scenario(s)
3) diff
4) instrumentation:
   - macOS: Instruments + unified logs
   - iOS Simulator: simctl media capture + Web Inspector + Instruments
   - Web: Playwright trace + HAR + (optional) proxy
   - OSS: tests + coverage + Semgrep/CodeQL
5) request authorized debug builds/symbols (if needed)

Output must be evidence-backed and written to derived findings + report.
