# Project Understanding Playbook

## Table of Contents
- [Purpose](#purpose)
- [Command sequence](#command-sequence)
- [Interpretation template](#interpretation-template)
- [Quality gates](#quality-gates)

## Purpose

Turn diagram artifacts into a concise architecture brief that helps users understand how the repository is organized, where coupling risk lives, and what to inspect next.

## Command sequence

```bash
npx --yes @brainwav/diagram analyze . --json > Infrastructure/artifacts/diagrams/analyze.json
npx --yes @brainwav/diagram all . --output-dir .diagram
npx --yes @brainwav/diagram manifest . --manifest-dir .diagram --require-types architecture,dependency,security,auth --fail-on-placeholder
```

If architecture rules are configured:

```bash
npx --yes @brainwav/diagram test . --format console
```

## Interpretation template

Use this structure for the user-facing summary:

1. **System shape**
   - top-level modules and dominant directories
   - primary boundaries (core/domain/infrastructure/interfaces)
2. **Dependency hotspots**
   - highest fan-in / fan-out clusters
   - suspicious cross-boundary links
3. **Risk scan**
   - auth and security flow surprises
   - placeholder or sparse diagram types
4. **Actionable next steps**
   - 2–5 concrete commands or files to inspect next

## Quality gates

- Confirm artifact files exist and are non-empty.
- Fail if `manifest` reports missing required types or placeholders.
- If rules are enabled, fail on `diagram test` violations before publishing conclusions.
- Redact sensitive names/tokens before sharing artifacts externally.
