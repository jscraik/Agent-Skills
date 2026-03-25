---
date: 2026-03-24
topic: skill-lifecycle-scaffold-memory-program
source_ideation: docs/ideation/2026-03-24-open-ideation.md
---

# Brainstorm: Skill Lifecycle, Scaffold Quality, and Institutional Memory Program

## Summary

The repo should treat these three ideas as one coordinated program:
- establish lifecycle and ownership metadata as the control plane
- upgrade scaffold generators so new assets enter the system in a high-quality state
- create a `docs/solutions/` memory loop so shipped fixes and decisions become reusable knowledge

The recommendation is to anchor the program on lifecycle metadata first, then design scaffolds and memory capture around that model rather than launching three disconnected initiatives.

## Problem

`Agent-Skills` has reached the point where breadth is becoming a first-order operational challenge.

Observed repo signals:
- the skill surface is large and spans many domains and runtimes
- the repo already has strong validation, sync, and governance mechanics
- scaffolds still emit broad placeholder content that creates downstream cleanup
- the repo lacks the shared `docs/solutions/` layer some workflows already assume exists
- plans, brainstorms, scripts, and todos hold important context, but ownership, maturity, and lifecycle are not surfaced as a canonical model

The combined effect is that the repo is good at producing and validating assets, but weaker at answering:
- what is active versus experimental
- who is responsible for each skill or package
- what quality bar new generated assets should meet by default
- where solved problems should live so they can be reused instead of rediscovered

## Goal

Create one coherent operating model for the skill library so new assets are born cleaner, existing assets are easier to manage, and completed work leaves durable memory behind.

## Users

- maintainers deciding what deserves review, hardening, promotion, or retirement
- contributors adding or updating skills, plugins, and related docs
- agents navigating the repo and trying to follow the right lifecycle and quality expectations

## Approaches

### Approach A: Metadata-first program

Start by defining lifecycle and ownership metadata for skills and related packages, then make scaffolds and `docs/solutions/` conform to that model.

**Why it helps**
- creates a control plane before adding more automation
- gives scaffold outputs a clear target state
- ensures memory artifacts plug into the same lifecycle system instead of becoming an isolated docs layer

**Trade-offs**
- requires more up-front thinking than simply improving templates
- risks becoming abstract if not quickly tied to visible workflows

### Approach B: Scaffold-first quality push

Start by making scaffold outputs realistic and validator-clean, then layer metadata and memory capture on later.

**Why it helps**
- delivers a fast quality win
- reduces the visible placeholder debt contributors hit immediately
- keeps the first phase narrow and concrete

**Trade-offs**
- can encode the wrong assumptions if the lifecycle model is not defined yet
- improves new assets but does little to organize the existing portfolio

### Approach C: Memory-first knowledge loop

Start by creating `docs/solutions/` and teaching the repo to preserve fixes, repeated gotchas, and completed CE outputs there, then connect scaffolds and lifecycle later.

**Why it helps**
- closes a real missing layer the repo already implicitly wants
- reduces repeated rediscovery of solutions
- improves continuity across sessions and contributors

**Trade-offs**
- knowledge systems get noisy fast without ownership and lifecycle rules
- does not directly improve the quality of newly generated assets

## Recommendation

Choose **Approach A: metadata-first program**.

This is the smallest decision that makes the other two ideas stronger instead of parallel. Once the repo has a canonical lifecycle model, we can answer:
- which metadata fields scaffolds must generate or request
- which assets are required to enter `docs/solutions/`
- what counts as active, experimental, deprecated, or unowned
- how review cadence and ownership should influence validation and visibility

## Program Shape

### Track 1: Lifecycle and ownership control plane

Define a lightweight canonical model for:
- lifecycle state
- owner or maintainer
- maturity
- review cadence
- optional companion relationships such as source skill, generated projection, or linked memory artifacts

This track should become the anchor because it changes how the repo reasons about the rest of the surface.

### Track 2: Reality-first scaffold generation

Use the lifecycle model to upgrade scaffold generators so new skills and plugins start closer to publishable quality.

Likely principles:
- fewer placeholder blocks
- stronger realistic defaults
- required metadata captured at creation time
- generated examples aligned with validator expectations

### Track 3: `docs/solutions/` memory loop

Create a durable library for solved problems, repeated fixes, and reusable patterns that can be linked back to skills, brainstorms, and later work artifacts.

The key is not just adding a folder, but deciding:
- what qualifies as a reusable solution
- who curates it
- how it links back to lifecycle-owned assets

## Key Decisions

- Treat the three ideas as one program, not three unrelated bets.
- Make lifecycle metadata the anchor track.
- Treat scaffold improvement and institutional memory as dependent companion tracks.
- Avoid starting with a dashboard or operator wrapper; those are more valuable after the control plane exists.

## Success Criteria

- maintainers can tell which skills are active, owned, experimental, or deprecated without ad hoc repo archaeology
- new generated skills and plugins require materially less manual cleanup
- solved problems have a canonical durable home and can be linked from future work
- the three tracks reinforce one another instead of creating duplicate governance layers

## Open Questions

- What is the smallest metadata schema that is useful without becoming ceremony?
- Which asset types should participate first: skills only, or also plugins, agents, and major references?
- What should be the entry rule for `docs/solutions/` so it stays high signal?

## Resolved Questions

- Should we pursue all three ideas? Yes, but as one sequenced program rather than parallel unrelated efforts.
- Which idea should anchor the program? Lifecycle and ownership metadata.
- Should we jump directly to planning? No. The program still needs a clearer contract before planning work would be reliable.

## Recommendation Status

- `spec_required`: `lite`
- `risk_level`: `medium`
- `complexity`: `medium`

## Next Step

Proceed to a **lite spec** that defines:
- the lifecycle metadata contract
- the relationship between lifecycle metadata, scaffold outputs, and `docs/solutions/`
- the initial scope boundary for phase one

That spec should be narrow enough to preserve momentum, but explicit enough that later planning does not split the program into conflicting implementations.
