## Simplification Analysis

### Core Purpose
The PU-006 code path adds read-only Codex runtime preview surfaces (`load-preview`, `render-preview`, `config explain`, `inject-preview`, `implicit-preview`) so `./bin/ask` can explain skill loading/rendering behavior with source-identity metadata and explicit blocked-fidelity checks.

### Unnecessary Complexity Found
- **Low** - duplicated conservative parser logic across modules
  - Evidence: `Infrastructure/scripts/lib/ask/services/codex_preview.py:39-104`, `Infrastructure/scripts/lib/ask/services/codex_preview.py:107-142`, `Infrastructure/scripts/lib/ask/commands/skills_impl.py:380-464`, `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2914-2949`
  - Why unnecessary: the same frontmatter/YAML subset parser behavior now exists in two places, increasing drift risk and test burden without adding differentiated behavior.
  - Suggested simplification: extract the conservative parsing helpers into one shared internal utility (for example under `ask/services` or a small parser module) and have both callers import it.

- **Low** - repeated one-line preview wrapper boilerplate in command handlers
  - Evidence: `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2845-2877`
  - Why unnecessary: each function repeats identical `CallResult` scaffolding with only command string, payload key, and builder differing.
  - Suggested simplification: introduce a tiny internal helper such as `_skills_preview_result(command, key, payload)` and keep public wrappers as one-liners.

### Code to Remove
- `Infrastructure/scripts/lib/ask/services/codex_preview.py:39-104` or `Infrastructure/scripts/lib/ask/commands/skills_impl.py:380-464` (one duplicated parser implementation) - reduce parser duplication.
- `Infrastructure/scripts/lib/ask/services/codex_preview.py:107-142` or `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2914-2949` (one duplicated `agents/openai.yaml` parser implementation) - reduce parser duplication.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2845-2877` (boilerplate extraction candidate) - reduce repeated wrapper scaffolding.
- Estimated LOC reduction: ~60-110 lines (depending on extraction style and whether wrappers are condensed).

### Simplification Recommendations
1. Consolidate parser helpers into one shared module
   - Current: two separate implementations parse the same conservative frontmatter/YAML subset.
   - Proposed: one shared parser API reused by `skills_impl` and `codex_preview`.
   - Impact: lower drift risk, fewer tests to maintain, and simpler future schema adjustments.

2. Collapse preview wrapper boilerplate in `skills_impl`
   - Current: five near-identical wrappers build `CallResult` objects.
   - Proposed: one helper to stamp metadata and data key, with wrappers only passing args.
   - Impact: small LOC reduction and easier additions for future preview subcommands.

### YAGNI Violations
- No high-confidence YAGNI violations found in the preview payload model itself.
- The modeled-rule and blocked-check payload depth appears intentional for auditability and aligns with the feature's explicit "source-backed explanation" scope.

### Final Assessment
Total potential LOC reduction: ~6-10% within the PU-006 touched surfaces.
Complexity score: Medium.
Recommended action: Minor tweaks only (parser dedupe first; wrapper condensation optional).

Residual risk: if parser duplication remains, behavior drift between package/readiness paths and preview paths is the most likely maintenance regression.

WROTE: artifacts/reviews/jsc-351-pu006/simplicity.md
