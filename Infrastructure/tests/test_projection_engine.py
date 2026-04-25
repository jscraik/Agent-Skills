import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

from projection_engine import (  # noqa: E402
    ProjectionModeError,
    ensure_mutation_supported,
    normalize_projection_mode,
)


class TestProjectionEngine(unittest.TestCase):
    def test_default_projection_mode_is_rooted(self) -> None:
        decision = normalize_projection_mode(env={})

        self.assertEqual(decision.projection_mode, "rooted")
        self.assertEqual(decision.mode_source, "default")
        self.assertTrue(decision.mutation_available)

    def test_env_projection_mode_is_used_when_cli_missing(self) -> None:
        decision = normalize_projection_mode(env={"SYNC_SKILLS_PROJECTION_MODE": "rooted"})

        self.assertEqual(decision.projection_mode, "rooted")
        self.assertEqual(decision.mode_source, "env")
        self.assertTrue(decision.mutation_available)

    def test_cli_projection_mode_wins_over_env(self) -> None:
        decision = normalize_projection_mode("flat", env={"SYNC_SKILLS_PROJECTION_MODE": "rooted"})

        self.assertEqual(decision.projection_mode, "flat")
        self.assertEqual(decision.mode_source, "cli")

    def test_skill_tree_alias_maps_to_rooted(self) -> None:
        decision = normalize_projection_mode("skill-tree", env={})

        self.assertEqual(decision.projection_mode, "rooted")
        self.assertEqual(decision.alias_of, "rooted")

    def test_hybrid_is_deferred(self) -> None:
        with self.assertRaises(ProjectionModeError) as ctx:
            normalize_projection_mode("hybrid", env={})

        self.assertEqual(ctx.exception.code, "ERR_DEFERRED_PROJECTION_MODE")

    def test_rooted_non_dry_run_is_mutation_supported(self) -> None:
        decision = normalize_projection_mode("rooted", env={})

        ensure_mutation_supported(decision, dry_run=False)


if __name__ == "__main__":
    unittest.main()
