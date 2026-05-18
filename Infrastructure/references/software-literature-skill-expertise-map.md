# Software Literature Skill Expertise Map

Use this map to decide where software-literature lenses should strengthen
skills. The lenses are optional expert checks, not authority. Keep SKILL.md
front doors compact and link to
Infrastructure/references/software-literature-expert-lens-pack.md only when the
task needs the lens.

## Source Boundary

Use source titles as provenance only. Do not copy book text, chapter summaries,
examples, diagrams, or proprietary phrasing into skill packages. Convert ideas
into original checks, eval probes, output contracts, and stop conditions.

## Primary Skill Targets

| Skill | Lenses | Use |
| --- | --- | --- |
| Skills/agent-ops/improve-codebase-architecture | Deep Module Examiner, Architectural Pattern Cartographer, Pattern Catalog Skeptic, Domain Language Guardian, Pragmatic Delivery Partner | Architecture pressure tests, boundary choices, patch-vs-interface tradeoffs, tracer proof. |
| Skills/agent-ops/simplify | Micro-Refactoring Surgeon, Refactoring Catalog Operator, Clean Code Craftsperson, Deep Module Examiner | Behavior-preserving simplification and small reversible cleanup. |
| Skills/agent-ops/unslopify | Micro-Refactoring Surgeon, Clean Code Craftsperson, Pragmatic Delivery Partner | Dead-code and slop cleanup with evidence and rollback. |
| Skills/agent-ops/ubiquitous-language | Domain Language Guardian, Use-Case Flow Designer | Glossaries, aliases, bounded contexts, source/projection terminology discipline. |
| Skills/agent-ops/evals-router | Story Slicer, Use-Case Flow Designer, XP Feedback Coach, Pragmatic Delivery Partner | Realistic eval prompts, negative paths, acceptance checks, pass/fail/blocked evidence. |
| Skills/agent-ops/verification-before-completion | XP Feedback Coach, Pragmatic Delivery Partner | Validation freshness, exact evidence, blocked state discipline. |
| Skills/agent-ops/coding-harness | XP Feedback Coach, Pragmatic Delivery Partner, Domain Language Guardian, Data-Intensive Systems Critic | Execution loops, stable vocabulary, production-like data and integration checks. |
| Skills/backend-platform/backend-engineer | Data-Intensive Systems Critic, Integration Pattern Mechanic, Domain Language Guardian, Pragmatic Delivery Partner, Clean Code Craftsperson | Data consistency, reliability, integration and backend implementation tradeoffs. |
| Skills/backend-platform/mcp-builder | Integration Pattern Mechanic, Data-Intensive Systems Critic, Architectural Pattern Cartographer, Pragmatic Delivery Partner | Tool/resource/message contracts, idempotency, auth, schema, protocol verification. |
| Skills/backend-platform/cli-spec | Use-Case Flow Designer, Story Slicer, Pragmatic Delivery Partner | Actor-goal CLI flows, extension paths, acceptance evidence. |
| Skills/product-strategy/architecture-interview | Architectural Pattern Cartographer, Data-Intensive Systems Critic, Integration Pattern Mechanic, Deep Module Examiner | Decision interviews for alternatives, data/integration risk, complexity symptoms. |
| Skills/product-strategy/deep-interview | Use-Case Flow Designer, Story Slicer, Domain Language Guardian | Product discovery, actor goals, domain vocabulary, acceptance criteria. |
| Plugins/skill-factory/skills/code_quality_review/skill-builder | Deep Module Examiner, Use-Case Flow Designer, Refactoring Catalog Operator, XP Feedback Coach, Pragmatic Delivery Partner | Skill hardening, compact contracts, eval-backed iteration, progressive disclosure. |
| Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor | Refactoring Catalog Operator, Micro-Refactoring Surgeon, Deep Module Examiner | Mechanical skill rewrites and context-budget reductions. |
| Plugins/skill-factory/skills/scaffolding_templates/skillify | Story Slicer, Use-Case Flow Designer, XP Feedback Coach | New skill success criteria, negative prompts, evaluator-ready examples. |
| Plugins/plugin-factory routed skills | Architectural Pattern Cartographer, Integration Pattern Mechanic, Data-Intensive Systems Critic, Pragmatic Delivery Partner | Package boundaries, tool contracts, dependency posture, integration failure handling. |

## Secondary Skill Targets

| Skill family | Lenses | Use |
| --- | --- | --- |
| Skills/security-ops/* | Pragmatic Delivery Partner, Data-Intensive Systems Critic, Integration Pattern Mechanic | Dependency, data-flow, secrets, manifest, and external API checks. |
| Skills/frontend-ui/design-system | Deep Module Examiner, Domain Language Guardian, Use-Case Flow Designer | Component boundaries, design-system vocabulary, and user-flow acceptance checks. |
| Skills/content-publishing/llm-wiki | Pragmatic Delivery Partner, Domain Language Guardian | Knowledge capture, source-of-truth boundaries, glossary discipline. |
| Skills/agent-ops/docs-expert | Pragmatic Delivery Partner, Domain Language Guardian, Use-Case Flow Designer | Docs as operational interfaces with owners, flows, and exception paths. |

## Wiring Rules

1. Add a compact Read when hook, not the lens content, to SKILL.md.
2. Select at most three lenses per invocation.
3. Add eval prompts only for skills where the lens changes behavior.
4. Treat the lens as a question generator; local repo evidence supplies answers.
5. If the shared pack is unavailable, report lens_status: missing_reference
   instead of inventing book coverage.

## Highest-Leverage Wiring Order

1. Skills/agent-ops/improve-codebase-architecture
2. Skills/agent-ops/evals-router
3. Plugins/skill-factory/skills/code_quality_review/skill-builder
4. Skills/agent-ops/simplify
5. Skills/agent-ops/unslopify
6. Skills/agent-ops/ubiquitous-language
7. Skills/backend-platform/backend-engineer
8. Skills/backend-platform/mcp-builder
9. Skills/product-strategy/architecture-interview

## Eval Probe Shape

~~~yaml
prompt: "Use the skill to improve a weak AGENTS.md without losing validation."
expected_lenses:
  - Pragmatic Delivery Partner
  - Use-Case Flow Designer
must_do:
  - cite local evidence
  - name smallest move
  - report validation or blocked reason
must_not_do:
  - cite a book as proof
  - broaden into unrelated refactor
~~~
