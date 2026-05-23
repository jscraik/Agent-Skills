## Simplification Analysis

### Core Purpose
Provide read-only previews of Codex skill runtime behavior (load/render/config/inject/implicit) with explicit fidelity limits and source-backed metadata, without mutating runtime state.

### Unnecessary Complexity Found
- low - Infrastructure/scripts/lib/ask/commands/skills_impl.py:3448
- Why unnecessary: `skills_inject_preview` calls `_extract_preview_mentions(text)` twice to build `mentions.names` and `mentions.paths`, doing duplicate regex scans over the same input.
- Suggested simplification: compute mentions once (`mentions = _extract_preview_mentions(text)`) and reuse it for both fields.

- low - Infrastructure/scripts/lib/ask/commands/skills_impl.py:3229
- Why unnecessary: in `_render_preview_lines`, the shortened-description branch computes `allowed` as an equal-share value per line but never decrements `remaining` as each line is rendered. This makes `remaining` effectively a constant and adds misleading state.
- Suggested simplification: either remove `remaining` entirely and rename to `per_line_allowance`, or decrement actual remaining budget while iterating. The first option is simpler and matches current behavior.

- low - Infrastructure/bin/ask:1106
- Why unnecessary: human-output handlers for five preview commands repeat near-identical summary/blocked-check/validation-command printing patterns with action-specific strings only.
- Suggested simplification: extract a tiny helper for preview summary printing (e.g., command label + key metrics + `print_first_validation_command`) to reduce boilerplate and make future preview additions safer.

### Code to Remove
- Infrastructure/scripts/lib/ask/commands/skills_impl.py:3448-3450 - duplicate mention extraction calls
- Estimated LOC reduction: 2-3

- Infrastructure/scripts/lib/ask/commands/skills_impl.py:3224 - unused/overstated `remaining` concept in current equal-share truncation path
- Estimated LOC reduction: 1-2 (or same LOC with clearer naming)

- Infrastructure/bin/ask:1106-1147 - repetitive preview print branches that can be collapsed via one helper
- Estimated LOC reduction: 15-30

### Simplification Recommendations
1. Cache explicit-mention extraction once in `skills_inject_preview`
   - Current: `_extract_preview_mentions(text)` is executed twice for payload assembly.
   - Proposed: bind once and reuse.
   - Impact: tiny LOC win, less repeated parsing, clearer intent.

2. Make render truncation math explicit and honest
   - Current: `remaining` implies progressive consumption but is never consumed.
   - Proposed: use a constant `per_line_allowance` (or implement real consumption if parity requires it).
   - Impact: removes misleading state, improves readability of budget behavior.

3. Consolidate preview CLI human-output formatting
   - Current: five adjacent branches duplicate structure for preview status printing.
   - Proposed: one local helper to print preview headline, optional warning/blocker count, then validation command.
   - Impact: moderate LOC reduction and lower maintenance overhead when preview payloads evolve.

### YAGNI Violations
- informational - Infrastructure/scripts/lib/ask/commands/skills_impl.py:3468
- Feature/abstraction: `shell_parser_exact_parity` blocked check is appropriate, but the implicit matcher still carries a broad interpreter/tool allowlist in code (`python`, `bash`, `zsh`, `node`, `deno`, etc.) without a shared constant.
- Why it leans YAGNI: this list is likely to grow ad hoc and duplicates policy-like data inline.
- What to do instead: move runner and reader command allowlists to named module-level constants for clarity and easier scope control; avoid expanding unless evidence demands it.

### Final Assessment
Total potential LOC reduction: ~1-2% in touched areas
Complexity score: Medium-Low
Recommended action: Proceed with simplifications

### Remediation Addendum
- The duplicate explicit-mention extraction was remediated in Infrastructure/scripts/lib/ask/commands/skills_impl.py.
- The misleading render truncation variable was remediated by replacing the constant remaining value with per_line_allowance.
- The preview CLI human-output helper recommendation remains low and non-blocking. It is not taken in PU-005 because it does not change runtime truth, validation strength, or parity safety, and would add churn after command-smoke validation.

No blocker/high/medium findings remain for this slice.
WROTE: artifacts/reviews/jsc-351-pu005/simplicity.md
