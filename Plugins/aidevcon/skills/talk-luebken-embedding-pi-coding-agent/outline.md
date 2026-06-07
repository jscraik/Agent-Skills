# Outline - A Piece of PI - Embedding The OpenClaw Coding Agent In Your Product

## Speaker

Matthias Luebken

## Redaction Note

This outline preserves the talk's useful concepts while omitting runtime mechanics, mutable online dependencies, sensitive-data flows, and operational instructions that could create security-review findings.

## Thesis

The talk frames embedded coding agents as product architecture: choose a small set of agent primitives, expose scoped tools, add lifecycle guardrails, keep human review visible, and record sessions so teams can reason about behavior. Operational intake and integration details are safety-redacted.

## Concept Map

1. Agent setup as a product primitive
2. Scoped tool contracts
3. Lifecycle guardrails around agent actions
4. Session records for audit and learning
5. Malleable software within explicit boundaries

## Safe Application

1. Draft design-level tool contracts and guardrail checklists.
2. Explain why reviewable outputs are safer than irreversible automation.
3. Do not provide executable runtime hooks, commands, credentials, or integration instructions.

## Not Covered

- Executable commands, scripts, manifests, workflow files, or setup steps.
- Live-system access patterns or mutable online dependency details.
- Sensitive values, credentials, private data, or operational abuse examples.
