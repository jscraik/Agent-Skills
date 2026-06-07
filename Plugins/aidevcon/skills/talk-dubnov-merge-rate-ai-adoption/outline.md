# Outline — When Our PM Started Writing Code

## Speaker

**Tammuz Dubnov** — Founder & CTO of Autonomy AI, which builds autonomous AI agents enabling non-technical and technical users to ship code safely into enterprise codebases through agent-driven workflows. Over a decade leading AI startups across text, vision, audio, and vector domains; holds several patents and authored multiple publications. Served as an elite academic officer in Unit 8200, leading AI-driven projects. UC Berkeley graduate at 18 with honours in Theoretical Mathematics; master's in AI from UC San Diego. International speaker, university lecturer, and award-winning performer.

## Abstract (as provided)

> In early 2026, our PM started opening pull requests to our production codebase. Not prototypes — real, merged code. This talk is about what that demanded from the engineering team, and from the PM herself.
>
> AI didn't eliminate our bottleneck — it moved it. Code generation stopped being the constraint. Review, coordination, and architectural alignment became the new pressure points. Merge rate — the percentage of PRs that actually land in production — became the signal that told us whether the team was adapting or drowning.
>
> Getting there required change on both sides. Engineers had to rethink how they review, what they gate on, and how much bandwidth they allocate. The PM had to learn which changes she could ship independently and which required coordination first. Neither side got it right immediately.
>
> Once we found that alignment, the effect compounded. Features that used to take a full sprint now land in days. Entire product areas are owned end-to-end by the PM. The developers freed from feature delivery work at a higher level — focused on architecture, patterns, and system design. The team didn't just absorb the change. It got faster because of it.

## Thesis (synthesis, not the abstract)

"AI-native" doesn't mean giving developers bigger token budgets — it means **collapsing the handover** so the person who cares and has authority can also execute, with agents doing the work. The bottleneck has moved from code generation to review/coordination/architecture. **Merge rate** (and especially the share of non-tech-authored PRs that merge with zero dev touches) is the metric that tells you if you're actually adapting. Doing this requires (a) tools tuned for the role — not cloud code for everyone, (b) a **harness** that evolves as agents make mistakes, and (c) keeping engineering guards (tests, feature flags, architecture review) in place even as velocity rises.

## Section TOC

| § | Heading | 1-line summary | Lines |
|---|---|---|---|
| 1 | Intro & framing questions | Host intro; Tammuz polls the room on CFO AI-spend conversations and on whether PMs/designers are opening PRs | ~1–25 |
| 2 | What "AI-native" actually means | Tammuz's definition: the person who cares + has authority is also the person who can do the work; AI collapses the handover | ~26–55 |
| 3 | Why handover is the real bottleneck | Sprint-cycle handovers from PM→design→dev→review compress to ~13 minutes; everyone gets to focus on what they care about | ~56–95 |
| 4 | Wrong ways to go AI-native — Uber & Microsoft cautionary tales | Uber 6× AI spend exhausted in 4 months with no measurable feature-velocity link; Microsoft pulling back Claude Code rollout | ~96–125 |
| 5 | Where the tokens actually go | Of $100 spent on AI, only ~$18 ships meaningful code; rest goes to rework/bugs | ~126–138 |
| 6 | Right way — Shopify as positive example | Empowering non-engineers with thousands of Cursor licenses; ~50% of non-eng output accepted as-is | ~139–160 |
| 7 | Wrong-vs-right patterns enumerated | (a) more tokens to same devs ≠ velocity; (b) PM prototyping tools = "hurry up and wait"; (c) cloud code to everyone = PR fatigue + desk visits | ~161–195 |
| 8 | Harness engineering | Definition of harness; principles (onboard self, product-level language, long sessions, self-check, learn across users); feasibility on complex monorepos | ~196–250 |
| 9 | Authority boundaries — the failed PR example | Designer's image-versioning PR was tech-correct but storage-architecture-wrong; got rebuilt by dev, design retained | ~251–285 |
| 10 | How to measure AI-native adoption | (a) PR count per non-tech contributor; (b) merge rate (~74% benchmark); (c) zero-dev-touch rate of merged PRs (~84% benchmark) | ~286–315 |
| 11 | Closing — democratising authorship | Need an "OS unco" [likely "OS uncomplicated" / agent-OS] absolutely coupled to your codebase | ~316–330 |
| 12 | Q&A — measurement tooling | Tammuz: Autonomy's own system tracks author (shows as "Tammuz I bought" bot) + commit stream for post-merge touches | ~331–345 |
| 13 | Q&A — do engineers move into UI/PM space? | Yes — devs make product decisions to merge fast, everything feature-flagged, PMs/QA follow up with cleanup PRs | ~346–375 |
| 14 | Q&A — rollback / safety mechanisms | Depends on org's existing CI; harness adopts your practices (feature flags if you have them, tests if you write them); not opinionated | ~376–395 |
| 15 | Q&A — proving PR-fatigue cost to leadership | Agent labels every PR with risk level + size so reviewers can prioritise; team-wide load visibility | ~396–425 |
| 16 | Wrap-up & off-mic fragments | Host wraps; trailing post-talk fragments (someone from "Grana lamps" / Granola? on a green-field project) | ~426–end |

