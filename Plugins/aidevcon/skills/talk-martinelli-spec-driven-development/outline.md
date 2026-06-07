# Outline — Lessons from Spec-driven Development

## Speaker

**Simon Martinelli** — Java Champion, Vaadin Champion, Oracle ACE Pro. Owner of Martinelli LLC. 30+ years as software architect, developer, consultant, and trainer. Specializes in optimizing full-stack Java development with AI, modern architectures, and software modernization. Lecturer at two Swiss universities. Blog: martinelli.ch ("Keep IT Simple"). Consults primarily for insurance, wholesale/retail, government, and large enterprises — *"I'm doing business applications. So I don't do tools, I don't do products, I do business applications."*

## Abstract (as provided)

> In many projects, specifications and code drift apart over time. Requirements change, documentation becomes outdated, and developers rely mainly on the code. This increases risk and makes changes harder, especially in long-living business applications.
>
> This talk presents the AI Unified Process, a spec-driven approach where system use cases are the central artifact. A system use case describes observable system behavior and acts as a stable contract for the application. Code is derived from these use cases instead of treating the code itself as the source of truth.
>
> AI is used as a supporting tool to generate and update code and tests from system use cases in small, controlled steps. The focus is not on full regeneration, but on keeping existing code and specifications aligned over time.
>
> Using concrete examples, the talk shows how backend logic, database access, and UI behavior can evolve together. It also explains when code is generated, when it is updated, and how version control and reviews help keep changes small and understandable.
>
> The session shares concrete workflows and lessons learned from three customer projects, including limitations and trade-offs of using AI in this way.

## Thesis (synthesis)

System use cases — not user stories, not PRDs — are the right unit of specification for AI-assisted enterprise development because they're well-defined, AI already knows the format, and they survive technology changes. Tool-centric spec-driven approaches (Kiro, Spec Kit, PM-method) are too developer-centric and force a PRD→plan→tasks→code pipeline; Simon's process-centric **AI Unified Process** skips the plan/task phase and generates code directly from use cases. The approach only works if architecture style supports it: microservices fragment context too much, modular monoliths overload context, but **self-contained systems** (one vertical = UI + logic + DB in one repo) give the AI exactly the right context window.

## Section TOC

