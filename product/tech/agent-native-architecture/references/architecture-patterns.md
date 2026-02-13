# Architecture Patterns (Codex Adaptation)

This reference captures architecture patterns for agent-native systems adapted for Codex workflows.

## 1) Event-driven agent loop

Treat events as prompts and tools as capabilities:

- Event source (user message, webhook, timer)
- Agent loop (reason + call tools)
- State update
- Completion or next iteration

Design implication: avoid forcing one-shot request/response behavior for multi-step outcomes.

## 2) Shared workspace pattern

Keep user and agent on the same truth surface whenever possible:

- Shared artifacts/state store.
- Deterministic update path from agent actions to user-visible state.
- Explicit refresh semantics when eventual consistency exists.

Design implication: avoid isolated agent-only state that users cannot inspect.

## 3) Two-layer durability model

Separate what should be versioned from what should remain local/runtime-specific:

- Versioned logic/prompts/contracts.
- Local/runtime state, logs, ephemeral artifacts.

Design implication: reproducible architecture changes without leaking instance-local data.

## 4) Progressive capability evolution

Start with primitives; add domain tools only when repeated patterns justify it:

1. Observe repeated multi-step composition.
2. Validate pain and error rate.
3. Introduce domain shortcut tool.
4. Keep primitive fallback paths available.

Design implication: avoid overfitting early with rigid domain workflows.

## 5) Approval-boundary architecture

Define action classes and approval requirements before implementation:

- Low risk: autonomous.
- Medium risk: bounded autonomy with confirmation points.
- High risk/destructive: explicit approval required.

Design implication: safety boundaries should be architectural, not ad hoc.

## Checklist

- Parity map exists.
- Shared state model is explicit.
- Completion semantics are explicit.
- Rollback path exists.
- Observability and audit trail are defined.
