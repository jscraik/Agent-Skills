# Outline — Built for Humans. Now Agents Are Here.

## Speaker

**Dana Lawson**, Chief Technology Officer at Netlify. Leads Engineering, Product, and Design. Previously at GitHub, Heptio, and New Relic. Two-plus decades of leadership experience; describes herself in the talk as having been "a software developer builder QA... since the 90s." Self-described "AI overlord" friend; close personal anecdote about her friend Toria runs through the talk.

> ⚠️ The verbatim transcript has **no per-speaker labels**. The MC's intro garbles "Dana" as "Dan Austin." Participants in the transcript:
> - The **MC** (unnamed) — opens and closes the session, manages Q&A.
> - **Dana Lawson** — the speaker (the vast majority of the transcript).
> - **Audience member #1** — asks about the 500M apps / environmental impact / what to build.
> - **Audience member #2** — asks about accountability when abstractions hide what's underneath.
>
> Other names mentioned (not present): **Toria** (Lawson's friend, the worked example), **Matt Biemann** (Lawson's boss; credited with coining "agent experience"), **Jeremiah** (credited with coining "developer experience" in 2012 — surname garbled in transcript as "leafed Spotify"), **"guy"** (refers to a previous speaker whose talk Lawson references).

## Abstract (as provided by user)

> Netlify was built around a human loop: a developer pushes code, scans the build logs, checks the deploy preview, decides it's good. Every part of the platform — the CLI, the API, the branch workflow — it was designed assuming someone was paying attention. Then agents started driving it. And things broke in unexpected ways.
>
> Agents don't scan logs — they need structured, actionable signals or they retry blindly. Deploy previews designed for human eyeballs don't tell an agent whether the result is correct. CLI output written for readability becomes noise when a machine is parsing it for intent. The branch workflow that feels intuitive to a developer becomes an ambiguous decision tree for an agent with no intuition.
>
> This talk is about what Netlify's platform revealed when agents came to work on it — and what Agent Experience (AX) means in practice: redesigning the surfaces, signals, and feedback loops that platforms expose so that humans and agents can build together without humans becoming the bottleneck.

## Thesis (synthesis)

The builder persona has expanded beyond developers — agents now let "anybody" (therapists, teachers, students) build real applications. When Netlify redesigned its surfaces (build logs, CLI, APIs, deploy previews) so agents could drive them, **the same changes also made the platform better for human developers** — the "AX paradox." Lawson's prescription: move from APIs to capabilities, from request/response to event-driven, and make architecture legible to agents (via "blueprints"), all wrapped in three trust primitives (sandbox, human-in-loop, audit/rollback). Code is no longer the scarce resource — **taste and judgment** are.

## Section TOC

| Section | Summary | Approx. line range in `transcript.md` |
|---|---|---|
| §1 MC intro | Brief intro and welcome | 5–15 |
| §2 Opening + premise: builder persona has expanded | "We ain't precious no more" — IDC's 500M apps stat, English as the strongest programming language | 16–60 |
| §3 The Toria story (part 1) | Lawson's massage-therapist friend trying to build, hitting `git` as the first wall | 61–110 |
| §4 The AX paradox introduced | Designing for agents made the platform better for humans too | 111–150 |
| §5 Coining AX | UX (2012, "Jeremiah"), DX, now AX (Matt Biemann); the three are collapsing | 151–185 |
| §6 The current AI-coding landscape | Claude Code, Cursor, v0, Bolt, Lovable, Copilot agents, "software factory" | 186–220 |
| §7 Shift 1 — specs to intent | From PRDs/Jira to prompts; "agent runners" at Netlify | 221–250 |
| §8 Shift 2 — sequential handoffs to shared creation | Designers in code, engineers validating architecture, everyone participates | 251–285 |
| §9 Shift 3 — passive CI to autonomous development loops | Agents generate tests, diagnose failures, open PRs; deploy previews bring humans back in | 286–325 |
| §10 Worked example: redesigned build logs | Structured machine-readable error codes alongside human text — clearer for both | 326–360 |
| §11 Legacy systems & three architectural shifts | APIs → capabilities; request/response → event-driven; tribal knowledge → legible (blueprints) | 361–445 |
| §12 Trust primitives | Sandbox execution, human-in-loop by default, audit + rollback | 446–480 |
| §13 Organizational impact | "Build it yourself"; engineering shifts to guardrails, skills, recipes, context | 481–510 |
| §14 Takeaways | Four takeaways: builder persona expanded; legacy must evolve; trust foundational; ship structured errors / events / blueprints tomorrow | 511–545 |
| §15 Closing: why it matters | Code no longer scarce — taste and judgment are; back to Toria; netlify.com/ax | 546–585 |
| §16 Q&A 1 — 500M apps / environment | Bitter truth about obsolescence; engineering responsibility for compression, etc. | 586–620 |
| §17 Q&A 2 — accountability under abstractions | Push/pull; Netlify takes accountability for hobbyists; control planes / policy engines for enterprises | 621–665 |

