---
name: cli-spec
description: Create an implementation-grade CLI specification when the user requests a binding technical contract for a new or existing command-line interface.
metadata:
  skill-type: scaffolding_templates
---

# CLI Spec (Implementation-Grade)

**Note: The current year is 2026.** Use this when dating specification artifacts.

`ce-spec` defines system contracts. `cli-spec` defines the **CLI Implementation Contract** (command trees, JSON schemas, dry-run plans, and safety gates).

This skill produces a technical contract at `docs/cli-specs/`. It does **not** produce implementation code.

## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Workflow](#workflow)
- [Artifact contracts](#artifact-contracts)
- [Validation and Gates](#validation-and-gates)
- [Philosophy](#philosophy)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Response format](#call-signature)
- [See Also](#see-also)

## Working agreement
- Specification answers **WHAT** the CLI owns, how it behaves in dual-mode (Human/Agent), and how correctness is verified.
- Use the most authoritative source; do not invent behavior that belongs in a parent product spec.
- Prefer the smallest spec that removes ambiguity; scope to one tool or 3-5 tightly coupled commands.
- Leave a written artifact in `docs/cli-specs/` for substantial work.
- Every acceptance criterion must have a stable **`CA`** ID (e.g., `CA1`, `CA2`).

## When to use
Use this skill when you need a binding technical design for a CLI before planning or coding begins.

Primary triggers:
- "Create an implementation-grade CLI spec for [context]."
- "Turn this brainstorm into a formal CLI contract."
- "Refactor this legacy CLI into a Gold Standard 2026 interface."
- "Define the command tree, JSON schema, and safety gates for [tool]."

## Inputs
- **Source:** A brainstorm path, feature description, or legacy tool definition.
- **Audience:** Human-first, Agent-first, or Dual-mode hybrid.
- **Constraints:** Secret handling requirements, platform limits, and ecosystem (Rust, Go, etc.).

## Outputs
- **Technical Contract:** A markdown file in `docs/cli-specs/` following the `schema_version: 1` standard.
- **CA Matrix:** A set of stable CLI Acceptance IDs for verification.
- **JSON Schemas:** Machine-readable definitions for all command outputs.

## Workflow

### Phase 1: Local Grounding
Research existing CLI patterns in the repository to ensure consistency.
- Use `repo-research-analyst` to find similar tools.
- Check `Infrastructure/references/cli-guidelines.md` for local standards.
- Consult `assets/cli-spec.png` for the canonical command tree layout.

### Phase 2: Build the Contract
Draft the technical specification. Ensure the document answers:
- **Strategic Alignment:** Problem statement and audience goals.
- **Command Model:** The `<topic> <action>` hierarchy.
- **Type-Safe Signatures:** TypeScript-style help declarations.
- **Response Envelope:** The `CallResult` JSON contract (trace_id, status, errors).
- **Safety Spec:** Detailed `--dry-run` behavior and plan schema.
- **Acceptance Matrix:** Sequential `CA` IDs for happy and failure paths.

### Phase 3: Write the Artifact
Save the spec to `docs/cli-specs/YYYY-MM-DD-<name>-cli-spec.md`. Use the canonical frontmatter from `Infrastructure/references/cli-spec-artifacts.md`.

## Artifact contracts
- **Standard Path:** `docs/cli-specs/YYYY-MM-DD-<tool-name>-cli-spec.md`
- **Stable IDs:** Use `CA1`, `CA2` for all verification items.
- **Output:** Must include a JSON schema for all machine-readable endpoints.

## Validation and Gates
Fail fast: stop at first failed gate and do not proceed. Review the detailed contracts before claiming completion:
- `Infrastructure/references/contract.yaml`
- `Infrastructure/references/evals.yaml`
- `Infrastructure/references/gold-standard-2026.md`
- `Infrastructure/references/cli-spec-artifacts.md`
- `Infrastructure/references/advanced-patterns-2026.md`
- `Infrastructure/references/lifecycle-and-errors-2026.md`

Run these checks:
```bash
python3 Infrastructure/scripts/diagnose_skill.py backend/cli-spec
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py backend/cli-spec --mode strict
```

## Philosophy
- **Predictability beats Cleverness:** A command should be deterministic.
- **The "Plan" Pattern:** Always show what *would* happen before changing state.
- **Agent-Native DX:** Structured data is a first-class requirement, not an export option.

## Constraints
- **Absolute Paths:** Do not use absolute paths from your local machine in examples.
- **Redaction:** Always redact secrets, API keys, or PII when providing sample outputs or logs.
- **Scope:** Do not implement logic; stay focused on the interface contract.

## Anti-patterns
- **God Commands:** Overloading a single command with too many flags.
- **Regex-Parsing:** Forcing users to parse text output instead of providing JSON.
- **Vague Errors:** Returning non-zero exit codes without a machine-readable error object.

## Examples
- **When the user asks:** "I need an implementation-grade spec for a CLI that manages our S3 bucket permissions. Save it to docs."
- **When the user says:** "Refactor the `mcporter` command tree into a formal CLI contract with `CA` IDs and JSON schemas."
- **When the user asks:** "Create a Gold Standard 2026 spec for a new internal tool called 'vault-sync'."

## Response format
Use these headings in order:
1. `## Strategic alignment` (Confirming Gold Standard goals)
2. `## Command model` (The `<topic> <action>` tree)
3. `## Type-safe Signatures` (TypeScript-style help)
4. `## Response Envelope and Exits` (The `CallResult` contract)
5. `## Safety and Dry-run spec`
6. `## Verification checklist (CA IDs)`

## Required inputs
- Tool name, primary ecosystem (e.g., Rust, Go, Node), and target audience.
- Interaction Model: human, agent, or dual-mode hybrid.
- Data Flow: inbound (args, stdin, files) and outbound (structured JSON, logs, exit codes).
- Security Posture: secret management requirements and isolation levels.
- Maturity Level: prototype or production-grade "Gold" CLI.

## Deliverables
- Command Hierarchy: logical `<topic> <action>` tree.
- Flags & Schema: comprehensive table with type-safety and defaults.
- Output Contract: JSON schema, field masking, and `next_steps` metadata.
- Failure Model: semantic exit codes and machine-readable error objects.
- Safety Spec: dry-run behavior and confirmation gates.

## Failure mode
- If required inputs are incomplete, stop and request clarification before proceeding.
- If the CLI design conflicts with established project patterns, flag this explicitly and suggest alternatives.
- If safety gates cannot be met, do not proceed with the spec.

## Gotchas
- **Absolute Paths:** Never use absolute paths from your local machine in examples.
- **Secret Redaction:** Always redact secrets, API keys, or PII in sample outputs.
- **NO_COLOR Standard:** Respect the `NO_COLOR` environment variable standard in all output examples.

## See Also
| Skill | When to use together |
|---|---|
| [[ce-spec]] | Use when the CLI is a front for a broader system spec |
| [[agent-native-architecture]] | Ensure the CLI fits into an autonomous workflow |
| [[docs-expert]] | Generate user-facing docs from the technical contract |

**Topic map:** [[backend-platform]]
