# Software Literature Skill Expertise Map

Use this map when deciding where the books staged in tmp/ can strengthen the skill system. The books are expertise sources, not content to paste into skills: extract small decision lenses, evaluator checks, and review questions; do not copy chapters, examples, diagrams, or proprietary text into repository skill files.

Companion reusable lens pack: [software-literature-expert-lens-pack.md](./software-literature-expert-lens-pack.md).

## Source Inventory

| Source in tmp/ | Expertise lens to extract | Best use |
| --- | --- | --- |
| Clean Code A Handbook of Agile Software Craftsmanship copy.pdf | readability, naming, small functions, error handling, testable code, cleanup discipline | Code review and unslopifying implementation output. |
| Designing Data-Intensive Applications - Martin Kleppmann copy.pdf | data modeling, consistency, replication, partitioning, streams, batch/online boundaries, reliability tradeoffs | Backend, architecture, integration, and production-readiness skills. |
| Domain Driven Design Tackling Complexity in the Heart of Software - Eric Evans copy.pdf | ubiquitous language, bounded contexts, model integrity, domain/service separation, anti-corruption layers | Architecture, language, specification, and product-discovery skills. |
| Enterprise Integration Patterns - Designing, Building And Deploying Messaging copy.pdf | message channels, routing, transformation, correlation, idempotent receivers, integration ownership | MCP, CLI, backend integration, workflow, and event-driven skills. |
| Erich Gamma, Richard Helm, Ralph Johnson, John M. Vlissides-Design Patterns_ Elements of Reusable Object-Oriented Software  -Addison-Wesley Professional (1994) copy.pdf | reusable collaboration patterns, object boundaries, extension points, composition over inheritance | Architecture and refactoring skills, especially when naming structural alternatives. |
| Extreme-programming-explained-embrace-change-2 (1) copy.pdf | feedback loops, small releases, test-first thinking, collective ownership, sustainable pace | Evals, planning, validation, and Harness Engineering execution skills. |
| Five Lines of Code_ How and when to refactor copy.epub | small mechanical refactoring moves, rules of thumb, behavior preservation | Simplification, refactoring, and skill-builder rewrite loops. |
| Martin Fowler - Refactoring - Improving the Design of Existing Code copy.pdf | catalogued behavior-preserving transformations, code smells, incremental improvement | Code review, simplify, fix-bugs, and architecture-first refactoring. |
| Pattern-Oriented Software Architecture, Volume 1 - A System Of Patterns copy.pdf | layered systems, pipes and filters, brokers, microkernel, reflection, architectural pattern tradeoffs | System architecture, plugin architecture, and integration design. |
| philosophy_of_software_design copy.md | deep modules, shallow modules, information hiding, change amplification, complexity diagnosis | Architecture critique, skill design, code simplification, and repo cognition. |
| the-pragmatic-programmer copy.pdf | DRY, orthogonality, reversibility, tracer bullets, automation, broken windows, knowledge capture | Agent operations, repo hygiene, review contracts, and delivery discipline. |
| User-Stories-Applied-Mike-Cohn copy.pdf | user roles, goal-oriented stories, acceptance criteria, splitting and prioritization | Product strategy, HE spec, eval prompts, and skill acceptance examples. |
| Writing Effective Use Cases copy.pdf | actor-goal flows, main success scenarios, extensions, scope levels, preconditions/postconditions | Product specs, CLI/app flows, negative-path evals, and agent workflow design. |

## Primary Skill Targets

