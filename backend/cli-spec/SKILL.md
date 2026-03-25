---
name: cli-spec
description: Plan and draft CLI UX and surface area (commands, flags, help, output). Use when specifying or refactoring a command-line interface.
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
- [Verification](#verification)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Response format](#response-format)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Design CLIs for both humans and automation unless the request explicitly narrows the audience.
- Make output predictable, composable, and easy to script.
- Treat safety, exit codes, and non-interactive behavior as first-class design requirements.

## When to use
- Specify a new CLI surface area.
- Refactor an existing CLI’s commands, flags, output, or help behavior.
- Review a CLI proposal for consistency, usability, and scriptability.
- Define a command tree, error model, config precedence, or automation-safe UX.

## When not to use
- Full backend or application implementation with no CLI design decision in scope.
- Generic shell scripting help where there is no CLI product or interface to specify.
- Visual UX or frontend workflow design.

## Required inputs
- Command name and one-sentence purpose.
- Primary users: humans, automation, or both.
- Inputs and outputs: args, stdin, files, URLs, structured output, exit-code needs.
- Safety requirements: confirmations, dry-run, non-interactive mode, access constraints.
- Platform/runtime constraints and any compatibility promises.

If key details are missing, ask only the minimum needed to lock the interface shape.

## Deliverables
- Command tree and usage synopsis.
- Flags and arguments table with defaults, requiredness, and semantics.
- Output contract: stdout vs stderr, machine-readable modes, quiet/verbose behavior.
- Exit-code and failure-mode map.
- Config and env precedence.
- Example invocations covering the common path plus at least one safety-sensitive or automation path.

## Philosophy
- Human-friendly by default, automation-friendly by design.
- Predictability beats cleverness.
- Destructive actions should be obviously safe or obviously gated.
- The help text is part of the product, not documentation afterthought.

## Workflow
1. Identify the core jobs the CLI must do and keep verbs distinct.
2. Separate what belongs in subcommands from what belongs in flags.
3. Define the output contract before polishing syntax so scripting expectations stay stable.
4. Design failure behavior explicitly: validation errors, operational errors, and partial success.
5. Add safety controls for destructive or expensive operations.
6. Verify naming consistency across synopsis, examples, flags, and exit codes.

## Verification
- Check that every command and flag is named consistently across all sections.
- Verify config precedence is explicit and non-contradictory.
- Verify destructive operations have confirmation, force, or dry-run behavior when appropriate.
- Verify at least one automation-safe example uses structured output or non-interactive mode when relevant.

## Validation
- Verify the spec names the command tree, output contract, and exit rules explicitly.
- Verify examples match the declared syntax exactly.
- Use `references/cli-guidelines.md` and other `references/` docs in this skill folder as the default rubric before inventing custom CLI rules.
- Reuse any skill `assets/` templates that help keep the spec structure consistent.

## Constraints
- Never recommend passing secrets directly via command-line flags when env vars, stdin, files, or secret stores are more appropriate.
- Do not invent unsupported behavior and present it as existing.
- Prefer plain, stable nouns and verbs over brand-heavy or novelty naming.

## Anti-patterns
- Overloading one command with unrelated behaviors instead of using clear subcommands.
- Designing output purely for human reading and leaving automation as an afterthought.
- Hiding destructive behavior behind ambiguous verbs.
- Specifying flags or examples that conflict with the stated precedence or output rules.
- Treating `--json` as an afterthought instead of a contract.

## Examples
- "Design a CLI for syncing issues from stdin or a file and returning JSON results."
- "Refactor this CLI spec so destructive commands require `--force` or a confirmation step."

## Response format
Use these headings in order:
1. `## When to use`
2. `## Inputs`
3. `## Outputs`
4. `## Command model`
5. `## Output and exit rules`
6. `## Safety rules`
7. `## Verification`

## See Also

| Skill | When to use together |
|---|---|
| [[writing-plans]] | Turn the CLI spec into an implementation plan |
| [[test-driven-development]] | Write CLI acceptance tests from the spec |
| [[docs-expert]] | Document the CLI surface after speccing it |
| [[product-spec]] | Produce a broader product spec alongside the CLI spec |

**Topic map:** [[backend-platform]]

## Remember
- A good CLI spec reduces implementation churn later.
- Optimize for the common path, but make failure and automation paths explicit.
- If the CLI will be used by agents or scripts, design for deterministic parsing from the start.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If the command goals, user workflows, or output contract are underspecified, stop, name the ambiguity, and fall back to a smaller CLI surface proposal before locking in flags or behaviors.
