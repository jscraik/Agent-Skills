# Outline — The Reinvention of the Dev Team

## Speaker

**Hannah Foxwell** — independent advisor, writer and creator at the intersection of Platform Engineering, Security and AI. Founder of *AI for the Rest of Us*, creating accessible AI learning experiences for everyone regardless of role or background. Over a decade in technology transformation; has worked on both product and engineering sides. Currently also building **Bib**, a base image management platform, as a two-person team (1 dev : 1 PM, with Foxwell wearing the product hat).

## Abstract (as provided)

> I don't need to tell you that AI has changed software development forever… Just a few years ago I would have advocated for The Balanced Team. A Product Manager, a Product Designer, an Engineering Manager and 4-8 Developers. It worked.
>
> 18 months ago I was telling people that "I've never seen a dev team get to the end of their backlog, I don't see that happening". I've seen it now. Actually, I've seen it more than once.
>
> The balanced team as we knew it doesn't work any more… What I propose is that we go back to fundamentals, refocus on outcomes and evaluate our options for evolving team composition. In this talk I bring you these options, what I've seen work, what I'm ready to throw out, and most importantly, the things I will keep no matter what.

## Thesis (synthesis)

Agentic software development has delivered the velocity that engineering leaders have been chasing for a decade, but the classic "balanced team" (1 PM + 1 designer + 1 EM + 4–8 devs) can't absorb it — back pressure now sits in product, on the path to production, and in human-scale practices like code review and on-call. Foxwell proposes navigating the shift by holding three anchors steady (*build something worth building*, *speed requires safety*, *people matter*) and experimenting with concrete team-composition changes (forward-deployed engineers, product engineers, varied dev:PM ratios, smaller "tapas" teams, beefier platform/SRE capability). She offers no prescription — explicitly "we are sailing these turbulent waters together" — but supplies a Keep / Trash / Try inventory under each anchor.

## Section TOC

| Section | Summary | Approx. transcript lines |
|---|---|---|
| 1. Introduction & framing | MC intro; Foxwell sets up agentic dev as the next velocity unlock after cloud and DevOps. | ~1–40 |
| 2. The agentic maturity ladder | References a borrowed slide (levels 1–8 of agentic coding maturity); reassures audience that being at level 2–3 is fine. Cites Cursor's "third era of software development" blog post. | ~40–60 |
| 3. Three anchors | Introduces the three things she believes will remain true: build something worth building; speed requires safety; people matter. | ~60–70 |
| 4. Anchor 1 — Build something worth building | Outcome over task; back pressure in product; prototyping is now cheap; team-composition patterns (vibe-coding PM, forward-deployed engineer, product engineer); experiments with dev:PM ratios (2:1, even 1:2); CTO panel observation that team sizes aren't shrinking but output expectations are; her own Bib experience. Closes with Keep / Trash / Try list. | ~70–180 |
| 5. Anchor 2 — Speed requires safety | Path-to-production as bottleneck; AI is great at writing tests (JP Morgan continuous component testing); split teams between features and pipeline; cost of day two > day one; users expect reliability and security invisibly; progressive delivery (feature flags, blue-green); SRE language (SLIs, SLOs, error budgets); rising importance of platform & SRE teams. Bib's first two weeks: very little feature work, mostly scalability and security. Keep / Trash / Try list. | ~180–280 |
| 6. Anchor 3 — People matter | Reviewing thousands of lines of AI-authored code "is not a very fun job"; shifting left on peer review (to the spec); Joseph Ruscio quote on unread code; sustainable on-call as the "minimum viable human" constraint (~4 people); challenge planning ceremony (two-week sprints too long); the "broken comb" career model (vs T-shaped) per Sophie Weston's KubeCon talk; user empathy as a non-negotiable hire criterion. Keep / Trash / Try list. | ~280–360 |
| 7. Close | "Experiment with empathy"; the three things she keeps no matter what. | ~360–380 |
| 8. Post-talk announcements | MC: tube strike notice, recordings, workshop waitlist, drinks reception. **Not Foxwell.** | ~380–end |

## Terminology glossary (verbatim definitions where available)

