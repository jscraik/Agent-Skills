# Agent-Native Compression Contract

Read when: HE work touches a user-facing command, docs entrypoint, workflow
gate, artifact, policy surface, command catalog, or "cockpit" / "next" style
experience.

## Non-Negotiable Rule

An agent should only need to remember the golden-path entrypoint for the target
product. In coding-harness-managed repos, that entrypoint is:

```sh
harness next --json
```

Every other visible surface must prove why it remains first-contact visible, or
it must become one of:

- selected by the golden-path entrypoint
- emitted inside a readiness packet such as `pr-ready`
- emitted inside a learning packet such as `learn`
- hidden as advanced or plumbing
- archived, deprecated, merged, or deleted

Classification, metadata, docs routing, and command existence are not
compression by themselves.

## Required Gates

- First-contact budget: default help or README front-door surfaces must expose
  only the small set of public rails needed to start, check, diagnose, and list
  agent-safe commands. Full catalogs require an explicit advanced/all flag.
- Agent catalog budget: agent-facing command catalogs should be limited to
  public rails by purpose, not to every useful expert command.
- Standalone command admission: a new top-level command is blocked unless the
  spec or plan proves why it cannot be a subcommand, recommendation, readiness
  section, learning stage, or hidden plumbing command.
- Docs deletion budget: cockpit or agent-native plans must remove, collapse, or
  demote at least as much first-contact prose as they add.
- Fresh-agent eval: acceptance must include a new-session path that starts from
  the golden-path command, follows its recommendation, produces evidence, and
  reaches ready-or-blocked without opening docs for basic navigation.
- Ablation proof: every visible command family must answer whether hiding it
  from default help, making it reachable only through the golden path, or merging
  it into readiness/learning would make task completion worse.
- Evidence-backed metric: status matrices are not source of truth for north-star
  progress; use generated evidence for lead time, retries, interventions, merge
  blockers, or record a blocking evidence gap.

## Stage Duties

- `he-spec`: make compression gates acceptance criteria whenever prior work
  failed because additive compatibility was treated as harder than
  decluttering.
- `he-plan`: sequence the subtractive moves first: default-help budget, agent
  catalog budget, docs front-door rewrite, admission tests, fresh-agent eval,
  and ablation decisions.
- `he-work`: implement the smallest subtractive slice before adding new
  metadata, docs, or policy surfaces.
- `he-code-review`: block readiness when implementation proves presence but not
  compression, fresh-agent usability, or ablation.
- `he-compound`: when a lifecycle diagnosis says `spec_refresh_required` for
  product compression, route back to `he-spec` instead of approving more
  implementation.
- `he-improve`: prefer tightening an existing shared contract, eval, or high
  traffic stage over creating another standalone skill.

## Blackboard Delta Shape

```yaml
schema_version: he-blackboard-delta/v1
topic: agent-native-compression
finding:
  previous_specs_failed_because: compression was advisory while additive compatibility was mandatory
  golden_path: harness next --json
  recovery_stage: spec_refresh_required
  non_negotiable_rule: agents should only need to remember the golden-path command
  required_gates:
    - first_contact_budget
    - agent_catalog_budget
    - standalone_command_admission
    - docs_deletion_budget
    - fresh_agent_eval
    - ablation_proof
    - evidence_backed_metric
```
