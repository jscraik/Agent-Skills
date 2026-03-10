---
name: spreadsheet
description: Use when tasks involve creating, editing, analyzing, or formatting spreadsheets (`.xlsx`, `.csv`, `.tsv`) with formula-aware workflows, cached recalculation, and visual review.
---

# Spreadsheet Skill

Create, edit, analyze, and review spreadsheets with strong defaults for formulas, formatting, and final verification.

## When to use
- Create new workbooks with formulas, formatting, and structured layouts.
- Read or analyze tabular data, including filtering, aggregation, pivots, and metric calculations.
- Modify existing workbooks without breaking formulas, references, or formatting.
- Visualize data with charts, summary tables, and presentation-ready spreadsheet styling.
- Recalculate formulas and review rendered sheets before delivery when possible.

## Inputs
- Requested spreadsheet task and target file type (`.xlsx`, `.csv`, or `.tsv`).
- Source file paths, destination path, or required output location.
- Formatting expectations, charting needs, and whether visual review matters.
- Constraints on dependencies, local tooling, or whether installs are allowed.

## Outputs
- Updated or newly created spreadsheet artifact, or a clear blocked result if dependencies are missing.
- Short evidence summary covering formulas, formatting, and validation performed.
- When a structured status report is requested, include a `schema_version` field in the returned report payload.
- Notes on any missing recalculation or rendering capability that still requires local review.

## Philosophy
- Prefer deterministic workbook edits over ad hoc manual changes.
- Preserve formulas and formatting unless the user explicitly asks for a redesign.
- Use formulas for derived values rather than hardcoding results.
- What is the smallest spreadsheet change that solves the task safely?
- What evidence proves the workbook still calculates and renders correctly?

## Constraints
- Redact secrets, tokens, credentials, and sensitive spreadsheet content by default.
- Do not expose internal spreadsheet tooling, private APIs, or hidden recalculation systems in user-facing explanations.
- Do not overwrite established formatting unless the user explicitly asks for visual changes.
- If dependency installation is blocked, report the missing package or system tool and stop instead of improvising.

## Workflow
1. Confirm the file type and goal: create, edit, analyze, or visualize.
2. Prefer `openpyxl` for `.xlsx` editing and formatting; use `pandas` for analysis and CSV/TSV workflows.
3. If spreadsheet recalculation or rendering tooling is available, use it before delivery so formulas and layout can be reviewed.
4. Use formulas for derived values instead of hardcoding computed results.
5. If layout matters, render and inspect the relevant sheets before finalizing.
6. Save outputs with stable names and clean up intermediate files.

## Tooling
- Use `openpyxl` for creating or editing `.xlsx` files while preserving formatting.
- Use `pandas` for analysis-heavy CSV/TSV or tabular transformations, then write results back to `.xlsx` or `.csv` when needed.
- Use `openpyxl.chart` for native Excel charts.
- If LibreOffice (`soffice`) and Poppler (`pdftoppm`) are available, render sheets for visual review.

## Temp and output conventions
- Use `tmp/spreadsheets/` for intermediate files and delete them when done.
- Write final artifacts under `output/spreadsheet/` when working in this repo unless the task specifies a different destination.
- Keep filenames stable, descriptive, and easy to reopen.

## Dependencies
Prefer `uv` for Python dependency management.

Python packages:

```bash
uv pip install openpyxl pandas
```

If `uv` is unavailable:

```bash
python3 -m pip install openpyxl pandas
```

Optional charting support:

```bash
uv pip install matplotlib
```

If `uv` is unavailable:

```bash
python3 -m pip install matplotlib
```

System tools for rendering:

```bash
# macOS (Homebrew)
brew install libreoffice poppler

# Ubuntu/Debian
sudo apt-get install -y libreoffice poppler-utils
```

If installation is not possible in the current environment, report the missing dependency and provide the exact local install step instead of continuing blindly.

## Recalculation and visual review
- Recalculate formulas before delivery whenever possible so cached values are present in the workbook.
- Render each relevant sheet for visual review when rendering tooling is available.
- `openpyxl` does not evaluate formulas, so preserve formulas and use recalculation tooling where available.
- Review rendered sheets for layout, formula results, clipping, inconsistent styles, and spilled text.

Helpful rendering commands:

