{
  "reviewer": "maintainability",
  "findings": [
    {
      "severity": "medium",
      "title": "SkillPackage metadata envelope still accepts unknown keys",
      "evidence": [
        "Infrastructure/config/schemas/skill-package.v1.schema.json:48 keeps metadata.additionalProperties=true."
      ],
      "impact": "The remediation intent was to tighten schema drift boundaries, but unknown metadata keys are still silently accepted, so typo or contract-sprawl drift inside metadata will not be caught by schema validation or snapshot checks.",
      "remediation": "Set metadata.additionalProperties=false and explicitly enumerate allowed metadata keys, or document and test a deliberate compatibility exception if extensibility is required."
    }
  ],
  "residual_risks": [
    "Top-level readiness and contract envelopes are now strict, but metadata-level drift remains possible until metadata key strictness is resolved."
  ],
  "testing_gaps": [
    "No test currently asserts rejection of an unknown key inside skill_package_contract.metadata."
  ]
}
WROTE: artifacts/reviews/jsc-351-pu004/maintainability-docs-rereview.md
