# Outline — Building Product Teams in the Age of AI

## Speaker

**Christopher Batey** — CTO, Core Engineering Consulting Group. Over 20 years across software delivery, product development, JVM library development (concurrency/distributed systems), infrastructure engineering, architecture & system design, and most recently platform engineering. Open-source contributions including Akka and Kubernetes. Focus: speed and stability — what to do next to speed up the software delivery lifecycle.

Hosted by Katie Roberts on the Latent Space stage (the transcript opens with her introduction; she also says "Thanks very much, Dave" — likely a transcription artifact, since the speaker is Christopher).

## Abstract (as provided by user)

> Over the last year, I've built and scaled a new product engineering team from scratch: hiring, training, and shipping a real product while AI-assisted development rapidly changed how software gets built. ... This talk shares three practical pillars we've learned for running product development in the age of AI:
> 1. Path to Production at AI Speed
> 2. Training and Evaluating AI-Enabled Engineers
> 3. Designing Workflow for Parallel Change
>
> This isn't a theoretical talk about AI replacing engineers. It's a practical account of what changed when a real team tried to ship real software while development speed fundamentally increased.

## Thesis (synthesised)

AI is an **amplifier**, not a replacement: it dramatically accelerates code production but exposes — and worsens — every weakness elsewhere in the delivery lifecycle (product decisions, adoption, shared system understanding, review capacity). The fix isn't more tooling; it's disciplined practice: refuse to delegate systems thinking to agents, write human-authored ADRs *before* implementation, keep teams small with adoption-bound missions, work in parallel but limit each engineer to one complex cognitive task at a time, and measure adoption rather than vanity metrics like commits or PRs merged.

## Section TOC

| § | Heading | Summary | Transcript lines |
|---|---|---|---|
| 1 | Intro & company context | Host hand-off; Core Engineering Consulting Group's history as a platform/CD consultancy; how internal training/processes/reference impls looked two years ago. | ~1–35 |
| 2 | Where they are now (with AI) | Interactive training platform that provisions real environments; maturity tooling became SaaS; ref impls became a product for SMEs; the consultancy is its own best customer. | ~35–65 |
| 3 | The stakes — sensitive systems | Two product types: one holding sensitive client data, one managing client production environments. The talk is scoped to systems where it really matters if things go wrong. | ~65–80 |
| 4 | The fear: software no human has seen | Code can do anything with data it has access to; banks/healthcare doing this is scary. | ~80–95 |
| 5 | Audience polls | What % of your code is written by AI? (most: 50–100%) and what % goes to production with no human review? Batey's claim: at his company, 90–100% is AI-written, but ~0% goes without human critical thinking. | ~95–125 |
| 6 | AI as amplifier | AI amplifies what you already do well *and* what you do badly. Enables delivery-focused engineers. The deeper worry: what % of your *system* goes to production without human understanding? | ~125–145 |
| 7 | Don't delegate systems thinking to agents | Concrete example: managed service + client-side deployment + auth boundary. Lists system-level questions a 7,000-line PR needs answered. | ~145–195 |
| 8 | ADR-first workflow | Agents wrote verbose ADRs no one read. Fix: humans write the ADR first with diagrams, review it carefully; then agents are good at reviewing follow-up PRs against it. | ~195–220 |
| 9 | The producer "black box" — harness, host, model | Three layers of opacity. Choose open-source harnesses / alternative hosts / open-weight models to switch providers quickly during outages. Vendor lock-in is fine if it's a conscious choice; baking it into your *product* is a different game. | ~220–270 |
| 10 | The whole flow: idea → product mgmt → ownership → build → adoption | Different stages get different AI speed-ups. Building got an order-of-magnitude faster; product decisions did not. Look for friction caused by uneven acceleration. | ~270–305 |
| 11 | "You build it, you run it, you drive adoption" | Engineers must drive adoption of the feature they built before starting the next one. Otherwise they build features for fun. | ~305–325 |
| 12 | Engineer day-to-day: plan / execute / refine | Plan and refine use the human brain; execute is what AI accelerates. Refinement is the magic — fast user-feedback iteration. Superpowers and spec-driven frameworks help. | ~325–355 |
| 13 | Parallelism — but one complex task at a time | Everyone starts multiple tasks in parallel. They got worse output by the third complex task because the human brain is depleted. Mandate parallel work, but only one *complex* task per engineer at a time. | ~355–385 |
| 14 | Team shape — two-to-four sub-streams | Two-pizza teams generate 48 PRs; review becomes the bottleneck. Break into 2–4 person sub-streams with adoption-bound missions; cross-stream architects review key ADRs and integration. | ~385–435 |
| 15 | Does AI need good engineering practices? | Made-up velocity-degradation graph. Causes: technical debt + success. Loose coupling, fast feedback (<15 min full test suite), and blast-radius–aware design matter more under AI velocity. | ~435–480 |
| 16 | Closing — find your principles | Decide what humans must understand vs. agents; decide vendor-lock tolerance; identify the real bottleneck idea→adoption; reject vanity metrics (tokens, commits, PRs); measure adoption. QR code for follow-up articles. | ~480–510 |

