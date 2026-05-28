# Skill Builder Repair Examples

Use one example per iteration, then rerun the named gate.

## Description Repair

Before:

```yaml
description: "Use when evals weak."
```

After:

```yaml
description: "Improves SKILL.md packages by fixing audit findings, adding realistic evals, and rerunning release proof. Use when the user asks to improve a skill, raise a Tessl score, or prepare a plugin skill for release."
```

Proof:

```bash
./bin/ask skills external-review <target> --audit-level compat --skip-plugin-eval --json --robot
```

## Weak Eval Repair

Before:

```yaml
acceptance:
  - type: contains
    value: validation
```

After:

```yaml
expected_artifact: "A response naming the exact audit command."
reproduce: "./bin/ask evals run <target> --mode smoke --skip-tessl --json --robot"
acceptance:
  - type: regex
    value: "(?is)\\./bin/ask skills audit .* --json --robot"
```

Proof:

```bash
./bin/ask evals run <target> --mode smoke --json --robot
```
