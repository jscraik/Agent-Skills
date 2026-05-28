# Skillify SKILL.md Template

Copy this template only after the candidate passes the evidence-discovery criteria and the smallest-form decision is `skill`.

Template:

    ---
    name: <skill-name>
    description: "Performs <concrete action> for <domain>. Use when the user says <natural trigger>, <alternate trigger>, or needs <release/eval outcome>."
    metadata:
      version: "1.0.0"
      skill-type: <category>
    ---

    # <Skill Name>

    ## When To Use

    - <repeatable trigger backed by evidence>
    - <alternate natural-language trigger>

    ## Inputs

    - <required path, artifact, report, or user-provided context>

    ## Workflow

    1. Confirm the canonical source path and applicable instructions.
    2. Read the smallest evidence surface needed for the request.
    3. Produce the required output shape.
    4. Run the validation command and stop at the first failed gate.

    ## Output Template

    schema_version: 1
    status: pass|blocked
    source_evidence: [<path or command>]
    validation:
      - command: <exact command>
        outcome: pass|fail|blocked
    blocked_by: null

    ## Execution Boundaries

    - Do not widen scope beyond the named workflow.
    - Redact secrets and sensitive data by default.
    - Return `blocked_by` instead of inventing missing evidence.

    ## Anti-Patterns

    - Packaging one-off work, private logs, or contradictory guidance.
    - Claiming readiness from skipped validation.

    ## Validation

    Run `./bin/ask skills audit <skill-path> --level strict --json --robot`. Fail fast at the first failed gate.
