# Architecture Re-review - JSC-351 PU-003

## Findings (Severity-ranked)

### Informational
- No actionable architecture or ubiquitous-language risks found after remediation.

## Re-review Scope
- Removed compatibility wrapper _skill_doctor_next_command.
- Added public CLI subprocess regression for invalid --runtime-target.
- Updated implementation notes language for T012 closeout context.

## Assessment
- The wrapper removal improves cohesion and removes duplicate decision-path indirection without changing doctor contract semantics. Evidence: _skill_doctor_next_command_decision remains the single selector path (Infrastructure/scripts/lib/ask/commands/skills_impl.py:2599-2714), and no remaining wrapper references exist in implementation/tests.
- The new subprocess regression strengthens the command-surface contract by proving invalid runtime target failures now traverse public CLI JSON output and include runtime_failure fields, preventing parser-only blind spots. Evidence: CLI subprocess assertion coverage (Infrastructure/tests/test_ask_skills_doctor.py:310-339).
- Notes update stays aligned with architectural intent and boundary ownership: parser validation handoff to command implementation is documented as a governed scope correction, not a platform ownership shift (.harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html:259-263).

## Compliance Check
- Boundary integrity: upheld.
- Contract stability: upheld (decision-first payload strategy remains additive and machine-readable).
- Coupling/circular dependency risk: none introduced.
- Ubiquitous-language drift: none observed in touched surfaces.

## Residual Risk
- Low and unchanged from prior review: external consumers of doctor schema must remain synchronized with next_command_decision requirements.

Validation evidence:
- python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q -> 15 passed, 15 subtests passed.

WROTE: artifacts/reviews/jsc-351-pu003/architecture-rereview.md
