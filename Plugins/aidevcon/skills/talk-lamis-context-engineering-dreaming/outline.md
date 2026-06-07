# Outline — Context Engineering, Memory Systems, and Dreaming — Lamis

## Speaker

**Lamis** — Member of Technical Staff at Anthropic, on the Applied AI team. Per the talk: *"this is a team which sits between research, product and go-to-market. So we do a mixture of working on internal projects as well as directly with customers who are building agents at the frontier."* Lamis works specifically with startups and founders.

**Introducer / host:** Simon Maple, Head of Developer Relations at Tessl and AI Native Dev co-host. Previously Field CTO and VP Developer Relations at Snyk, ZeroTurnaround, and IBM. Java Champion (2014), JavaOne Rockstar (2014, 2017), Duke's Choice award winner, Virtual JUG founder.

Note: the transcript has no speaker labels. The opening welcome ("Hey everyone... hopefully we'll be having a wonderful day so far here at AI DevCon") reads as Simon's host intro, but transitions into Lamis's talk by the line *"By way of introduction, my name is Lamis."* without a clear break.

## Abstract

[Not provided by the user.] [Inferred:] A tour of the past year of context-engineering primitives at Anthropic — `CLAUDE.md`, memory tools, Skills, and filesystem-as-memory — followed by the production engineering guardrails (versioning, concurrency, permissioning, portability) needed to scale these to multi-agent fleets, and culminating in **dreaming**: an out-of-band, asynchronous memory-curation process inspired by the analogy of a head teacher reviewing student work to spot patterns and update the curriculum.

## Thesis (synthesis)

Raw model intelligence doesn't compound in your organization unless you invest in context engineering — and the state of the art has converged on filesystem-style memory stores of markdown files that agents autonomously read, write, and search. But to scale these to production you need classic engineering primitives (versioning, hash-based concurrency, permissioning, portability) baked into the harness. And to escape the limits of *in-band* memory (where the same agent juggles task-completion and memory curation), you add an *out-of-band* asynchronous process — **dreaming** — that reviews many transcripts at once, finds cross-session patterns, and proposes memory updates.

## Section TOC

| Section | Summary | Transcript lines |
|---|---|---|
| 1. Welcome & host intro | Simon's welcome to AI Native DevCon | ~1–3 |
| 2. Speaker intro — Lamis & Applied AI at Anthropic | Lamis introduces themselves and their team | ~3–10 |
| 3. Talk roadmap | Four-part plan: recap, state of the art, productionizing, dreaming | ~10–17 |
| 4. Why context engineering matters | Intelligence alone doesn't compound without org-specific context | ~17–30 |
| 5. Timeline of context-engineering primitives | CLAUDE.md → memory tools → skills → filesystem-as-memory | ~30–70 |
| 5a. CLAUDE.md files | "Unreasonably effective" markdown injected at session start | ~32–42 |
| 5b. Memory tools | Agents autonomously read/write/update memories in-band | ~42–50 |
| 5c. Skills & progressive disclosure | Frontmatter for discovery, body loaded on demand; **bookshelf analogy** | ~50–62 |
| 5d. Filesystem-as-memory | State of the art: just markdown in a directory, use bash/grep | ~62–72 |
| 6. Production problems at scale | Concurrent writes, bad org-wide writes, stale memories, prompt injection | ~72–88 |
| 7. Four production principles | **Versioning, Concurrency (hashing), Permissioning, Portability** | ~88–112 |
| 8. Benefits when guardrails are in place | Better accuracy, lower cost/latency, freed-up product capacity | ~112–122 |
| 9. Limits of in-band memory | Split focus; per-session visibility limit | ~122–138 |
| 10. Dreaming introduced — school analogy | Teachers/head teacher analogy for dedicated out-of-band curation | ~138–150 |
| 11. What dreaming looks like mechanically | Memory store + transcripts → review agent → proposed changes | ~150–168 |
| 12. Dreaming examples (school analogy continued) | Missing curriculum topic; calculator-in-radians; org-wide em-dash | ~168–184 |
| 13. Designing dreaming in production | Orchestrator + sub-agents, steering, prevalence stats, human accept/reject | ~184–208 |
| 14. Memory + dreaming in parallel | In-band = faster feedback; out-of-band = broader visibility & dedicated tokens | ~208–222 |
| 15. Summary & call to action | "Keep thinking, keep learning, keep dreaming" | ~222–238 |
| 16. Q&A — memory store implementations | Question about enterprise memory stores; answer points to Claude Managed Agents | ~238–256 |
| 17. Q&A — guardrails & permissions for dreaming | How dreaming respects per-user permission sets | ~256–272 |
| 18. Q&A — "are we reinventing databases?" | On finding the right boundary between agent autonomy and harness primitives | ~272–290 |
| 19. Close | Applause; informal post-talk chatter | ~290–end |

