import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.golden_path import build_golden_path_payload, render_golden_path_summary  # noqa: E402


class TestAskGoldenPath(unittest.TestCase):
    def test_blockers_are_sorted_and_select_primary_next_command(self) -> None:
        payload = build_golden_path_payload(
            signals={
                "zeta": {
                    "state": "block",
                    "severity": "blocker",
                    "summary": "Zeta blocked.",
                    "next_command": "ask zeta",
                },
                "alpha": {
                    "state": "block",
                    "severity": "blocker",
                    "summary": "Alpha blocked.",
                    "next_command": "ask alpha",
                },
            },
            normal_next_command="ask repo status",
        )

        self.assertTrue(payload["blocking"])
        self.assertEqual([item["id"] for item in payload["blockers"]], ["alpha", "zeta"])
        self.assertEqual(payload["next_command"], "ask alpha")
        self.assertEqual(payload["next_command_kind"], "blocking_repair")
        self.assertTrue(payload["next_command_blocks_task"])

    def test_all_pass_uses_normal_next_command(self) -> None:
        payload = build_golden_path_payload(
            signals={
                "repo_status": {
                    "state": "pass",
                    "severity": "info",
                    "summary": "Repository status is readable.",
                },
            },
            normal_next_command="./bin/ask repo status --json --robot",
        )

        self.assertFalse(payload["blocking"])
        self.assertEqual(payload["blockers"], [])
        self.assertEqual(payload["diagnostic_debt"], [])
        self.assertEqual(payload["next_command"], "./bin/ask repo status --json --robot")
        self.assertEqual(payload["next_command_kind"], "normal_inspection")
        self.assertFalse(payload["next_command_blocks_task"])

    def test_diagnostic_warning_selects_advisory_next_command(self) -> None:
        payload = build_golden_path_payload(
            signals={
                "repo_surface": {
                    "state": "warn",
                    "severity": "warning",
                    "summary": "Repo surface has diagnostic debt.",
                    "next_command": "./bin/ask repo surface --json --robot",
                },
            },
            normal_next_command="./bin/ask repo status --json --robot",
        )

        self.assertFalse(payload["blocking"])
        self.assertEqual(payload["blockers"], [])
        self.assertEqual(payload["diagnostic_debt"][0]["id"], "repo_surface")
        self.assertEqual(payload["next_command"], "./bin/ask repo surface --json --robot")
        self.assertEqual(payload["next_command_kind"], "diagnostic_advisory")
        self.assertFalse(payload["next_command_blocks_task"])

    def test_blocker_without_recovery_is_classified_as_no_safe_command(self) -> None:
        payload = build_golden_path_payload(
            signals={
                "catalog_parity": {
                    "state": "block",
                    "severity": "blocker",
                    "summary": "Catalog parity blocked without recovery.",
                },
            },
            normal_next_command="./bin/ask repo status --json --robot",
        )

        self.assertTrue(payload["blocking"])
        self.assertEqual(payload["next_command"], None)
        self.assertEqual(payload["next_command_kind"], "no_safe_command")
        self.assertTrue(payload["next_command_blocks_task"])

    def test_render_summary_supports_success_and_error_shapes(self) -> None:
        payload = {
            "agent_summary": "Usable: repo doctor found no blocking issues.",
            "blocking": False,
            "next_command": "./bin/ask repo status --json --robot",
        }

        self.assertEqual(
            render_golden_path_summary(payload, title="Repo doctor", status_icon="✅"),
            [
                "✅ Repo doctor: Usable: repo doctor found no blocking issues.",
                "  Blocking: False",
                "  Next: ./bin/ask repo status --json --robot",
            ],
        )
        self.assertEqual(
            render_golden_path_summary(payload, indent="   "),
            [
                "   Summary: Usable: repo doctor found no blocking issues.",
                "   Blocking: False",
                "   Next: ./bin/ask repo status --json --robot",
            ],
        )


if __name__ == "__main__":
    unittest.main()
