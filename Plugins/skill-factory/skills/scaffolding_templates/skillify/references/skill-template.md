# Skillify SKILL.md Template

Copy this template only after the candidate passes the evidence-discovery criteria
and the smallest-form decision is skill.

For deterministic SDK stage skills, preserve this exact heading order. The repo
validator enforces it for every SKILL.md with metadata.sdk_stage, and also
requires references/source-context.yaml for template and source-context provenance.

Template:

    ---
    name: <skill-name>
    description: "Performs <concrete stage action> for <domain>. Use when the user says <natural trigger>, <alternate trigger>, or needs <stage outcome>."
    metadata:
      version: "1.0.0"
      skill-type: team_automation
      sdk_stage: <stage-name>
      lifecycle_state: active
      command_visibility: orchestrator
    ---

    # <Skill Name>

    ## Stage Contract

    Previous stage: <previous-stage-or-none>
    Current stage: <stage-name>
    Next stage: <next-stage-or-terminal>

    Stage purpose: <one sentence purpose>

    ## Philosophy

    <principles that keep the stage bounded, evidence-backed, and safe>

    ## When To Use

    Use when <repeatable trigger backed by evidence>.

    ## Avoid

    Do not use when <anti-trigger or narrower owner applies>.

    ## Inputs

    - <required path, artifact, report, or user-provided context>

    ## Outputs

    - <required artifact, response schema, command output, or handoff field>

    ## Procedure

    Preconditions: <freshness, authority, source ownership, or dependency condition>.

    1. Confirm the canonical source path and applicable instructions.
    2. Read the smallest evidence surface needed for the stage.
    3. Produce only the required stage deliverable.
    4. Run the validation command and stop at the first failed gate.

    ## Constraints

    Allowed writes: <paths, artifacts, or systems this stage may mutate>.
    Forbidden writes:

    - <generated surfaces, external systems, or downstream-stage outputs>.

    Exit criteria:

    - <conditions required before handoff>

    Handoff: to <next-stage> only after exit criteria pass; otherwise return a blocker.

    ## Execution Boundaries

    - Do not widen scope beyond the named stage.
    - Redact secrets and sensitive data by default.
    - Return blocked_by instead of inventing missing evidence.

    ## Failure Mode

    - <blocker class>: <required recovery action>

    ## Validation

    Run the SDK handoff proof ladder before release, install, sync, publish, or live Tessl claims:

    0. ./bin/ask sdk start <skill-path> --json --robot
    1. ./bin/ask skills audit <skill-path> --level strict --json --robot
    1a. ./bin/ask skills package verify <skill-path> --json --robot
        - reference_quality must include no reference_heading_invocable blockers.
    2. ./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot
    3. ./bin/ask sdk security risk-modes <skill-path> --preview --json --robot
    4. ./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot
    5. ./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot
    6. ./bin/ask sdk eval run <skill-path> --runner internal --mode smoke --codex-profile oss-local --json --robot
    7. ./bin/ask sdk eval run <skill-path> --runner internal --mode smoke --codex-profile oss-cloud --json --robot
    8. ./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace jscraik --execute --json --robot
    9. ./bin/ask evals run <skill-path> --mode smoke --runner discovery-smoke --tessl-live-private --tessl-workspace jscraik --tessl-live-dry-run --json --robot
    10. ./bin/ask sdk eval handoff-readiness --skill <skill-path> --preview --json --robot
    11. ./bin/ask skills external-review <skill-path> --json --robot

    Fail fast at the first failed gate. Treat oss-local as the 70-75 internal discovery band, oss-cloud as the path to >=90 internal success, and Tessl live as external confirmation at >=90 and >= baseline. Do not treat ./bin/ask evals run --runner codex, preview-only Tessl local proof, or a dry-run command string as handoff evidence.

    ## Gotchas

    - <recurring mistake and safer alternative>

    ## Examples

    - Good: <minimal positive example>
    - Bad: <minimal negative example>

    ## References

    - Contract: [contract](./references/contract.yaml)
    - Eval cases: [evals](./references/evals.yaml)
    - Task profile: [task profile](./references/task-profile.json)
    - Source context: [source context](./references/source-context.yaml)

Source context companion:

    schema_version: 1
    skill: <skill-name>
    stage: <stage-name>
    template:
      path: Infrastructure/references/sdk-stage-skill-template.md
      validator: Infrastructure/scripts/validation-and-linting/check_sdk_stage_skill_shape.py
      heading_contract: sdk-deterministic-stage-v1
    original_references:
      - path: <source reference path>
        purpose: <why this reference shaped the skill>
        load_when: <when this reference should be loaded during execution>
    archived_context: []
    stage_companions:
      - path: references/contract.yaml
        purpose: machine-readable stage contract
      - path: references/evals.yaml
        purpose: deterministic trigger and behavior eval cases
      - path: references/task-profile.json
        purpose: reviewer and picker-facing task profile
    provenance_policy:
      canonical_source: <skill directory>
      context_loading: Load SKILL.md first, then source-context.yaml when provenance or deferred context is needed.
      projection_rule: Runtime caches and home skill roots are generated projections, not source.
      template_rule: Preserve the fixed SDK stage heading order.