## Terminology glossary (speaker's own framing)

- **Amplifier (AI as)** — *"AI is an amplifier. So for the things that we did really well as a company, it allows us to do it much quicker. ... For the things that we did really badly ... then all it's done is amplified the things that we didn't do so well."*
- **Architectural Decision Record (ADR)** — *"about documenting your technical decisions along with your code so that you can someone can quickly learn why we made the decision so we don't keep on discussing them again."* Under AI workflow: humans write them *first*, with diagrams; agents review subsequent PRs against them.
- **The producer black box** — Three opaque layers: the **harness/interface** (Claude Code, OpenCode, Codex, agentic workflows), the **model host**, and the **model** itself. *"Really your back box is made of three things that you don't understand."*
- **Vanity metric** — *"out of all that code ... it's all written by AI now. But how much of it was written without any human intervention?"* Specifically called out as vanity: token usage, commits, PRs merged, % of code written by AI.
- **Blast radius** — *"What is the worst thing that can go wrong in one instance of a pipeline after reduction happens"* — design so one component going down still leaves most product functionality working.
- **You build it, you run it, you drive adoption** — Batey's extension of the classic Werner Vogels DevOps mantra: *"for now it's like you build it, you run it and you have to drive the adoption of that feature."*
- **Sub-streams of two-to-four** — Smaller-than-two-pizza units inside a 6–8-person team, each with an adoption-bound mission. *"you get three pizzas because honestly you can't have a two tin subs you share pizzas."*
- **Spec-driven frameworks** — Tooling like Superpowers used during the planning/refinement phases. *"superpowers, I would highly recommend it."*

## Named frameworks / concepts introduced

1. **The three pillars** (from the abstract; the talk delivers on them in scrambled order):
   1. Path to Production at AI Speed — automated architectural checks, API/schema protection, static validation, testing for high change velocity.
   2. Training and Evaluating AI-Enabled Engineers — explicit coaching in AI workflows; rethinking what signals indicate effective AI-assisted development.
   3. Designing Workflow for Parallel Change — preview environments, isolated branches, architectural boundaries enabling concurrent change.
2. **Don't delegate systems thinking to agents** — and the example list of system-level questions for a multi-tenant managed service ↔ on-prem agent connection.
3. **ADR-first workflow with AI** — humans write ADRs first (with diagrams); agents enforce them on follow-up PRs.
4. **Producer black box (harness / host / model)** — and the prescription to retain the ability to switch providers.
5. **Idea → Product Mgmt → Product Ownership → Build → Adoption** — uneven AI acceleration across stages creates friction.
6. **Parallel work, one complex task at a time** — mandate parallelism but cap cognitive load.
7. **Two-to-four-person sub-streams with adoption missions** — replace 6–8-person two-pizza teams when AI inflates PR throughput.
8. **Closing principles checklist** — what humans understand vs. agents; vendor-lock tolerance; identify real bottleneck; reject vanity metrics; define "good" concretely; hold AI accountable to it.

## Open questions / not covered

- **Specific test taxonomy** — Batey explicitly cut this: *"I was going to go through an example of the types of tests we use but I'm not going to have time but feel taught in me after it if you want to."* The talk does not enumerate the testing strategies despite the abstract promising them.
- **Concrete training-platform mechanics** — he mentions the interactive training platform but doesn't detail curriculum or evaluation rubrics for AI-enabled engineers.
- **How "evaluating AI-enabled engineers" actually works** — pillar #2 of the abstract is the thinnest in the delivered talk. Specific signals/metrics for effective AI-assisted development are not enumerated.
- **Hiring practices** — abstract mentions hiring from scratch; the talk doesn't address interview design or hiring criteria.
- **Preview environments / isolated branches** — promised in pillar #3 of the abstract but not walked through.
- **Specific tools beyond Superpowers** — Claude Code, OpenCode, Codex are mentioned as examples of harnesses; no detailed comparison.
- **Concrete adoption metrics** — Batey says "measure adoption" but doesn't define how.
- **Q&A** — host says "I'm sorry there's no questions because I'm sure there are plenty for this. I'll stay here and I'll go outside if anyone's got any questions" — so no on-stage Q&A is captured.
