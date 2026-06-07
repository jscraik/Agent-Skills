# Outline — More software, faster: Odevo's AI Native transformation

## Speakers

- **Daniel Jones** ("DJ" / "Deejay") — ex-developer, co-founder of multiple cloud-native businesses (grown and sold). Currently with **re-cinq**, a small boutique consultancy based in northern Europe specialising in AI-native transformation (background in cloud-native / Kubernetes transformation). Has keynoted tech conferences, appeared in Kerrang!, won national martial arts competitions, was filmed for Grand Designs.
- **Tomasz** — Ex-McKinsey consultant, joined **Odevo** in 2024. Leads Odevo's ways-of-working and AI transformation effort. Polish (the talk references Polish independence day, 11 November). Co-hosts a podcast referenced in the talk.

## Abstract (provided by user)

> How did Sweden's third-largest tech company become AI native? What were the drivers, the challenges, the solutions, and outcomes? Why isn't it as simple as providing training and buying licences?
>
> Tomasz and Deejay take you through Odevo's journey adopting agentic coding and AI-enabled product management, sharing what worked, what didn't, what this means for the company, and of course some tasty metrics about the outcomes!

## Thesis

Adopting agentic coding successfully is not "buy licences + run training." It requires (1) honest discovery of software-delivery fundamentals (CI/CD, platform, tests, standards), (2) workshops that surface developer fears and shared diagnostic language *before* training, (3) in-person, hands-off-laptop training with train-the-trainer capability, and (4) a willingness to redesign the SDLC once adoption lands — otherwise the bottleneck just moves (to product, in Odevo's case). The biggest measurable outcome isn't throughput numbers; it's **boldness**: how many previously-unthinkable things teams now attempt.

## Section TOC

1. **Intros & framing** — DJ from re-cinq, Tomasz ex-McKinsey now at Odevo; the talk is "more software, faster."
2. **About Odevo** — residential property management; 3rd largest private tech co in Sweden; 50k → 2.5M homes, 1k → 14k employees in 7 years; weekly acquisitions; heavily heterogeneous tech stacks; still-paper-heavy industry.
3. **Starting state (2024)** — GitHub Copilot in pockets, internal "DOGPT" built on OpenAI for data-privacy reasons, ~30% adoption, slow time-to-merge, large/rare PRs. 18 months spent systematising ways of working and creating transparency *before* AI training.
4. **The RFP & partner selection** — LinkedIn-induced flood of ~80 dubious replies, shortlist of 10, finalists of 3, chose "the idiot with the mustache" (re-cinq / DJ). Pre-spec-kit era; "with AI bad things get worse and good things can get better."
5. **Discovery** — paid, expected, required in RFP; covers CI/CD, platform, tests, coding standards. Paraphrased Dora 2025 finding: good gets exponentially better, bad gets worse, balance point unknown.
6. **Workshops (pre-training)** — in-person; liberating structures format; TRIZ exercise ("200 junior devs who never sleep, never say no — how do we make this a disaster?"); unanimous cross-stack recognition of weak fundamentals; "spider-man memes situation."
7. **Pilot training** — small group on 11 November (Polish independence day); learned the failure modes before the 80-person session.
8. **Training delivery** — in-person, food, after party, no laptops first half; "what did we just do?" debrief technique after every exercise.
9. **Syllabus** — context management / maximum effective context window; agents.md anti-pattern; failure modes & hallucination with old models; jump from VS Code + Copilot to terminal-based Claude Code (psychological shift); MCP; spec-driven development; multi-agent workflows (gas town / gas city); homework-style follow-ups after each weekly half-day module.
10. **Impact metrics** — ~94% AI adoption (used in last 10 PRs); ~60% used it in 3+ PRs; ~6% non-adopters being interviewed for "why not"; time-to-market up; throughput up; cross-org dashboards built for transparency.
11. **Boldness as the real metric** — 8-year platform rewrite in 3 weeks at feature parity with 4 devs; mobile app in 3 days attempt (didn't go great but they tried); ambition to unify fragmented regional software stack.
12. **SDLC reinvention** — one team went AI-first: 2 weeks of product requirements with auto-transcribed conversations, agents produce wireframe doc + ERD + business logic, task plan split by agents, devs pick 2 epics/day, choose own tooling (BMAD / spec-kit / vibe coding), no human code review — 7-8 passes of agentic code review then self-merge PRs.
13. **People stories** — Dominic, the AI sceptic flipped by Opus 4.5; the demo-team developer who hasn't written work code in 4-5 months but does carpentry-style coding at home; Nicholas, train-the-trainer graduate now training other Odevo companies.
14. **What's next** — training pivoting to product managers / designers / BAs (the new bottleneck); eventual goal of basic AI training for all ~13k remaining employees (accountants already using Claude Code to build local apps).
15. **Cautions** — compulsion / overwork: engineers working until 1am, "I can't turn it off"; references Lauren Pete (CEO of multitudes) research on perceived feature pressure causing overtime.
16. **"Everyone a builder" vision** — devolution from paper forms → engineers as gatekeepers → cloud complexity → re-empowering business users; more, more bespoke, more usable software, not fewer developers.

## Terminology glossary (speakers' own definitions)

- **Liberating structures** — "a menu of different meeting formats and ways of facilitating conversations that tend to subvert power dynamics and make sure that idiots with loud voices like me don't dominate the entire conversation."
- **TRIZ** — "some acronym for the creative theory problem solving" (Russian origin); used here as a workshop format: pose an absurd negative scenario, gather ideas, then ask "what do we do here that's a bit like some of those bad things?"
- **Maximum effective context window** — "the more you add into your context window more off the rail to the airline is going to get."
- **agents.md anti-pattern** — adding "every possible instruction for every possible scenario" has been "shown in a couple of academic studies now to have negative impact. You're better off having no instructions in your agent's MD then lots of them."
- **"What did we just do?" technique** — post-exercise socratic debrief: "okay you typed in a prompt where did that prompt go and then it called a tool. Okay where do tools actually execute? How does the model decide which tool to use" — cements knowledge via social pressure and visual representation.
- **DOGPT** — Odevo's internal ChatGPT built on OpenAI, built so employees would not upload sensitive customer data to external chat tools.
- **Boldness (as a metric)** — "how many more bold things are you doing? How many experiments are you trying out? Are you actually trying to do a full end-to-end agentic workflow?"
- **"Everyone a builder"** — Odevo's ambition that all 14k employees build software, not just the ~200 engineers; "we want to pivot from software we built for our opcos to opcos build software with our support."

## Named frameworks / concepts introduced

1. **The "bad things get worse, good things can get better" frame** (paraphrasing Dora 2025) — applied to deciding whether your org is ready to throw agentic coding at the wall.
2. **Discovery → workshops → pilot → full training → train-the-trainer → SDLC redesign** — the re-cinq playbook for AI-native transformation.
3. **Prerequisite fundamentals for agentic coding**: CI/CD, platform, tests, coding standards — explicitly enumerated as where rollout will fail if missing.
4. **TRIZ "200 sleepless junior devs" exercise** — a specific liberating-structures-style workshop format for surfacing org weaknesses without blame.
5. **"What did we just do?" socratic debrief** — training technique applied after every exercise.
6. **Weekly half-day training cadence with homework** — module then "go back to your desk, install the geo MCP, ask it what ticket I should do next."
7. **AI-first SDLC** (one Odevo team's design) — 2-week product-requirements phase → agentic wireframe + ERD + business logic + task plan → devs pick 2 epics/day with free choice of tooling → no human code review, 7-8 passes of agentic code review → self-merged PRs.
8. **Boldness-as-success-metric** — explicit replacement / complement to throughput metrics.
9. **Bottleneck migration** — once engineering ships fast, product becomes the new bottleneck (matches their podcast guest's observation).

## Open questions / not covered

- Specific tools selected (the talk mentions Claude Code, GitHub Copilot, MCP, "spec-kit", "BMAD", "gas town/gas city" but does not give a defended tooling matrix).
- Concrete dollar/euro ROI numbers (only percentages and ratios are given).
- Detailed before/after Dora metrics (throughput and time-to-market are mentioned as "up" with adoption %s, but lead time, MTTR, change-fail rate are not quantified).
- The exact training partner pricing or RFP scoring rubric.
- The mobile-app-in-3-days attempt details (acknowledged as not working well, but no post-mortem given).
- How Odevo handles model-cost governance across 200+ engineers.
- Security / data-privacy specifics beyond "we built DOGPT."
- The specific identity of the second-place private tech company in Sweden (company name unknown).
- Whether and how the "everyone a builder" vision handles production-grade vs throwaway business-user software.
- Any quantitative measure of the "boldness" metric the speakers advocate for.

## Notable verbatim quotes (sampling)

- "With AI bad things get worse and good things can get better."
- "If agents can't run tests to find out they've broken your software, don't be surprised when they break your software."
- "If you don't have a platform like you can't ship code reliably and quickly and then you're just going to generate all this code out of nowhere to go with it."
- "If the humans in your organization don't agree what good looks like then there's a very low chance that an agent is going to be able to produce code that your team is going to approve of."
- "How many more bold things are you doing? How many experiments are you trying out?"
- "Something that we built for eight years we were able to rewrite in three weeks teacher parity one to one."
- "Humans doing stat analysis of code is a silly idea on birthplace" (likely transcription artifact for "in the first place").
- "I haven't written any code at work for four or five months" — Dominic, the converted sceptic, on the podcast.
- "We want to pivot from software we built for our opcos to opcos build software with our support."

## Transcription-artifact warnings

This transcript has several speech-to-text errors that should be preserved but flagged:
- "magenta coding" → "agentic coding"
- "a gentle coding" → "agentic coding"
- "DOGPT" → likely a custom GPT product name spelled phonetically
- "loan bull" → likely "Klarna" (the Swedish fintech, context "number one private tech co in Sweden")
- "the dopamine in Russia" → "the dopamine rush"
- "teacher parity" → "feature parity"
- "Ralph Wiggum loops" → unclear, possibly a coding-agent loop pattern name
- "geo MCP" → likely "Jira MCP"
- "ethics" in "pick a couple of ethics a day" → "epics"
- "gas town, now gas city" → unclear, possibly a multi-agent framework name
- "BMAD" → "BMAD" (a known agent framework) — likely accurate
- "Lauren Pete" → "Lauren Peate" of Multitudes (likely)
