# Talk outline — Patrick Debois: Agent enablement

> **Speaker label warning:** The source transcript has no per-speaker labels and contains visible speech-to-text artefacts. The talk is single-speaker (Patrick Debois) bookended by a brief MC intro and outro. There is no captured Q&A.

## Speaker

**Patrick Debois** — independent consultant, fractional CTO, and content curator of the AI Native Developer community. Coined the term "DevOps", co-authored the *DevOps Handbook*, and organised the first DevOpsDays in 2009. Former VP Engineering / Distinguished Engineer / CTO; previously at Atlassian and Snyk. Focuses on bridging engineering rigour and GenAI adoption.

## Abstract (as provided)

> Every company wants to know how others are actually scaling AI coding. But it's hard to get past the generic transformation stories. What are the new practices showing up in real engineering orgs? What does maturity actually look like, and what separates teams that are moving from teams that are stuck? What are the patterns for enabling humans and agents, together?
>
> Patrick Debois has been collecting the practices and patterns, talking to the early Agent Enablement teams already on the job, team leads, and VPs of Engineering. What's showing up is a new function: a team that enables other teams to get real leverage out of their agents.
>
> This talk takes the Context Development Lifecycle off the individual laptop and onto the org chart, grouped across three pillars: Enablement, Platform, Governance.

## Thesis (synthesised)

Scaling AI coding agents is the same organisational problem as scaling DevOps or Cloud was: every team is reinventing the wheel, which is fine for learning but unsustainable. A dedicated **Agent Enablement** function — operating across Enablement / Platform / Governance pillars and supporting Developer / Team Lead / VP roles — is emerging as the answer. The core mindset shift is to **fix the system that produces the code, not the code itself**, and to treat agents as team members whose performance is part of a team's KPIs. Continuous Learning is the new CI/CD.

## Section TOC

| # | Section | Lines | Summary |
|---|---|---|---|
| 1 | MC intro | ~1–10 | MC introduces Debois; notes the intro itself was AI-generated. |
| 2 | Framing & disclaimer | ~11–30 | New talk written days before; "we're not building the thing, we're building the thing that builds the thing"; everyone reinventing the wheel is unsustainable. |
| 3 | Enable the agent (developer level) | ~31–95 | AI product engineer role; fix-the-system not fix-the-code; specs/planning/testing/observability; reusability; smaller tasks; standardised context libraries; access control; blast radius. |
| 4 | Enable the team (team lead level) | ~96–135 | Team leads accountable for agent performance too; token spend; new practices: curriculum, definition of done including agent quality, turns-per-task metric, agent retros; training "context providers"; ownership of shared skill libraries. |
| 5 | Enable the platform | ~136–200 | Incubation → shared platform pattern; cross-team reuse of harnesses/skills; learning from prod (gap between coding vendors and AI-platform observability vendors); shared memory backbone; registries; MCP gateways; ownership of shared components; evals as the new "I'll write tests later"; extensibility vs forking. |
| 6 | Enable the organisation (VP level) | ~201–260 | VPs balance investment across teams; ownership drives improvement; sustainable pace across teams; cost beyond licences (education, monitoring); governance (approved skills, KPIs for agent quality); making pain visible to justify ROI to the business/CFO. |
| 7 | The barrel mental model & Continuous Learning | ~261–290 | No playbook; raise all staves of the barrel together; Continuous Integration → Continuous Delivery → **Continuous Learning** as the next era. |
| 8 | Debois's own research method | ~291–310 | Agent that distils social posts into patterns; filtering vendor bias; surveys too slow. |
| 9 | Close & MC outro | ~311–end | Call for stories; LinkedIn for slides in exchange for feedback; MC wraps. |

## Terminology glossary (Debois's own framing)

- **Agent Enablement** — a new function: "a team that enables other teams to get real leverage out of their agents" (abstract); analogous to DevOps team, Agile team, Platform team in previous eras.
- **AI product engineer** — the internal term Debois's org settled on, because "AI engineer" was confusing ("is it AI in the products"). Customer-focused; blends requirements/build/figure-out-what-to-build.
- **Building the thing that builds the thing** — the new mentality: improve the system that produces code, not the code itself.
- **Harness** — the surrounding scaffolding (specs, tools, pipelines) an agent runs in. "Within Tessl we have now five or six harnesses being built… probably only a few should survive."
- **Context library / shared skills** — standardised reusable context, instead of everyone maintaining their own Claude.md.
- **Turns per task** — a metric Debois "really likes": "how many turns does an agent need to do to do the right thing" — proxy for harness/context efficiency.
- **Agent retro** — "how did our agents work?" run at the end of a cycle, feeding back into the next.
- **Context provider / agent whisperer** — the new craft: writing context well, replacing "the coding rock star".
- **Evals** — the agent-era equivalent of tests; same procrastination pattern ("we'll do that after the project").
- **Barrel mental model** — borrowed from DevOps automation: a barrel held by staves of unequal height leaks at the lowest stave; improvement must happen across all pillars together, not just automation.
- **Continuous Learning** — Debois's proposed successor to CI/CD: accumulating knowledge across teams and adopting new tech fast as a business edge.

## Named frameworks / concepts introduced

1. **Three pillars of Agent Enablement** — Enablement, Platform, Governance.
2. **Three organisational lenses** — Developer / Team Lead / VP of Engineering, each with their own mindset shift.
3. **Context Development Lifecycle, scaled to the org chart** — the talk's stated subject (referenced via the abstract; in the transcript itself the connection is implicit through the three pillars).
4. **Fix the system, not the code** — primary mindset shift for individual developers.
5. **Agents as team members** — primary mindset shift for team leads (KPIs include agent performance).
6. **Barrel model of balanced maturity** — primary mindset for VPs / org-wide work.
7. **CI → CD → Continuous Learning** — historical arc Debois places this work inside.

## Open questions / not covered

- **No concrete KPI definitions** — Debois admits the KPI side is still vague: *"I know there's still sounds a little bit vague and that's kind of what I'm working on."* Listeners shouldn't expect prescriptive metric formulas.
- **No vendor recommendations** — talk is vendor-neutral on tooling beyond mentions of Claude.md and MCP gateways.
- **No detailed org-design templates** — no headcounts, reporting lines, or hiring profiles for the Agent Enablement team itself.
- **No deep dive on security/compliance** — access control and blast radius are flagged as "a running problem" but not solved in the talk.
- **No captured Q&A** — the transcript ends with the close; the MC mentions further sessions but no audience questions are recorded.
- **No quantitative case studies** — Debois explicitly avoids "generic transformation stories" but also doesn't supply company-specific numbers.
- **Context Development Lifecycle itself** — referenced in the abstract (Tessl blog) but not unpacked stage-by-stage in the spoken transcript.
