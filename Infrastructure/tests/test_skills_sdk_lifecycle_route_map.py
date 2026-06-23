import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.lifecycle_route_map import (  # noqa: E402
    REQUIRED_LOOPS,
    REQUIRED_ROUTE_IDS,
    REQUIRED_STAGES,
    build_lifecycle_route_map_receipt,
)


class TestSkillsSdkLifecycleRouteMap(unittest.TestCase):
    def test_route_map_binds_recommendations_to_artifacts(self) -> None:
        receipt = build_lifecycle_route_map_receipt(REPO_ROOT)

        self.assertEqual(receipt["status"], "pass")
        route_ids = {route["id"] for route in receipt["routes"]}
        self.assertLessEqual(REQUIRED_ROUTE_IDS, route_ids)
        self.assertEqual(receipt["blockers"], [])
        self.assertTrue(all(route["command"].startswith("./bin/ask ") for route in receipt["routes"]))

        for route in receipt["routes"]:
            with self.subTest(route_id=route["id"]):
                self.assertIn("loop", route, f"Route {route['id']} missing 'loop' property")
                self.assertIn("pipeline_stage", route, f"Route {route['id']} missing 'pipeline_stage' property")
                self.assertIn(route["loop"], REQUIRED_LOOPS, f"Route {route['id']} has invalid loop: {route['loop']}")
                self.assertIn(route["pipeline_stage"], REQUIRED_STAGES, f"Route {route['id']} has invalid stage: {route['pipeline_stage']}")


if __name__ == "__main__":
    unittest.main()