| Skill | Add these lenses | Why it helps |
| --- | --- | --- |
| Skills/agent-ops/improve-codebase-architecture | DDIA, DDD, Enterprise Integration Patterns, POSA, GoF, Philosophy of Software Design, Refactoring, Pragmatic Programmer | This is the main architecture pressure-test skill. It should turn literature into questions about boundaries, data contracts, reversibility, and complexity symptoms. |
| Skills/agent-ops/simplify | Five Lines of Code, Refactoring, Clean Code, Philosophy of Software Design, Pragmatic Programmer | Simplification needs small behavior-preserving moves, not broad aesthetic cleanup. |
| Skills/agent-ops/unslopify | Clean Code, Refactoring, Five Lines of Code, Pragmatic Programmer | This skill benefits from sharper checks for vague naming, ceremony, dead prose, and unverified polish. |
| Skills/agent-ops/ubiquitous-language | Domain-Driven Design | This is the obvious owner for bounded-context language, alias cleanup, and source/projection terminology discipline. |
| Skills/agent-ops/evals-router | XP, User Stories Applied, Writing Effective Use Cases, Pragmatic Programmer | Evals should prove behavior through small feedback loops, actor-goal prompts, negative paths, and observable acceptance checks. |
| Skills/agent-ops/verification-before-completion | XP, Pragmatic Programmer | The skill can use feedback-loop and automation discipline to classify pass/fail/blocked evidence cleanly. |
| Skills/agent-ops/coding-harness | XP, Pragmatic Programmer, DDD, DDIA | Harness work needs feedback loops, stable vocabulary, and production-like data/integration thinking. |
| Skills/backend-platform/backend-engineer | DDIA, Enterprise Integration Patterns, DDD, Pragmatic Programmer, Clean Code | Backend implementation should expose data consistency, integration, and reliability tradeoffs earlier. |
| Skills/backend-platform/mcp-builder | Enterprise Integration Patterns, DDIA, POSA, Pragmatic Programmer | MCP tools are integration boundaries; message shape, idempotence, routing, and failure semantics matter. |
| Skills/backend-platform/cli-spec | Writing Effective Use Cases, User Stories Applied, Pragmatic Programmer | CLI specs become stronger when commands map to actor goals, main flows, extensions, and acceptance evidence. |
| Skills/product-strategy/architecture-interview | DDD, DDIA, Enterprise Integration Patterns, POSA, Philosophy of Software Design | Architecture interviews should expose bounded contexts, data/integration risks, and complexity symptoms before implementation starts. |
| Skills/product-strategy/deep-interview | User Stories Applied, Writing Effective Use Cases, DDD | Product discovery should capture actor goals, domain vocabulary, scope, extensions, and acceptance criteria. |
| Plugins/harness-engineering/skills/he-spec | User Stories Applied, Writing Effective Use Cases, DDD, XP | Specs should define user intent, domain terms, main/alternative flows, and feedback-ready acceptance criteria. |
| Plugins/harness-engineering/skills/he-plan | XP, User Stories Applied, Writing Effective Use Cases, Pragmatic Programmer | Plans should split work into thin feedback slices with clear stop conditions and validation evidence. |
| Plugins/harness-engineering/skills/he-code-review | Clean Code, Refactoring, Five Lines of Code, DDIA, EIP, DDD, Pragmatic Programmer | Code review should combine code smell detection with data/integration and domain-boundary review. |
| Plugins/harness-engineering/skills/he-strategy | Philosophy of Software Design, DDD, XP, Pragmatic Programmer, DDIA, POSA | This skill already has an architecture lens canon; use the staged books to refresh that canon when needed. |
| Plugins/harness-engineering/skills/he-work | XP, Pragmatic Programmer, Refactoring | Execution work should stay small, validated, reversible, and learning-oriented. |
| Plugins/skill-factory/skills/code_quality_review/skill-builder | Clean Code, Five Lines of Code, Refactoring, Philosophy of Software Design, XP | Skill editing needs concise structure, trigger clarity, progressive disclosure, and eval-backed iteration. |
| Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor | Refactoring, Five Lines of Code, Philosophy of Software Design | This is the direct home for mechanical skill rewrites and context budget reductions. |
| Plugins/skill-factory/skills/scaffolding_templates/skillify | User Stories Applied, Writing Effective Use Cases, XP | New skill scaffolds should include success criteria, negative prompts, and evaluator-ready examples from the start. |
| Plugins/plugin-factory routed skills | POSA, Enterprise Integration Patterns, Pragmatic Programmer, DDIA | Plugin design needs stronger package boundaries, tool contracts, dependency posture, and integration failure handling. |

## Secondary Skill Targets

| Skill family | Useful source material | Suggested use |
| --- | --- | --- |
| Skills/security-ops/* | Pragmatic Programmer, DDIA, EIP | Add dependency, integration, and operational-security questions where the skill touches manifests, data flows, secrets, or external APIs. |
| Skills/frontend-ui/design-system | Philosophy of Software Design, DDD, Use Cases | Use for design-system vocabulary, component boundary clarity, and user-flow acceptance checks. |
| Skills/content-publishing/llm-wiki | Pragmatic Programmer, DDD | Improve knowledge capture, glossary discipline, and source-of-truth boundaries. |
| Skills/agent-ops/technical-writer | Pragmatic Programmer, DDD, Use Cases | Strengthen docs as operational interfaces: clear owners, vocabulary, main flows, and exception paths. |

## How To Use The Material

1. Start from the target skill's purpose and pick at most three lenses.
2. Convert each lens into checks or questions, not summaries.
3. Keep the SKILL.md trigger and front-door instructions small.
4. Put longer lens packs in references/ files owned by the skill or by Infrastructure/references/.
5. Add eval prompts that prove the lens changed behavior.
6. For copyrighted sources, cite only the title as inspiration and store derived, high-level review questions.

## Good Extraction Shape

Use this shape when turning one book into skill material:

~~~yaml
source_title: Domain Driven Design
skill_targets:
  - Skills/agent-ops/ubiquitous-language
  - Skills/product-strategy/architecture-interview
lens:
  - Ask what term the user, repo docs, CLI, and runtime projection each use.
  - Identify bounded contexts before merging concepts.
  - Mark anti-corruption boundaries where external tools or plugins impose foreign terms.
eval_checks:
  - Given mixed source/projection wording, does the skill normalize to canonical repo terms?
  - Given a proposed skill blend, does it identify duplicate or conflicting bounded contexts?
do_not_do:
  - Do not paste book definitions or long excerpts.
  - Do not replace repo evidence with domain theory.
~~~

## Highest-Leverage Wiring Order

1. Skills/agent-ops/improve-codebase-architecture
2. Skills/agent-ops/evals-router
3. Plugins/skill-factory/skills/code_quality_review/skill-builder
4. Plugins/harness-engineering/skills/he-spec
5. Plugins/harness-engineering/skills/he-code-review
6. Skills/backend-platform/backend-engineer

This order gives the biggest compounding return: architecture decides what should change, evals prove it, skill-builder preserves the new behavior, HE spec and review carry it into daily work, and backend-platform gets the data and integration rigor where production risk is highest.
