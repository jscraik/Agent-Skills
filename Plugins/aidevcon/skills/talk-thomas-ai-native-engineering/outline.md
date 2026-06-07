# Outline — AI Native Engineering (Ian Thomas)

## Speaker

**Ian Thomas** — Software Engineer at Meta, currently Tech Lead in Risk & Privacy (Transparency and Choice area). Works remotely from Yorkshire, UK. Previously helped lead development of Horizon Worlds (web, mobile, VR), Horizon Workrooms, and Workplace. Before Meta, spent nearly a decade building sports betting systems for Sky Bet and PokerStars. Interested in languages, platforms, developer tools, engineering excellence, and developer experience.

The talk draws on his time in **Horizon Experiences** (part of Reality Labs), where he helped run the **AI4P (AI For Productivity)** programme.

## Abstract (as provided by user, verbatim)

> Meta is making a big, public bet on AI - and not just in our products. Teams across the company are building new tools to leverage best-in-class models to enhance productivity, quality and understanding. As part of Horizon Experiences in Reality Labs, we have created a dedicated AI4P (AI For Productivity) programme to help teams effectively navigate the rapidly changing AI enhanced engineering landscape. Our ambition is to help fulfil the vision of AI Native Engineering and this talk discusses what we've tried, what worked, what's still to be proven and what we've discounted (at least for now).
>
> We'll discuss how we measure effectiveness of tools for our teams, how agentic AI has become part of our day to day coding activities and how standalone agents are working more like early career engineers than dumb machines. We'll also talk about the leadership strategies employed to help people embrace and grow their understanding of the tools and associated techniques for optimal usage. Finally, we'll look at how various platform integrations have led to step changes in output quality and engineer satisfaction.

## Thesis (synthesised)

In a large social-culture engineering org, AI tooling adoption succeeds when it is framed as an **engineering-excellence** initiative grown **ground-up through a small community of motivated engineers**, then amplified by top-down support **after** a critical mass forms. A **6-dimension / 5-level maturity model**, run as recurring team self-assessment workshops, gives teams a way to find their own gaps and track progress without falling into vanity metrics like weekly active users, lines of generated code, or token usage.

## Section TOC

| # | Section | 1-line summary | Transcript lines (approx) |
|---|---------|----------------|---------------------------|
| 1 | Introduction by host | Host introduces Thomas; met him at QCon AI New York. | 1–10 |
| 2 | Setup and outcomes preview | Thomas frames the case study and shares headline outcomes (40× community growth, 80%+ weekly usage). | 11–35 |
| 3 | The leadership vision | Leadership wanted to reduce toil from ~50% to ~5% so engineers could innovate. | 36–48 |
| 4 | The starting problem | Hill-tracking, ad-hoc adoption, siloed wins, low perceived ROI. | 49–62 |
| 5 | Speaker self-intro | Yorkshire-based, Risk team, ex-Horizon Worlds / Workrooms. | 63–72 |
| 6 | Where to start: engineering excellence | Avoid novel product work; start with code modernisation, admin tasks, bugs, ops. The 500M-lines-of-hack scale problem. | 73–98 |
| 7 | Engineering excellence as a vehicle | EE = implementation quality + production excellence + better engineering. Why it fits Meta's social, ground-up culture. | 99–122 |
| 8 | Building the community | Small group, safe space, low overhead, intangible "sense of belonging" metrics. | 123–148 |
| 9 | The AI Maturity Model | 6 dimensions × 5 levels (sit → leap), based partly on DORA research, distributed as a self-assessment workshop. | 149–180 |
| 10 | Running the workshop | Kaizen retro format, anonymous Miro voting, 20–45 min discussion, every 3–4 weeks, shared on Workplace. | 181–205 |
| 11 | "Can we trust the code?" | Recurring senior-engineer concern → led to anti-test-slop initiative using AI to judge AI output. | 206–230 |
| 12 | Top-down support kicks in | Once momentum built, leadership pushed it across the whole metaverse org → step-change snowball. | 231–248 |
| 13 | Pattern 1: AI-driven test coverage prioritisation | Engineer taught agent to use coverage + hotspot data; ~3 hours vs ~half a week; ~60 diffs merged. | 249–270 |
| 14 | Pattern 2: Agent-led refactoring at scale | Teach AI a refactor pattern, find similar code, run agents in parallel, human as architectural reviewer. | 271–290 |
| 15 | Pattern 3: Horizon MCP server | Bridge giving models context about Horizon world state → removed Windows-PC-with-big-GPU constraint, paralleled work, improved quality. | 291–310 |
| 16 | Pattern 4: Autonomous code mods | Meta's code-mod infra + AI + rules/runbooks ("look basically like skills or context files") → 30+ autonomous diffs (early figure). | 311–330 |
| 17 | What made the wins work | Clear problem definition, shared tools, human oversight, agile iteration — all on commercial tools. | 331–345 |
| 18 | Mapping AI tools across the SDLC | Code is only one part; strong investment in platforms / platform engineering underpins everything. Build-your-own-agents ("fuse"), DRS risk scoring. | 346–375 |
| 19 | What worked / what's TBD / what was discounted | Start small, community-led, then top-down. TBD: code review bottlenecks, long-term cost. Discounted: full autonomy, vanity metrics. | 376–408 |
| 20 | Closing strategies and call to action | Permission to fail, ground-up credibility, top-down push at scale, invest in education, find a couple of people and start. | 409–end |

