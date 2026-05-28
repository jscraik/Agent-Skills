# Skill Factory Router Policy Handles

Use this package-local reference to keep the staged skill tile self-contained. In the source repository, the authoritative policy files are loaded by path when needed; do not link to files outside the package from `SKILL.md`.

## Major Authoring Design Check

Source handle: `Infrastructure/references/openai-style-plugin-design-contract.md`.

Load only for broad new-skill or broad-rewrite requests where the router must decide whether the user is asking for a skill, docs, script, hook, validator, rule, or direct answer.

## First-Principles Gate

Source handle: `Infrastructure/references/first-principles-factory-gate.md`.

Use before routing expensive or high-blast-radius authoring work. The router should return the selected lane plus the first-principles result, not execute downstream edits.

## Operator Pattern Map

Source handle: `Plugins/skill-factory/references/operator-pattern-map.md`.

Use when a request spans multiple skill-factory lanes or when prior operator patterns clarify whether work belongs in `skillify`, `skill-builder`, `skill-refactor`, `.system/skill-creator`, `.system/skill-installer`, or `plugin-factory`.

## Live Deferred-Context Policy

Source handle: `Plugins/skill-factory/references/live-deferred-context.md`.

Use when routing depends on whether context should stay in the entrypoint or move to package-local references. The default is to keep the router small and load downstream references only after lane selection.

## Packaging Rule

`SKILL.md` must link only to package-local references. Source-repo paths above are handles for agents working in this repository; they are intentionally not Markdown links so Tessl staging remains valid.
