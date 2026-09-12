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

from run_skill_evals import detect_skill_selected, evaluate_assertions_json, evaluate_assertions_text  # noqa: E402
import run_skill_evals_assertions as assertions_module  # noqa: E402
import run_skill_evals_assertions_core as assertions_core  # noqa: E402


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
    def test_existing_runner_reexports_remain_available(self) -> None:
        self.assertTrue(set(assertions_core.__all__).issubset(assertions_module.__all__))
        for name in assertions_core.__all__:
            with self.subTest(name=name):
                self.assertIs(getattr(assertions_module, name), getattr(assertions_core, name))
        with self.assertRaises(AttributeError):
            getattr(assertions_module, "unknown_export")

    def test_selection_ignores_file_links_and_tool_output(self) -> None:
        output = "The fix is present at [alignment-checkpoint/SKILL.md:70](/repo/Skills/alignment-checkpoint/SKILL.md:70)."
        selected = detect_skill_selected(
            skill_name="alignment-checkpoint", output_text=output,
            stdout_text='{"output":"Using alignment-checkpoint"}',
            stderr_text="skill_name: alignment-checkpoint",
            events=[{"type": "item.completed", "item": {
                "type": "command_execution", "aggregated_output": "Using alignment-checkpoint"
            }}],
        )
        self.assertIsNone(selected)
        self.assertEqual(evaluate_assertions_text(output, [
            {"type": "skill_not_selected", "expected_skill": "alignment-checkpoint"}
        ], skill_name="alignment-checkpoint", selected_skill=selected), [])

    def test_selection_preserves_real_activation_and_exact_identity(self) -> None:
        for output, events, expected in [
            ("I am using alignment-checkpoint for this decision.", [], True),
            ("I'm applying the supplied alignment-checkpoint skill directly.", [], True),
            ("I did not use alignment-checkpoint.", [], False),
            ("I used rg to inspect alignment-checkpoint/SKILL.md.", [], None),
            ("I am using alignment-checkpoint-extra.", [], None),
            ("", [{"selected_skill": "alignment-checkpoint"}], True),
            ("", [{"selected_skill": "alignment-checkpoint-extra"}], None),
            ("", [{"type": "item.completed", "item": {
                "type": "agent_message", "text": "I am using alignment-checkpoint."
            }}], True),
        ]:
            with self.subTest(output=output, events=events):
                self.assertIs(detect_skill_selected(
                    skill_name="alignment-checkpoint", output_text=output,
                    stdout_text="", stderr_text="", events=events,
                ), expected)

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
