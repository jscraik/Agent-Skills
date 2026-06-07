## Speaker

**Edouard Maleix** — freelance consultant based in Vienna, helping startups scale past their MVP. Focus areas: system design, application security, dev productivity, AI integration. He works with CTOs and tech leads on authentication, application performance, and productivity challenges, and is building an open-source project called **MoltNet** — a platform to turn AI agents' experience into proven, reusable context. The talk draws on customers he's helped adopt coding agents.

## Abstract (as provided by speaker)

> Most teams have begun surrounding coding agents with rules, notes, and feedback controls, but these are rarely coherent enough to function as a real system. Agents repeat mistakes across sessions, guidance grows without being validated, and what teams accumulate is instructions, not reusable knowledge. That gap becomes obvious the moment a teammate's agent opens a pull request: the code is visible, but authorship, rationale, and trust are still not.
>
> What if each agent had its own identity, its own signed commits, its own reasoning linked to every change and its own track record within the team? And when it encounters a bug or an incident or a WTF moment — the kind someone swore would never happen twice — it captures the interruption. It links that to the fix, compares it with lessons from other agents and humans, tests it against real tasks, and feeds what survives back into future work.
>
> I have been looking for a practical way to make mistakes compound into collective intelligence instead of disappearing into chat history. This talk is about the workflow that makes that knowledge reusable, attributable, and trustworthy.

## Thesis (synthesis)

Agent-generated lessons currently die in closed chat sessions because there's no system that catches them, attributes them, validates them, and feeds the survivors back into future work. Edouard proposes a three-act pipeline — Identity + Diary → Pack + Curation + Render → Evals + Autonomy — where every entry preserves human-and-agent attribution, packs are rendered into agent-readable skills only after passing fidelity and usefulness evals, and over time agents can voluntarily pick tasks while humans retain "the goal, the judgment and the responsibility."

## Section TOC

| Section | Summary | Approx. transcript lines |
|---|---|---|
| Opening & framing | Hosts intro; Edouard sets the stage that agents are moving from isolated environments into teams. | 1–20 |
| The familiar obstacles | Lessons evaporate; rules/skills pile up; PRs go green without showing what shaped the work. | 20–40 |
| What we actually need | Not another wiki — a "factory" that catches interruptions, tests guidance, lets decayed knowledge die. | 40–55 |
| Speaker background | Edouard's consulting work and the open-source infrastructure (MoltNet) behind the talk. | 55–65 |
| Act 1 — Identity & the Testify PR anecdote | The Testify PR ghostwritten by Claude under his GPG signature; agents need their own identity, signed commits, access rules. | 65–95 |
| Act 1 — The Diary primitive | Diary as the place where work becomes a forward artifact; first access-boundary surface; commits reference entries for rationale. | 95–115 |
| Bridging example — the Go SDK incident | Mon/Tue/Wed regression where the agent keeps forgetting to regenerate the Go SDK; iteration waste. | 115–140 |
| Entries, categories, linking | Four categories of entries; WTF-moment entry for the Tuesday incident; linking entries to fixes and PR comments. | 140–165 |
| Passive accumulation | Initial phase is just letting the agent capture entries; magic happens later in curation. | 165–175 |
| Curation — discover, slice, expand, search | Mapping the territory of accumulated entries; building thematic Packs (not a "bag of toys" — a "gallery exhibition"). | 175–200 |
| Render — pack → markdown skill with attribution | Rendering entries into a token-budgeted markdown the agent reads; every section keeps source + human + agent attribution. | 200–220 |
| Act 2 summary — interruption → entry → pack → render | The compounding pipeline; one developer pays once, the team gets the asset. Compound engineering. | 220–230 |
| Who decides what survives? | Humans use ADRs/wikis/postmortems; agents have no feedback loop — need instruments to judge. | 230–245 |
| Evals — controlled VM environment | Sandboxed environment with controlled file/network access; per-task prompts, criteria, references. | 245–260 |
| Evals — Fidelity | Does the rendered pack faithfully reflect the entries? Warning: lazy prompts/criteria give false confidence — be the judge yourself first. | 260–280 |
| Evals — Usefulness | Reuse captured incidents as eval tasks; compare runs with vs. without the pack. Go SDK case: 67% fail without pack, always pass with. | 280–305 |
| Act 3 — Autonomy & voluntary task picking | Drop "the agent always agrees" vanity; bucket of tasks, agents pre-pick based on capabilities; specialized coder/critic/management agents. | 305–325 |
| Closing | "What is your agents learned yesterday that your team still knows today?" + QR code to the repository. | 325–335 |
| Q&A — MoltNet vs. mem-palace-like memory | Memory is one component but the workflow matters more than memory storage. | 335–350 |
| Q&A — Real-world edge cases & nuance | Entries persist; fix may not land same day; need workflow intelligence to relate to existing entries; one-offs are fine to ignore. | 350–365 |
| Q&A — Maintenance as code evolves | Same as maintaining skills: rendered packs become markdown → skills; run regular evals; if not useful, it dies. | 365–380 |
| Q&A — How do you choose? Curation responsibility | Mix; start manually so you master the workflow yourself before delegating curation to an LLM. | 380–395 |