## Terminology glossary (speaker's own definitions)

- **AI-native** — Tammuz's definition: "the person that cares, the person has the authority to make the decision. It's also the person who can do the work. That basically AI collapses the gap. Collapses the handover." Common misdefinition he rejects: "being an animated [AI-native] means that rpms are designers in our QAs, more people who've been pull requests" — he calls this "the symptom" not the cause.
- **Harness** — "you saw the agent make mistake and you make it unfeasible for the agent to make the same sticky game [mistake again]. You put in some sort of wall." Must adapt over time as new mistakes are made.
- **Merge rate** — share of non-technical contributors' opened PRs that land in production. Autonomy's benchmark: **~74%** (one in four PRs overstep, which Tammuz calls healthy).
- **Zero-dev-touch rate** — of PRs that merge, share that merge "without any dev interfering without them pushing more commits to fix change adjust." Autonomy's benchmark: **~84%**.
- **PR fatigue** — burden on dev team from reviewing too many low-quality / oversized PRs.
- **Calamarous Coding** — Tammuz's own methodology for keeping engineering guards in place while moving quickly. Source text reads variously "clamorous college", "climate astrology", "Calamarous Coding" — likely speech-to-text artifacts of the same term. He explicitly defers detail: "I'm not going to talk about it in this talk because there's not enough time."

> ⚠️ The transcript contains heavy speech-to-text noise. "Animated" almost always means "AI-native". "Heard" / "harness" appears garbled in places. "Autonomy" is sometimes "Autonomy AI" / "Tanya" / "antinomy". Quote what's actually in the transcript and flag the likely intended word.

## Named frameworks / concepts

1. **The handover-collapse definition of AI-native** — authority + caring + execution converge on one person, with agents executing.
2. **Harness engineering principles** — (a) agent onboards itself to the codebase; (b) understands product-level language; (c) manages long sessions; (d) self-checks with automatic feedback loops; (e) knows what "good" means and can prove it; (f) for non-tech users specifically: own/read code, check itself constantly, learn across all users in parallel.
3. **Three measurement dimensions** —
   - PR count per non-technical contributor (adoption breadth)
   - Merge rate (~74% healthy benchmark)
   - Zero-dev-touch rate on merged PRs (~84% healthy benchmark)
4. **Wrong-way patterns** — (a) bigger token budgets to same uninterested devs; (b) prototyping-only tools for PMs; (c) Claude Code for everyone.
5. **Right-way patterns** — (a) role-tuned tools; (b) keep engineering guards (tests, feature flags, architecture review); (c) accept the merge rate < 100% and treat it as healthy signal.
6. **Feature-flag-led developer autonomy** (from Q&A) — devs ship fast under feature flags, PMs/QA tune UX in follow-up PRs.
7. **Agent-labelled PRs** (from Q&A) — automatic risk + size labels on each PR to combat reviewer overload.

## Open questions / not covered

- **Calamarous Coding methodology details** — Tammuz explicitly defers ("I'm not going to talk about it in this talk because there's not enough time").
- **Specific CI / rollback tooling recommendations** — he says "depends on organizations" and the agent adopts whatever practices already exist; he is "not opinionated".
- **How to bootstrap harness from zero** — he says everything is feasible and they've "never knocked any of it" but doesn't walk through setup.
- **Cost / pricing of Autonomy AI** vs Claude Code / Cursor — not discussed.
- **Security/permissions model for non-technical contributors** beyond "secrets to access private repositories and artifact registries" — mentioned but not detailed.
- **Team-size thresholds** at which the merge-rate numbers apply — Autonomy quotes hundreds of orgs / thousands of PRs but doesn't break down by team size.
- **What happens to junior engineers** in this model — talk focuses on senior engineers moving up to architecture and PMs moving down to code; juniors not addressed.
- **Specific evidence on Shopify** beyond "thousands of cursor licenses" and "50% just gets accepted" — no source citation in talk.
