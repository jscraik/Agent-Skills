{
  "reviewer": "maintainability",
  "findings": [
    {
      "severity": "high",
      "title": "Codex ABI source path is hardcoded to a machine-local absolute path",
      "evidence": [
        "Infrastructure/scripts/lib/ask/commands/skills_impl.py:2936 hardcodes \"/Users/jamiecraik/dev/codex/codex-rs/core-skills/src/model.rs\" in codex_abi_source.path.",
        "Infrastructure/scripts/lib/ask/commands/skills_impl.py:2970 repeats the same hardcoded path in _empty_skill_package_contract."
      ],
      "impact": "The contract payload encodes host-specific filesystem topology, which drifts across machines/workspaces and makes ABI provenance non-portable for CI and other contributors.",
      "remediation": "Replace the absolute path with a repo-stable identifier (for example a logical source key plus optional relative path when discoverable), or resolve it at runtime with a fallback that avoids embedding user-home paths."
    },
    {
      "severity": "medium",
      "title": "Schema strictness is too loose for a drift-proof contract surface",
      "evidence": [
        "Infrastructure/config/schemas/skill-package.v1.schema.json:6 sets root additionalProperties=true.",
        "Infrastructure/config/schemas/skill-package.v1.schema.json:48 sets metadata.additionalProperties=true.",
        "Infrastructure/config/schemas/skill-package-readiness.v1.schema.json:6 sets root additionalProperties=true."
      ],
      "impact": "Unknown or misspelled keys are silently accepted, weakening schema identity as a guardrail and reducing snapshot/test sensitivity to accidental contract drift.",
      "remediation": "Tighten additionalProperties for contract-critical envelopes (root and metadata) or add a strict compatibility profile for snapshot validation while keeping permissive runtime behavior if needed."
    },
    {
      "severity": "medium",
      "title": "Snapshot projection omits Codex ABI evidence fields from drift checks",
      "evidence": [
        "Infrastructure/tests/test_ask_skills_package_contract.py:143-192 omits skill_package_contract.codex_abi_source in _snapshot_projection.",
        "Infrastructure/tests/test_ask_skills_package_contract.py:161-173 snapshots only metadata.name, description, short_description, and interface, excluding dependencies, policy, scope, and plugin_id."
      ],
      "impact": "Compatibility snapshot checks can pass even if ABI provenance or declared Codex metadata fields regress, which undercuts drift-proof contract identity.",
      "remediation": "Include codex_abi_source and the full Codex metadata field set in snapshot projection, or add a dedicated ABI-focused snapshot assertion."
    }
  ],
  "residual_risks": [
    "Implementation notes still document ABI source as an absolute local path (.harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html:281), so docs and payloads may drift together while remaining non-portable."
  ],
  "testing_gaps": [
    "No explicit test asserts codex_abi_source.path is portable and non-user-specific.",
    "No strict-mode schema test proves unknown top-level fields are rejected for skill-package.v1 and skill-package-readiness.v1."
  ]
}
WROTE: artifacts/reviews/jsc-351-pu004/maintainability-docs.md
