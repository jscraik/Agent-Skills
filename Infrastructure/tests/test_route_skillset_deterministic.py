import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROUTE_SCRIPT = "Infrastructure/scripts/lifecycle-and-sync/route_skillset.py"
SOURCE_PATHS = {
    "he-brainstorm": "Plugins/harness-engineering/skills/he-brainstorm/SKILL.md",
    "he-code-review": "Plugins/harness-engineering/skills/he-code-review/SKILL.md",
    "he-ideate": "Plugins/harness-engineering/skills/team_automation/he-ideate/SKILL.md",
    "he-router": "Plugins/harness-engineering/skills/he-router/SKILL.md",
    "he-technical-review": "Plugins/harness-engineering/skills/code_quality_review/he-technical-review/SKILL.md",
    "he-tdd": "Plugins/harness-engineering/skills/team_automation/he-tdd/SKILL.md",
    "he-work": "Plugins/harness-engineering/skills/he-work/SKILL.md",
    "plugin-builder": "Plugins/plugin-factory/skills/code_quality_review/plugin-builder/SKILL.md",
    "plugin-creator": "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md",
    "plugin-factory-router": "Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md",
    "plugin-installer": "Plugins/plugin-factory/skills/infrastructure_ops/plugin-installer/SKILL.md",
    "plugin-router": "Plugins/plugin-factory/skills/team_automation/plugin-router/SKILL.md",
    "skill-builder": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
    "skill-creator": "Plugins/skill-factory/skills/scaffolding_templates/skill-creator/SKILL.md",
    "skill-factory-router": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
    "skillify": "Plugins/skill-factory/skills/scaffolding_templates/skillify/SKILL.md",
}


