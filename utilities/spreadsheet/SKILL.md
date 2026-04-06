---
name: spreadsheet
description: "Create, edit, analyze, or format spreadsheets with formula-aware workflows and visual review. Use when the user wants `.xlsx`, `.csv`, or `.tsv` work, not plain text tables."
metadata:
  skill-type: data_fetch_analysis
---

# Spreadsheet

Create, edit, analyze, and validate spreadsheets with strong defaults for formulas, formatting preservation, and evidence-backed review.

## Standards snapshot (March 2026)
- Prefer deterministic workbook edits over ad hoc manual spreadsheet manipulation.
- Preserve formulas, references, and established formatting unless the user explicitly asks for redesign.
- Treat recalculation and render review as quality gates whenever tooling is available.
- Keep outputs auditable: make it obvious what changed, what was recalculated, and what still needs local review.

## When to use
- Creating new workbooks with formulas, structured layouts, and formatting.
- Analyzing tabular data including filtering, aggregation, pivots, and summary metrics.
- Modifying existing workbooks without breaking formulas, references, or styles.
- Producing spreadsheet-native charts, summary tabs, or presentation-quality workbook outputs.

## When not to use
- The task is plain-text table formatting with no spreadsheet artifact.
- A database, notebook, or code-first analysis output is the real deliverable instead of `.xlsx`, `.csv`, or `.tsv`.
- The user only wants a narrative summary and no spreadsheet mutation or output.

## Required inputs
- The spreadsheet goal and target file type.
- Source and destination file paths.
- Formatting, charting, and visual-review expectations.
- Constraints on dependencies, installs, or whether recalculation/render tooling is available.

## Deliverables
- The updated or newly created spreadsheet artifact, or a clear blocked result when dependencies are missing.
- A short evidence summary covering formulas, formatting, recalculation, and validation.
- Notes on any missing recalculation or rendering capability that still requires local review.
- If requested, a structured status report with `schema_version: 1` aligned to `references/contract.yaml`.

## Failure mode
- If dependency installation or rendering support is unavailable, report the exact blocker and stop instead of improvising.
- If recalculation cannot be performed, preserve formulas and explicitly mark cached-value validation as unverified.
- If formatting preservation matters, do not silently restyle an existing workbook.

## Workflow
1. Confirm whether the task is create, edit, analyze, or visualize.
2. Prefer `openpyxl` for `.xlsx` editing and formatting-preserving work.
3. Prefer `pandas` for analysis-heavy CSV or TSV workflows, then write back to the requested output format.
4. Use formulas for derived values instead of hardcoding results.
5. Run `scripts/spreadsheet_workflows.sh deps-check` to verify core and optional tooling.
6. Recalculate and render the relevant sheets when tooling is available.
7. Save stable outputs, review them, and clean up intermediate files.

## Script helpers
- `scripts/spreadsheet_workflows.sh deps-check`
  - Reports availability of Python tooling (`openpyxl`, `pandas`) and optional render binaries.
- `scripts/spreadsheet_workflows.sh print-install core|charting|render`
  - Prints deterministic install commands without executing them.
- `scripts/spreadsheet_workflows.sh paths`
  - Prints canonical temporary and output directories used by this skill.

## Tooling and references
- Use `openpyxl` for workbook-preserving `.xlsx` edits and formatting.
- Use `pandas` for analysis-heavy tabular transforms.
- Use `openpyxl.chart` for native Excel charts.
- If available, use LibreOffice (`soffice`) and Poppler (`pdftoppm`) for render review.
- Reference files:
  - `references/contract.yaml`
  - `references/evals.yaml`
  - `references/examples/openpyxl/`
  - `scripts/spreadsheet_workflows.sh`
  - `agents/openai.yaml`

## Temp and output conventions
- Use `tmp/spreadsheets/` for intermediate files and delete them when done.
- Write final artifacts under `output/spreadsheet/` in this repo unless the task specifies a different destination.
- Keep filenames stable, descriptive, and easy to reopen.