- **Agentic maturity levels 1–8** — A borrowed slide. Level 1 = "narrow IDE agent"; Level 8 = "agentic dream… pure agentic development." Foxwell: "I don't know many people who are operating at level eight and I certainly don't know anybody who can say creditably that they're doing this safely."
- **Third era of software development** — Cursor's framing; the point at which "agentic task started to supersede the top completes [tab completes] and accept."
- **Back pressure in product** — "the pace that we can address these problems in the development team creating what I call back pressure in product. The speed of decision making, the speed of analysis is actually not able to keep up with the pace of software development in a typical team."
- **Vibe-coding product manager** — "That product manager is building prototypes themselves and they're testing the ideas to make sure that the work that's funneling through to the dev team is [validated]." (Transcript says "live coding" — almost certainly speech-to-text for "vibe coding"; she confirms the term immediately after.)
- **Forward-deployed engineer** — "a forward deployment isn't a sales engineer, they're not a [solutions] architect. They're an empowered engineer that sits side by side with the users. And if they see a gap in the product, they are empowered to fix the product and deliver that value to that user."
- **Product engineer** — "engineers that don't need to ask permission of a product manager [to] go and improve the product. And this pattern works incredibly well if you're building products for software developers." References Incident.io's writing.
- **Tapas team** — Replacement for "two-pizza team". "the teeny tiny tapas tea, the small plates" [transcript garble; clearly "tapas team"]. Heard at another conference earlier in the year.
- **Path to production** — The pipeline between code being written and value being delivered to users. Manual steps anywhere on this path produce bottlenecks.
- **Progressive delivery** — "feature flags. So that you decouple feature delivery from the actual deployment of the software… blue green deployments where you can actually have a new release being used by a subset of your users."
- **SLI / SLO / Error budget** — From SRE: "SLIs, [Service] level indicators that tell you whether your product is doing the right thing for its users, objectives about how often it has to work to be your user's needs and error budgets, the amount of kind of forgivable failure in the system."
- **Minimum viable human** — Foxwell's coinage. The smallest team that can sustain an on-call rotation: "I think it's four people. Four people capable of supporting them that product in production because you always have a primary and who is on the secondary and you can't be on call more than 50% of the time."
- **Broken comb** (transcript says "broken cone") — From Sophie Weston's KubeCon talk. Career model replacing T-shape: "develop people who have a broad understanding and a few various areas of depth."
- **Shift-left on peer review** — Moving review from post-code to "the point where you write the spec for the agent."

## Named frameworks / concepts

1. **The three anchors** — (a) Build something worth building; (b) Speed requires safety; (c) People matter.
2. **Keeping / Trashing / Trying** — Applied once per anchor. See `transcript.md` for the verbatim lists.
3. **Team-composition patterns** — Vibe-coding PM; forward-deployed engineer; product engineer; varied dev:PM ratios (2:1 dev-to-PM at "NBIM" [likely n8n]; 1:2 dev-to-PM per Andrew Ng at Davos; 1:1 in her own Bib team).
4. **Two-pizza team → tapas team** — Explicit replacement.
5. **The agentic maturity ladder (levels 1–8)** — Borrowed; she credits a "his" deck without naming.
6. **Cursor's "third era"** — Cited as the industry signal that agentic dev has crossed over.
7. **SRE language for velocity/reliability tradeoff** — SLIs, SLOs, error budgets.
8. **Minimum viable human** — Floor for team size set by sustainable on-call (≈4).
9. **Broken comb careers** — Credited to Sophie Weston, KubeCon last year.

## Open questions / not covered

- **Specific tooling**: she's explicit she is *not* talking about tools or technology — don't expect recommendations on Cursor vs Claude Code vs Copilot, IDE setups, agent frameworks, etc.
- **Concrete cost/ROI numbers** on AI-driven dev productivity.
- **Hiring and layoffs strategy** — touched on briefly ("I don't think it's necessarily about reducing headcount") but no detailed guidance.
- **How to actually do shift-left peer review** — she names the direction but offers no process.
- **Designer role** — the original "balanced team" included a product designer; she doesn't return to designers in the new composition.
- **Engineering management role evolution** — she acknowledges "It's a tough time to be a manager" but does not specify what the role becomes.
- **Compensation, levelling, performance review** under broken-comb careers.
- **Safety/governance of agentic systems themselves** — she flags level-8 isn't being done safely but doesn't prescribe controls.
- **Non-software contexts** — entire talk is software product orgs.
