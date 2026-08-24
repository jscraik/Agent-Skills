"""Direct rendering contracts for successful human-facing ask CLI output."""

from __future__ import annotations

import contextlib
import io
import unittest
from types import SimpleNamespace

from ask_test_paths import ensure_ask_lib_path


ensure_ask_lib_path()

from ask.cli_human_success import render_success  # noqa: E402
from ask.envelope import CallResult  # noqa: E402


def _args(topic: str, action: str, **values: object) -> SimpleNamespace:
    return SimpleNamespace(topic=topic, action=action, **values)


def _render(args: SimpleNamespace, data: dict[str, object]) -> str:
    result = CallResult(status="success", data=data)
    result.metadata["command"] = "ask repo status"
    with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
        render_success(None, args, result)
        return buffer.getvalue()


class TestRenderSuccess(unittest.TestCase):
    def test_renders_repo_status_and_validation_command(self) -> None:
        output = _render(
            _args("repo", "status"),
            {
                "repo_root": "/repo",
                "skills_synced": True,
                "validation_commands": ["./bin/ask repo status --json --robot"],
            },
        )

        self.assertEqual(
            output,
            "✅ Success: ask repo status\n"
            "  Root: /repo\n"
            "  Synced: True\n"
            "Validation: ./bin/ask repo status --json --robot\n",
        )

    def test_renders_profiles_readiness_without_a_name_error(self) -> None:
        output = _render(
            _args("skills", "profiles"),
            {
                "skill_profiles": {
                    "status": "pass",
                    "agent_summary": "Profiles are ready.",
                    "profile_order": ["standard"],
                    "validation_commands": ["./bin/ask skills profiles --json --robot"],
                },
            },
        )

        self.assertIn("Skill profiles: pass", output)
        self.assertIn("Profiles are ready.", output)
        self.assertIn("Profiles: standard", output)
        self.assertIn("Validation: ./bin/ask skills profiles --json --robot", output)

    def test_preserves_graph_list_identifier_alignment(self) -> None:
        output = _render(
            _args("graph", "list"),
            {
                "filters": {"topic": None, "tier": None},
                "count": 1,
                "skills": [
                    {
                        "id": "example-skill",
                        "topic": "testing",
                        "tier": "stable",
                        "in_degree": 2,
                    }
                ],
                "validation_commands": ["./bin/ask graph list --json --robot"],
            },
        )

        self.assertIn(f"★ {'example-skill':<35} [testing] ↓2", output)
        self.assertIn("Validation: ./bin/ask graph list --json --robot", output)

    def test_does_not_render_unmatched_success_topic(self) -> None:
        self.assertEqual(_render(_args("unknown", "noop"), {}), "")


if __name__ == "__main__":
    unittest.main()
