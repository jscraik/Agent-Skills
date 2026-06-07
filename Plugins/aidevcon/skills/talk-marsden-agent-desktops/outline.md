# Outline — Giving Every Agent Its Own Desktop

## Speaker

**Luke Marsden** — Hacker and entrepreneur. CEO of Helix (private agents). Previously: SIG cluster-lifecycle lead in Kubernetes; founder of ClusterHQ (storage for Docker & Kubernetes, early Docker era); founder of Dotscience (end-to-end MLOps). Works at the intersection of AI agents and DevOps. Self-describes in the talk as "a client human".

## Abstract (as supplied)

> It was winter 2025, and I started to go a bit crazy with this idea that we could make the snake eat its own tail. We were building an agent platform that runs entirely on your own computers, and we had a user in Paris start pushing us towards coding agents as a primary use case. … Fast forward to summer '26. We're now using this system to build itself. Claude Code and Codex and Qwen Code with local models all happily coexist. We forked Zed so we could remote control it inside the agent desktops. … The next tantalising pivot? Building a self-improving company.

## Thesis (synthesised)

All information work is converging on agent management; the right primitive is to give *each agent* — not each human — its own isolated computer with a GPU-accelerated streaming desktop and a real IDE inside it, orchestrated through a Kanban-shaped task pool and driven by spec-driven (plan-then-implement) prompts, so that humans can review specs and QA running apps from anywhere (including a phone at the gym) while the platform dogfoods itself into building itself.

## Section TOC

| # | Section | Summary | Lines (approx) |
|---|---|---|---|
| 1 | Intro & thesis | Self-intro; "all information work is eventually going to become managing agents"; Steve Yegge's stages of AI adoption | L1–L20 |
| 2 | The pain that motivated this | Five parallel agents on one working directory; one `git stash`-ed the others; another `rm -rf .`'d the checkout | L21–L35 |
| 3 | Design space — opinionated tour | Warning: "contains opinions"; framing for the rest of the talk | L36–L48 |
| 4 | Opinion 1: Local vs centralized | "Give each agent their own computer, not each human" — global teams, sun-follows-the-team, Devicon quote | L49–L70 |
| 5 | Opinion 2: Do we still need an IDE? | Claude Code "made me stupider"; need a visual display following the agent; rant on Cursor latency and Claude Code being React | L71–L85 |
| 6 | Opinion 3: Scale by task vs by org-shape | Org-shape agents devolve into "enterprise politics"; hybrid: coarse roles + per-task scaling | L86–L105 |
| 7 | Demo 1: Kanban + agent desktops | Three agents on three to-do-app tasks; GPU-accelerated desktops; forked Zed for remote control + MCP | L106–L130 |
| 8 | Spec-driven development | Short human prompt → plan phase reads code → spec written as markdown → human comments in Google-Docs-style UI → approve → implementation phase | L131–L160 |
| 9 | Demo 2: Spec review + in-browser QA | Bug-deletion task; agent QAs by typing "buy groceries"/"walk the dog"; "fiery CSS animation" / "burning in hell" prompt iteration | L161–L195 |
| 10 | Mobile + multiplayer | "Best way to run Zed on your iPad while you're at the gym"; Figma-style multiple cursors on one agent desktop | L196–L210 |
| 11 | Dev-env bootstrap speed (ZFS) | 40-minute Docker build was the blocker; ZFS clones + Docker-in-Docker (up to 16 levels deep, they use ~3) to give each agent a primed env | L211–L235 |
| 12 | Dogfooding — Helix builds Helix | Reviewing PRs by looking at screenshots; commenting two lines on a spec is the main work now | L236–L255 |
| 13 | Token costs, privacy, "Donald Trump" | Local models (Llama 3.1) do ~80%; invest in 8×RTX 6000 Pro instead of next 3 months of tokens; burst to Claude Opus 4.1 for hard stuff | L256–L275 |
| 14 | Self-improving business | Self-improving codebase → product/support agents → sales/marketing/finance/legal → founder layer; LinkedIn outreach demo ("2FA please") | L276–L300 |
| 15 | Recap | Seven design-space takeaways | L301–L315 |
| 16 | Q&A — security/guardrails | "Better than opening the floor on your `~`"; per-project MCP config; needs governance tooling, would rather partner | L316–L335 |
| 17 | Q&A — GPU VMs implementation | Mutter (Wayland compositor) in Docker; GStreamer plugins; Wolf project (C++) → ported the Rust NVIDIA CUDA plugin out | L336–L355 |
| 18 | Q&A — Why still an IDE / what kind | Zed is fast, low memory matters when running hundreds; ambient knowledge from watching agent flow; "you need an IDE on the inside" + a meta-IDE control plane | L356–L375 |

