# Source Parity Notes

## Table of Contents
- [Source inputs](#source-inputs)
- [Preserved behaviors](#preserved-behaviors)
- [Intentional modernizations](#intentional-modernizations)

## Source inputs
This package was refreshed against:
- `https://github.com/EveryInc/compound-engineering-plugin/tree/847ce3f156a5cdf75667d9802e95d68e6b3c53a4/Plugins/compound-engineering/skills/agent-native-architecture`

## Preserved behaviors
- the donor's five core principles: parity, granularity, composability, emergent capability, and improvement over time
- the 13-path intake router covering design, files, tool design, prompts, context, parity, self-modification, product patterns, mobile, testing, and refactoring
- the architecture review checklist as the pre-implementation quality gate
- the imported reference set as the canonical deep doctrine rather than re-expanding everything inside `SKILL.md`
- the quick-start framing that starts with atomic tools, prompt-defined behavior, and explicit completion loops

## Intentional modernizations
- kept the local wrapper's stronger `When to use`, `Required inputs`, `Deliverables`, and `Failure mode` sections instead of collapsing back to the donor's single-file structure
- removed the stale pinned-ref note in favor of an explicit parity record for future refreshes
- taught the intake menu to skip itself when the user already named the architecture surface, which fits this repo's "keep communication single-threaded" guidance better
- added local package governance surfaces (`agents/openai.yaml`, `contract.yaml`, `evals.yaml`) so the skill can be validated and maintained like the rest of the repo
