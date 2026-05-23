{
  "reviewer": "testing",
  "findings": [
    {
      "severity": "medium",
      "title": "Skill package metadata contract still permits undeclared keys, so drift is not blocked",
      "evidence": [
        "Infrastructure/config/schemas/skill-package.v1.schema.json:48",
        "Infrastructure/tests/test_ask_skills_package_contract.py:248"
      ],
      "why_it_matters": "PU-004 compatibility aims to be drift-proof around Codex metadata identity. metadata.additionalProperties remains true, so unexpected metadata keys pass schema validation, and there is no negative test injecting an unknown metadata key to prove rejection.",
      "remediation": "Set skill-package.v1 metadata.additionalProperties to false and add a contract test that injects an unknown key under skill_package_contract.metadata and asserts schema validation fails."
    }
  ],
  "testing_gaps": [],
  "residual_risks": []
}
