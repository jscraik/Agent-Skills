# Output Schema

Use for structured, risky, blocked, handoff, or eval-proof output.

~~~json
{
  "fresh_evidence": [{"file": "path:line", "claim": ""}],
  "missing_evidence": [],
  "agent_safe_boundary": {"status": "safe|risky|blocked", "evidence": [], "reason": ""},
  "source_of_truth": {"path": "", "status": "canonical|generated|projection|cache|unknown"},
  "public_surface": [],
  "caller_map": {"status": "complete|partial|missing", "evidence": []},
  "integration_path": {"entrypoint": "", "registration": [], "normal_caller": [], "status": "wired|partial|orphaned|unknown", "evidence": []},
  "change_class": "patch|staged_adoption|interface_migration|ownership_move|dependency_direction|abstraction|projection_lifecycle|evidence_only|no_justified_edit",
  "adoption_stages": [{"stage": "", "owner": "", "entry_condition": "", "verifier": "", "rollback": ""}],
  "patch_design": {"change": "", "reversible": true, "public_contract_change": false, "caller_impact": "known|partial|unknown", "verifier": "", "risk": ""},
  "interface_design": {"change": "", "migration_needed": true, "owner_alignment": "present|missing", "caller_map": "complete|partial|missing", "tracer": "present|missing", "verifier": "", "risk": ""},
  "request_user_input": null,
  "recommended_first_move": "",
  "tracer_proof": "",
  "validation": [{"command": "", "outcome": "pass|fail|blocked"}],
  "decision_surface": "",
  "confidence": "low|medium|high",
  "schema_version": 1
}
~~~

For prose, preserve the same concepts without emitting JSON.
