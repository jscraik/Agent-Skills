# JSC-351 PU-001 Architecture Review

## Scope
Reviewed only:
- Infrastructure/bin/ask
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/tests/test_ask_skills_doctor.py
- .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md
- .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md
- docs/goals/jsc-351-agent-skills-codex-abi-conformance/**
- .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html

## Findings (Severity-ranked)

### informational — PU-001 architectural boundary and trust-boundary intent are preserved
Evidence:
- Parser additions are additive and scoped to PU-001 contract:
  - Infrastructure/bin/ask:135-138 adds skills proof --runtime-target.
  - Infrastructure/bin/ask:141-142 adds skills doctor --codex-parity.
  - Infrastructure/bin/ask:530-537 wires both flags into existing command dispatch without broad command-surface refactor.
- Runtime-target gate semantics are explicit and fail-closed for Codex target:
  - Infrastructure/scripts/lib/ask/commands/skills_impl.py:1179-1184 maps required gate by target (any|codex|agents) and computes required readiness per target.
  - Infrastructure/scripts/lib/ask/commands/skills_impl.py:1192 sets proof status to fail unless core gates plus required runtime gate pass.
  - Infrastructure/scripts/lib/ask/commands/skills_impl.py:1205-1209 documents target-specific required semantics.
  - Infrastructure/scripts/lib/ask/commands/skills_impl.py:1227-1233 reports runtime_satisfied_by as None when target-specific gate is unsatisfied.
- Doctor parity path reuses proof contract instead of introducing a parallel coupling path:
  - Infrastructure/scripts/lib/ask/commands/skills_impl.py:3200-3201 routes parity via skills_proof(..., runtime_target="codex").
  - Infrastructure/scripts/lib/ask/commands/skills_impl.py:3215-3221 classifies parity miss as blocked_runtime.
  - Infrastructure/scripts/lib/ask/commands/skills_impl.py:3228-3241 fail-closes path targets under --codex-parity when no command handle is available.
- Tests explicitly enforce the intended trust boundary:
  - Infrastructure/tests/test_ask_skills_doctor.py:210-230 proves .agents readiness can satisfy any but cannot satisfy codex.
  - Infrastructure/tests/test_ask_skills_doctor.py:306-347 verifies doctor parity invokes codex-targeted proof and yields blocker-first next command behavior.
- Plan/spec alignment:
  - Plan requires fail-closed codex-targeted proof and scoped files (.harness/plan/...:213-227), which the implementation follows.
  - Plan guardrail “Do not claim Codex ABI conformance from .agents runtime readiness” (.harness/plan/...:174) is upheld by code paths above.

Remediation:
- None required for PU-001 architecture closure.

## Residual risk / test gaps
- Residual low risk: no independent focused test in this file for path-target + --codex-parity blocker payload shape (code exists at skills_impl.py:3228-3241). This is not a PU-001 blocker, but adding one assertion case would further harden regression detection.
- Non-architecture operational note: local-memory bootstrap/search could not run in this sandbox due to PID-file permission on ~/.local-memory/local-memory.pid; review conclusions are based on direct repo evidence only.

## Closure recommendation
- PU-001 is architecturally fit to proceed to PM/git triage.
- No unresolved blocker/high/medium findings for this slice.
- Later PU boundaries (PU-002+) appear preserved: no broad service extraction, no generated projection edits, and no ownership-boundary drift in reviewed files.

WROTE: artifacts/reviews/jsc-351-pu001/architecture.md
