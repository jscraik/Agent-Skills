#!/usr/bin/env python3
"""Import-light tests for run_skill_evals assertion semantics."""

from __future__ import annotations

import sys
import textwrap
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_skill_evals import evaluate_assertions_json, evaluate_assertions_text  # noqa: E402


def _publication_markdown() -> str:
    return textwrap.dedent(
        """
        **Routing**

        - publication_gate_status: draft_only
        - evidence_level: user-supplied brief only
        - primary_draft: absent
        """
    )


def _publication_assertions() -> list[dict[str, object]]:
    return [
        {"type": "text_field_equals", "field": "publication_gate_status", "value": "draft_only"},
        {
            "type": "text_field_in",
            "fields": ["source_confidence", "evidence_level"],
            "values": ["supplied brief only", "user-supplied brief only"],
        },
        {"type": "text_field_absent", "field": "external_factual_claims"},
    ]


class RunSkillEvalsAssertionTests(unittest.TestCase):
    def test_text_field_acceptance_checks_markdown_key_values_without_regex(self) -> None:
        self.assertEqual(
            evaluate_assertions_text(
                _publication_markdown(),
                _publication_assertions(),
                skill_name="x-content-writer",
                selected_skill=True,
            ),
            [],
        )

        failures = evaluate_assertions_text(
            _publication_markdown(),
            [
                {
                    "type": "text_field_equals",
                    "fields": ["publication_status", "publication_gate_status"],
                    "value": "published",
                }
            ],
            skill_name="x-content-writer",
            selected_skill=True,
        )
        self.assertEqual(
            failures,
            ["text_field_equals failed at publication_status|publication_gate_status: got='draft_only' expected='published'"],
        )

    def test_text_field_acceptance_checks_structured_json_without_trailing_commas(self) -> None:
        output = {
            "publication_gate_status": "draft_only",
            "evidence_level": "user-supplied brief only",
            "next_step": "write blocker note",
        }

        self.assertEqual(
            evaluate_assertions_json(
                output,
                _publication_assertions(),
                skill_name="x-content-writer",
                selected_skill=True,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
