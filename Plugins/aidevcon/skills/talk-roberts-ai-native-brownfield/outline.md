# Outline — Stop Maintaining, Start Evolving (Katie Roberts)

## Speaker

**Katie Roberts** — Technical Director and AI-Native Engineering Specialist with 20+ years of experience in large-scale software delivery and organisational transformation. Focuses on the strategic evolution of engineering practices, helping teams adopt AI-native ways of working at scale in mature brownfield environments. Partners with senior stakeholders to introduce these practices pragmatically with a focus on measurable improvements and engineering excellence.

## Abstract (as supplied)

> The "AI-Native" dream is often sold as a greenfield paradise: starting from scratch with perfect prompts and zero technical debt. But for most engineers, reality is a mature "brownfield" estate, a highly successful product, with a complex codebase and a build pipeline held together by hope.
>
> In this session we re-examine AI Native Engineering practices as the engine for architectural reclamation.
>
> Drawing on real-world experience modernising complex legacy systems, I will demonstrate how to apply the Strangler Fig Pattern in an AI-native context. We will walk through the practical workflow of identifying high-risk areas in your codebase, using AI document functionality and creating test suites for undocumented code, and isolating legacy logic behind facades to facilitate a clean rewrite.
>
> Stop using AI to add to your technical debt. Learn how to use it to pay it down.

## Thesis (synthesised)

The delivered talk pivots from the abstract's Strangler Fig framing into a case study of building a ~350k-line Rust S3-compatible object store with AI, in months rather than years. Katie's argument: large AI-driven systems are achievable, but quality only survives if you (a) ground the AI against an **external test oracle** (real behaviour, not docs), (b) refuse to tolerate flaky tests despite the AI's training-data-induced laziness, (c) keep a human firmly in the loop as the QA conscience, and (d) lean on the type system and tracing to encode invariants tests can't reach. 100% test coverage is *not* the goal; lots of meaningful tests are.

## Section TOC

- **L1–L8 — Opening: infrastructure metaphor.** Roman road in East England as visual for what happens when infrastructure isn't maintained; introduces obsession with object storage and the MinIO situation.
- **L8–L20 — The experiment setup.** MinIO stopped maintaining their S3 clone; Katie tried to rebuild it in "a week" (became months). 350k lines of Rust. Couldn't read it, only half-knew Rust, would reverse-engineer by talking to AI. Wanted to test "can AI build huge complex things?"
- **L20–L30 — Goals and constraints.** Architectural opinions, security, performance, "real human in the loop", ambition to build things teams normally can't.
- **L30–L42 — Quality via testing; against 100% coverage.** Deming quote on quality. 100% coverage produces trivial tests and silly error-injection cases. 75% of codebase is tests; per-file coverage 75–100% — without obsessing over 100%.
- **L42–L60 — Test oracle pattern.** Using real S3 as oracle for 1500 tests. Recommendation: even for greenfield, write a trivial simple version first as oracle. Caveats: S3 eventual consistency forces retries; public APIs don't expose internal behaviour; **S3 documentation is mostly wrong in every detail** — trust the oracle, not the docs.
- **L60–L78 — Edge cases.** Found two repeatable 500 errors in S3 that Amazon clearly hadn't tested for. Edge cases as confidence signal. Katie finds edge cases by reading AWS docs sceptically; AI is *bad* at finding edge cases from docs but okay at obvious length-based ones (0, 1, 10001).
- **L78–L96 — Flaky tests with AI: the hard rule.** "Never have flaky tests with AI" — fix immediately. AI's training data says devs ignore flakes; AI will silently match AWS's flapping behaviour by editing your code back and forth. "AI is good at" fixing flakes if you make it. 5000 tests in 2 minutes; overnight repeated runs to find rare flakes.
- **L96–L108 — Asking AI for new kinds of tests.** Property-based testing surfaced issues. Periodically ask: "what tests would have caught this?"
- **L108–L120 — What tests can't find.** Architecture quality; sometimes race conditions; ongoing performance; security partially; anything you can't measure. Don't just chase coverage — think about what's *outside* the box. Build more testable interfaces (regrets not building management/reporting APIs for testability).
- **L120–L135 — AI-built tracing as debugging tool.** Hand-built tracing framework, not tied to production. Lets AI debug rare overnight failures from traces instead of guessing. "Big performance gaps" visible despite overhead.
- **L135–L150 — AI performance engineering.** Like human perf work — often makes it worse before better. Treat as cheap throwaway work. Comparison vs another S3 impl revealed they skipped fsync — don't chase performance against systems doing the wrong thing.
- **L150–L162 — Type system over tests for invariants.** TOCTOU-style double permission checks: instead of tracing, encode "authorized request" as a type that can't be re-authorized; gate functions on it. Eliminates whole class of tests.
- **L162–L175 — Security review with Codex.** Codex security reviews → check findings into repo → ask AI to review them. 3/4 valid. Periodic review sessions: "what tests would have caught these?" Reviews on whole codebase, not just PRs.
- **L175–L182 — Human in the loop philosophy.** "I view myself as part of the feedback loop." Deliberately avoids over-automating to stay responsible for quality.
- **L182–L200 — Lessons / closing.** Test oracle valuable. Copying existing things is honourable AI-vehicles tradition. Refactoring is enormous and constant — one week was +120k/-75k lines, including refactoring a single 43k-line file. Tests + refactoring = the convergence loop. Will open-source the code in ~a week once distributed system is finished.
- **L200–end — Q&A.** (1) Formal verification — not yet, looking at it next once distributed system runs, fascinated by the area. (2) The "tautology" risk of test oracles when you don't have an external one — Katie agrees, would build the oracle outside the repo as a "fixed, very done model."

