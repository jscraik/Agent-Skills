# PU-005 Architecture Review

## Findings

No blocker, high, or medium architecture findings remain.

- informational - Infrastructure/scripts/lib/ask/commands/skills_impl.py:2865
  - Evidence: source identity is derived from a sibling Codex checkout and returns a structured blocked state when the checkout is unavailable.
  - Assessment: acceptable for this slice because the preview payload reports codex_source_identity as a blocked check instead of claiming runtime parity without source evidence.
  - Remediation: none required for PU-005.

- informational - Infrastructure/scripts/lib/ask/commands/skills_impl.py:3069
  - Evidence: live config layer and plugin root parity gaps are represented as structured blocked checks.
  - Assessment: this matches the slice constraint that unsupported parity dimensions must be JSON-visible blockers, not prose-only caveats.
  - Remediation: none required for PU-005.

- informational - Infrastructure/scripts/lib/ask/commands/skills_impl.py:3475
  - Evidence: implicit preview includes shell_parser_exact_parity as a blocked check before modeling attribution.
  - Assessment: this prevents over-claiming exact Codex runtime shell parsing while still making the useful deterministic subset available.
  - Remediation: none required for PU-005.

## Validation Notes

- python3 -m py_compile Infrastructure/bin/ask Infrastructure/scripts/lib/ask/commands/skills_impl.py passed.
- All five preview commands exit 0 and return source identity plus structured blocked checks where parity cannot be proven.
- ./bin/ask repo doctor --json --robot exits 0 and reports no blockers.

## Residual Risk

The preview commands are source-backed models, not live Codex runtime execution. That residual is intentionally surfaced through status=partial and blocked checks for live config layers, runtime plugin roots, structured UI skill selection, and exact shell parser parity.

WROTE: artifacts/reviews/jsc-351-pu005/architecture.md