def _write_manifest(root: Path, skill_set: str, rows: list[dict[str, object]]) -> None:
    manifest_dir = root / skill_set
    manifest_dir.mkdir(parents=True)
    with (manifest_dir / "manifest.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _write_source_files(root: Path, rows: list[dict[str, object]]) -> None:
    for row in rows:
        source_path = str(row.get("source_path", ""))
        if not source_path or "Plugins/missing/" in source_path:
            continue
        skill_file = root / source_path
        skill_file.parent.mkdir(parents=True, exist_ok=True)
        skill_file.write_text("# Test skill\n", encoding="utf-8")


def _row(skill_id: str, description: str) -> dict[str, object]:
    return {
        "id": skill_id,
        "description": description,
        "level": "atom",
        "source_path": SOURCE_PATHS[skill_id],
        "triggers": [skill_id.replace("-", " ")],
    }


class TestRouteSkillsetDeterministic(unittest.TestCase):
    def _route(
        self,
        skill_set: str,
        task: str,
        rows: list[dict[str, object]],
        *,
        expected_returncode: int = 0,
    ) -> dict[str, object]:
        with tempfile.TemporaryDirectory(prefix="route-skillset-") as tmp:
            fixture_root = Path(tmp)
            skillsets_dir = fixture_root / ".skillsets"
            _write_source_files(fixture_root, rows)
            _write_manifest(skillsets_dir, skill_set, rows)
            result = subprocess.run(
                [
                    "python3",
                    ROUTE_SCRIPT,
                    "--skill-set",
                    skill_set,
                    "--task",
                    task,
                    "--skillsets-dir",
                    str(skillsets_dir),
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, expected_returncode, result.stderr)
        return json.loads(result.stdout)

    def test_plugin_factory_create_routes_to_creator(self) -> None:
        payload = self._route(
            "plugin-factory",
            "create a new plugin",
            [
                _row("plugin-builder", "Harden and validate plugin packages."),
                _row("plugin-creator", "Scaffold a minimal Codex plugin package."),
                _row("plugin-factory-router", "Route plugin work."),
            ],
        )

        self.assertEqual(payload["selected"]["id"], "plugin-creator")
        self.assertIn("deterministic plugin-factory", payload["candidates"][0]["reason"])

    def test_plugin_factory_mixed_intent_routes_to_router(self) -> None:
        payload = self._route(
            "plugin-factory",
            "create and validate a new plugin",
            [
                _row("plugin-builder", "Harden and validate plugin packages."),
                _row("plugin-creator", "Scaffold a minimal Codex plugin package."),
                _row("plugin-factory-router", "Route plugin work."),
            ],
        )

        self.assertEqual(payload["selected"]["id"], "plugin-factory-router")

    def test_plugin_factory_visibility_repair_routes_to_installer(self) -> None:
        payload = self._route(
            "plugin-factory",
            "repair plugin visibility after import",
            [
                _row("plugin-builder", "Harden and validate plugin packages."),
                _row("plugin-creator", "Scaffold a minimal Codex plugin package."),
                _row("plugin-factory-router", "Route plugin work."),
                _row("plugin-installer", "Install validated plugins with provenance and rollback safety."),
            ],
        )

        self.assertEqual(payload["selected"]["id"], "plugin-installer")
        self.assertIn("install-plugin", payload["candidates"][0]["reason"])

    def test_plugin_factory_internal_lane_mentions_route_to_router(self) -> None:
        payload = self._route(
            "plugin-factory",
            "should I use plugin-builder or plugin-router for this package?",
            [
                _row("plugin-builder", "Harden and validate plugin packages."),
                _row("plugin-factory-router", "Route plugin work."),
                _row("plugin-router", "Route plugin tasks."),
            ],
        )

        self.assertEqual(payload["selected"]["id"], "plugin-factory-router")
        self.assertIn("internal-lane-mention", payload["candidates"][0]["reason"])

    def test_skill_factory_create_routes_to_creator(self) -> None:
        payload = self._route(
            "skill-factory",
            "create a new skill",
            [
                _row("skill-builder", "Harden and validate skills."),
                _row("skill-creator", "Guide for creating effective skills."),
                _row("skill-factory-router", "Route skill work."),
            ],
        )

        self.assertEqual(payload["selected"]["id"], "skill-creator")

    def test_skill_factory_workflow_to_skill_routes_to_skillify(self) -> None:
        payload = self._route(
            "skill-factory",
            "turn this session workflow into a reusable skill",
            [
                _row("skill-builder", "Harden and validate skills."),
                _row("skill-factory-router", "Route skill work."),
                _row("skillify", "Turn repeated workflows into skills."),
            ],
        )

        self.assertEqual(payload["selected"]["id"], "skillify")
        self.assertIn("skillify-workflow", payload["candidates"][0]["reason"])

    def test_harness_engineering_folded_direct_stage_routes_to_parent(self) -> None:
        payload = self._route(
            "harness-engineering",
            "use he-ideate to explore options",
            [
                _row("he-brainstorm", "Shape ambiguous requirements and compare directions."),
                _row("he-ideate", "Generate and compare implementation opportunities."),
                _row("he-router", "Route Harness Engineering stages."),
            ],
        )

        self.assertEqual(payload["selected"]["id"], "he-brainstorm")
        self.assertIn("folded stage alias 'he-ideate'", payload["candidates"][0]["reason"])

    def test_harness_engineering_folded_review_stage_routes_to_parent(self) -> None:
        payload = self._route(
            "harness-engineering",
            "run he-technical-review on the PR comments",
            [
                _row("he-code-review", "Review PRs for readiness and technical risk."),
                _row("he-router", "Route Harness Engineering stages."),
                _row("he-technical-review", "Deep technical review."),
            ],
        )

        self.assertEqual(payload["selected"]["id"], "he-code-review")
        self.assertIn("folded stage alias 'he-technical-review'", payload["candidates"][0]["reason"])

    def test_harness_engineering_folded_stage_correctness_still_routes_to_router(self) -> None:
        payload = self._route(
            "harness-engineering",
            "is he-tdd right for this request?",
            [
                _row("he-router", "Route Harness Engineering stages."),
                _row("he-tdd", "Test-first implementation."),
                _row("he-work", "Implement approved work."),
            ],
        )

        self.assertEqual(payload["selected"]["id"], "he-router")
        self.assertIn("stage-correctness-question", payload["candidates"][0]["reason"])

    def test_manifest_with_missing_source_path_returns_invalid(self) -> None:
        payload = self._route(
            "skill-factory",
            "create a new skill",
            [
                {
                    **_row("skill-creator", "Guide for creating effective skills."),
                    "source_path": "Plugins/missing/skills/skill-creator/SKILL.md",
                },
            ],
            expected_returncode=1,
        )

        self.assertEqual(payload["status"], "manifest_invalid")
        self.assertIsNone(payload["selected"])
        self.assertIn("source_path", payload["error"])
        self.assertIn("does not exist", payload["error"])


if __name__ == "__main__":
    unittest.main()
