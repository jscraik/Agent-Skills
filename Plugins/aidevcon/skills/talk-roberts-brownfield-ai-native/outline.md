# Outline — Stop Maintaining, Start Evolving (Katie Roberts, AI Native DevCon, 2 June 2026)

## Speaker

**Katie Roberts** — Technical Director at Nearform (six years); previously at the BBC working across digital platform projects. Nearform is a consultancy that "support our clients in solving difficult software problems." Sponsor of the event.

## Host / MC

Introduction delivered by **Simon Maple** (Head of Developer Relations, Tessl; AI Native Dev co-host). Simon described himself as "one of those people who basically uses AI to create new things [a]nd then abandon them" and said he was "interested to hear as well, Katie from Nearform has to say about brownfield co-bases."

## Abstract

[inferred] Greenfield AI-native engineering is celebrated and well-documented, but 60–70% of enterprise software lives in brownfield codebases where AI agents can do more harm than good. Katie presents three methodologies for evolving brownfield systems with AI — pseudo-greenfield development, the strangler fig pattern, and branch by abstraction — plus a set of core principles and two Nearform case studies (a "six months in eight weeks" pseudo-greenfield rebuild and an AG Grid upgrade across a 500,000-line tightly-coupled distributed monolith via branch by abstraction).

## Thesis (synthesis)

Brownfield codebases are not balls of mud to be "let AI loose" on; they are evolved cities whose well-trodden paths and dark alleys must be mapped before they can be modernized. AI-native engineering works in brownfield only when you (a) treat developers as eyewitnesses to a crime scene, (b) extend the planning phase (not skip it), (c) pick a deliberate evolution methodology — pseudo-greenfield, strangler fig, or branch by abstraction — based on the specific legacy pathology, and (d) put guardrails (tests, SonarQube, version control, human review, skill rules) around every agent action. The payoff is a flywheel: each iteration produces reusable skills that compound across the codebase.

## Section TOC

| § | Heading | 1-line summary | Approx. transcript lines |
|---|---|---|---|
| 1 | Intro by Simon Maple | Logistics, video uploads, intro to Katie's brownfield topic | 1–12 |
| 2 | Who Katie is / who Nearform is | Speaker bio + Nearform pitch | 13–22 |
| 3 | Why greenfield AI works | "Match made in heaven" — design+spec+agents; PMs more involved | 23–40 |
| 4 | Greenfield metrics from Nearform | 80% faster kickoff, reduced sprint zero, 50% faster MVP, 4× dev velocity | 41–52 |
| 5 | Brownfield reality | 60–70% of enterprise; tech debt, tribal knowledge, dependency rot, fear-driven dev, test rot, tight coupling | 53–80 |
| 6 | Ball of mud vs city metaphor | Brownfield is an evolved city, not a ball of mud — well-trodden paths and dead ends | 81–100 |
| 7 | Three methodologies — overview | Pseudo-greenfield, strangler fig, branch by abstraction | 101–110 |
| 8 | Pseudo-greenfield development | Branch and treat as greenfield; fast early, painful merge; developers become "tourists"; duplication of shared concerns | 111–135 |
| 9 | Strangler fig pattern | Mark[Martin] Fowler 2000s; vine metaphor; replace alongside without downtime; used by Uber, Netflix, BBC; facade + routing layer; AB/canary/traffic split; requires running two systems; commitment to completion | 136–170 |
| 10 | Branch by abstraction | Work from inside; abstraction interface + feature flag; both implementations live; kidney-replacement metaphor; abstraction must eventually be deleted | 171–200 |
| 11 | How NOT to use AI in brownfield | Don't let agents loose; "AI will confidently hallucinate about your code"; over-optimization; safety safety safety (referencing Don's previous talk) | 201–225 |
| 12 | The crime-scene approach | Start with developers as eyewitnesses (Alan Hills [Adam Tornhill], *Your Code as a Crime Scene*); mirror exercise; value vs complexity graph | 226–245 |
| 13 | Focused AI investigations | Dead code, duplication, pattern inconsistencies, complexity hotspots, OWASP-style scanning, dependency graphs, code-behaviour maps | 246–265 |
| 14 | The objectivity halo effect | AI-generated findings aren't authored by "the cleverest person on the team"; broke bike-shedding; surfaced more contributors | 266–280 |
| 15 | Core principles for brownfield AI dev | Don't trust AI blindly; small scopes; version control; findings backlog; human-readable docs; guardrails; one area at a time; skill rules to avoid repeating bad patterns | 281–305 |
| 16 | Case study: pseudo-greenfield ("six months in eight weeks") | Reverse-engineered PRDs (months → week), code-base mapping (2 weeks → hours), automated Jira ticket skill, 4× competitor estimate | 306–330 |
| 17 | Case study: branch by abstraction — AG Grid upgrade | 500k LOC tightly-coupled distributed monolith; first AG Grid upgrade took ~1 month; built plan skill + multi-agent developer skill | 331–360 |
| 18 | The multi-agent developer skill flow | Orchestrator → ADR check → test scaffolding → implementation → static analysis & quality gates → self-review → human review → main pipeline → updates master plan | 361–380 |
| 19 | Flywheel + skills library | Slow start, then velocity compounds; reusable skills library across codebase | 381–395 |
| 20 | Practical takeaways | Start with a [path] not migration; specs are the contract; thin slices not rewrites; complexity is the opportunity | 396–410 |
| 21 | Q&A — slicing skills across feature teams | Slice at epic level; smaller teams (1–2 people + agents); watch for skill divergence; cross-team review | 411–430 |

