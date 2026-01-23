---
name: report_compiler
description: Compile multiple run findings into a single report with cross-run diffs and stable conclusions.
---

Inputs:
- A list of run folders containing derived/findings.json.

Output:
- consolidated report.md:
  - what changed between baseline and stimulus
  - stable behaviors (observed repeatedly)
  - open questions and recommended next probes
