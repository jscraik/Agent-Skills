# Agent-Native Primitives

Use this reference when the target repository contains an agent-facing app, product workflow, MCP server, autonomous loop, system prompt, tool surface, or UI action that agents are expected to operate. Apply these criteria inside the normal readiness scorecard; do not create a separate report.

## Action Parity

- Every meaningful UI or user workflow action has an agent-accessible equivalent, or an explicit reason it is user-only.
- A capability map exists or can be derived from UI actions, routes, commands, tools, and prompt capability docs.
- New UI or product capabilities update the corresponding tool, prompt capability text, capability map, and parity test in the same change.

Good next move: add a small capability map that lists user action, location, agent tool or workflow, prompt reference, and status.

## Primitive Tool Design

- Tools expose capabilities, not pre-decided workflows.
- Tools accept data, not hidden business judgments that should belong in the agent prompt or policy.
- Tool names use user vocabulary where possible.
- Tool outputs include enough state for the agent to verify, recover, and iterate.
- Core entities expose create, read, update, and delete coverage unless a missing operation has a safety or product reason.

Flag workflow-shaped tools such as process_feedback, analyze_and_organize, or do_everything_for_case when they combine classification, persistence, notification, and policy decisions without a clear boundary.

## Dynamic Context

- Agent prompts include the current resources the user can see or operate.
- Prompts map user vocabulary to product locations, tools, and expected outcomes.
- Long-running sessions can refresh app state through a context builder, hook, tool, or equivalent.
- The agent can discover available capabilities without relying on stale static instructions.

Context starvation is a readiness gap when the user can see or name something in the product but the agent cannot infer the target resource, location, or tool.

## Shared Workspace

- Agent and user operate on the same underlying data plane where practical.
- Agent writes are reflected in the UI or user-visible workflow without silent state divergence.
- Generated outputs have a clear ownership, rollback, and freshness boundary.

If the agent writes to a separate scratch space while the user operates another state space, classify that as a shared-workspace gap unless isolation is intentional.

## Execution Signals

- Agent-facing products expose explicit completion, checkpoint, resume, or handoff signals.
- Multi-step tasks record enough progress for recovery after interruption or context loss.
- Completion is not inferred only from silence, elapsed time, or absence of tool calls.

Good next move: add a complete_task tool, progress record, or durable handoff artifact when tasks can span multiple turns.

## Outcome Tests

- Tests verify user-visible outcomes, not only exact tool-call sequences.
- Parity tests check that meaningful UI actions have agent capabilities.
- Context tests prove the agent can understand user vocabulary and current app state.
- Open-ended capability tests verify the agent can accomplish an in-domain outcome that was not implemented as a single hard-coded feature.

Static checks remain useful, but lint, typecheck, and unit tests do not prove product-agent readiness by themselves.

## Evidence Boundary

Use file-path evidence from the target repository: prompts, tools, MCP schemas, UI routes, docs, tests, capability maps, workflow state, logs, screenshots, or product smoke artifacts. If those surfaces are missing, report the missing surface as the evidence.

Name this reference in the scorecard only when it materially informs the finding: references/agent-native-primitives.md.