## Terminology glossary (Katie's own definitions/usages)

- **Test oracle** — An independent reference implementation or system whose behaviour you treat as ground truth, so the AI cannot drift. For Katie this was real Amazon S3 (1500 tests run against it). Recommendation even for greenfield: "write it really, really simple version that's kind of trivial that basically has the same behavior that you can use as a test oracle."
- **Flaky test (in AI context)** — A test whose AI-induced failure mode is that the agent will either declare flakes normal ("training data says that developers never fix flaky tests, so we ignore them") or worse, *change the code* to match a flapping oracle ("AWS converges to truth over time... we'll just change the code to match again").
- **Human in the loop** — Katie's stance: "I view myself as part of the feedback loop. I have opinions and I'm here to find out what's going wrong... I've been not trying to automate things too much because I want to actually understand what's going wrong."
- **Hand-built tracing framework** — An AI-built tracing layer used purely as a debugging aid for the AI itself, not wired into production. Lets the agent reproduce rare bugs from captured traces.
- **Refactor week** — Periodic dedicated refactoring (one was +120k/-75k lines including a 43k-line single file) treated as a normal part of the convergence-on-quality loop, not as failure.

## Named frameworks / concepts introduced

- **Test-oracle-first development for AI** — copy or build a trivial reference, then build the complex version against it.
- **"Never have flaky tests with AI" hard rule** — non-negotiable, with overnight repeated-run infrastructure to find rare flakes.
- **Types over tests for invariants** — e.g. `AuthorizedRequest` type that gates downstream functions, eliminating TOCTOU permission-check tests.
- **AI-built tracing for AI debugging** — internal-only tracing the agent uses to reproduce and fix rare failures.
- **Periodic post-mortem test-design sessions** — feed security findings / failures back: "what tests should we have that would fix these?"
- **Refactor-as-feedback-loop** — refactoring weeks are how the system converges, not a sign of failure.

## Open questions / not covered

- **Strangler Fig Pattern.** Despite the abstract's promise, the delivered talk does **not** walk through the Strangler Fig pattern. The talk is a greenfield-reimplementation case study, not a brownfield strangulation walkthrough.
- **AI document functionality for undocumented code.** Abstract mentions this; talk does not cover it in any depth.
- **Isolating legacy logic behind facades.** Promised in abstract; not addressed in the delivered content.
- **Specific socio-technical / organisational adoption practices.** Despite Katie's bio focus, the delivered talk is highly technical, not organisational.
- **Formal verification results.** Katie says she's about to try this "next week" — no findings yet.
- **Distributed-system testing specifics.** She mentions she's mid-implementation; details deferred.
- **Cost / token economics** of running 5000 tests, overnight runs, large refactor weeks — not discussed.
- **Specific AI tooling stack** (which agent, which models) — not named beyond "Codex security" reviews.
- **Team-scale practices.** Talk is about Katie's solo experiment; doesn't directly address how a team applies the same loop.
