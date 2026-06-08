# Outline — Skills are the new Code

## Speaker

**Guy Podjarny** — Founder of Tessl, reimagining software development for the AI era and helping shape AI-Native Development. Previously founded Snyk (created the Developer Security category; now a multi-billion-dollar company with 1,000+ employees). Former CTO at Akamai (following acquisition of his first startup). Active angel investor and co-host of the AI Native Dev podcast.

## Abstract (verbatim, as provided)

> Software development has always revolved around the instructions we give the machine — punch cards, then assembly, then code. As agentic development takes hold, agent skills are becoming our unit of software — but we're not treating them this way.
>
> In this keynote, I'll make the case that agent skills deserve the same rigour we've spent decades applying to code. Crafted with intention. Tested against real behaviour. Versioned and maintained in step with the project around them. Treating skills as an afterthought isn't just technical debt, it's the difference between AI that ships and AI that drifts.

## Thesis

Agentic development is producing a recognisable new software stack — models, tools, context, harnesses, factory lines — and within it, **context (especially skills) is the new code**: the place where you actually program the model. Because skills are code, they inherit code's classic problems (security, governance, reuse, rot) and therefore need code's classic disciplines: static analysis, tests (evals), security testing, dependency management, and observability.

## Section TOC

| # | Section | Summary | Lines |
|---|---|---|---|
| 1 | Opening & framing | Tessl founded 2+ years ago on belief that dev is moving from code/implementation to intent/instructions; the new stack is coming into view. | 1–18 |
| 2 | The agentic stack overview | Four layers introduced: models (primitives) → tools → context → harnesses → composing into factory lines and factories. | 18–28 |
| 3 | Tools layer | Tools are utilities (CLI, MCP, APIs) that give models arms/legs; often cheaper/faster/better than the model itself (grep, ffmpeg examples). Tools compose. | 28–44 |
| 4 | Context layer | Context = info the agent doesn't have or can't efficiently get. Three buckets (policies/practices, specs, workflows). Loading matrix: rules (always loaded), skills (on-demand), passive context (docs). Skills compose by calling tools and other skills (incident-response example). | 44–66 |
| 5 | Harnesses layer | Deterministic software wrapping a probabilistic model (Claude Code as example). Loads rules/skills, defines available tools, supports plugins and hooks. Intercom and OpenAI (Will DePue) examples of blocking actions unless conditions are met. Harnesses compose into factory lines. | 66–94 |
| 6 | Stack recap & "context is the new code" | The stack starts looking like a software stack; tools/harnesses/factory lines are all software wrapping the model. Models and context are the two new compute entities; context is the new code. | 94–104 |
| 7 | Skills as reusable context | Spectrum: prompts → docs → rules → skills. Skills are libraries — designed for reusability. ~2 million skills on GitHub (up from ~0 at start of year, per joint GitHub analysis). | 104–118 |
| 8 | Three challenge buckets | (1) Security: malicious skills (>30% on one open-floor ecosystem), negligence skills, vulnerable skills. (2) Governance follows from security. (3) Reuse & collaboration: shared-repo failure story from a "large unicorn". (4) Lifecycle: skills rot like software; maintenance vs. optimisation framing. | 118–158 |
| 9 | Five software disciplines applied to skills | Static analysis (linting → security analysis → agentic review; Tessl's `lint` and `review`). Tests → evals (skill-level / project-level / comprehensive; analogous to unit / integration / end-to-end). Security testing (static, dynamic/red-teaming, supply chain). Dependency management (registry, versioning, install/update, supply-chain visibility, quality/security gates, cross-agent compatibility). Observability (monitor agents, mine for new skills, extract eval scenarios). | 158–224 |
| 10 | Context development lifecycle | Humans should live in the CDLC; agents do the SDLC. Generate → evaluate → test → optimise → distribute via package management → secure → consume → observe → repeat. | 224–232 |
| 11 | Summary & Tessl agent pitch | Recap of the stack. Skills are the new code; treat them that way. Tessl agent (nascent) — vertical agent to help develop content, harnesses, factory lines, factories. Early access at booth 4x or tessl.co/agents. | 232–254 |
| 12 | Closing thanks (Podjarny) | New paradigm is a community activity, not any one vendor's job. | 254–262 |
| 13 | MC handoff (not Podjarny) | Compacting joke, live-stream callout (~2,000 viewers + ~650 in room), break and next-session announcements. | 262–end |

## Terminology glossary (definitions the speaker actually gave)

- **Tools** — *"pieces of software, their utilities that in part indeed they turn models into agents… arms and legs to be able to affect the world and gather information"*; also a way to do something *"more cheaply or faster or better than just passing it on to the model"*. Common forms: CLI tools, MCP tools, APIs.
- **Context** — everything that goes into the model call, but as developers care about: *"information that the agent either doesn't have and can't know or information that you can [figure out] but it's very inefficient or error[-prone] for it to find out"*. Three types: **policies and practices**, **specs** (definitions of product), **workflows**.
- **Rules** — context that *"always get shoved into the context window"* (e.g. `CLAUDE.md`-equivalents).
- **Skills** — context *"loaded on demand either in [tool call] or through some hints to the agent"*; designed to be reusable; *"light libraries"*. *"If you think you're going to do it multiple times, you turn it into [skills]."*
- **Passive context** — *"just docs like architecture [doc] or other information that's just available there in the repo"*, retrieved via agentic search.
- **Harness** — *"deterministic software that wraps a probabilistic model. It harnesses the model."* Claude Code is given as the canonical example. Owns rules loading, skills loading, container config, available tools, plugins, and hooks.
- **Hook** — deterministic code that runs *"every time a prompt comes along"* or every time a tool is called; can edit or disallow the action.
- **Factory line** — a composition of harnesses into a pipeline (e.g. product harness → coding harness → security harness → devops harness) that *"feel very much like [pipe]lines. You have repeatable type of input coming in [and] successful output coming out"*.
- **Factory** — full dev processes composed of factory lines.
- **Eval** — the skills equivalent of tests: *"You take, you define an environment for some skill to run, you actually practically run an agent through a task in that environment. And then you judge the result."* Tiers: **skill eval** (unit-test analogue, skill in isolation), **project eval** (integration-test analogue, multiple skills in a repo), **comprehensive test** (end-to-end analogue, model selection / regression).
- **Quality score** — aggregated output of static + dynamic analysis, used when *"consuming a skill, like in that shared repo, you can actually figure out which one is of high quality"*.
- **Malicious skills** — *"literally built to cause harm"*.
- **Negligence skills** — *"skills that really urge the user to do something but do not have any safety instructions in it. Do not set any boundaries."* The "drop the table" example.
- **Vulnerable skills** — skills that *"guide for information [that] just leaves you exposed"*; example given is API tokens / secrets ending up in logs.
- **Context Development Lifecycle (CDLC)** — *"a context development lifecycle, not a skill[, not a software, not] life cycle"*. The human-facing counterpart to SDLC; agents own SDLC.

## Named frameworks / concepts

1. **The agentic software stack (5 layers)** — models → tools → context → harnesses → factory lines → factories. Each layer composes the one below.
2. **Context-loading matrix** — rules (always loaded) vs skills (on-demand) vs passive context (available, retrieved).
3. **Three context types** — policies & practices, specs, workflows.
4. **Three challenge buckets for skills in the enterprise** — (a) security & governance, (b) reuse & collaboration, (c) lifecycle (rot vs optimisation).
5. **Three skill risk types** — malicious, negligence, vulnerable.
6. **The five software-engineering disciplines applied to skills** — static analysis, tests (evals), security testing, dependency management, observability.
7. **Eval tiers** — skill eval (unit), project eval (integration), comprehensive eval (end-to-end / model selection).
8. **Context Development Lifecycle (CDLC)** — generate → evaluate → test → optimise → distribute → secure → consume → observe → repeat.

## Open questions / not covered

- No concrete numbers for enterprise skill counts (only the GitHub public figure of ~2 million).
- No detailed methodology behind the ">30% malicious skills" stat on the unnamed "open floor ecosystem".
- Dynamic security testing / red-teaming of skills is acknowledged as *"a more nascent world"* — no prescription given.
- Cross-agent compatibility is invoked as a goal (*"just like npm doesn't care if you're on windows or a [Linux] machine"*) but no concrete mechanism is described.
- No comparison between specific skill formats / specs (e.g. Anthropic skills vs other ecosystems) beyond mentioning *"the anthropic best practices"* as something Tessl review matches against.
- Quality-score weighting and rubric are not detailed.
- Pricing / availability of Tessl agent beyond *"nascent"* and "early access" not covered.
- How the framework adapts when there is no clear human "skill owner" is not addressed.