| Section | Summary | Approx. transcript lines |
|---|---|---|
| 1. Opening story (volunteer management system) | How Simon ended up doing spec-driven dev: built a volunteer system for his sports club in 2024, then a music festival wanted it too — needed a stable spec to negotiate features against. | ~10–60 |
| 2. Discovery of spec-driven dev via nativedev.io / Tessl | Found Siren Mace's article on AI-native development on nativedev.io (Tessl); started thinking about what specs should be for business applications. | ~60–80 |
| 3. Landscape: tool-centric vs process-centric | Existing tools (Kiro, Spec Kit, PM-method, Tessl) are developer-centric; Simon's AI Unified Process is process-centric and covers the whole SDLC. References IREB's new "AI for Requirements Engineering" micro credential. | ~80–110 |
| 4. Why system use cases | Jacobson 1987. Used them at Swiss railways in early 2000s. Components: actor, preconditions, scenarios (main success + alternative flows), postconditions. User stories = collection of flows from a use case. | ~110–150 |
| 5. The pipeline: use cases → code (skipping plan/tasks) | Use cases + entity model + architecture → generated code. Skip the PRD-plan-task phase that Kiro and similar use. UI needs additional spec (e.g. Figma via MCP). | ~150–190 |
| 6. Test order and reviews tied to risk | UI-heavy = code first then tests; API = TDD. Review intensity depends on module criticality (inventory failure = coffee break; order management failure = lost money). | ~190–220 |
| 7. Greenfield vs modernization flows | Greenfield: specs → review → engine generates code. Modernization (more common for Simon): extract use cases + entity model from existing code/docs, business review, regenerate. *"Modernization is not lift-and-shift modernization is rethinking how people are working with the software."* | ~220–280 |
| 8. PetClinic demo / reverse-engineered use cases | Showed PetClinic with use case UML diagram (visitor, clinic user actors), entity model from DB, and a fully reverse-engineered "list doctors" use case including API. Generated end-to-end implementation from it. | ~280–360 |
| 9. Skills, MCP servers, guardrails | Don't put everything in CLAUDE.md / system prompt (Zurich study: bigger prompt → more hallucinations). Use architecture docs + skills + MCP servers (for in-house framework docs via vector search). Simon publishes process skills at aiunifiedprocess.com. | ~360–420 |
| 10. Architecture's impact: SCS vs microservices vs monolith | 500-microservice insurance customer = worst case for AI context. Modular monolith = context too big. **Self-contained systems** (vertical = UI + logic + DB in one repo) = right granularity. Different verticals can use different tech stacks. | ~420–500 |
| 11. Team and process changes | No two-week sprints — too slow. Pair-size dev teams (1–2 not 5–7). Continuous flow, kanban-style use case tracking. Pair programming + ongoing peer reviews replace pull requests. | ~500–550 |
| 12. Determinism, regeneration, and conclusion | With good guardrails, get near-deterministic regeneration. Specs are sustainable across tech changes. Work shifts left to requirements engineering. *"You should know your architectural domain."* | ~550–600 |
| 13. Q&A | Use case generation flow from existing docs; what happens when a use case changes (regenerate, don't manually edit); verification/drift-management skills in pipeline; black-box Playwright tests vs Simon's millisecond integration tests with server-side-rendered Vaadin. | ~600–end |

## Terminology glossary (Simon's own definitions)

- **System use case** — *"created by Ivar Jakob's own back in 1987"* [Jacobson]. Contains: actor, preconditions, scenarios (main success + alternative flows), postconditions. Postconditions function as acceptance criteria.
- **User story** (in contrast) — *"one user story is usually a flow in the use case"* — i.e. user stories are sub-units of use cases, *"simply big"* [likely: simply small / too small].
- **AI Unified Process** — Simon's process-centric framework. Website: aiunifiedprocess.com. Diagram is color-coded for greenfield vs modernization paths.
- **Self-contained system** — *"we create verticals. So we split our application to verticals which has UI, space logic and database in one report"* — one repo per vertical. Created around the same time as microservices.
- **Skills** — Simon distinguishes specification-level skills from stack-specific skills. *"in those projects we don't prompt. So we have skills for everything and we iterate in these fields."*
- **MCP servers (his use)** — for in-house framework documentation via vector search, so AI can "research in the document page" without bloating the system prompt.
- **Guardrails** — architecture docs + skills + MCP servers + minimal CLAUDE.md. Backed by Zurich study: *"the bigger system prompt more hallucinations."*
- **Drift management** — pipeline skill that detects when AI-generated implementation has drifted from the use case spec.
- **Reflection** — pipeline step verifying that implementation matches use case; flags AI-generated "useless tests" or incomplete implementation.

## Named frameworks / concepts

1. **AI Unified Process** — process-centric SDLC for spec-driven AI development. Spec → engine (skills + MCP + guardrails) → code, skipping plan/task phase.
2. **System use case structure** — actor, preconditions, scenarios (main success + alternatives), postconditions (= acceptance criteria), optionally API.
3. **Self-contained systems** as the architecture style that makes AI workflows tractable.
4. **Risk-based review intensity** — review investment proportional to cost of module failure.
5. **Team shape** — 1–2 devs per stream, continuous flow, kanban on use cases, pair programming + peer review instead of PRs.
6. **Two-level skill organization** — specification skills (process-level) vs stack-specific skills (per tech combination).

## Open questions / not covered

- How to govern skill distribution across an org when teams use different AI agents (Simon flagged it as a current problem but didn't solve it).
- Concrete metrics for the "near-deterministic" regeneration claim (no error rates given).
- How to handle cross-vertical changes when self-contained systems need to evolve together.
- Specific tooling for "drift management" and "reflection" pipelines — mentioned but not demoed.
- Migration path for existing microservice estates toward self-contained systems beyond "stop here, don't do modular monolith".
- Cost / token economics of regeneration vs incremental editing.
- How non-Java stacks compare (Simon's examples are Vaadin + Spring Boot, with mentions of React + Quarkus / Angular + Spring Boot but no deep treatment).
- Security, compliance, and audit implications of regenerated code.