## Terminology glossary (definitions the speaker actually gave)

- **Context engineering** — the work of translating raw model intelligence into "durable, scalable, useful product" by giving agents the context they need to perform org-specific tasks. *"a really great investment ... has the effect of multiplying the intelligence even as models get smarter."*
- **CLAUDE.md** — a markdown file shipped with Claude Code that "just gives the agent a couple of instructions about making your way around the code base, the organization, your own user preferences" and is injected at the beginning of a session.
- **Memory tools** — tools that let agents "autonomously manage their own memory systems ... decide when they read, when they write and when they update memories ... all happening in band."
- **Skills** — units with a few-sentence frontmatter the agent scans first, plus a deep body loaded only when relevant. Suited to "processes where you have like a procedural workflow ... an opinion about how the process works end to end."
- **Progressive disclosure** — the design idea behind skills: surface a short title/frontmatter for discovery, only load full detail when needed. Speaker's analogy: a **bookshelf** of books you scan by title and pull out when relevant — *"if someone walked up to me and started speaking to me in French and I noticed I have a French dictionary, I can pull that out."*
- **Filesystem-as-memory** — current state of the art per the speaker: "modeling these memory systems just as file systems ... fill them up with markdown. Agents actually just very good at using normal file system tools like bash and rep."
- **In-band memory** — memory read/written by an agent within a specific session. Limitations: "inherent split of focus and resources" between task and curation, plus per-session visibility only.
- **Out-of-band memory curation** — a separate asynchronous process with its own resources and broader visibility, dedicated to memory hygiene.
- **Dreaming** — speaker's term for an out-of-band process: *"a second order process over memory ... runs in batch and asynchronously, with its own allocated resources to ensure that those memories themselves are affected up to date."* Inputs: existing memory store + a batch of agent transcripts. Output: proposed changes to the memory store, with example transcripts and prevalence stats.
- **Memory store** — *"a collection of memories. Memories themselves might just be marked down files. Organized in this directory."*
- **Steering** (of dreaming) — telling the orchestrator/sub-agents "in your specific case, these are the kinds of things I think are important and relevant. These are the kinds of things that are not important and relevant."

## Named frameworks / concepts

### The four production principles for memory systems

1. **Versioning** — store versions, allow rollback, track what context the update was based on (which session, which transcript) and who/which agent made it.
2. **Concurrency (hash-based)** — before writing, the agent hashes the memory; drafts its edit; hashes again before commit. *"If those two things do not match then the agent cannot write it because it means that some update was made in the meantime."* Agent then re-drafts.
3. **Permissioning** — tier memory from "top level organizational wide knowledge" (often read-only) down to per-agent scratch pads (read/write). Guardrails prevent one agent corrupting org-wide context.
4. **Portability** — clean API so the curated memory is accessible across multiple products and systems.

### The context-engineering timeline (Anthropic's "do the simple thing that works")

`CLAUDE.md` → autonomous memory tools → Skills (progressive disclosure) → Filesystem-as-memory → (production guardrails) → **Dreaming** (out-of-band curation).

### Dreaming process

- Inputs: existing memory store + batch of transcripts (including tool calls and metadata, not just text exchanges)
- Orchestrator deploys a fleet of sub-agents to analyze transcripts
- Steering: humans tell the system what's important/not
- Orchestrator aggregates patterns, proposes memory changes
- Output includes **example transcripts** demonstrating the pattern and **prevalence stats** justifying the change
- Human reviews and accepts/rejects

### Two analogies the speaker uses

- **Bookshelf** — for progressive disclosure / skills.
- **School (students, teachers, head teacher)** — for dreaming: dedicated capacity for helping people learn, plus fleet-wide visibility to spot patterns and update the curriculum.

## Open questions / not covered

- The talk does not give a concrete spec for the markdown directory layout of a memory store beyond "marked down files. Organized in this directory."
- It does not benchmark dreaming quantitatively — claims of "better accuracy", lower cost, lower latency are stated as observations without numbers.
- It does not address adversarial robustness in detail beyond mentioning "maliciously injected" memories as a risk.
- It does not compare dreaming to existing eval-loop or RLHF practices.
- It deliberately avoids product-pitching until directly asked in Q&A (*"I was kind of coy in the talk because we're not allowed to make product transactions"*), at which point it points to Anthropic's memory and dreaming APIs via Claude Managed Agents.
- The Q&A on permissions across enterprise users gets a high-level answer ("you decide exactly which session transcripts to attach") but does not detail concrete mechanisms.
- The "reinventing databases" question gets a philosophical answer ("threading the needle") but no concrete guidance on when to use a real database vs the markdown approach.
- The talk does not cover real-time / low-latency inference constraints, cost ceilings for dreaming, or how often dreaming should run.
