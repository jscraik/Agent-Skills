{
  "reviewer": "maintainability",
  "findings": [
    {
      "severity": "medium",
      "title": "Unused wrapper adds an extra indirection layer for next-command selection",
      "evidence": [
        {
          "file": "Infrastructure/scripts/lib/ask/commands/skills_impl.py",
          "line": 2717,
          "detail": "_skill_doctor_next_command(...) is defined as a thin wrapper that only calls _skill_doctor_next_command_decision(...)[\"command\"]."
        },
        {
          "file": "Infrastructure/scripts/lib/ask/commands/skills_impl.py",
          "line": 3497,
          "detail": "Production code in skills_doctor already calls _skill_doctor_next_command_decision(...) directly."
        },
        {
          "file": "Infrastructure/tests/test_ask_skills_doctor.py",
          "line": 637,
          "detail": "The wrapper is only exercised by tests, which keeps a non-production helper alive as API surface."
        }
      ],
      "remediation": "Delete _skill_doctor_next_command and have tests assert against _skill_doctor_next_command_decision()[\"command\"] directly. This removes a dead pass-through and keeps the decision contract singular.",
      "confidence": 0.9
    },
    {
      "severity": "low",
      "title": "Implementation notes still include future-tense planning text in an implementation section",
      "evidence": [
        {
          "file": ".harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html",
          "line": 261,
          "detail": "The note says \"T012 will add those machine-readable fields...\", which reads as planned work rather than current-state evidence."
        }
      ],
      "remediation": "Rewrite this sentence to past/present evidence language (what is implemented and validated now) or move future intent into an explicit planning section outside implementation evidence.",
      "confidence": 0.88
    }
  ],
  "residual_risks": [
    "next_command_decision in schema allows additionalProperties=true, so accidental extra keys can ship without contract pressure; this is acceptable for compatibility but may weaken long-term payload discipline."
  ],
  "testing_gaps": []
}
