# Outline — From Pipelines to Prompts: Surviving the Shift to AI

## Panelists

- **Stephane Jourdan** — Co-founder & CTO of anyshift.io. Previously co-founder of Camunda-era consultancy and Container Solutions; built startups for "manager function systems" (likely garbled — possibly configuration management); last company acquired by Snyk ("snake" in transcript).
- **Simon** — Head of Enterprise Architecture and Ways of Working at Saxo Bank ("taxi bank" in transcript) in Denmark; heads their "AI ways of excellence" function, spearheading AI rollout across ~700 developers. Works in a regulated industry. Has 30+ years in the industry, still building hands-on.
- **Samantha** — Third panelist; specific affiliation not clearly captured in the transcript (speech-to-text degraded around her introduction).
- **Moderator** — Unnamed; opens the panel, manages questions.

> ⚠️ **Speaker labels are absent** in the source transcript and the speech-to-text has noticeable garbling (e.g. "taxi bank" = Saxo Bank, "snake" = Snyk, "Could you be resnick" is garbled). Hedge attributions.

## Abstract (as provided)

> The people in this room have lived through more than one industry earthquake. They built the cloud, championed DevOps, and bolted security onto delivery pipelines with DevSecOps. Now they're facing the next one: the move to AI-native development. This panel brings together practitioners who've reinvented how software gets built before, and asks them to reflect honestly on doing it again. What habits from the cloud and DevOps eras still hold? What assumptions are breaking? Where is the hype outrunning reality, and what's quietly becoming foundational?

## Thesis (synthesis)

The AI shift is bigger and faster than cloud-native because it forces every department to adapt, not just engineering. Teams that thrive will combine (a) deterministic feedback loops around AI-generated code — "harness engineering" — with (b) observability-grounded agents for production, and (c) explicit management of developer cognitive load. Software engineering as a profession is not going away; "vibe coding" stops at the last mile, and hallucination is inherent rather than something to be solved.

## Section TOC

1. **Intros & framing** (lines ~1–40) — Moderator introduces the panel; each panelist gives background.
2. **Is this shift bigger than past ones?** (lines ~40–75) — Cloud-native (2014) comparison; AI's impact is "a hundred times more dramatic" because it spreads beyond engineering.
3. **AI in production / observability** (lines ~75–130) — Agents creating PRs 24/7; need for proactive agents with context; using agents to diagnose production incidents (elastic logs + ServiceNow + code).
4. **Guardrails and "musts"** (lines ~130–175) — Linting as absolute basics; harness engineering; the limits of human review at AI throughput.
5. **Explainability and the next abstraction** (lines ~175–220) — Can humans skim what AI produces? Need for deterministic tools above the code layer; inheriting unfamiliar systems.
6. **Hallucination and acceptable error rates** (lines ~220–245) — Compare to self-driving cars: not zero accidents, just fewer than humans.
7. **Recent AI outages — what to do** (lines ~245–290) — Feedback loops; healthy CI/CD discipline applied to AI; self-learning reflector agents for prod.
8. **On-call and pager duty** (lines ~290–315) — Agents as first responders / triage; routing to the right team.
9. **Two-year forecast** (lines ~315–365) — Software development as profession survives; "explosion of small software" on the last mile; citizen developers limited; hallucination won't be solved.
10. **Audience Q1 — Is this all chaos?** (lines ~365–410) — Microsoft/Uber cancelling Claude Code licenses; self-driving analogy revisited; harness engineering as the differentiator.
11. **Audience Q2 — Cognitive load** (lines ~410–460) — Different cognitive rhythm; bursts of intense engagement; one customer sends people home for a week to recover.

## Terminology glossary (panelists' own framings)

- **Harness engineering** — Attributed to Mitchell Hashimoto ("hashimoto harness engineer"). The discipline of investing in deterministic checks, linting, and feedback loops around AI-generated code. Quote: *"If you spend about as much time engineering your harness as you do on top table of the actual functional output, you will get really good quality stuff."*
- **Reflector agents / self-learning agents for production** — Agents that learn from both the problem and the solution; memory gets added over time. Quote: *"That's a new class of agents for prod. That's very exciting because it really learns something very specific to the company."*
- **Co-driving (vs. self-driving)** — Analogy for human-AI collaboration in software development. Quote: *"Very much co-driving but I think the quality is there."*
- **Explainability of code/systems** — The new skill: understanding what the code does, not writing it. *"The explainability of the code being able to understand the cog [code] rather write it is the new skill."*
- **"Lowering the waterline"** — Continuous-improvement metaphor: advanced teams explicitly expose underwater problems and fix them. *"The most advanced teams they explicitly lower the water, expose the underwater stones and then fix them."*
- **Vibe coding / last mile** — The class of small, personal, front-end software that everyone will build themselves on top of larger platforms. Not for "real business logic."

## Named frameworks / concepts

- **Harness engineering** (Hashimoto) — invest in linting, deterministic checks, feedback loops proportional to your functional code.
- **Feedback-loop discipline** — when something goes wrong, feed it back into the harness so that class of error never happens again. Explicit parallel to healthy CI/CD teams.
- **Self-learning reflector agents** — production agents with company-specific memory that learn from incidents.
- **Co-driving model** — humans + LLMs together, not LLMs replacing humans.
- **The self-driving-car analogy** — applied twice: (a) hallucination is fine as long as it's less error-prone than humans; (b) skeptic in audience uses the same analogy to argue AI coding is overhyped.

## Agreements / Disagreements / Open threads

- **Agreed**: linting and deterministic checks are non-negotiable; human review can't scale to AI throughput; observability is essential; software engineering as a profession survives.
- **Disagreed**: One panelist explicitly took the other side — *"I think hallucination is going to work. I don't think hallucination problem is going away... because I think it's inherent."* Others were more optimistic about quality improving.
- **Open / explicitly uncertain**: All three panelists hedged the two-year forecast — *"I have no crystal ball. I literally like cannot see."*
- **Open**: How to manage developer cognitive load at AI throughput — *"I don't have a clear answer for that but it's a really big topic."*

## Open questions / not covered

- Specific tooling recommendations beyond linting + a vague mention of "code house" (likely CodeScene or similar — garbled).
- How to handle AI in regulated industries beyond "we can't quite move as fast" (Simon at Saxo Bank).
- Cost/economics of agentic workflows (only touched on via Microsoft/Uber cancelling Claude Code licenses).
- Security implications of agent-deployed services beyond "from a security perspective all the things that are being patched."
- How to onboard junior engineers when senior engineers can't keep up with reviewing code.
- Concrete metrics for "harness engineering" — what counts as enough harness investment.
