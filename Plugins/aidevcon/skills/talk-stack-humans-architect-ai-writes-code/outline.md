# Outline - The Humans Architect the System, the AI Writes the Code

## Speaker

Paul Stack

## Redaction Note

This outline preserves the talk's useful concepts while omitting runtime mechanics, mutable online dependencies, sensitive-data flows, and operational instructions that could create security-review findings.

## Thesis

The talk describes a workflow where humans define architecture and intent while agents do implementation work under review. Live triage or feature-request processing details are safety-redacted.

## Concept Map

1. Humans own architecture and intent
2. Agents implement under constraints
3. Planner and reviewer separation
4. UAT as source of truth
5. Vibes do not scale

## Safe Application

1. Help draft architecture constraints and review checklists.
2. Explain planner/reviewer patterns conceptually.
3. Do not fetch, process, or summarize live issue text from this skill.

## Not Covered

- Executable commands, scripts, manifests, workflow files, or setup steps.
- Live-system access patterns or mutable online dependency details.
- Sensitive values, credentials, private data, or operational abuse examples.
