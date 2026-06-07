# Outline -- State of Play: AI Coding Assistants

## Speaker

**Birgitta Böckeler** -- Global Lead for AI-assisted Software Delivery at Thoughtworks; software developer, architect, and technical leader. In the transcript she says that three years ago she moved into a full-time role immersed in AI coding and AI on software teams, helping Thoughtworks colleagues and clients and writing about the space, including on Martin Fowler's website. The speech-to-text source renders her name and organization inconsistently; preserve those artifacts when quoting.

## Abstract (as provided)

> The hype and momentum around AI coding assistants show no signs of slowing down. Every other week, we're urged to try a new model, a new workflow, or a new way of writing specs. This presentation takes a step back and looks at the past 12 months from a higher altitude: what are the broad shifts that have taken place, and where do we stand today? If you're deeply immersed in the space, this will help you see the forest for the trees. If you've been overwhelmed by the steady stream of weekly news and updates, this offers the cliff notes.

## Thesis (synthesis)

Böckeler argues that the interesting work has moved from model-watching alone to understanding the whole coding-assistant system: model capabilities, harness features, context/harness engineering, guide-and-sensor feedback loops, and the risks of escalating autonomy. Her practical frame is not "use more AI everywhere" but match task complexity, context, harness capability, and supervision level through risk assessment while watching the human and organizational costs.

## Section TOC

| # | Section | Summary | Source lines / time |
|---|---|---|---|
| 1 | Host introduction (Simon Maple) | Simon introduces Birgitta as a Thoughtworks distinguished engineer, mentions her Martin Fowler-site writing, and frames the closing session as a look back over the previous 12 months. | L0001-L0024 / 00:00-00:57 |
| 2 | Birgitta's self-introduction and framing | Birgitta explains her Thoughtworks role, her three years immersed in AI coding and AI on software teams, and sets up the talk as a forest-for-the-trees recap. | L0025-L0062 / 01:06-02:25 |
| 3 | Models, learning map, and model selection | She argues that models matter but the ecosystem around them is more interesting, then lays out a learning map: not magic, statelessness, context window vs attention, and choosing models by task. | L0063-L0214 / 02:28-07:54 |
| 4 | Coding harnesses and their features | She defines the coding harness/agent layer: prompts, tool integrations, code search, orchestration, UI, extensibility, observability, and the growing need to understand tool footprint and features. | L0215-L0349 / 07:55-12:46 |
| 5 | Harness engineering as context engineering | She describes harness engineering as context engineering for coding agents and separates markdown/context guides into normative, informative, and instructional material. | L0350-L0460 / 12:47-16:51 |
| 6 | Guides, sensors, and self-correction loops | She presents feed-forward guides and feedback sensors, distinguishing inferential review agents from computational tools such as static analysis, code mods, lint rules, and import checks. | L0461-L0560 / 16:52-20:39 |
| 7 | Where to place sensors in the path to production | She recommends deciding where sensors run: inside coding sessions, before commits, during PR review, in CI, as scheduled drift detection, and from production observability data. | L0561-L0643 / 20:44-23:40 |
| 8 | Summary: what coding-agent users need to learn | She recaps the model, task, harness, and context-engineering knowledge practitioners need in order to use coding agents well. | L0644-L0665 / 23:44-24:30 |
| 9 | Autonomy, background agents, swarms, and the four-year arc | She summarizes the drive toward more autonomy and less supervision, including background/cloud agents, brute-force swarms, the four-year arc from autocomplete to skills/OpenClaw, and renewed attention spikes. | L0666-L0784 / 24:32-28:53 |
| 10 | Costs and second-order consequences | She outlines the costs: security, stability, changeability, token cost, cognitive load and burnout, review bottlenecks, backlog/prototype flow problems, and possible congestion collapse. | L0785-L0925 / 28:58-34:17 |
| 11 | Risk assessment for reducing supervision | She frames autonomy as unevenly distributed and proposes a probability-impact-detectability risk assessment for deciding workflow, review depth, and supervision level. | L0926-L0990 / 34:20-36:46 |
| 12 | Cognitive surrender and closing call to action | She warns against moving unthinkingly from in-the-loop to out-of-the-loop, names cognitive load/debt/deferral/surrender, and calls for critical thinking, risk assessment, patience, and sustainable delivery. | L0991-L1127 / 36:48-41:45 |

## Terminology Glossary

- **Model learning map** -- The four things users need to understand: models are not magic, statelessness, context-window/attention trade-offs, and choosing the right model for the task.
- **Coding harness / coding agent** -- The layer around the model that provides prompts, tool integrations, code search, orchestration, UI, extensibility, and observability.
- **Harness engineering** -- Böckeler's working term for context engineering for coding agents: expanding the harness with codebase-specific context, skills, MCP servers, sub-agents, plugins, hooks, and similar features.
- **Guides and sensors** -- Her conceptual model for harness engineering. Guides feed information and constraints forward; sensors provide feedback so the agent can self-correct.
- **Inferential sensors** -- LLM-based checks, such as code review agents judging another LLM's work.
- **Computational sensors** -- Deterministic or CPU-style checks, such as static analysis, lint rules, import scanners, tests, and logs.
- **Continuous drift detection / garbage collection** -- Scheduled reviews for accumulating debt or risks that need not run on every CI build.
- **Probability / impact / detectability** -- The risk-assessment triad Böckeler uses to decide how much autonomy and supervision are appropriate for a coding-agent task.
- **Cognitive X / cognitive surrender** -- Her umbrella for cognitive load, cognitive debt, cognitive deferral, and the danger of surrendering active thinking to AI.

## Named Frameworks / Concepts

1. **The model-user learning map:** not magic; statelessness; context window vs attention; which model for which task.
2. **Model-task matching:** reflect on files involved, blast radius, uncertainty, context size, reasoning level, and tool-calling needs before choosing a model/workflow.
3. **Harness feature model:** prompts, tool integrations, code search, orchestration/sub-agents, caching, UI, extensibility, and observability.
4. **Harness engineering = context engineering for coding agents:** use harness features to provide codebase- and workflow-specific context.
5. **Guide/sensor model:** combine feed-forward guidance with feedback sensors to improve first-pass quality and trigger self-correction.
6. **Sensor placement along the path to production:** coding session, pre-commit/integration, PR process, CI, scheduled drift detection, and production observability.
7. **Autonomy risk assessment:** probability, impact, and detectability determine whether the human stays in the loop, on the loop, or moves out of the loop.
8. **Cognitive surrender checklist:** watch for surrendering review, architectural understanding, junior development, cost discipline, sandboxing, and organizational learning.

## Open Questions / Not Covered

- The transcript does not provide a detailed benchmark table comparing specific models.
- It names several tools and trends, but does not provide setup instructions for any specific harness.
- It does not prescribe one universal review policy; it says supervision depends on risk, task, context, and feedback loops.
- It references external posts, newsletters, papers, and talks, but this bundle only grounds answers in the transcript itself.
