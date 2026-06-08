# Outline — The beginner's guide to training AI on your own code

## Speaker

**Brian Douglas** ("bdougie" / "bw" on the internet). Founder of **Paper Compute** ("distributed systems primitives for AI agents"). Previously founded **Open Sauced**, which joined the Linux Foundation in 2024. Background in finance ("My background is finance. I went to school for it"). Self-describes as an "elder millennial" and a front-end developer by trade. Previously worked at a company called **continue** where they trained a model called "next edit" using SFT — this is where his fine-tuning experience comes from.

## Abstract (as provided by user)

> Every AI agent call generates training data. Most teams throw it away. Tapes is an open source telemetry proxy that intercepts LLM API calls and builds a content-addressable Merkle DAG of every conversation turn, with zero instrumentation required. […] We built this pipeline by running parallel agents speedrunning Gameboy games. […] The result: a closed loop where your agents generate the data that trains the next version of the model they run on. No external training data. No third-party model outputs. Your code, your agent traces, your model.

The talk delivered is a looser, more narrative version of this abstract — Brian explicitly says "This is not a workshop, so don't expect to, like, step one, step two, step three. I'm going to just share my journey of how I learned this."

## Thesis (synthesized)

Every agent session you run produces telemetry that is currently being thrown away (Claude Code stores sessions for 30 days then deletes them). If you capture those sessions with a tool like **tapes**, you can (1) feed past context back into future runs to build a self-healing loop, (2) extract reusable **skills** from the traces, and (3) optionally fine-tune small local models on the cleaned data. Brian validated this by speedrunning Pokémon Red with 10 parallel agents, then applied the same machinery to his own codebases ("super agents" / "sweeper agent"). His strong recommendation is the first two steps; the fine-tuning step (especially DPO) is expensive and only worth it for bespoke cases.

## Section-by-section TOC

| # | Section | Summary | Approx. location in `transcript.md` |
|---|---|---|---|
| 0 | MC intro | The MC welcomes the audience, asks people to scoot in, mentions sessions have moved rooms, introduces Brian. | Lines 1–18 |
| 1 | Brian's intro & disclaimer | Self-intro as bdougie/bw, mentions Paper Compute, says he has "nothing to sell" — this is open source. | Lines 19–34 |
| 2 | Pokémon case study setup | Why Pokémon Red on Game Boy: validating tapes at scale via 1000-turn sessions, speedrunning to get the first Pokémon. | Lines 35–58 |
| 3 | The Pokémon agent setup | pygame-boy + Claude Code as harness, headless emulation, screenshots every 10 turns, 10 parallel agents. | Lines 59–86 |
| 4 | The "politely hallucinating" failure | Agent wouldn't progress because it never learned to talk to NPCs (Mom). Self-imposed rule: no internet lookup. | Lines 87–104 |
| 5 | observation.md & observer-state.json | Markdown observations written by the agent at end of session ("journal" analogy); JSON for game-state things like the 7-second door cooldown. | Lines 105–138 |
| 6 | Kafka + anomaly detection on the Pokémon loop | 10 sims publishing to Kafka, anomaly detection catching things like "not going through doors" and HP/berry battle nuance. | Lines 139–158 |
| 7 | From Pokémon to codebases | The same nuance-discovery applies to 5–20 year old codebases; we currently "shoot from the hip" every 5-hour session without learning. | Lines 159–178 |
| 8 | Super Agent & Sweeper Agent | Applying the same setup to his own code: 10 parallel agents on separate VMs (steros) fixing lint, writing docs, generating context. | Lines 179–210 |
| 9 | The data-value argument | Anthropic/Cursor are paying $10M+ for training data deals. "You should be extracting value." Use cheaper models (Haiku) for bespoke at-scale work. | Lines 211–240 |
| 10 | Aside: auto-research / Qwen 3.6 / unbanned from Claude | He got blocked by Anthropic for running 10 parallel super-agents; got unblocked in ~12 hours after a blog post. Same week, Qwen released auto-research. | Lines 241–270 |
| 11 | Tapes architecture: Merkle DAG of sessions/turns | Every commit/session/turn is content-addressed. Session = from `claude` to `/clear` or close. Built by his co-founder. | Lines 271–305 |
| 12 | "Check the tapes" skill | Use stored sessions to reconstruct *why* something was done 6 months ago; he used it to recover prompts for designer wireframes. | Lines 306–340 |
| 13 | TapeDeck UI | CLI + visualization of session probability ("tape deck" — "tape being the most durable form medium"). Shows tool calls and skill invocations. | Lines 341–365 |
| 14 | Generating skills from tapes | Use a small/cheap model (he uses GPT-4o) to draft skills from filtered tape sessions; recommends human review. | Lines 366–385 |
| 15 | The book analogy for SFT | Model = book; SFT = writing skills in the margins. Used Qwen 4B, embedded his + 3 teammates' skills. Works for bespoke, not daily-driver. | Lines 386–425 |
| 16 | DPO: the Cliff Notes / Matthew McConaughey aside | DPO = "alright alright alright" — picks the best every time. Very expensive. Don't bother unless you're a researcher at Meta. | Lines 426–470 |
| 17 | Hardware results | 4070 RTX 24GB worked for SFT; needed 32GB so upgraded to 5090; DPO needed h100s (borrowed via an Nvidia friend); DPO on 4B = "not even worth it", on 7B = "go for it" but expensive. | Lines 471–495 |
| 18 | Wrap-up: the three steps | (1) Capture sessions, (2) Knowledge transfer via skills (multiplayer coding), (3) Harness/model freedom. Anthropic IPO mention. | Lines 496–525 |
| 19 | Q&A | One question on Codex support: works with Claude Code, Conductor, Ollama today; happy to add Codex if someone asks. | Lines 526–end |

