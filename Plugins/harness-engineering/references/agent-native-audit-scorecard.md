# Agent-Native Audit Scorecard

Read when: reviewing or generating HE artifacts for skills, plugins, CLIs,
agent docs, evals, routing, projections, automation, or workflow surfaces.

## Purpose

Use this as a Harness Engineering lens, not a standalone lifecycle stage. The
scorecard determines whether a change remains genuinely agent-native: locally
discoverable, deterministic, proof-backed, and safe for future agents to operate.

## Required Dimensions

For each relevant dimension record `pass`, `partial`, `fail`, or `unknown` plus
evidence:

- Action parity: every meaningful human action has an agent-operable route.
- Capability discovery: the agent can find the right command, skill, or artifact
  without broad tree loading.
- Context injection: required context is explicit, bounded, and stage-owned.
- Shared truth surface: artifacts, plans, evals, and state live in stable
  repo-readable surfaces instead of chat-only memory.
- Entity completion: work items, artifacts, and proof states have clear create,
  update, review, and completion paths.
- Integration feedback: UI, CLI, plugin, or workflow surfaces return actionable
  status, errors, and next steps.
- Prompt-native composability: specialist prompts or skills improve the current
  stage without replacing HE routing or expanding the approved slice.
- Deterministic completion: done state is backed by validation, evals, or
  explicitly blocked evidence.

## Closure Rules

- A `fail` in action parity, capability discovery, shared truth surface, or
  deterministic completion blocks readiness for agent-facing changes unless a
  justified exception is recorded.
- `unknown` is not passing evidence. State the missing inspection method and
  whether it blocks closure.
- Do not claim agent-native quality from naming, docs, routing metadata, or green
  CI alone. Require observable workflow, artifact, or command evidence.

## Output Fields

When structured output is used, include:

```yaml
agent_native_scorecard_status: pass|partial|fail|unknown|not_applicable
scorecard_dimensions:
  action_parity: pass|partial|fail|unknown|not_applicable
  capability_discovery: pass|partial|fail|unknown|not_applicable
  context_injection: pass|partial|fail|unknown|not_applicable
  shared_truth_surface: pass|partial|fail|unknown|not_applicable
  entity_completion: pass|partial|fail|unknown|not_applicable
  integration_feedback: pass|partial|fail|unknown|not_applicable
  prompt_native_composability: pass|partial|fail|unknown|not_applicable
  deterministic_completion: pass|partial|fail|unknown|not_applicable
scorecard_evidence: "<files, commands, artifacts, or inspection method>"
scorecard_blocks_closure: yes|no
scorecard_required_action: "<required repair or not_applicable>"
```

## Anti-Patterns

- Treating an agent-facing README as proof that agents can operate the system.
- Adding more prompt text instead of improving commands, artifacts, or evals.
- Accepting broad skill enumeration as discoverability.
- Calling a workflow deterministic when the completion signal is chat-only.
