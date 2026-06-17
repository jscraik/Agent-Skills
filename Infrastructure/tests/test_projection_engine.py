import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

from projection_engine import (  # noqa: E402
    ProjectionModeError,
    normalize_projection_mode,
)


class TestProjectionEngine(unittest.TestCase):
    def test_default_projection_mode_is_flat(self) -> None:
        decision = normalize_projection_mode(env={})

        self.assertEqual(decision.projection_mode, "flat")
        self.assertEqual(decision.mode_source, "default")

    def test_env_projection_mode_rejects_removed_rooted_mode(self) -> None:
        with self.assertRaises(ProjectionModeError) as ctx:
            normalize_projection_mode(env={"SYNC_SKILLS_PROJECTION_MODE": "rooted"})

        self.assertEqual(ctx.exception.code, "ERR_INVALID_PROJECTION_MODE")

    def test_cli_projection_mode_wins_over_env(self) -> None:
        decision = normalize_projection_mode("flat", env={"SYNC_SKILLS_PROJECTION_MODE": "hybrid"})

        self.assertEqual(decision.projection_mode, "flat")
        self.assertEqual(decision.mode_source, "cli")

    def test_skill_tree_alias_is_removed_with_rooted_mode(self) -> None:
        with self.assertRaises(ProjectionModeError) as ctx:
            normalize_projection_mode("skill-tree", env={})

        self.assertEqual(ctx.exception.code, "ERR_INVALID_PROJECTION_MODE")

    def test_hybrid_is_deferred(self) -> None:
        with self.assertRaises(ProjectionModeError) as ctx:
            normalize_projection_mode("hybrid", env={})

        self.assertEqual(ctx.exception.code, "ERR_DEFERRED_PROJECTION_MODE")


if __name__ == "__main__":
    unittest.main()