## Terminology glossary

- **AI Native Engineering** — Thomas's vision for an engineering practice where AI tooling is "seamlessly integrated... across many different processes" such that teams "self identify as AI native". (His level-5 description of the workflow-integration dimension.)
- **AI4P (AI For Productivity)** — A dedicated programme in Horizon Experiences / Reality Labs to help teams navigate AI-enhanced engineering. *(Named in the user-provided abstract; the talk body itself doesn't expand the acronym.)*
- **Engineering Excellence** — Thomas defines it as "consistent of three main parts: implementation quality, production excellence and better engineering."
- **Hill-tracking** — Thomas's term for the early-adoption pattern where individuals climb local hills of competence in isolation without uniform org-wide progress. *("there was a bit of hill tracking going on. And the adoption wasn't uniform. It was ad hoc at best.")*
- **The AI Maturity Model** — 6 dimensions × 5 levels (zero-indexed: sit, [intermediate names not stated], leap), based on DORA research and Horizon experiences. Dimensions are "largely independent of each other."
- **The six maturity dimensions** — Workflow integration; prompting / sharing information; distribution across the team; individual productivity gains; team-level improvements; use-case leverage. *(Thomas lists these informally; only "workflow integration" is given a worked level-by-level example in the talk.)*
- **Anti-test-slop initiative** — A CI-side initiative where "we could go and validate the changes that were being made in the autonomous way using a different AI tool to judge the quality of the output." Originated in Horizon, later adopted by Infra company-wide.
- **DRS** — A tool that "runs on every single diff in a company that gives us a score of risk based on how likely we think that changes to create a set" [sic — likely "cause an incident", but quote verbatim from transcript artifact].
- **Fuse** — Meta's internal platform "where people can build their own agents and have them to be highly specific."
- **MCP server (for Horizon)** — A bridge between models and "the data that backs Horizon... how world state looks, how things are built, the models, the kind of textures and everything that are in the world" — taught models what they needed to know about Horizon so they could work in on-demand environments rather than requiring a beefy Windows PC.
- **Code mods** — Automated codebase transformations; Meta's existing infra was extended with agentic code mods using "rules and runbooks to the AI that look basically like skills or context files."
- **Vanity metrics** — Thomas's label for weekly tool usage counts, diffs generated, lines of code written by agents, and token usage: "they're vanity metrics... it's a good indicator that someone's using something but that's about it. It's not actually proving any value."

## Named frameworks / concepts

1. **The Engineering-Excellence framing for AI adoption** — start with bugs, ops, code modernisation, admin tasks (NOT novel product work).
2. **Ground-up community + delayed top-down support** — small motivated group first, then leadership push after critical mass.
3. **6-dimension × 5-level AI Maturity Model** — with sit→leap levels, run as a recurring self-assessment workshop (Kaizen retro format, anonymous voting, 3–4 week cadence, results shared on Workplace).
4. **Four scaled patterns**: (a) AI-driven test-coverage prioritisation, (b) agent-led refactoring with human as architectural reviewer, (c) MCP-server context bridges to remove environment constraints, (d) autonomous code-mods with rules/runbooks.
5. **The "what made wins work" checklist**: clear problem definition; shared tools; human oversight in the loop; agile iteration; commercial (not bespoke) tools.
6. **The "worked / TBD / discounted" retrospective rubric** for evaluating an adoption programme.

## Outcomes Thomas claims (verbatim phrasings)

- "we grew an organic community that was over 40 times bigger than when we started... well over 500 people"
- "Well over 80% of people were using these tools weekly, which was up from under half"
- "consistently now, I think I see this in the mid to high 90s"
- Test-coverage pattern: "three hours he achieved what he would have taken about half a week normally"
- Refactoring pattern: "roughly half the time spent in achieving his goal"
- Code-mods: "30 diffs generated autonomously is a pretty low number. I'm fairly confident that that number is several orders of magnitude higher now"

## Open questions / not covered

- The talk does **not** give a level-by-level rubric for five of the six maturity dimensions (only workflow integration is worked through).
- The talk does **not** define what "AI4P" stands for in the body (the acronym only appears in the user-supplied abstract).
- The talk does **not** name specific commercial AI coding tools used (Cursor, Copilot, Claude Code, etc. are never mentioned).
- The talk does **not** provide hard productivity numbers beyond the two anecdotal time-saving estimates.
- The talk does **not** describe individual engineers by name (one passing reference to "Simon" in New York is the only named individual besides Thomas himself).
- The talk does **not** address: compensation/performance-review implications, hiring impact, headcount changes, junior-engineer skill development concerns, security/IP concerns with AI tooling, or specific model choices.
- "What does this mean for code review?" and "what's the cost... 9, 12, 3 years down the line?" are explicitly flagged by Thomas as **still to be proven** — he does not answer them.
- Full autonomy is explicitly **discounted (for now)**.
