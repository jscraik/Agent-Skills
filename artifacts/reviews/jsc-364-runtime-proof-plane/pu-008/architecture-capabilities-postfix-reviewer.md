# Architecture Capabilities Postfix Review

## Scope
Post-fix review of runtime target contract placement after moving target constants to the SDK runtime adapter contract.

Reviewed files:
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py
- Infrastructure/scripts/lib/ask/commands/skills.py

## Severity-ranked findings

### No material findings
No remaining architectural violations were found in the reviewed scope.

1. Resolved: command-layer no longer owns runtime target constants.
- Evidence: `skills_impl.py` imports `SUPPORTED_RUNTIME_TARGETS` and `EVIDENCE_RUNTIME_TARGETS` from runtime adapter contract ([Infrastructure/scripts/lib/ask/commands/skills_impl.py:72](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:72), [Infrastructure/scripts/lib/ask/commands/skills_impl.py:73](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:73), [Infrastructure/scripts/lib/ask/commands/skills_impl.py:74](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:74)).
- Evidence: canonical target sets are defined in SDK runtime boundary ([Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:14](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:14), [Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:15](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:15)).
- Architectural effect: ownership is now correctly inverted to the adapter/contract layer, reducing command-surface drift risk.

2. Command-layer abstraction remains orchestration-only.
- Evidence: `skills_capabilities` consumes normalized target + SDK constants, then emits capability discovery payload without re-defining contract constants ([Infrastructure/scripts/lib/ask/commands/skills_impl.py:2629](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2629), [Infrastructure/scripts/lib/ask/commands/skills_impl.py:2632](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2632), [Infrastructure/scripts/lib/ask/commands/skills_impl.py:2646](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2646)).
- Architectural effect: preserves separation between policy contract (SDK) and response assembly (command handler).

3. Modeled-vs-live runtime truth boundary is explicit and preserved.
- Evidence: capability discovery encodes non-claim posture for live parity plus truth boundary fields ([Infrastructure/scripts/lib/ask/commands/skills_impl.py:2647](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2647), [Infrastructure/scripts/lib/ask/commands/skills_impl.py:2707](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2707), [Infrastructure/scripts/lib/ask/commands/skills_impl.py:2710](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2710)).
- Architectural effect: avoids leaky abstraction where discovery output could be misread as proof.

## Residual risks (non-blocking)
1. `runtime_target_support.evidence_targets` remains literal in response payload.
- Evidence: hardcoded `["codex", "agents"]` ([Infrastructure/scripts/lib/ask/commands/skills_impl.py:2664](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2664)).
- Risk: if adapter contract changes, this field could drift from SDK constants while validation still passes elsewhere.
- Suggested hardening: derive payload `evidence_targets` directly from `EVIDENCE_RUNTIME_TARGETS` (sorted for stable output).

## Overall assessment
- Command-layer placement: compliant
- Target contract ownership: compliant
- Abstraction level: compliant
- Ask result pattern: compliant for this scope
- Modeled-vs-live truth boundary: compliant

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/architecture-capabilities-postfix-reviewer.md