## Terminology glossary

Definitions are Brian's own framing, paraphrased only when no clean verbatim exists.

- **Tapes / tapes.dev** — "an open source telemetry proxy that intercepts LLM API calls" (from abstract); in the talk: "takes that dev as a way to capture aging sessions" [tapes.dev — captures agent sessions]. CLI-based, no signup, runs on your machine, stores raw data in (originally) SQLite, moving to Postgres for concurrency.
- **Steros** — "a runtime for agents. So like a sandbox would actually battery included." Used to give parallel agents separate VMs.
- **Session** — "every time you talk tight clawed codex, olama, whatever, that's your session. […] When you do clear that's a new session. When you close it, you start again that's a new session."
- **Turn** — A single round within a session. Pokémon target was "a thousand turns per session".
- **Merkle DAG** — Brian frames it via git: "every git commits sits within a bag. So you can go and have hash right your commitments. And they have these branches."
- **Observation memory (observation.md)** — Markdown notes the agent writes at the end of a session, framed via the journal analogy: "the end of the day, you open up your journal and you're like, man, I saw this amazing talk…". Concept credited to "a master blog post observational memory."
- **Observer state (observer-state.json)** — Structured machine-readable state, e.g. "up down left right" for Pokémon, or the 7-second door cooldown rule.
- **Check the tapes (skill)** — A skill Brian built: "I can go back six months and say check the tapes. Like how do we get here?"
- **Super agent / Sweeper agent** — Applying the parallel-agent setup to his own codebases. "Super agent I thought would be funny to say that out loud sweeper agent. But it goes to our code base in this sweeps there." Sweeper Agent is open source.
- **SFT (Supervised Fine Tuning / "specialized fine tuning")** — "as if you were to write your skill in the margins of the book. So you're now adding extra context and extra notes into the book." Same technique Cursor used for Composer 2 and continue used for "next edit".
- **DPO (Direct Preference Optimization / "right preference optimization")** — "if you have two choices, it will always pick the best choice no matter what." Cliff Notes analogy: "you will get the cliff note and then you'll take the test." And: "All it does is pick the rights selection every single time. All the time." (Matthew McConaughey "alright alright alright" reference.)
- **Anomaly detection (in the pipeline)** — Catches both failures *and* successes: "if you have 26 skills and vocations out of like 10 sessions like there's probably something good happening there."

## Named frameworks / concepts

1. **The three-step wrap-up pipeline:**
   - Step 1: **Capture sessions** ("if you leave this room today, go look at that clause sessions and start using them")
   - Step 2: **Knowledge transfer** via skills ("multiplayer coding session" — transfer knowledge between solo-player agents/machines)
   - Step 3: **Harness/model freedom** (you can swap Claude → Codex → Cursor, use cheaper models where appropriate)

2. **The Pokémon validation loop:** 10 parallel agents × 1000 turns × screenshots every 10 turns → recorded to tapes → observations → observer-state → self-healing loop. Validated speedrunning to get the first Pokémon from Professor Oak.

3. **The book analogy for fine-tuning:** Model = book containing co-located ideas. SFT = margin notes (your skills embedded). DPO = throwing out the book and reading Cliff Notes instead.

4. **The cost/value argument:** Claude Code stores sessions for 30 days then deletes them. Anthropic/Cursor sell training-data access for millions ("Cursor currently is in a deal for $10 million at minimum with SpaceX"). Therefore capture and own your own session data.

## Open questions / Not covered

- **Codex support for tapes** — Brian explicitly says: "today works for, it does not work for codecs. […] We're more than happy to make it work for Codex if someone needs to say they need it." So as of the talk, no Codex support.
- **Concrete fine-tuning hyperparameters** — Brian mentions Qwen 4B / Qwen 7B, QLoRA (in abstract), unsloth, PyTorch, but does not walk through specific configs.
- **Multi-machine / team data syncing** — He gestures at "multiplayer" coding but says "If you have a second machine, you're probably not transmitted data back and forth" — i.e. cross-machine sync is a gap.
- **Prompt sanitization / secrets handling** — He says "what if you didn't put sensitive information in your prompts? But this is all on you. […] So don't put secrets in your clock code. But we'll get there." Explicitly an open area.
- **Scorecard / evaluation of generated skills** — He says he'd "love to talk to the Tessl people about that next" — not solved in the talk.
- **DPO at scale on consumer hardware** — He confirms it doesn't work; needed h100s borrowed from a friend at Nvidia.
- **Whether the fine-tuned small model is a daily-driver replacement** — He is emphatic: it is not.

## Source transcript artifacts to be aware of

The speech-to-text frequently garbles key terms. When quoting verbatim, preserve the artifact and clarify in brackets. Common substitutions seen:

- "tapes" ↔ "takes" / "taste" / "Tess" / "Tessl" (note: Tessl is a real separate company Brian references near the end re: scorecards — don't conflate)
- "Paper Compute" ↔ "PC"
- "Claude" / "Claude Code" ↔ "quad" / "clog" / "clogged code" / "cloud" / "clock code" / "crop code"
- "Codex" ↔ "codecs"
- "steros" ↔ "stereos"
- "Qwen" ↔ "Quin" / "Quinn"
- "Sweeper Agent" ↔ "super agent" (Brian himself jokes about this slip)
- "Open Sauced" ↔ not directly garbled but referenced as his prior company
- "bdougie" ↔ "bw" (both are real handles he uses)
