---
title: Agent Skills Kit Intent, Product Thesis, And Moat
status: draft-for-review
date: 2026-05-07
audience: Codex agents
primary_moat: agent-memory-with-proof
---

# Agent Skills Kit Intent, Product Thesis, And Moat

## Why This Document Exists

This document captures what a future Codex agent should understand about this
repository before it changes code, docs, runtime projections, skills, plugins,
or governance policy.

The short version: this repo is not merely a collection of prompt files. It is
trying to become an agent capability control plane: a local, governed way to
teach coding agents how Jamie's work actually works, keep the visible context
small, route intent into the right workflow, and prove that the workflow changed
agent behavior.

Future agents should read this as product intent, not just documentation. The
implementation can change, but this north star should stay stable unless Jamie
explicitly replaces it.

## What Is Certain From The Repo

The repository identifies itself as **Agent Skills Kit**: a governed system for
authoring, validating, discovering, and syncing Codex skills, operator docs, and
agent workflows.

The repo's public promise is:

> Teach your coding agents how your work actually works, then prove they
> remembered.

That promise is supported by repeated source-of-truth surfaces:

- `README.md` describes the repo as an agent capability control plane for Codex
  and AI coding agents.
- `Docs/product/agent-capability-control-plane.md` defines four outcomes:
  remember workflows, keep context small, prevent drift, and prove quality.
- `UBIQUITOUS_LANGUAGE.md` defines canonical vocabulary around canonical skill
  sources, runtime projections, generated command handles, workspace sync, user
  sync, and visible runtime surfaces.
- `Docs/agents/14-path-ownership-boundaries.md` defines a three-plane model:
  product plane, factory plane, and runtime plane.
- `Docs/agents/16-agent-operating-contract.md` makes `./bin/ask` the public
  command interface for agents.
- `Infrastructure/bin/ask` and `Infrastructure/scripts/lib/ask/**` implement a
  namespace-first CLI for repo, skills, runtime, plugins, evals, graph, mcp,
  wiki, and workouts.
- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py` controls the
  visible runtime surface, hidden lanes, root skill-set names, system bridges,
  and projection modes.
- `Infrastructure/scripts/lifecycle-and-sync/command_surface.py` implements the
  generated `$handle` contract and explicitly states that generated command
  handles are runtime pointers, not canonical skill sources.

The live repo health surfaces also confirm the control-plane direction:

- `./bin/ask skills list --json --robot` currently exposes a compact visible
  surface made of root routers plus selected direct capabilities.
- `./bin/ask skills handles --json --no-handles` reports a passing command
  surface with 93 generated command handles.
- `./bin/ask repo doctor --json --robot` composes repo status, projection sync,
  catalog parity, runtime budget, command handles, and repo surface diagnostics
  into one agent-facing payload.
- Runtime budget currently passes with 10 default-visible root entries and no
  policy violations.
- The doctor also reports catalog parity drift and large repo-surface diagnostic
  debt, which means the repo's own quality gates can identify when its
  operating surfaces fall out of alignment.

## What The Repo Is Really Trying To Do

The core idea is to make agent behavior governable.

Most agent instructions fail because they are too scattered, too long, too
implicit, or too dependent on a model remembering prior conversations. This repo
is an attempt to turn that messy operator knowledge into a system with:

- canonical source files for durable workflows;
- generated runtime projections for Codex and agent runtimes;
- small router skills that keep the always-loaded surface manageable;
- generated command handles so Jamie can say `$autofix`, `$context7`, or
  `$he-work` and get a real workflow rather than a vague prompt;
- validation that catches drift between source, generated surfaces, docs, and
  runtime visibility;
- outcome proof that distinguishes "this skill exists" from "this skill made an
  agent do better work";
- closeout commands that prevent agents from claiming completion without fresh
  evidence.

The strongest product loop is:

```text
user goal -> repo health -> candidate capability -> explanation -> proof -> sync/closeout
```

That loop is more important than any individual skill. If the repo keeps this
loop sharp, the project becomes a serious local operating layer for agent work.
If the repo loses this loop, it becomes a large and impressive pile of
instructions.

## The Agent-Native Architecture

The architecture is agent-native in a real way.

It gives future agents the things agents need most:

- a stable entrypoint: `./bin/ask`;
- a robot mode: `--json --robot`;
- machine-readable envelopes with status, metadata, data, telemetry, and
  errors;
- one-next-command guidance;
- explicit blocker classification;
- source/projection/runtime ownership boundaries;
- handles that are cheap to mention and resolve;
- validation commands that reflect the repo's own rules;
- vocabulary that translates Jamie's terse phrases into repo-native actions.

The three-plane model is especially strong:

- **Product plane:** canonical skill and plugin content under `Skills/**` and
  `Plugins/**`.
- **Factory plane:** sync, projection, graph, validation, installation, and
  command-surface mechanics under `Infrastructure/**`.
- **Runtime plane:** generated `.agents/**`, `.skillsets/**`, plugin caches,
  and user runtime links.

That separation is the backbone of the project. It is what lets an agent know
where to edit, where not to edit, what to regenerate, and what to prove.

The generated command-handle design is also strong. It solves a real Codex
problem: a user wants terse, memorable handles, but the full workflow bodies are
too expensive to expose all the time. A generated handle gives the model a
small invocation target while preserving the full workflow in canonical source.

## My Blunt Product Take

This is a strong idea with too much surface area.

The project is valuable because it attacks one of the hardest problems in agent
work: agents forget how a person or organization works. The idea of turning
operator knowledge into governed, validated, proof-backed skills is compelling.
The repo already has more agent-native design than most agent tooling: it has
machine-readable commands, projection boundaries, runtime budgets, command
handles, validation, evidence surfaces, and a vocabulary layer.

The weak point is not ambition. The weak point is focus.

Right now, the repo sometimes reads like three products sharing one checkout:

1. A skill authoring and publishing kit.
2. A local Codex runtime control plane.
3. A broad knowledge/evidence/workout/wiki/governance operating system.

Those may eventually belong together, but the first-read product is harder than
it needs to be. A future agent can find the correct path, but it has to push
through many adjacent surfaces before the core loop becomes obvious.

If this is meant to be Jamie's moat, the moat is not "many skills." The moat is:

```text
Agents reliably remember high-value workflows and prove the workflow improved
their behavior on real work.
```

Everything else should earn its place by strengthening that sentence.

## Is It Pragmatic?

Yes, but it is pragmatic in the engineering sense, not yet in the product sense.

It is pragmatic because it encodes things agents actually need:

- command wrappers instead of ad hoc shell spelunking;
- structured JSON for machine consumers;
- sync commands instead of hand-edited runtime projections;
- validation gates instead of trust-me docs;
- explicit policy identities and drift checks;
- small visible surfaces instead of loading every skill body.

It is less pragmatic where there are too many overlapping ways to understand or
prove the same thing. For example, a new agent may see repo doctor, repo status,
doctor-catalog, repo surface, runtime budget, command handles, closeout, skill
proof, skill prove, workouts, evals, wiki, and memory. Each may be justified,
but the product needs a clearer "start here, then this, then stop" path.

The current golden-path commands are the right pragmatic direction. The repo
should double down on them and reduce the need for agents to know the internals.

## Is It Well Designed?

The core is well designed. The outer rings need pruning.

Strong design choices:

- `./bin/ask` as a single public entrypoint.
- Namespace-first commands instead of top-level command sprawl.
- `--json --robot` as a first-class agent contract.
- Generated command handles that keep invocation small.
- Explicit separation of canonical source from generated runtime surfaces.
- Runtime budget validation.
- Repo doctor and closeout concepts.
- Skill audit, proof, sync, resolve, and explain flows.
- Ubiquitous language for ambiguous operator terms.

Design risks:

- The repo has high surface-area gravity: every solved problem tends to add a
  new command, doc, artifact type, or skill.
- Some proof language still risks conflating reachability, structural quality,
  and real outcome proof.
- The artifact and historical evidence areas are large enough that they can
  obscure the canonical product path.
- Plugin, skill, and harness concerns can blur unless the three-plane ownership
  model is enforced hard.
- The visible product story is still more obvious to someone who already knows
  Jamie's operating style than to a cold agent entering the repo.

## What Would Make It More Useful

Make the repo answer five agent questions with almost no context:

1. Can I work safely here?
2. What capability matches this task?
3. How do I use that capability?
4. What proof exists that it works?
5. What must pass before I say done?

The README already names these commands. The implementation should keep making
them the product:

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills prove <handle> --json --robot
./bin/ask repo closeout --changed --json --robot
```

The more these commands compose underlying details, the less future agents need
to memorize the repo's internal topology.

Useful next improvements:

- Make `repo doctor` the unavoidable first stop for agents and docs.
- Make `skills improve` return one primary recommended capability, not a buffet.
- Make `skills explain` include "when not to use this" and "what to run next."
- Make `skills prove` clearly separate reachability, quality, and outcome proof.
- Make `repo closeout --changed` infer the focused validation lane and sync
  needs from the actual diff.
- Add a short "agent first five minutes" doc generated from live command output.
- Keep command output small enough that an agent can use it without summarizing
  itself into mistakes.

## What Would Make It More Compelling

The compelling product story is not "write skills." It is "stop agents
forgetting."

The repo should make that emotional and operationally concrete:

- Before: agents ignore project-specific rules, choose the wrong workflow,
  over-edit generated files, miss validation, and claim done too early.
- After: agents ask `repo doctor`, route to the right capability, load only the
  needed workflow, produce exact evidence, and close out honestly.

That is the story worth repeating in the README, product docs, generated
onboarding, and root skill surfaces.

The project becomes more compelling when it shows before/after proof for real
agent behavior:

- a PR-review skill that caught findings a generic agent missed;
- a sync/projection skill that prevented runtime drift;
- a closeout command that stopped a false completion claim;
- a docs skill that repaired stale instructions from live command evidence;
- a harness skill that converted a messy repeated request into a reusable
  workflow.

Those examples are stronger than catalog size.

## What Would Make It More Intuitive For Humans

Humans should not need to understand projections, command surfaces, rooted
manifests, visible flat skill names, hidden lanes, and policy identity before
they can benefit.

Make the human front door this simple:

```text
Tell ask what you want agents to get better at.
It recommends one capability.
It shows the proof.
It tells you the next command.
```

Human-facing improvements:

- Add a short `./bin/ask repo onboard --profile human` output.
- Keep README product copy centered on agent memory and proof, not catalog
  mechanics.
- Use examples that start with Jamie-style natural language, then show the
  exact `ask` command that handles it.
- Make "skill exists" versus "skill is available to Codex" visually obvious in
  docs and command output.
- Expose a small "top workflows" page instead of expecting humans to browse all
  skills.

## What Would Make It More Intuitive For AI Coding Agents

Agents need fewer choices and stronger stop signs.

Agent-facing improvements:

- Every primary `ask` command should return exactly one recommended next
  command unless there is a real ambiguity.
- Every blocker should include one exact fix command or one exact file to read.
- Every generated surface should say "do not edit me" and point to the canonical
  source.
- Every skill explanation should include the smallest validation command that
  proves the changed surface.
- Every closeout should say whether sync is needed, whether generated files are
  expected, and whether commit readiness is blocked.
- Every proof payload should say whether it is reachability proof, quality
  proof, or outcome proof.

The agent-native ideal is that a new Codex thread can run:

```bash
./bin/ask repo doctor --json --robot
```

and then follow `next_command` until the repo itself has guided the agent into
the correct lane.

## What To Cut If Agent Memory Plus Proof Is The Moat

Cut anything that does not make agents remember better, choose better, or prove
better.

Specific cuts or hard constraints:

- Cut catalog-size bragging as a primary value prop. Catalog size is evidence of
  effort, not proof of utility.
- Cut duplicate proof paths that cannot explain whether they prove
  reachability, structure, quality, or outcome.
- Cut top-level command growth unless telemetry or baseline friction proves a
  namespace command is not enough.
- Cut hand-maintained docs that repeat live command output without being
  generated or validated.
- Cut any runtime projection editing path that bypasses canonical sources.
- Cut stale artifacts from the primary browsing path. Historical evidence can
  exist, but it should not compete with the current operating contract.
- Cut weak skills that do not encode a repeatable, high-value behavior.
- Cut broad router language that gives agents too many adjacent choices.
- Cut "maybe useful someday" skill categories until they have realistic
  scenarios and outcome proof.
- Cut proof claims based only on structural audits. A passing audit means the
  package is shaped correctly; it does not mean the agent became better.

The harshest version: if a skill cannot show a realistic scenario where it
changes agent behavior, it should be latent, experimental, or removed from the
primary product story.

## What To Keep At All Costs

Keep these even if the repo is simplified:

- `./bin/ask` as the public agent entrypoint.
- `--json --robot` as a machine-readable operating contract.
- The three-plane ownership model.
- Canonical source versus runtime projection separation.
- Generated command handles as small invocation pointers.
- Runtime budget enforcement.
- `repo doctor`, `skills improve`, `skills explain`, `skills prove`, and
  `repo closeout`.
- Ubiquitous language for translating Jamie's intent into repo-native actions.
- Validation that reports exact blockers and next commands.
- Outcome proof as a first-class concept.

These are the durable pieces of the moat.

## Guidance For Future Agents

Before changing this repo, assume the user's real goal is not "edit a skill
file." The real goal is usually one of:

- make a repeated workflow durable;
- make a skill visible and routable;
- repair drift between canonical source and runtime projection;
- prove a capability works;
- reduce agent confusion;
- turn a repeated operator request into a validated command or skill.

Start with:

```bash
./bin/ask repo doctor --json --robot
```

Then follow the repo's command surfaces rather than guessing. Edit canonical
sources, regenerate projections through repo wrappers, and validate the smallest
surface that proves the change.

When writing docs or code, prefer language that preserves this core idea:

```text
Agent Skills Kit helps Codex agents remember high-value workflows and prove
they remembered through source-backed, runtime-visible, validated capabilities.
```

## Open Questions For Jamie

These are product questions the code cannot answer with certainty:

- Should the public product be sold as a personal/local Codex operating layer,
  or as a reusable open-source skill control plane for teams?
- Should plugin marketplace distribution remain a first-class product goal, or
  should it be secondary to Jamie's own local agent memory system?
- How much historical evidence should remain in this repo versus a separate
  archive or indexed memory store?
- What is the minimum proof threshold for promoting a skill into the visible
  runtime surface?
- Should weak or rarely used skills be removed, hidden, or kept as latent
  examples?
- Which five workflows are the canonical demos of the moat?

## Current Evidence Snapshot

Fresh evidence gathered on 2026-05-07:

- `./bin/ask repo doctor --json --robot` ran and reported a blocking catalog
  parity drift: `count_mismatch`.
- The same doctor run reported runtime budget as passing with
  `default_visible_count: 10` and `violation_count: 0`.
- The same doctor run reported command handles as passing with
  `handle_count: 93`.
- The same doctor run reported repo-surface diagnostic debt with
  `blocking_findings: 4543`.
- `./bin/ask skills list --json --robot` ran and returned root routers plus
  direct agent-ops capabilities in the default visible surface.
- `./bin/ask skills handles --json --no-handles` ran and returned status
  `pass`, `handle_count: 93`, and no violations.
- `find Skills Plugins -path '*/SKILL.md' | wc -l` reported 182 `SKILL.md`
  files across canonical skills, plugin skills, and nested plugin fixtures.

This snapshot matters because the repo's own state supports both sides of the
critique: the control-plane architecture is real, and the surface area is still
too large to be intuitively product-shaped without stronger golden-path
compression.
