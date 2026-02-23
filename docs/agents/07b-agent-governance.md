# Agent Governance

## Table of Contents
- [Prompting contract](#prompting-contract)
- [Coordination constraints](#coordination-constraints)

## Prompting contract
- Keep output concise and actionable, with minimal diffs.
- Prefer repo evidence over assumptions.
- Report unknowns before proceeding if a decision blocks progress.

## Coordination constraints
- Do not add deps or toolchain changes unless explicitly requested.
- Do not leave the workflow state ambiguous: list next action after each edit batch.
