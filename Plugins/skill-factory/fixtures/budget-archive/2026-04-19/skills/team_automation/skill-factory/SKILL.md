---
name: skill-factory
description: Front-door router for the Skill Factory plugin. Use when users ask generally to create, improve, install, or skillify skills and need the correct lane selected before deeper execution.
metadata:
  short-description: Route to the right skill-authoring lane
  skill-type: team_automation
---

# Skill Factory

Route broad skill-authoring requests to one lane:
- create -> `[[skill-creator]]`
- improve -> `[[skill-builder]]`
- refactor -> `[[skill-refactor]]`
- install -> `[[skill-installer]]`
- skillify -> `[[skillify]]`

Read when: lane contract details are required: [router contract](./references/contract.yaml)
