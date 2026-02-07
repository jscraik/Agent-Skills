---
name: worst_case_interrogation
description: Plan an escalation ladder for hardened/minified/low-signal targets using
  observation-first instrumentation and baseline/stimulus diffs. Use when standard
  probes fail.
metadata:
  source_repo: https://github.com/jscraik/Agent-Skills
  source_rev: 7e31061c353c94746910d239ae122900cc5324fb-dirty
  source_dirty: 'true'
  source_dirty_paths: utilities/recon-workbench/references/evals.yaml, utilities/skill-creator/scripts/run_skill_evals.py,
    design/better-icons/
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

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

