---
name: elixir-pro
description: Create and review idiomatic Elixir code with OTP patterns, supervision trees, and Phoenix LiveView. Use when building or debugging Elixir services that need reliable concurrency and fault tolerance.
metadata:
  skill-type: code_quality_review
---

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [OTP Structure](#otp-structure)
- [Reliability](#reliability)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use

- Use for Elixir/OTP implementation and review work.
- Use when fault tolerance or process boundaries are central.

## Required inputs

- App context and supervision tree scope.
- Expected process lifecycle behavior.
- Error and retry expectations.

## Deliverables

- Idiomatic Elixir updates.
- Clear OTP process boundaries.
- Explicit reliability notes when behavior changes.

## OTP Structure

- Keep supervision trees explicit and shallow.
- Model long-lived state with GenServer only when state is required.
- Prefer pure modules for domain logic outside process boundaries.

## Reliability

- Let supervisors restart failed workers.
- Use pattern matching to make invalid states impossible.
- Keep message protocols explicit and documented.

## Examples

```elixir
defmodule PortParser do
  def parse(value) do
    case Integer.parse(value) do
      {port, ""} when port > 0 -> {:ok, port}
      _ -> {:error, :invalid_port}
    end
  end
end
```

## Failure mode

- If supervision strategy is unclear, hold structural changes and confirm intent.

## Gotchas

- Process state mutations without clear ownership cause flaky behavior.

## See Also

| Skill | When to use |
|---|---|
| [[rust-pro]] | Systems-level concurrency patterns that share OTP-style supervision thinking |
| [[he-fix-bugs]] | Triage distributed process failures with evidence-first diagnosis |

**Topic map:** [[agent-ops]]


## Philosophy

- Optimize for clear, verifiable outcomes with the minimum necessary changes.
- Keep guidance deterministic so repeated runs produce consistent decisions.

## Procedure

1. Confirm scope, constraints, and required inputs before edits.
2. Apply focused changes tied directly to the requested outcome.
3. Re-run the highest-signal validations and capture concrete evidence.

## Validation

- Run the relevant local checks for touched files and workflow contracts.
- Fail fast: stop at the first blocking validation failure and report exact evidence.
- Re-run checks after fixes and record residual risk if any remains.

## Constraints

- Redact secrets, tokens, credentials, and sensitive data by default.
- Do not expand scope beyond the request unless explicitly asked.
- Prefer safe, reversible edits over broad refactors.

## Anti-patterns

- Skipping validation after making changes.
- Applying broad refactors to solve narrow issues.
- Assuming behavior without evidence from current checks.

## References and assets

- Open deep guidance: `Infrastructure/references/deep-guidance.md`
- Read when: the task needs advanced edge cases, migration-safe patterns, or runtime-specific nuance beyond the core checklist.
