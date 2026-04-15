---
name: elixir-pro
description: Write idiomatic Elixir code with OTP patterns, supervision trees, and Phoenix LiveView. Masters concurrency, fault tolerance, and distributed systems.
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

## References and assets

- Open deep guidance: `Infrastructure/references/deep-guidance.md`
- Read when: the task needs advanced edge cases, migration-safe patterns, or runtime-specific nuance beyond the core checklist.
