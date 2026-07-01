# devrel-hack-coach

SDK-native version of a DevCon-style hackathon coaching skill. It helps an
engineer turn a vague AI-native hackathon idea into a spec, timeboxed plan, and
concise demo pitch before writing code.

## What It Does

- Interrogates stack, track, and one named itch.
- Forces a one-page spec before implementation.
- Cuts the plan into checkpoints sized to the user's available timebox.
- Produces a three-sentence pitch and judge Q&A.
- Refuses code, file structures, and implementation help until the spec is
  locked.

## Package Shape

This package contains:

- `SKILL.md`
- `agents/openai.yaml`
- `references/contract.yaml`
- `references/evals.yaml`
- phase references and worked examples

## Validation Boundary

This skill is a coaching workflow. It does not generate code or advance
registry readiness by itself. Skills SDK receipts and eval artifacts remain the
authority for package and release claims.
