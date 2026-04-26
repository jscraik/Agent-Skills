---
name: biome-linting
description: "Guide Biome linting and formatting workflows with safe-fix strategy and CI-ready rule triage. Use when a user needs Biome command, diagnostics, or remediation guidance in JavaScript/TypeScript projects."
metadata:
  skill-type: runbook
---

# Biome Linting

Use this skill for Biome-first lint/format/check workflows, especially when users need exact CLI commands, safe-vs-unsafe fix guidance, or CI-ready lint gates.

## When to use

- The repo already uses Biome or is migrating to Biome checks.
- The user asks to fix Biome linting issues.
- The user needs CI-safe Biome command contracts.
- The user asks how to suppress diagnostics responsibly.

## Non-triggers

- ESLint-specific plugin architecture work with no Biome usage.
- Non-JS/TS linting ecosystems outside Biome scope.

## Philosophy

- Start read-only, then escalate to safe fixes, then unsafe fixes only by explicit approval.
- Keep rule scope intentional (`--only`, `--skip`) before suppressing diagnostics.
- Treat CI commands as the release contract for style and lint quality.

## Required inputs

- Current Biome config location (`biome.json`, `biome.jsonc`, or package scripts).
- Requested operation (`lint`, `format`, `check`, `ci`, suppression triage).
- Risk posture for fixes (`read-only`, `safe-write`, `unsafe-write`).

## Deliverables

- Exact Biome command sequence for the request.
- Rule-level guidance (`--only`, `--skip`, suppressions) when relevant.
- CI gate recommendation (`biome ci` or equivalent script contract).
- Validation summary with pass/fail/blocked outcomes.
- Structured outputs should include `schema_version` when a schema-bound contract is requested.

## Rules

**Start read-only, then escalate only when requested**:

```bash
./bin/ask -- biome lint .
./bin/ask -- biome lint --write .
if [ "${ALLOW_UNSAFE_FIXES:-}" = "true" ]; then
  ./bin/ask -- biome lint --write --unsafe .
fi
```

**Prefer focused rule targeting for noisy codebases**:

```bash
./bin/ask -- biome lint --only=correctness --only=suspicious/noDebugger .
./bin/ask -- biome lint --skip=style --skip=complexity/noExcessiveCognitiveComplexity .
```

**Use CI mode for enforcement**:

```bash
./bin/ask -- npx @biomejs/biome ci
```

**Use explicit suppressions only with reasons**:

```javascript
// biome-ignore lint/suspicious/noDebugger: Temporary production triage
```

## Workflow

1. Confirm Biome ownership and requested risk posture.
2. Run/describe read-only lint path (`biome lint .`).
3. If remediation is requested, preview the read-only diagnostics, then apply safe fixes first (`--write`) only to the scoped repo path.
4. Use `--unsafe` only if explicitly approved and behavior risk is documented.
5. For recurring issues, tighten rules (`--only`/`--skip`) or add scoped suppressions with reasons.
6. Finalize with CI contract command and expected pass criteria.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not recommend blanket suppressions when scoped rule targeting can solve the issue.
- Treat unsafe autofixes as destructive-risk operations requiring explicit confirmation.

## Validation

- Baseline: `./bin/ask -- biome lint .`
- Safe remediation: `./bin/ask -- biome lint --write .`
- Full contract: `./bin/ask -- npx @biomejs/biome ci`
- Stop at first failing command and report exact failure output.

## Failure mode

- If Biome reports parser/config errors, stop and capture the first failing file and diagnostic code.
- If safe fixes fail, do not jump to `--unsafe`; report blocker and request explicit approval.

## Gotchas

- `--unsafe` can change runtime behavior.
- Broad skip/suppress patterns hide regressions.
- `biome ci` may catch formatting differences missed by lint-only runs.

## Anti-patterns

- Jumping directly to unsafe fixes.
- Replacing diagnostics with blanket suppressions.
- Mixing Biome and legacy lint contracts without a clear source of truth.

## Examples

- "Our `pnpm check` is failing because Biome reports `noDebugger` and format drift; show me the safe fix path first."
- "We are enabling Biome incrementally in a monorepo. How do we enforce correctness rules now and defer style rules?"
- "Give me one suppression example with a reason for a temporary false positive."

## References

- `references/contract.yaml`
- `references/evals.yaml`
- `references/context7-notes.md`

## See Also

| Skill | When to use together |
|---|---|
| [[pnpm-manager]] | Target Biome checks to changed workspaces before broad runs |
| [[npm-workflow-discipline]] | Keep npm/pnpm script contracts aligned with Biome gates |
| [[typescript]] | Pair lint remediation with type-safety guidance in TS repos |
