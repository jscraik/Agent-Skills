## Speaker

**May Walter** — Co-founder and CTO of Hud, where she's building "a runtime intelligence layer for coding agents… a sensor that runs with your app in production and captures what coding agents need to reason over production." Previously founding CTO at Santa, CTO at Bond (acquired by REEF Technology). Background in runtime internals and adversarial red-team cybersecurity. Speaks at the intersection of deep tech and engineering culture.

## Abstract (verbatim, from user metadata)

> Performance issues silently pile up in mature codebases. Teams know things could be faster, but can never justify pausing feature work to investigate. You have to put engineers on it just to find out if there's something worth fixing, and the effort is completely unpredictable: it could take an hour or three weeks.
>
> In this talk, we'll walk through a real case study of adding runtime intelligence to coding agents to enable continuous performance optimization in production. We'll cover the pain that led us here, the technical approach (agents analyzing real production context to surface high-ROI fixes scored by complexity and impact), and what we had to improve along the way to get reliable results.
>
> This approach surfaced and fixed N+1 queries and missing database indexes within the first week, with measurable P90 latency improvements after deployment. Tech leads now receive actionable reports before sprint planning and can make decisions starting from the fix, not the problem.

## Thesis (synthesis, not the abstract)

The bottleneck in performance work is the *investigation*, not the fix — and that's exactly what agents with production runtime context can automate. But the path from "agent can find issues" to "merged PR" requires treating the human reviewer, not the agent, as the scarce resource: score by impact and risk, present human-readable quick wins anchored in business-relevant endpoints, and only automate things you're confident enough to merge (because "if it works 90% of the time, it's not an automation"). Agentic engineering is a distinct discipline from coding-with-an-agent — it demands a higher confidence bar, and getting there is incremental.

## Section TOC

1. **Opening / framing the pain** — the PM-to-engineering-manager scenario; only one engineer left who knows the codebase. (transcript lines ~1–25)
2. **What Hud is building** — runtime intelligence layer / sensor for coding agents. (~25–40)
3. **Why performance work stalls** — the leaky bucket, research-cost-before-knowing-value, "an hour to three weeks". (~40–60)
4. **The reframe: automate investigation, not the fix** — weekly/biweekly scans for high-ROI safe opportunities. (~60–75)
5. **Where the agent runs** — vendor-neutral compute, neutral harness/model, GitHub Actions as path of least resistance. (~75–105)
6. **The workflow shape** — Claude + GitHub Actions + Slack + Hud MCP server, per-tech-lead reports. (~105–130)
7. **What went wrong first** — plausible-but-unverified offers, query complexity, "lazy fix" pattern. (~130–155)
8. **The context problem** — production speaks endpoint/service, agents speak function/class; bridging requires "prod-to-code". (~155–180)
9. **Layered architecture** — query language (ClickHouse) → skills (HTTP 500, memory leak, perf degradation) → automations (refactors, dead-code removal). (~180–210)
10. **Why blind auto-PRs failed** — humans won't review 80 PRs; need to convince the human, not just the agent. (~210–235)
11. **The working pattern: scored quick wins** — map hot paths, business impact, lowest-risk highest-impact, human-readable summary, dive-deeper/ticket/PR options. (~235–260)
12. **Four takeaways** — (1) still need to define what matters; (2) automate investigation to maintain prioritization; (3) context over cleverness; (4) agentic engineering ≠ coding with an agent. (~260–295)
13. **The vision and the value-along-the-way pitch** — get to the "click merge as-is" point incrementally. (~295–315)
14. **Q&A** — one audience question on differentiation vs. DataDog/Sentry; "espresso shop" answer. (~315–end)

## Terminology glossary (Walter's actual phrasings)

- **Runtime intelligence layer / sensor** — "a sensor that runs with your app in production and captures what coding agents need to reason over production. So, like, for every function, how often it runs, how long it takes, whether it's [failing]."
- **Leaky bucket** — performance issues being ignored until crisis: "we kind of ignore the issue and then it degrades and then it becomes a crisis. And now we have to prioritize it… That is a leaky bucket. By definition."
- **The research-phase problem** — "It's kind of like taking something from the grocery store and then going all the way to the cashier just to know how much it cost so that you understand if you want it or not."
- **Lazy fix** — "oh, there's an exception. Let's catch it. This is great, but it's not helpful at all." Optimizing locally around a symptom instead of the broader cause.
- **Prod-to-code** — "a mapping of what's going on in production to the function level. So you have… the end point or the service and the endpoints or event consumers and the [cron] jobs that it runs. And then the mapping of the functions that are involved within." Enables both "this is slow, why?" and the inverse "I'm going to touch this, what does it impact?"
- **Skills** (in Hud's architecture) — "how to approach an HTTP 500, how to approach a memory leak. How to approach a performance degradation" — methodology layers sitting between raw query language and automations.
- **Automation vs. streamlined humans** — "If something works 90% of the time, it's not an automation. It's [streamlining] humans."
- **Quick wins** — human-readable, scored opportunities with three actions: "dive deeper, they can create a ticket or create a PR."
- **Espresso shop (Hud's positioning vs. DataDog/Sentry)** — "we're like an espresso shop. We only have an espresso, but it's the best one in town."

## Named frameworks / concepts

1. **Automate the investigation, not the fix** — the central reframe. Investigation cost is what blocks prioritization; once cost+impact are known, fixing fits normally into sprint planning.
2. **Score by impact and risk, not best-possible optimization** — "We are not looking for the best optimizations. We are looking for the highest impact, lowest risk changes."
3. **Convince the human, not the agent** — "we actually need to convince the human that it's worth the attention instead of convincing the agent that it's worth the [tokens]." Means: business-impact mapping, hot-path mapping, human-readable summary.
4. **Layered architecture: query language → skills → automations** — each layer is independently usable so the agent can drop down a level when it needs to, without re-implementing methodology in prompts.
5. **The four takeaways**
   1. We still need to define what matters (humans decide what's worth tokens/time).
   2. Automate the investigation phase to maintain prioritization.
   3. Context over cleverness — "the agents get useful once they see what's going on."
   4. Agentic engineering is not like coding with an agent — automation demands higher confidence.
6. **Vendor-neutral / harness-neutral / model-neutral choice** — "We don't know. No one knows what's the best. There are seasons." Choose the path of least resistance through the customer's existing stack (in this case GitHub Actions + Claude + Slack).

## Open questions / not covered

- Specific numbers beyond a few illustrative figures (P90 ~100ms with 45s spikes; "30, 40%" improvement; "70 seconds" p100). No aggregate metrics for the case study customer are given in this transcript beyond "fixed N+1 queries and missing database indexes within the first week, with measurable P90 latency improvements" (from the abstract, not elaborated on stage).
- Pricing or commercial details for Hud.
- Concrete details on the ClickHouse schema or sensor implementation (mentioned only at a high level).
- Details on which other agentic harnesses/runtimes were evaluated and rejected — Cursor is mentioned as a "locked to that specific vendor" cautionary example but not deeply compared.
- The talk does not cover non-performance use cases in depth — Walter mentions "We're doing several things for reliability and the other things" but doesn't elaborate.
- No discussion of how the sensor handles privacy/PII in production data capture.
- No discussion of multi-language or polyglot codebase support.
- The audience-question answer on DataDog/Sentry differentiation is short ("espresso shop") and does not go into technical comparison.
