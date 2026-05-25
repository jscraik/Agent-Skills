{
  "reviewer": "maintainability",
  "findings": [
    {
      "severity": "medium",
      "title": "Runtime-separation fixture check is coupled to non-deterministic plugin ordering",
      "confidence": 0.78,
      "evidence": [
        {
          "path": "Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py",
          "line": 149,
          "snippet": "plugins = plugins_payload.get(\"data\", {}).get(\"installed_state\", {}).get(\"plugins\", [])"
        },
        {
          "path": "Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py",
          "line": 151,
          "snippet": "candidate = plugins[0].get(\"name\") if isinstance(plugins[0], dict) else None"
        },
        {
          "path": "Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py",
          "line": 156,
          "snippet": "_assert_envelope(repo_root, [\"Infrastructure/bin/ask\", \"plugins\", \"status\", plugin_name, \"--json\"], timeout_seconds)"
        }
      ],
      "impact": "The check selects whichever plugin appears first in an external list rather than a stable target. If list ordering changes across environments, fixture behavior can drift without any contract change, making failures harder to reason about and increasing long-term maintenance/debug cost.",
      "recommendation": "Use a deterministic selector (for example, sorted plugin names with a stable allowlist or preferred candidate) or validate only list-envelope shape unless a specific plugin identity is required by contract."
    }
  ],
  "residual_risks": [
    "Proof-command literals are duplicated in assertions for skills explain reachability and next_command; future contract string changes require multiple updates."
  ],
  "testing_gaps": [
    "No test currently exercises runtime-separation plugin selection determinism when plugins list returns multiple entries in varying order."
  ]
}
WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-004/unslopify-final-reviewer.md