## Dependencies
Prefer `uv` for Python dependency management.
- Core install command: `scripts/spreadsheet_workflows.sh print-install core`
- Optional charting install command: `scripts/spreadsheet_workflows.sh print-install charting`
- Optional rendering install command: `scripts/spreadsheet_workflows.sh print-install render`

If installation is not possible in the current environment, report the exact missing dependency and stop.

## Spreadsheet rules
### Formula rules
- Use formulas for derived values rather than hardcoding them.
- Do not use dynamic array functions such as `FILTER`, `XLOOKUP`, `SORT`, or `SEQUENCE`.
- Keep formulas legible and use helper cells for complex logic.
- Avoid volatile functions such as `INDIRECT` and `OFFSET` unless required.
- Guard against `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, and `#NAME?` errors.

### Formatting rules
- Render and inspect provided spreadsheets before modifying them when tooling is available.
- Preserve existing formatting exactly unless the user explicitly requests a redesign.
- Match styles for newly filled cells that were previously blank.
- Use whitespace, number formats, and emphasis intentionally in new workbooks.
- Do not add borders around every filled cell.

### Finance defaults
- Format zeros as `-`.
- Negative numbers should be red and in parentheses.
- Format multiples as `5.2x`.
- Always specify units in headers.

## Validation
- Verify the output file exists and opens as the expected spreadsheet type.
- Verify formulas remain intact and cached values are refreshed when recalculation tooling is available.
- Verify formatting and layout on rendered sheets when rendering tools are available.
- Fail fast at the first failed validation gate and report the exact blocker.

## Anti-patterns
- Hardcoding derived values that should be formulas.
- Breaking existing workbook formatting during routine updates.
- Claiming formulas were recalculated when no recalculation tooling was available.
- Proceeding after missing dependency or rendering blockers without telling the user.
- Exposing internal implementation details when the user only needs the spreadsheet result.

## Variation
- Use `openpyxl`-first workflows for workbook-preserving edits.
- Use `pandas`-first workflows for analysis-heavy CSV or TSV pipelines.
- Increase visual-review rigor for finance, board-facing, or layout-sensitive spreadsheets.

## Examples
- Create a budgeting workbook with formulas, totals, and clean formatting.
- Clean and analyze a CSV, then write the results into a formatted `.xlsx` summary.
- Update an existing financial model without breaking formulas or style.
- Render a spreadsheet for layout review before delivery.

## See Also

| Skill | When to use together |
|---|---|
| [[markdown-converter]] | Convert spreadsheet data to markdown for documentation |
| [[visual-explainer]] | Present spreadsheet data as a styled HTML table |
| [[evals-router]] | Track evaluation results in a spreadsheet |
| [[insight-report]] | Export session data to spreadsheet for analysis |

**Topic map:** [[content-publishing]]

## Remember
Spreadsheet work is only trustworthy when formulas, formatting, and rendered output all agree with the requested change.

## Gotchas
- Symptom: Totals or derived values are typed as literals.
  Cause: Formula workflow was skipped during quick edits.
  Do instead: Use formula-first updates for all derived cells.
  Check: Derived cells contain formulas, not hardcoded numbers.
- Symptom: Workbook styling drifts after routine updates.
  Cause: New cell writes ignored surrounding style context.
  Do instead: Preserve and mirror nearby styles unless redesign is requested.
  Check: Changed ranges match existing number formats, alignment, and emphasis.
- Symptom: Output is declared validated without recalculation evidence.
  Cause: Recalculation tool availability was assumed.
  Do instead: Run dependency check and mark recalculation as unverified when unavailable.
  Check: Evidence summary explicitly states recalculation status.
- Symptom: Delivery includes only a merged artifact with no auditable intermediates.
  Cause: Intermediate outputs were overwritten or skipped.
  Do instead: Keep stable temporary artifacts until review is complete.
  Check: Output notes reference source artifact paths and final destination.
