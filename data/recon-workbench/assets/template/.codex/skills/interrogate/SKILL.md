---
name: interrogate
description: Plan and execute an evidence-first interrogation using approved probes;
  outputs schema-valid findings + report.
metadata:
  source_repo: https://github.com/jscraik/Agent-Skills
  source_rev: 7e31061c353c94746910d239ae122900cc5324fb-dirty
  source_dirty: 'true'
  source_dirty_paths: utilities/recon-workbench/references/evals.yaml, utilities/skill-creator/scripts/run_skill_evals.py,
    design/better-icons/
---

You are operating in a reverse-engineering inspection context.

Guardrails:
- Only analyze targets the user owns/controls/has permission to test, or open-source repos.
- Do not propose or run DRM/TPM bypass, decryption/circumvention, or credential theft.
- Use only probes listed in probes/catalog.json unless the user explicitly expands the catalog.
- Every claim must cite an artifact path (runs/.../raw/...).

Workflow:
1) Run meta.doctor if toolchain readiness is unknown.
2) Produce a ProbePlan that includes:
   - baseline run
   - at least one stimulus run if goal involves behavior
3) After probes execute, summarize into findings.json per schemas/findings.schema.json.
4) If static signal is low or protections are detected, switch to $worst_case_interrogation.

Output:
- When planning: JSON matching schemas/probe-plan.schema.json
- When summarizing: JSON matching schemas/findings.schema.json
