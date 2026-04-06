---
name: cli-spec
description: Plan and draft high-performance, agent-native CLI UX and surface area (commands, flags, help, output). Use when specifying or refactoring modern command-line interfaces.
metadata:
  skill-type: scaffolding_templates
---

# CLI Spec

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Safety and Quality Standards](#safety-and-quality-standards)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Response format](#call-signature)
- [References](#references)
- [Validation](#validation)
- [See Also](#see-also)

## Standards snapshot (April 2026)
- **Agent-Native First:** Design for programmatic consumption (JSON) as a first-class citizen.
- **Dual-Mode DX:** Support "Human Mode" (rich TUI) and "Agent Mode" (deterministic structured data).
- **Type-Safe Help:** Use TypeScript-style signatures for precise, compact help documentation.
- **Hardened Safety:** Mandatory `--dry-run` for state mutations and strict adversarial input validation.
- **Lifecycle Provenance:** Embed regeneration metadata in generated artifacts for traceability.
- **Error Recoverability:** Use structured error envelopes with `fix_suggestions` for agent self-correction.

## When to use
- Specify a new CLI surface area for internal tools or public products.
- Refactor legacy CLIs to be "Agent-Compatible" (adding JSON, schemas, and dry-runs).
- "Mint" a CLI specification from an existing JSON-schema or MCP server definition.
- Review a CLI proposal for consistency with 2026 industry leaders (GH, Stripe, MCPorter).

## When not to use
- Full-stack application logic or API backend implementation (focus on the *interface*).
- Simple shell alias creation with no formal parameter or output design.
- TUI-only design where machine readability is explicitly forbidden.

## Required inputs
- **Context:** Tool name, primary ecosystem (e.g., Rust, Go, Node), and target audience.
- **Interaction Model:** Is this for humans, agents, or a dual-mode hybrid?
- **Data Flow:** Inbound (args, stdin, files) and Outbound (structured JSON, logs, exit codes).
- **Interface Evolution:** Are there legacy commands that need hidden aliases for compatibility?
- **Auth Strategy:** Requirements for OAuth, headless logins, or contextual token overrides.

## Deliverables
- **Command Hierarchy:** A logical `<topic> <action>` tree.
- **Signatures & Schema:** TypeScript-style help signatures and JSON-schema definitions.
- **Structured Response Envelope:** Definition of the `CallResult` envelope (status, trace_id, data, errors).
- **Failure Model:** Mapping of semantic exit codes and machine-readable error objects with fix hints.
- **Safety Spec:** Documentation of dry-run behavior and confirmation gates.

## Philosophy
- **Predictability beats Cleverness:** A command should do exactly what it says, every time.
- **The "Plan" Pattern:** Mutations should show what they *will* do before they do it.
- **Context Awareness:** Automatically discover environment state (git, org, project).
- **Stability by Design:** Use explicit coercion flags (`--raw-strings`) to prevent "magic" breaking changes.

## Workflow
1. **Identify the Data Model:** Define the objects the CLI will manipulate.
2. **Draft the JSON Envelope:** Design the `CallResult` contract first to ensure deterministic behavior.
3. **Map the Command Tree:** Use intuitive, natural-language verbs and stable nouns.
4. **Design Help Signatures:** Use type-safe declarations and progressive disclosure rules.
5. **Establish Safety Gates:** Design `--dry-run` and confirmation logic for all mutations.
6. **Plan for Evolution:** Define hidden aliases and flag transitions for backward compatibility.

## Safety and Quality Standards
- **Adversarial Input:** Ensure the spec handles edge cases like `../` or shell globbing safely.
- **Secret Hygiene:** Recommend environment variables or files over command flags for tokens.
- **Consistency Check:** Verify flag naming (e.g., using `--force` vs `-f`) is consistent across the entire tree.
- **Industry Alignment:** Compare the draft against `references/gold-standard-2026.md`.
- **Visualization:** Consult `assets/cli-spec.png` for the canonical command tree layout.

## Constraints
- **Absolute Paths:** Do not use absolute paths from your local machine in examples.
- **Environment Standards:** Never suggest patterns that violate the `NO_COLOR` or `CLICOLOR` standards.
- **Naming:** Avoid "novelty" flags; stick to industry-standard naming (e.g., `--verbose`, `--quiet`, `--version`).
- **Redaction:** Always redact secrets, API keys, or PII when providing sample outputs or logs.

## Anti-patterns
- **The "God" Command:** Putting too much logic into a single command with complex flag combinations.
- **Regex-Only Parsing:** Designing output that requires users to `grep` or `awk` to extract values.
- **Silent Failures:** Failing without a structured error object or a clear fix suggestion.
- **Magic Coercion:** Automatically converting types in a way that breaks when input formats drift.

## Examples
- **When the user asks:** "I need to spec a CLI for a new cloud provider called 'SkyLink'. It should handle VM creation and deletion. Make it Gold Standard for 2026."
- **When the user says:** "Review this legacy CLI command tree: `db-tool --action=cleanup --target=all`. Help me modernize it for agent consumption."
- **When the user asks:** "Help me draft a JSON response envelope for our internal deployment tool that supports trace-ids and next-step metadata."

## Response format
Use these headings in order:
1. `## Strategic alignment` (Confirming Gold Standard goals)
2. `## Command model` (The `<topic> <action>` tree)
3. `## Type-safe Signatures` (TypeScript-style help)
4. `## Response Envelope and Exits` (The `CallResult` contract)
5. `## Safety and Dry-run spec`
6. `## Verification checklist`

## References
Consult these resources for deeper architectural patterns:
- `references/gold-standard-2026.md`: Core requirements for modern CLIs.
- `references/advanced-patterns-2026.md`: TS-signatures and progressive help disclosure.
- `references/lifecycle-and-errors-2026.md`: Provenance metadata and structured error recovery.
- `references/cli-guidelines.md`: UX and syntax standards.
- `references/agentic-cli-design.md`: Optimization for autonomous agent callers.

## Validation
Fail fast: stop at first failed gate and do not proceed.

Review the detailed contracts and evaluation cases before making changes:
- `references/contract.yaml`
- `references/evals.yaml`

Run these checks:
```bash
python3 scripts/diagnose_skill.py backend/cli-spec
python3 utilities/skill-builder/scripts/quick_validate.py backend/cli-spec --mode strict
```

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
| [[agent-native-architecture]] | Ensure the CLI fits into an autonomous agent workflow |
| [[backend-engineer]] | Plan the implementation details of the CLI logic |
| [[docs-expert]] | Generate the user-facing documentation from the spec |
| [[product-spec]] | Align the CLI UX with the broader product vision |

**Topic map:** [[backend-platform]]
