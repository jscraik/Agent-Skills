# Outline — Vibe Coding: Is this really the best we can do?

## Speaker

**Dave Farley** — pioneer of Continuous Delivery; founder of Continuous Delivery Ltd
and the CD.Training school; creator of the Continuous Delivery YouTube channel;
co-author of the Reactive Manifesto; Duke Award winner for the open source LMAX
Disruptor project; author of *Continuous Delivery* and *Modern Software
Engineering*. Long-standing advocate of TDD, iterative development, continuous
integration, and high levels of automated testing in large-scale distributed
systems.

## Event context

Closing session of a conference day at what appears to be a Tessl-hosted event
(MC mentions Tessl office at King's Cross, "AI native DevCon"). Followed by a
party. Approx 30–40 minutes. No live Q&A — MC says "we don't actually have time
for questions".

## Abstract (as provided)

> It is clear that we are in the midst of a revolution in programming, whatever
> you think about AI's writing code, even if their development stops today,
> they will still change how programming works for good. … There are good reasons
> why Programming Languages have evolved to exist in the form that they do, and
> that natural languages, in important ways, represent a poor alternative. So
> what does the future bring, and what ideas look like they will give us some
> level of control over what we build in that future? What will programming look
> like?

## Thesis

Vibe coding with natural language is not enough because natural language lacks
the three properties (formal grammar, unambiguous intent, deterministic
execution) that make programming languages tools for thought, communication, and
machine instruction. AI coding accelerates the easy part of software development
and makes the hard parts — precise specification, verification, and
incrementalism — worse. The fix is to prompt AI agents with BDD-style executable
specifications written in problem-specific DSLs and verify the AI's output with
deployment pipelines: continuous delivery, reapplied to AI-driven development.
AI becomes "rather like the compiler" — a fifth-generation programming layer.

## Section TOC

| Section | Summary | Approx transcript line range |
|---|---|---|
| 1. MC intro | Conference housekeeping, introduces Farley | 1–15 |
| 2. Opening — what's durable | Farley positions himself as interested in durable practices despite the disruption | 16–35 |
| 3. Provocations | Lists ideas he's about to challenge: vibe coding, natural-language programming, "AI will write all the code", "no more junior developers", AI-generated tests | 36–55 |
| 4. What are tests for? | Tests as measurement; why AI-generated tests from existing code are a "dumb idea" | 56–95 |
| 5. What is a program for? | Rejects "sequence of instructions / algorithm / brilliant design" framings | 96–115 |
| 6. Three goals of programming languages | (1) organise our thinking, (2) communicate with other humans, (3) tell computers what to do | 116–140 |
| 7. Three techniques embodied in programming languages | (1) simple consistent grammar, (2) unambiguous expression of intent, (3) repeatable deterministic execution | 141–170 |
| 8. How natural language fails on each | Vague, ambiguous, non-deterministic, not version-controllable in a useful way | 171–220 |
| 9. Three problems AI programming creates | (1) how to specify what we want with precision, (2) how to confirm we got it, (3) loss of incrementalism | 221–270 |
| 10. The 12,000 lines/day anecdote | Verification can't keep up; theory-of-constraints bottleneck moves | 271–300 |
| 11. Past vs future — specification | Program was a precise solution; future program is a precise description of what we want, encoded as executable specifications | 301–340 |
| 12. Past vs future — verification | Executable specifications double as verification | 341–370 |
| 13. Past vs future — incrementalism | Same continuous-delivery practices, now applied to AI output | 371–400 |
| 14. Worked example | Flight-planning system built from vision → user story → examples → executable specs | 401–425 |
| 15. Conclusions | Natural language alone not enough; BDD-style DSLs the best alternative; AI ≈ compiler; fifth-generation programming; mentions N-able open-source project | 426–460 |
| 16. MC outro | Live-stream thanks, rail strikes, party logistics — NOT Farley | 461–end |

## Terminology glossary (Farley's own definitions)

- **Vibe coding** — "just chatting with the computer to express our needs"; Farley
  says this "alone is simply not good enough".
- **Tests (purpose)** — "our form of measurement … the equivalent of a carpenter
  having a tape measure in his pocket". Used to know we're doing the right things
  and that they remain right after change.
- **AI-generated tests (from existing code)** — Farley: "if the code is the only
  input, we can only verify that the code remains the same … mostly a dumb idea
  … a copper [cop-out] for people who … can't be bothered to state their goals".
  Useful for refactoring (behaviour-preserving change); not useful for development.
- **Three goals of a programming language** — (1) help us organise our thinking
  about a problem, (2) communicate our understanding with other programmers,
  (3) tell a computer what to do.
- **Three techniques embodied in programming languages** — (1) "a simple,
  consistent grammar", (2) "unambiguous expression of our intent", (3) "repeatable
  and deterministic in terms of execution".
- **Executable specifications** — BDD-style specifications that "both specify what
  we want and also verify that we got it". Take the form vision → user story →
  examples.
- **Problem-specific DSL** — "designing a domain specific language … for
  specifying what it is that we want from our software with a deal of precision".
- **Fifth-generation programming language / system** — Farley's framing of where
  this leads: "effectively what we're doing is we're … invoking a fifth
  generation programming language, a fifth generation programming system".
- **AI as compiler** — "AI assistance is rather like the compiler. We're not going
  to care for very much longer at all … about the code that it generates because
  we'll verify that we've got the results."
- **Incrementalism** — "high quality system development in software is always an
  incremental process of learning and discovery."

## Named frameworks / concepts

1. **The Three Goals of Programming Languages** — organise thinking, communicate
   with humans, instruct computers. Use as a lens to evaluate any new
   programming medium.
2. **The Three Techniques Embodied in Programming Languages** — formal grammar,
   unambiguous intent, deterministic execution. Natural language scores zero
   on all three.
3. **The Three Problems Programming-with-AI Presents** —
   (a) how to specify what we want with precision,
   (b) how to confirm we got what we wanted (verification),
   (c) how to retain incrementalism when the AI makes huge changes in one shot.
4. **Past vs Future of Programming** (three parallel slides) — moving from
   "program as precise solution" to "program as precise description of what we
   want, encoded as executable specifications".
5. **The Specification Pipeline** — vision → user story → worked examples →
   executable specifications → AI generates code → pipeline verifies (with some
   tests held back so AI can't game them).
6. **AI as Compiler / Fifth-Generation Programming** — we stop caring about the
   generated code itself, just as we stopped caring about compiler-generated
   assembly.
7. **Theory of Constraints applied to AI coding** — speeding up code generation
   just moves the bottleneck to verification and release.

## Worked example referenced

A **flight-planning system** Farley built (in a training course) using
vision → user story → examples as the AI prompt, producing a real working system.

## Open external references

- **N-able** — "open source project … that's worth a look. That applies this
  thinking and promotes this way of development." (Farley's recommendation.)
- **The Goal / Theory of Constraints** — Farley invokes this to explain bottleneck
  movement.
- **Andrej Karpathy** — Farley pushes back on a quoted Karpathy claim that "the
  programming language of the future is English": "I don't like that idea very
  much".
- **BDD (Behaviour-Driven Development)** — the style of executable specs Farley
  uses to prompt his AI.
- **Continuous Delivery** — Farley's own prior work; he positions the whole
  approach as CD applied to AI-driven development.

## Open questions / not covered

- **Specific tooling or vendor choices** for AI coding agents — Farley speaks
  generally about "my AI agent" without endorsing a specific product.
- **How to design a problem-specific DSL** in detail — he says "designing a
  domain specific language" but does not walk through the design process.
- **Concrete advice for junior developers** in this new world — he flags
  "sacking all junior developers" as one of his provocations but does not
  develop a detailed answer in the transcript.
- **The mechanics of "keeping some tests back"** so the AI can't game them —
  mentioned but not described in detail.
- **Cost / latency / token economics** of running large AI agents this way.
- **Security or governance specifics** beyond noting that security level is
  contextual (game vs bank).
- **Team / org structure implications** of this workflow.
- **What happens when the AI cannot satisfy the specifications** — failure modes
  not discussed.
- **Live audience Q&A** — none; MC explicitly says no time for questions.
