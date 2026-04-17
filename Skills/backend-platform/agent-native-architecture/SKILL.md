---
name: agent-native-architecture
description: Build applications where agents are first-class citizens. Use this skill when designing autonomous agents, creating MCP tools, implementing self-modifying systems, or building apps where features are outcomes achieved by agents operating in a loop.
metadata:
  skill-type: library_api_reference
---

# Agent-Native Architecture

Refreshed against the pinned donor snapshot in `EveryInc/compound-engineering-plugin`; see `Infrastructure/references/source-parity.md` for the exact source path and preserved behaviors.

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Why Now](#why-now)
- [Core Principles](#core-principles)
- [What Aspect Of Agent-Native Architecture Do You Need Help With?](#what-aspect-of-agent-native-architecture-do-you-need-help-with)
- [Architecture Review Checklist](#architecture-review-checklist)
- [Quick Start: Build An Agent-Native Feature](#quick-start-build-an-agent-native-feature)
- [Reference Files](#reference-files)
- [Reference Usage Contract](#reference-usage-contract)
- [Anti-Patterns](#anti-patterns)
- [Success Criteria](#success-criteria)
- [Gotchas](#gotchas)

<why_now>

## Why Now

Software agents work reliably now. Claude Code demonstrated that an LLM with access to bash and file tools, operating in a loop until an objective is achieved, can accomplish complex multi-step tasks autonomously.

The surprising discovery: **a really good coding agent is actually a really good general-purpose agent.** The same architecture that lets Claude Code refactor a codebase can let an agent organize your files, manage your reading list, or automate your workflows.

The Claude Code SDK makes this accessible. You can build applications where features aren't code you write—they're outcomes you describe, achieved by an agent with tools, operating in a loop until the outcome is reached.

This opens up a new field: software that works the way Claude Code works, applied to categories far beyond coding.
</why_now>

<core_principles>

## When to use

Use this skill when:

- you are designing an agent-native product or major subsystem from scratch;
- you need architecture guidance for agent loops, tool design, parity, or shared-workspace patterns;
- you want to refactor an existing application so agents can operate as first-class users;
- you need design criteria for MCP tools, dynamic context injection, agent-native testing, or self-modification guardrails.

Do not use this skill when:

- you need a repository audit of whether a workflow is agent-native in practice; use `agent-native-audit`;
- you need an ADR-style interview to force a design decision; use `architecture-interview`;
- you already know the implementation target and need file-level backend changes; use `backend-engineer` or a more specific build skill.

## Required inputs

- the product, workflow, or architecture surface being designed or reviewed;
- the primary agent goal or user outcome;
- any constraints around data, approvals, UI parity, safety, deployment, or platform limits;
- whether the ask is greenfield design, refactor guidance, tool design, testing, or self-modification.

## Deliverables

- an agent-native architecture recommendation grounded in parity, granularity, and composability;
- a focused checklist or review against the relevant patterns;
- explicit reference handoffs into the imported `Infrastructure/references/` material for the next deep-dive step;
- source-aware guidance that names the exact imported reference when the recommendation depends on a nuanced pattern or tradeoff;
- clear risks, constraints, and follow-up questions when the architecture boundary is still fuzzy.

## Failure mode

- If the target system or desired outcome is unclear, stop and narrow the architecture surface first.
- If the user actually wants an audit, ADR interview, or implementation patch, switch to the more specific skill instead of stretching this one.
- If the architecture depends on hidden platform constraints, call them out as unresolved inputs before recommending a pattern.

## Core Principles

The imported reference set centers on five ideas:

### 1. Parity

Whatever a human can do in the product, the agent should be able to achieve through tools or primitives. Read [action-parity-discipline.md](/docs/product/domain/agent-native-architecture/references/action-parity-discipline.md) when mapping UI actions to agent capabilities.

### 2. Granularity

Keep tools primitive and push decision-making into prompts and the agent loop. Read [mcp-tool-design.md](/docs/product/domain/agent-native-architecture/references/mcp-tool-design.md) and [from-primitives-to-domain-tools.md](/docs/product/domain/agent-native-architecture/references/from-primitives-to-domain-tools.md) when deciding where code stops and agent judgment starts.

### 3. Composability

New features should emerge from new prompts and tool composition rather than bespoke workflow code. Read [system-prompt-design.md](/docs/product/domain/agent-native-architecture/references/system-prompt-design.md) for the prompt-side discipline.

### 4. Emergent Capability

The architecture should let the agent solve domain-relevant requests you did not explicitly productize. Read [architecture-patterns.md](/docs/product/domain/agent-native-architecture/references/architecture-patterns.md) and [product-implications.md](/docs/product/domain/agent-native-architecture/references/product-implications.md) for the product and systems consequences.

### 5. Improvement Over Time

Agent-native systems should accumulate context, refine prompts, and optionally evolve behavior safely over time. Read [dynamic-context-injection.md](/docs/product/domain/agent-native-architecture/references/dynamic-context-injection.md), [shared-workspace-architecture.md](/docs/product/domain/agent-native-architecture/references/shared-workspace-architecture.md), and [self-modification.md](/docs/product/domain/agent-native-architecture/references/self-modification.md).
</core_principles>

<intake>
## What aspect of agent-native architecture do you need help with?

1. **Design architecture** - Plan a new agent-native system from scratch
2. **Files & workspace** - Use files as the universal interface, shared workspace patterns
3. **Tool design** - Build primitive tools, dynamic capability discovery, CRUD completeness
4. **Domain tools** - Know when to add domain tools vs stay with primitives
5. **Execution patterns** - Completion signals, partial completion, context limits
6. **System prompts** - Define agent behavior in prompts, judgment criteria
7. **Context injection** - Inject runtime app state into agent prompts
8. **Action parity** - Ensure agents can do everything users can do
9. **Self-modification** - Enable agents to safely evolve themselves
10. **Product design** - Progressive disclosure, latent demand, approval patterns
11. **Mobile patterns** - iOS storage, background execution, checkpoint/resume
12. **Testing** - Test agent-native apps for capability and parity
13. **Refactoring** - Make existing code more agent-native

**Wait for response before proceeding.**
If the user already named the architecture surface, skip this menu and route directly. Use it as an intake aid only when the ask is still broad.
</intake>

<routing>
| Response | Action |
|----------|--------|
| 1, "design", "architecture", "plan" | Read [architecture-patterns.md](/docs/product/domain/agent-native-architecture/references/architecture-patterns.md), then apply Architecture Checklist below |
| 2, "files", "workspace", "filesystem" | Read [files-universal-interface.md](/docs/product/domain/agent-native-architecture/references/files-universal-interface.md) and [shared-workspace-architecture.md](/docs/product/domain/agent-native-architecture/references/shared-workspace-architecture.md) |
| 3, "tool", "mcp", "primitive", "crud" | Read [mcp-tool-design.md](/docs/product/domain/agent-native-architecture/references/mcp-tool-design.md) |
| 4, "domain tool", "when to add" | Read [from-primitives-to-domain-tools.md](/docs/product/domain/agent-native-architecture/references/from-primitives-to-domain-tools.md) |
| 5, "execution", "completion", "loop" | Read [agent-execution-patterns.md](/docs/product/domain/agent-native-architecture/references/agent-execution-patterns.md) |
| 6, "prompt", "system prompt", "behavior" | Read [system-prompt-design.md](/docs/product/domain/agent-native-architecture/references/system-prompt-design.md) |
| 7, "context", "inject", "runtime", "dynamic" | Read [dynamic-context-injection.md](/docs/product/domain/agent-native-architecture/references/dynamic-context-injection.md) |
| 8, "parity", "ui action", "capability map" | Read [action-parity-discipline.md](/docs/product/domain/agent-native-architecture/references/action-parity-discipline.md) |
| 9, "self-modify", "evolve", "git" | Read [self-modification.md](/docs/product/domain/agent-native-architecture/references/self-modification.md) |
| 10, "product", "progressive", "approval", "latent demand" | Read [product-implications.md](/docs/product/domain/agent-native-architecture/references/product-implications.md) |
| 11, "mobile", "ios", "android", "background", "checkpoint" | Read [mobile-patterns.md](/docs/product/domain/agent-native-architecture/references/mobile-patterns.md) |
| 12, "test", "testing", "verify", "validate" | Read [agent-native-testing.md](/docs/product/domain/agent-native-architecture/references/agent-native-testing.md) |
| 13, "review", "refactor", "existing" | Read [refactoring-to-prompt-native.md](/docs/product/domain/agent-native-architecture/references/refactoring-to-prompt-native.md) |

**After reading the reference, apply those patterns to the user's specific context.**
</routing>

<architecture_checklist>

## Architecture Review Checklist

When designing an agent-native system, verify these **before implementation**:

### Core Principles

- [ ] **Parity:** Every UI action has a corresponding agent capability
- [ ] **Granularity:** Tools are primitives; features are prompt-defined outcomes
- [ ] **Composability:** New features can be added via prompts alone
- [ ] **Emergent Capability:** Agent can handle open-ended requests in your domain

### Tool Design

- [ ] **Dynamic vs Static:** For external APIs where agent should have full access, use Dynamic Capability Discovery
- [ ] **CRUD Completeness:** Every entity has create, read, update, AND delete
- [ ] **Primitives not Workflows:** Tools enable capability, don't encode business logic
- [ ] **API as Validator:** Use `z.string()` inputs when the API validates, not `z.enum()`

### Files & Workspace

- [ ] **Shared Workspace:** Agent and user work in same data space
- [ ] **context.md Pattern:** Agent reads/updates context file for accumulated knowledge
- [ ] **File Organization:** Entity-scoped directories with consistent naming

### Agent Execution

- [ ] **Completion Signals:** Agent has explicit `complete_task` tool (not heuristic detection)
- [ ] **Partial Completion:** Multi-step tasks track progress for resume
- [ ] **Context Limits:** Designed for bounded context from the start

### Context Injection

- [ ] **Available Resources:** System prompt includes what exists (files, data, types)
- [ ] **Available Capabilities:** System prompt documents tools with user vocabulary
- [ ] **Dynamic Context:** Context refreshes for long sessions (or provide `refresh_context` tool)

### UI Integration

- [ ] **Agent → UI:** Agent changes reflect in UI (shared service, file watching, or event bus)
- [ ] **No Silent Actions:** Agent writes trigger UI updates immediately
- [ ] **Capability Discovery:** Users can learn what agent can do

### Mobile (if applicable)

- [ ] **Checkpoint/Resume:** Handle iOS app suspension gracefully
- [ ] **iCloud Storage:** iCloud-first with local fallback for multi-device sync
- [ ] **Cost Awareness:** Model tier selection (Haiku/Sonnet/Opus)

**When designing architecture, explicitly address each checkbox in your plan.**
</architecture_checklist>

<quick_start>

## Quick Start: Build an Agent-Native Feature

1. Start with atomic read, write, list, update, and completion primitives.
2. Write the feature behavior in the system prompt instead of encoding the workflow in code.
3. Give the agent a loop with explicit completion signaling.
4. Verify parity, shared workspace, and CRUD completeness before adding polish.

For deeper implementation examples, use the imported references rather than expanding this wrapper.
Read `Infrastructure/references/architecture-patterns.md` and `Infrastructure/references/agent-execution-patterns.md` when you need concrete tool, prompt, or loop examples before recommending a pattern.
</quick_start>

<reference_index>

## Reference Files

Package surfaces:

- [source-parity.md](/docs/product/domain/agent-native-architecture/references/source-parity.md) - donor path, preserved behaviors, local adaptations
- [contract.yaml](/docs/product/domain/agent-native-architecture/references/contract.yaml) - compact contract for validators and future maintenance
- [evals.yaml](/docs/product/domain/agent-native-architecture/references/evals.yaml) - routing and pressure-test coverage for this wrapper
- [agents/openai.yaml](/docs/product/domain/agent-native-architecture/agents/openai.yaml) - Codex UI metadata for the local package

All references in `Infrastructure/references/`:

**Core Patterns:**

- [architecture-patterns.md](/docs/product/domain/agent-native-architecture/references/architecture-patterns.md) - Event-driven, unified orchestrator, agent-to-UI
- [files-universal-interface.md](/docs/product/domain/agent-native-architecture/references/files-universal-interface.md) - Why files, organization patterns, context.md
- [mcp-tool-design.md](/docs/product/domain/agent-native-architecture/references/mcp-tool-design.md) - Tool design, dynamic capability discovery, CRUD
- [from-primitives-to-domain-tools.md](/docs/product/domain/agent-native-architecture/references/from-primitives-to-domain-tools.md) - When to add domain tools, graduating to code
- [agent-execution-patterns.md](/docs/product/domain/agent-native-architecture/references/agent-execution-patterns.md) - Completion signals, partial completion, context limits
- [system-prompt-design.md](/docs/product/domain/agent-native-architecture/references/system-prompt-design.md) - Features as prompts, judgment criteria

**Agent-Native Disciplines:**

- [dynamic-context-injection.md](/docs/product/domain/agent-native-architecture/references/dynamic-context-injection.md) - Runtime context, what to inject
- [action-parity-discipline.md](/docs/product/domain/agent-native-architecture/references/action-parity-discipline.md) - Capability mapping, parity workflow
- [shared-workspace-architecture.md](/docs/product/domain/agent-native-architecture/references/shared-workspace-architecture.md) - Shared data space, UI integration
- [product-implications.md](/docs/product/domain/agent-native-architecture/references/product-implications.md) - Progressive disclosure, latent demand, approval
- [agent-native-testing.md](/docs/product/domain/agent-native-architecture/references/agent-native-testing.md) - Testing outcomes, parity tests

**Platform-Specific:**

- [mobile-patterns.md](/docs/product/domain/agent-native-architecture/references/mobile-patterns.md) - iOS storage, checkpoint/resume, cost awareness
- [self-modification.md](/docs/product/domain/agent-native-architecture/references/self-modification.md) - Git-based evolution, guardrails
- [refactoring-to-prompt-native.md](/docs/product/domain/agent-native-architecture/references/refactoring-to-prompt-native.md) - Migrating existing code
  </reference_index>

## Reference Usage Contract

Treat this `SKILL.md` as a router, not the full body of the architecture doctrine.

- When a user asks for concrete architecture advice, read the most relevant imported reference before recommending a pattern.
- If the recommendation depends on a subtle tradeoff, cite the specific reference file instead of flattening it into generic guidance.
- If multiple architecture surfaces are involved, combine the relevant references rather than relying on this wrapper alone.
- If the wrapper and a reference ever feel mismatched, treat the imported reference as canonical for the detailed pattern.
- Use `Infrastructure/references/source-parity.md` when refreshing this package again so the local wrapper keeps the donor's doctrine without losing repo-specific packaging and routing improvements.

<anti_patterns>

## Anti-Patterns

Watch for:

- agent-as-router designs where the agent only picks prewritten workflows;
- workflow-shaped tools that bury judgment in code instead of prompts;
- UI actions with no agent path to the same outcome;
- context-starved prompts that never tell the agent what resources exist;
- heuristic completion detection instead of an explicit completion signal;
- incomplete CRUD or overly static tool surfaces for dynamic domains.

Use the relevant imported reference before recommending a fix.
</anti_patterns>

<success_criteria>

## Success Criteria

You are in good shape when:

- the agent can achieve the same outcomes users can achieve through the product;
- tools stay atomic and features are expressed as outcomes, not hand-coded workflows;
- new behavior mostly comes from prompt and context changes rather than refactors;
- agents operate in the same workspace as users and surface explicit completion;
- the system can handle unanticipated but in-domain requests without collapsing into “I don’t have a feature for that.”
  </success_criteria>

## Gotchas

- This skill imports deep reference material intentionally; prefer reading the linked `Infrastructure/references/` files instead of re-expanding the wrapper.
- Do not “simplify” away the imported doctrine. Preserve impact by keeping the detailed patterns in `Infrastructure/references/` and routing to them explicitly.
- If you find yourself writing audit findings, ADR interviews, or file-level implementation plans, you have probably crossed into a neighboring skill.
- If the user already specified the architecture surface, do not force them back through the numbered intake menu; route directly to the matching reference and keep momentum.

## See Also

| Skill                      | When to use together                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------------ |
| [[agent-native-audit]]     | Audit whether an existing repo or workflow already meets agent-native operating principles |
| [[architecture-interview]] | Structure tradeoff-heavy architecture choices into an ADR-style decision                   |
| [[mcp-builder]]            | Build general MCP servers once the tool surface is clear                                   |
| [[chatgpt-apps]]           | Apply agent-native patterns inside a ChatGPT Apps SDK product                              |

**Topic map:** [[backend-platform]]
