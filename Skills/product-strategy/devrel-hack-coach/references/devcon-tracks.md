# DevCon Tracks: AI Native Hackathon Track Cheat Sheet

Use this file when the user is unsure which track fits their itch, or when
Phase 2 needs three concrete hack angles.

The original source package used AI Native DevCon 2026 tracks. Treat these as
AI-native hackathon categories unless the user supplies current event tracks.

## 1. Context Engineering

The discipline of giving an agent the right information at the right moment:
retrieval, prompt caching, grounding, context windows, and source selection.

Keywords: RAG, retrieval, prompt caching, context window, grounding,
embeddings, chunking, token budget, tool docs in context.

Example angles:

- CacheScope: diff consecutive API calls and highlight the line that broke
  prompt caching.
- RetrieveReplay: replay a run with different retrieval strategies and compare
  outputs.
- ContextMirror: show what the agent can see right now, with color-coded
  context sources.

Avoid: new embedding models, generic chatbots, or "we prompt-engineered it."

## 2. Agent Orchestration

Coordinating agents or long-running workflows: fan-out, checkpointing,
handoffs, recovery, routing, and retries.

Keywords: multi-agent, workflow, parallel, checkpoint, resume, routing,
handoff, dead-letter, long-running, retries, idempotency.

Example angles:

- LoopScope: visual debugger for agent loops and tool-call timelines.
- FanOut: bounded parallel research agents with conflict detection.
- CheckpointKit: make an agent workflow resumable from the last successful
  node.

Avoid: single-turn chat, pure prompt engineering, or generic job queues that do
not expose agent-shaped difficulty.

## 3. Agent Enablement Platform

Infrastructure for building and running agents: sandboxes, observability,
evals, deployment, permissions, test harnesses, and SDKs.

Keywords: sandbox, observability, evals, permissions, audit log, test harness,
SDK, platform, deploy, isolation.

Example angles:

- SandboxCLI: one-command sandbox with an audit log and egress tripwires.
- EvalsInCI: PR action that posts agent eval pass/fail diffs.
- AskBeforeAct: permission prompt before destructive agent actions.

Avoid: single-purpose end-user agents, model deployment alone, or vendor
wrappers with no distinct contribution.

## 4. Organizational Enablement

Teams adopting AI-native workflows: developer experience, metrics, governance,
training, review culture, and human-agent collaboration.

Keywords: DX, adoption, metrics, governance, review, training, team,
collaboration, workflow, ROI, culture.

Example angles:

- AgentLedger: weekly report of AI-assisted PR-cycle deltas.
- ReasoningPR: PR template and linter that require agent reasoning capture.
- OnboardingCopilot: coach junior devs to explain why an agent suggestion is
  correct before accepting it.

Avoid: pure technical tools with no team dimension, compliance-only plays, or
dashboards that do not drive decisions.

## Matching Rule

- Data going in or out of prompts -> Context Engineering.
- Multiple steps, agents, or long-running state -> Agent Orchestration.
- Infrastructure for other agents -> Agent Enablement Platform.
- Humans and teams adopting AI -> Organizational Enablement.

If the idea sits on a boundary, pick the track whose judges will care most.
Do not claim two tracks unless the current event explicitly allows it.
