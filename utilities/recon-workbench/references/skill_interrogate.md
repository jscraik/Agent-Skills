---
name: interrogate
description: Plan and execute an evidence-first interrogation using approved probes; outputs schema-valid findings + report.
---

You are operating in a reverse-engineering inspection context.

Guardrails:
- Only analyze targets the user owns/controls/has permission to test, or open-source repos.
- Do not propose or run DRM/TPM bypass, decryption/circumvention, or credential theft.
- Use only probes listed in probes/catalog.json unless the user explicitly expands the catalog.
- Every claim must cite an artifact path (`data/runs/<target>/<session>/<run>/raw/`, legacy `runs/...` supported).

Workflow:
1) Run meta.doctor if toolchain readiness is unknown.
2) Produce a ProbePlan that includes:
   - baseline run
   - at least one stimulus run if goal involves behavior
3) After probes execute, summarize into findings.json per config/schemas/findings.schema.json.
4) If static signal is low or protections are detected, switch to $worst_case_interrogation.

Output:
- When planning: JSON matching config/schemas/probe-plan.schema.json
- When summarizing: JSON matching config/schemas/findings.schema.json