## Terminology glossary (speaker's own definitions)

- **Identity (for an agent)** — *"give the agent an identity. That's the first primitive. Block. The identity gives us tier separate actor. It gives us some sign commits."* Includes its own identifier, access rules, and authorization separate from the human's.
- **Diary** — *"the place where the stops being just the work and the lessons start being a four-way artifact"* (likely "forward artifact"). Holds discoveries, WTF moments, and decision-making during work. First place where access policies (personal / repo-scoped / project-scoped) can be defined.
- **Entry** — a granular unit inside the diary. Four categories capture different situations; e.g. a "WTF moment" entry for the Tuesday API incident. Entries can be linked to each other (e.g. an entry linked to a PR comment that called out the issue, and to the fix).
- **Pack** — *"a small created bundle of entries"* that the agent should pick for one task or area. *"Clearly not your children bags of toys… Gallery exhibition. Really. You have to make sense with that pack."*
- **Render (a pack)** — converting raw entries in a pack into markdown files an agent can consume, fitted to the token budget, where *"every section can see points through given entry. And then resection. Keep the attribution live"* — source, human operator identifier, agent identifier.
- **Fidelity (eval dimension)** — *"whether the… Bank is true to the entries. Does it transform the entries. Does it include all of them?"*
- **Usefulness (eval dimension)** — measured by replaying captured incidents as tasks with and without the rendered pack and comparing the delta.
- **Activation** — *"did the scale did not get the story on time"* (likely: did the skill get the story / context on time). Mentioned but explicitly out of scope for the talk's eval section.
- **Voluntary task picking** — instead of assigning tasks to agents, you have a bucket of tasks; *"any of those agents can fire a task if it matches its capability. So it pre-picks voluntarily."*
- **Compound engineering** — referenced as a name for the discipline this workflow embodies: *"there is even a discipline. I did not hear the word yet today. It seemed to be called compound engineering."*

## Named frameworks / concepts

1. **The three-act pipeline**
   - **Act 1 — Identity + Diary**: agent has its own identity, signed commits, access rules; rationale captured in diary entries; commits reference entries.
   - **Act 2 — Curation + Pack + Render**: passive accumulation → discover/slice/expand/search entries → bundle into Packs → render to markdown skills with live attribution. *"Interruption becomes an entry. The right entries become a pack. Then the pack becomes something the agent can read."*
   - **Act 3 — Evals + Autonomy**: fidelity + usefulness evals in a controlled VM environment; eventually voluntary task picking by specialized agents (coder / critic / management). *"the human keep the goal, the judgment and the responsibility and the agents keep the continuity repetition."*

2. **"You are the judge before the LLM is"** — *"before you run an llm judge you are the judge. You do the work that the judge will do yourself."* Calibrate criteria against your own scoring first.

3. **Knowledge decay is acceptable** — *"you will let some of those guidance fail because some knowledge just decay. We have to accept that."* Don't try to keep static documentation alive; let it die when models or code evolve.

4. **The Testify-PR anecdote as moral hazard** — Edouard ghost-wrote ~95% of a PR with Claude under his own GPG signature because the maintainer was hostile to AI. Used as the framing for why agents need their own identity.

5. **The Go-SDK Mon/Tue/Wed regression** — recurring iteration waste because corrections stay trapped in one session.

## Open questions / not covered in this talk

- **Activation evals** — explicitly called out as out of scope: *"in that session we will just focus on fidelity and usefulness."*
- **Memory storage / retrieval internals** — in the Q&A Edouard says *"I did not spend most of my time refining how best the memory works, how best is stored and how best it can be retrieved."*
- **Specific tooling beyond MoltNet** — no comparison to other agent-memory products (the mem-palace question is briefly acknowledged but not engaged in depth).
- **Pricing / cost analysis** of running per-task VMs and evals.
- **Multi-team or org-wide governance** — scoping policies are mentioned (personal / repo / project) but not org-level federation.
- **Concrete agent-identity implementation details** — GPG keys, OIDC, GitHub bot accounts, etc. are not specified.
- **How the four entry categories are named/defined** — the speaker says there are four but only the "WTF moment" category is named explicitly.
- **Failure modes of voluntary task picking** — e.g. starvation of unattractive tasks, capability gaming.
- **Quantitative results beyond the Go SDK example** (67% baseline fail rate vs. always-pass with pack) — no broader benchmark numbers given.