## Terminology glossary (Marsden's own definitions)

- **"Snake eating its own tail"** — using the platform you're building to build itself; dogfooding to the limit. *(Marsden: "this idea of making the snake eat its own tail by actually using our own stuff that we were building to build itself.")*
- **Agent desktop** — a GPU-accelerated streaming Linux desktop, isolated per agent, in which the agent runs a real IDE and a real browser. *(Marsden: "give each agent their own computer, not each human… each agent has its own desktop environment.")*
- **Spec-driven development (Marsden's variant)** — a single agent with two phases: a planning phase that reads the codebase and writes a markdown spec from a short human prompt, then (after human comments + approval) an implementation phase. *(Marsden: "the agent has an explicit planning phase and later implementation phase… you get the agent to write a plan before it does the work, you get much better results.")*
- **Scaling by task vs by org-shape** — task-scaling: a pool of identical agents picking tasks (e.g. Kanban). Org-shape: CEO-agent → VP-agent → engineer-agents with names. Marsden found pure org-shape "devolve[s] into enterprise politics."
- **Hybrid org/task scaling** — coarse role categories (marketing/sales/engineering) with different tool/connectivity scopes, but within each role you scale by task — "a sort of pool of bees."
- **Meta-IDE** — the control plane wrapping all the agent desktops; "you need an IDE on the inside. You also need the meta IDE which is like the control plane for all of the different agency running."
- **ZFS-cloned Docker-in-Docker env** — pre-primed development environments cloned cheaply per agent so each starts from a "really fresh fully cached Docker environment."
- **"Background agent that feels like the foreground agent experience"** — Marsden's quality bar that drove the GPU-acceleration rabbit hole.

## Named frameworks / concepts introduced

1. **The seven design-space dimensions for systems that run agents** (Marsden's opinionated tour):
   1. Local (per-developer snowflake) vs centralized (org-pool of agents) — **opinion: centralize**.
   2. IDE or not — **opinion: still need an IDE**.
   3. Task-scaling vs org-shape scaling — **opinion: start task-scaled; long-term hybrid (coarse roles + task pool)**.
   4. Spec-driven development with plan/implement split — **opinion: a must**.
   5. Mobile + multiplayer access to agent desktops.
   6. Dev-environment bootstrap speed — **opinion: get this to seconds** (their fix: ZFS clones + Docker-in-Docker).
   7. Token-cost / model-mix strategy — **opinion: invest in local-model hardware, burst to frontier**.
2. **The plan→spec→approve→implement→QA loop** (Marsden's spec-driven flow).
3. **Steve Yegge's stages of AI adoption** — chat completion → single CLI agent → multiple agents in parallel → (where the problems start).
4. **The self-improving company stack** — self-improving codebase → product/support → sales/marketing/finance/legal → founder-layer hypothesis/direction.

## Open questions / not covered

- **Concrete security/governance design.** Marsden explicitly punts: needs tooling, would "rather partner with people who are doing good things in that space"; mentions "Ivan" is working on something.
- **How org-shape scaling could be made to work** — they're "researching" it but only have a negative result so far.
- **Pricing / commercial model for Helix.** Not discussed.
- **Detailed evals or benchmarks** showing local Llama 3.1 actually does "80%" of the work — asserted, not demonstrated.
- **Non-coding agent use cases beyond a brief LinkedIn outreach anecdote.** The "self-improving company" vision is sketched, not shown.
- **How specs are versioned/merged across the special branch** beyond "all just markdown files in a git repo… on a special branch."
- **Failure modes / cost of the ZFS clone approach** at depth, beyond noting Docker-in-Docker supports 16 levels and they use ~3.
- **What happens when agents conflict on shared resources** even with isolated Dockerized envs (e.g. external services, shared CI). Not addressed.

## Participants context for Q&A attribution

The Q&A names "Samuel" (asking about GPU VMs) and references "Ivan" (working on agent governance, third-party). No formal participant list was provided. Treat audience-question attributions cautiously.