## Terminology glossary (speaker's own definitions)

- **Brownfield codebase** — "account for an estimated 60 to 70% of enterprise software… they're hugely successful… that's why they've been around for 5, 10, 15 years. But with that comes accumulated technical debt."
- **Tribal knowledge** — "something was developed by somebody who's long left the organization… the only documentation was in their head."
- **Dependency rot** — "falling behind with a couple of dependencies and suddenly upgrading to the latest version of [Node] is going to take two months rather than two days."
- **Fear driven development** — "places in the code base where people just don't want to go. They don't want to touch it because it's so fragile."
- **Ball of mud pattern** — the standard derogatory term Katie pushes back against; she prefers the city metaphor.
- **City metaphor** — "A city is very successful and it's something that's evolved over time… well trodden [paths]… less well-maintained spaces. Dead ends and the places that you really wouldn't want to get caught in[…] late at night."
- **Pseudo-greenfield development** — "you branch out and say right this new feature I'm going to develop it. I'm going to treat it like a greenfield code base."
- **Strangler fig pattern** — "defined by Mark and Fowler, I think back in the 2000s" [canonical attribution: Martin Fowler]. "The vine drops a seed… sends down a route… builds up self around it slowly strangling out the nutrients from the tree until it remains… solitary itself is removed." Takes "the responsibility away from the old area of co[de] one slice at a time."
- **Branch by abstraction** — "working from inside the code base rather than around it. You put an interface within the code and you can then branch out to a new implementation."
- **Tourist (developer)** — what pseudo-greenfield developers become: "they never learn about the inline problems of the code base."
- **Plan skill** — "all the technical and product considerations captured and then the work was broken down by [AG] grid component skill that we created."
- **Developer skill** — a multi-agent flow that does ADR check, test scaffolding, implementation, static analysis, self-review, then hands to human review.

## Named frameworks / concepts

1. **The three brownfield-evolution methodologies**
   - Pseudo-greenfield development
   - Strangler fig pattern
   - Branch by abstraction
2. **Core principles for brownfield AI development**
   - Don't trust the AI input blindly
   - Work in small scopes
   - Version control everything
   - Create findings backlog and prioritize
   - Create human-readable docs
   - Put guardrails in place (tests, logs, static code analysis)
   - Focus on one area at a time
   - Skill rules that prevent repeating bad patterns
3. **The forensic / crime-scene approach** (credited in talk to "Alan Hills, *Your Code as a Crime Scene*" — canonical author is Adam Tornhill)
4. **The value-vs-complexity mirror exercise** for prioritizing improvement opportunities
5. **Multi-agent developer skill flow**: Orchestrator → ADR check → Test scaffolding → Implementation → Static analysis + quality gates → Pre-review → Human review → Main pipeline → Master-plan update
6. **Four practical takeaways**:
   - "Start with a [path] not migration"
   - "[Spec] be the contract"
   - "Thin slices and not rewrites"
   - "Complexity is the opportunity"

## Open questions / not covered

- Specific tooling: she mentions cursor, SonarQube ("son up queue"), and OWASP-style scanning by name but does not compare AI coding tools or recommend a specific agent platform.
- Concrete prompt content / skill file format — referenced as "skills" alongside code but never shown.
- Quantitative ROI / cost figures — the talk gives ratios ("4× faster", "six months in eight weeks", "weeks to hours") but no dollar costs or team sizes (beyond "four or five people [down to] one or two").
- Specific organization names for the AG Grid case study (only that it was "inherited from another supplier").
- Failure cases / project where the approach didn't work — she says "it isn't right for every project" but doesn't give a counter-example.
- Security and compliance considerations beyond mentioning OWASP scanning.
- How to handle agent-generated code in regulated industries.
- Detailed evaluation of when to choose strangler fig vs branch by abstraction beyond the situational criteria she names.
- Long-term maintenance of the skills library itself.