## Terminology glossary (Lawson's actual framings)

- **Agent Experience (AX)** — "the practice of designing where humans and agents collaborate seamlessly." Not just "making API calls agent friendly" — "you really do have to rethink the entire stack." Coined by Matt Biemann.
- **The AX paradox** — "when we designed our platform to work better for agents serving these new builders it got better for developers too."
- **Builder persona (expanded)** — "the person our platforms were built for are no longer just developers... therapists teachers small business owners students people in line at the store building experiences on their phone."
- **Software factory** — "this is not a new concept... but now with agents we can actually go and implement those software factories to go and just run."
- **Agent runners** (Netlify) — "an agent now or a harness takes the intent generates the code that output moves immediately into real engineering workflows."
- **Autonomous development loops** — "Agents don't just write the code they're participating in the entire infrastructure life cycle. They're generating the test detecting fall failing previews analyzing build blocks proposing fixes open PRs."
- **Capabilities (vs APIs)** — "intent level operations. Create a site... deploy repository. Provision edge compute. These are capability agents can reason about."
- **Blueprints** — Netlify's "system of record... yes this is skills, context and recipes. Think of it as the plaud mark number five agents indeed. The architecture decision records all design so coding agents understand the system for they make the changes."
- **Harness** — colloquial term for agent CLI / IDE tooling (Claude Code, Cursor, etc.); "I'm sure the name is going to change many many times."

## Named frameworks / concepts

### The three architectural shifts (legacy → agent-native)

1. **APIs → capabilities** — from REST endpoints to "intent level operations" agents can reason about. Netlify supports "both modes: traditional rest for existing integrations and capability based interfaces for agent interactions." Also extended to the CLI (the old "y/n/next parameter" flow doesn't work for agents).
2. **Request/response → event-driven** — "Traditional APIs are full based [pull-based]... agents have to pull guest retry. AI navy [native] systems expose events... deploy started. PR created agents subscribe to these events and act autonomously."
3. **Tribal knowledge → legible architecture** — eliminate the "slack thread from 2022 in an undocumented terraform module" problem; encode system understanding in **blueprints** so agents can operate safely.

### Three trust principles ("we have three principles we follow now five first")

Note: Lawson says "three principles... now five" but enumerates three:
1. **Sandbox execution** — "agents can't escape their sandbox and access resources they're not granted."
2. **Human-in-loop by default** — "the agent builds the human approves."
3. **Audit + rollback** — "every agent action is logged... we still have to have a system of records roll back."

### Three software-lifecycle shifts

1. Specs → intent (PRDs/Jira → prompts).
2. Sequential handoffs → shared creation (PM/design/eng/QA/DevOps relay → everyone collaborating with agents).
3. Passive CI pipelines → autonomous development loops.

### Concrete surface redesigns mentioned

- **Build logs**: human narratives → "mid structure machine readable error codes alongside that human text."
- **Deploy previews**: "give agents clear past fall [pass/fail] signals" while still letting humans visually inspect.
- **CLI**: redesigned away from interactive y/n prompts that block agents.
- **APIs**: dual-mode (REST + capability-level).

## Open questions / not covered

- Specific schema or format of Netlify's structured error codes (mentioned but not shown).
- Exact contents/template of a Netlify "blueprint" file (described conceptually only).
- How agent runners are isolated/sandboxed at the infrastructure level (named but not detailed).
- Pricing, business model, or rollout timeline for AX-mode Netlify features.
- Comparison to other vendors' agent-platform offerings beyond a name-check list.
- Any quantitative results / benchmarks of the AX redesign.
- Specifics of the "control plane" / "policy engine" for enterprises (mentioned briefly in Q&A 2 as work in progress).
- How agents handle multi-step workflows that span services Netlify doesn't own.
- Security model for agent-deployed code beyond the three trust principles.
- What happens when agents and humans disagree on a deploy decision.