```bash
soffice --headless --convert-to pdf --outdir "$OUTDIR" "$INPUT_XLSX"
pdftoppm -png "$OUTDIR/$BASENAME.pdf" "$OUTDIR/$BASENAME"
```

## Spreadsheet rules

### Formula rules
- Use formulas for derived values rather than hardcoding results.
- Do not use dynamic array functions such as `FILTER`, `XLOOKUP`, `SORT`, or `SEQUENCE`.
- Keep formulas simple and legible; use helper cells for complex logic.
- Avoid volatile functions like `INDIRECT` and `OFFSET` unless required.
- Prefer cell references over magic numbers.
- Guard against `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, and `#NAME?` errors.
- Check for off-by-one mistakes, circular references, and incorrect ranges.

### Citation rules
- Cite sources inside the spreadsheet using plain-text URLs.
- For financial models, cite model inputs in cell comments.
- For tabular data sourced externally, add a source column when each row represents a separate item.

### Formatting rules for existing spreadsheets
- Render and inspect a provided spreadsheet before modifying it when possible.
- Preserve existing formatting and style exactly.
- Match styles for newly filled cells that were previously blank.
- Never overwrite established formatting unless the user explicitly asks for a redesign.

### Formatting rules for new spreadsheets
- Use appropriate number and date formats.
- Make headers visually distinct from raw inputs and derived cells.
- Use fill colors, borders, spacing, and merged cells sparingly and intentionally.
- Set row heights and column widths so content is readable without excessive whitespace.
- Do not apply borders around every filled cell.
- Add whitespace to separate sections and keep text from spilling into adjacent cells.

### Finance defaults
- Format zeros as `-`.
- Negative numbers should be red and in parentheses.
- Format multiples as `5.2x`.
- Always specify units in headers.
- For new financial models without user-specified style, use blue text for hardcoded inputs, black for formulas, green for internal workbook links, red for external links, and yellow fill for key assumptions that need attention.

### Investment banking layouts
- Sum totals from the range directly above.
- Hide gridlines and use horizontal borders above totals across relevant columns.
- Use merged section headers with dark fill and white text.
- Right-align numeric column labels and left-align row labels.
- Indent submetrics under their parent line items.

## Validation
- Verify the output file exists and opens as the expected spreadsheet type.
- Verify formulas remain intact and cached values are refreshed when recalculation tooling is available.
- Verify formatting and layout on rendered sheets when rendering tools are available.
- Fail fast: stop at the first failed validation gate and report the exact blocker.

## Anti-patterns
- Hardcoding derived values that should be formulas.
- Breaking existing workbook formatting during a routine data update.
- Claiming formulas were recalculated when no recalculation tooling was available.
- Exposing internal spreadsheet tooling or implementation details in user-facing explanations.
- Proceeding after missing dependency or rendering blockers without telling the user.

## Variation
- Use `openpyxl`-first workflows for workbook-preserving edits and `pandas`-first workflows for analysis-heavy tabular transformations.
- Adjust validation depth based on whether the task is read-only analysis, workbook mutation, or presentation-quality formatting.
- Increase visual review rigor for finance, board-facing, or layout-sensitive spreadsheets.

## Examples
- Create a budgeting workbook with formulas, totals, and basic formatting.
- Clean and analyze a CSV, then write the results into a formatted `.xlsx` summary.
- Update an existing financial model without breaking formulas or style.
- Render a spreadsheet for layout review before delivery.

## Resource map
- Interface metadata: `agents/openai.yaml`
- Assets: `assets/spreadsheet-small.svg`, `assets/spreadsheet.png`
- Examples: `references/examples/openpyxl/`
- Validation contracts: `references/contract.yaml`, `references/evals.yaml`

## Quality Uplift
- Philosophy and approach: explain why the chosen spreadsheet workflow is the safest fit for the task, call out tradeoffs clearly, and verify before completion.
- Guiding question: What proves this workbook still calculates correctly after the change?
- Guiding question: Is the requested result primarily analysis, editing, or presentation?
- Anti-pattern warning: do not hide missing rendering or recalculation capability.
- Anti-pattern warning: avoid generic spreadsheet advice when the task has concrete workbook paths and output requirements.
- Variation: adapt the approach for workbook-preserving edits versus analysis-first CSV/TSV pipelines.
- Empowerment: help users make safe spreadsheet changes confidently by surfacing risks and keeping the workflow auditable.
