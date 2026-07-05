# Ryan Harness Principles

Use this reference for the reasoning behind agent-native repository improvements. It distills the pinned upstream Ryan/OpenAI harness source bundle into the principles needed for everyday audits.

## Core Thesis

The repository, tools, checks, docs, and runtime evidence form the harness around agents. The human role is to set intent, choose priorities, review outcomes, and improve the harness so agents can complete more of the job reliably.

## Principles

### Humans Steer, Agents Execute

Humans should spend attention on goals, acceptance criteria, taste, risk, and priority. Agents should handle implementation, tests, docs, validation, cleanup, and follow-through.

If the human repeats the same correction, treat it as a missing harness affordance rather than a one-off prompt failure.

### The Full Job Matters

A useful agent does not stop at changed files. It drives the change toward a verified result through checks, product paths, logs, artifacts, or another meaningful proof surface.

### Repeated Failure Becomes Harness

Convert repeated mistakes into tests, lints, scripts, validators, clearer docs, skills, better errors, or better CLI affordances.

One durable guardrail is stronger than repeating the same prompt text.

### Proof Beats Assertion

Final reports should name the evidence that mattered. If proof was not possible, state why and name the smallest harness improvement that would make it possible next time.

### Optimize For Agent Legibility

Agent-native repositories need predictable structure, explicit contracts, non-interactive commands, and failure output that points to the likely fix.

### Keep Solo Process Lightweight

Do not import heavyweight team ceremony by default. Add process only when it reduces repeated mistakes, speeds recovery, or improves proof.

## Do Not Import By Default

- mandatory PR ceremony for solo work
- branch-heavy workflows when direct guarded work is faster and recoverable
- large approval queues disconnected from actual risk
- security theater that does not match repo threats
- more skills or docs than an agent can reliably choose from
