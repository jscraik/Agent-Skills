# Skill Refactor Evidence Routing

Use this reference when a lifecycle analysis needs collector, generated-artifact, or external-document routing details. Keep the SKILL.md entrypoint focused on the decision workflow.

## Collector Inputs

Preferred session-collector inputs include:

- `skill_refactor_handoffs`
- `skill_refactor_evidence`
- `skillify_candidates`
- `skill_invocations`
- `skill_proof_candidates`
- bounded extracts from `~/.agents/session-collector/` outputs

Use raw transcripts only after bounded evidence is insufficient. Preserve collector-native root-cause labels when present; put derived analysis labels in `normalized_root_causes`.

## Generated Artifacts

Preferred generated collector artifacts include:

- `skill-invocations.json`
- `skill-invocation-summary.json`
- `skill-proof-candidates.json`
- `skillify-candidates.json`
- `skill-refactor-handoffs.json`
- `harness-engineering-evidence.json`

When using a combined collector bundle, prefer these fields before raw session bodies:

- `evidence_layers.skill_refactor_handoffs`
- `evidence_layers.skill_refactor_evidence`
- `evidence_layers.skillify_candidates`

## External Knowledge

Preserve route boundaries: use `openai-docs` only for official OpenAI, Codex, API, model, plugin, or skill behavior. Use current non-OpenAI dependency or API documentation only when the lifecycle question depends on external behavior.

Do not replace local session evidence with external docs when the question is about observed local behavior.
