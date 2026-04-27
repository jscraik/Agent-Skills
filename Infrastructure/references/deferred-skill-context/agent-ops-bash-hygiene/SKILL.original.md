---
name: bash-hygiene
description: "Write and review Bash scripts with safe structure and portability guardrails. Use when shell work needs strict mode defaults, robust quoting, and interpreter-compatible behavior."
metadata:
  skill-type: runbook
---

# Bash Hygiene

Practical Bash scripting hygiene for script structure, strict mode, quoting safety, and portability verification.

## When to use

- Creating or editing Bash scripts in `bin/`, `Infrastructure/scripts/`, or hooks.
- Reviewing shell scripts for reliability and maintainability.
- Debugging failures caused by word splitting, globbing, or shell incompatibility.
- Standardizing shell quality gates in CI.

## Philosophy

- Make interpreter intent explicit before writing logic.
- Prefer correctness and clarity over shell cleverness.
- Treat quoting and portability as baseline quality, not optional polish.

## Required inputs

- Target interpreter and shell compatibility goals.
- Script context (`hook`, `build script`, `utility`, or `CI helper`).
- Command/data inputs, including untrusted user-provided values.
- Existing linting/validation contract (for example ShellCheck).

## Deliverables

- A Bash script or review guidance with strict-mode and quoting safety.
- Interpreter-appropriate portability recommendations.
- A validation plan with linting and execution checks.
- Structured outputs should include `schema_version`.

## Procedure

### 1) Declare interpreter and script mode

- Use Bash shebang for Bash features.
- Keep POSIX `sh` scripts free of Bash-only constructs.

### 2) Apply strict defaults

- Enable strict mode for non-trivial scripts.
- Use explicit parameter defaults for optional values.

### 3) Harden expansions and arguments

- Quote variable expansions by default.
- Use `"$@"` and `"${array[@]}"` for argument boundaries.

### 4) Validate portability and behavior

- Run ShellCheck and fix high-signal diagnostics.
- Verify script behavior in the declared interpreter.

## Constraints

- Redact secrets, tokens, credentials, and sensitive runtime values by default.
- Avoid destructive or state-mutating suggestions unless explicitly requested.
- Do not recommend Bash-specific syntax under `#!/bin/sh`.
- Keep examples deterministic and copy-safe.

## Validation

- Run `shellcheck -x` on touched scripts.
- Confirm no unquoted-expansion hazards remain in critical paths.
- Confirm strict mode does not break expected control flow.
- Stop at first blocking lint/runtime error and report exact evidence.

## Anti-patterns

- Unquoted expansions (`$var`, `$*`) in command paths.
- Mixing Bash syntax into scripts declared as POSIX `sh`.
- Silent fallthrough from unset variables.
- Portability claims without interpreter-aligned checks.
- Script logic that depends on accidental word splitting.

## Rules

**Use an explicit shebang matching script features**: use `#!/usr/bin/env bash` for Bash features; do not label Bash scripts as POSIX `sh`.

```bash
#!/usr/bin/env bash
```

**Default to strict mode for non-trivial scripts**: fail early on errors and undefined variables.

```bash
set -euo pipefail
IFS=$'\n\t'
```

**Quote variable expansions unless intentional splitting is required**: prefer `"${var}"`, `"${array[@]}"`, and `"$@"`.

```bash
cp "$@" "$dest_dir"
cd "${subdir}"
```

**Run portability and lint checks**: validate scripts with ShellCheck and ensure shebang/feature compatibility.

```bash
shellcheck -x path/to/script.sh
```

## Patterns

### Script Skeleton

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

main() {
  local input="${1:-}"
  if [[ -z "$input" ]]; then
    echo "usage: $0 <input>" >&2
    return 2
  fi
  echo "processing: $input"
}

main "$@"
```

### Safe Conditionals and Defaults

```bash
if [[ -n "${OPTIONAL_VAR:-}" ]]; then
  echo "optional var present"
fi
```

### Argument and Array Safety

```bash
# Preserve argument boundaries
run_tool "$@"

# Preserve array element boundaries
printf '%s\n' "${items[@]}"
```

### Portability Checks

```bash
# Bash-targeted script quality gate
shellcheck -x Infrastructure/scripts/*.sh
```

- If script is intentionally POSIX `sh`, avoid Bash-only features (arrays, `[[ ... ]]`, `local` outside compatible shells).
- Keep signal traps and redirections portable for the declared interpreter.

## Examples

- "Review this `Infrastructure/scripts/deploy.sh` file for strict mode and quoting safety."
- "Convert this shell helper to Bash-safe argument handling."
- "Check whether this script is truly POSIX or should be declared Bash."

## Failure mode

- If interpreter target is ambiguous, pause and request `bash` vs `sh` intent.
- If strict mode introduces expected behavior changes, return partial with exact compatibility tradeoff.

## Gotchas

- Unquoted variables (`$var`) causing glob expansion and split bugs.
- Using `$*` when `"$@"` is required.
- Mixing Bash features into scripts declared as `#!/bin/sh`.
- Omitting strict mode in scripts that mutate state.
- Assuming portability without ShellCheck or interpreter-specific validation.

## See Also

| Skill | When to use |
|---|---|
| [[codex-hooks-builder]] | Harden shell-heavy hook scripts and hook-pack scaffolds with safer defaults |
| [[he-fix-bugs]] | Triage shell failures with evidence-first diagnosis before behavioral changes |
| [[verification-before-completion]] | Enforce verification routines after Bash script edits before claiming done |

**Topic map:** [[agent-ops]]

## References

- Contract: `Infrastructure/references/contract.yaml`
- Eval cases: `Infrastructure/references/evals.yaml`
