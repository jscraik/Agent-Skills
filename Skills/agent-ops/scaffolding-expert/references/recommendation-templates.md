# Recommendation Templates

## Tier Decision Output

```yaml
schema_version: "1.0"
recommendation_type: scaffold_tier_decision
tier: lite|growth|strict
confidence: high|medium|low
style_profile:
  source: Infrastructure/scripts/profile-dev-repos.sh --root <path> | skipped
  repo_count: <n>
  key_signals:
    - <signal>
  alignment_note: <how recommendation matches or intentionally diverges from observed style>
signals:
  - signal: <name>
    score: 0-3
    rationale: <why>
summary: <one-paragraph rationale>
next_actions:
  - <action 1>
  - <action 2>
```

## Drift Audit Output

```yaml
schema_version: "1.0"
recommendation_type: drift_conflict_audit
overall_risk: critical|high|medium|low
findings:
  - severity: critical|high|medium|low
    surface: instructions|validation|toolchain|projection|governance
    files:
      - /abs/path/file
    symptom: <what is wrong>
    minimum_fix: <smallest correction>
validation_plan:
  - lane: style-profile|shared|npm|bash|uv-python|external-docs
    commands:
      - <exact command>
blocked_by:
  - <blocker or empty list>
```

## Remediation Plan Output

```yaml
schema_version: "1.0"
recommendation_type: remediation_plan
ordered_steps:
  - id: 1
    action: <action>
    reason: <why first>
    blast_radius: low|medium|high
  - id: 2
    action: <action>
success_criteria:
  - <observable check>
```
