from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.docs_projection import (  # noqa: E402
    CANONICAL_ATLAS_PIPELINE_STEPS,
    verify_capability_docs_projection,
)
from ask.skills_sdk.typed_contracts import validate_robot_envelope  # noqa: E402


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


class TestSkillsSdkDocsProjection(unittest.TestCase):
    def test_default_capability_projection_matches_matrix(self) -> None:
        payload = verify_capability_docs_projection(REPO_ROOT)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["capability_count"], payload["projection_row_count"])
        self.assertFalse(payload["mutation_performed"])

    def test_public_cli_verifies_docs_projection(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "docs",
                "verify",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_docs_verify"]

        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["artifact_path"], "artifacts/recommended-skills-sdk-pipeline.html")

    def test_public_cli_verifies_reference_atlas_projection(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "docs",
                "verify",
                "--artifact",
                "Docs/reference/skills-sdk-platform-atlas.html",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_docs_verify"]

        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["artifact_path"], "Docs/reference/skills-sdk-platform-atlas.html")

    def test_verifier_blocks_status_drift(self) -> None:
        source = REPO_ROOT / "artifacts/recommended-skills-sdk-pipeline.html"
        with tempfile.TemporaryDirectory() as tmpdir:
            drifted = Path(tmpdir) / "drifted.html"
            drifted.write_text(
                source.read_text(encoding="utf-8").replace(
                    'data-capability-id="skill_ir" data-status="implemented"',
                    'data-capability-id="skill_ir" data-status="deferred"',
                    1,
                ),
                encoding="utf-8",
            )

            payload = verify_capability_docs_projection(REPO_ROOT, artifact_path=drifted)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["blockers"][0]["code"], "status_mismatch")
        self.assertEqual(payload["blockers"][0]["rows"][0]["id"], "skill_ir")

    def test_verifier_blocks_duplicate_capability_rows(self) -> None:
        source = REPO_ROOT / "artifacts/recommended-skills-sdk-pipeline.html"
        duplicate = (
            '<tr data-capability-id="skill_ir" data-status="implemented" '
            'data-pipeline-sections="compiler_emitter_discipline,domain_model_integrity,public_sdk_surface"></tr>'
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            drifted = Path(tmpdir) / "duplicate.html"
            drifted.write_text(source.read_text(encoding="utf-8") + duplicate, encoding="utf-8")

            payload = verify_capability_docs_projection(REPO_ROOT, artifact_path=drifted)

        self.assertEqual(payload["status"], "blocked")
        blocker_codes = {blocker["code"] for blocker in payload["blockers"]}
        self.assertIn("duplicate_capability_rows", blocker_codes)

    def test_verifier_blocks_visible_summary_count_drift(self) -> None:
        source = REPO_ROOT / "Docs/reference/skills-sdk-platform-atlas.html"
        with tempfile.TemporaryDirectory() as tmpdir:
            drifted = Path(tmpdir) / "drifted-summary.html"
            drifted.write_text(
                source.read_text(encoding="utf-8").replace(
                    'data-capability-summary-statuses="preview_only" data-count="18"',
                    'data-capability-summary-statuses="preview_only" data-count="17"',
                    1,
                ),
                encoding="utf-8",
            )

            payload = verify_capability_docs_projection(REPO_ROOT, artifact_path=drifted)

        self.assertEqual(payload["status"], "blocked")
        summary_blocker = next(
            blocker for blocker in payload["blockers"] if blocker["code"] == "summary_count_mismatch"
        )
        self.assertEqual(summary_blocker["expected"], 18)
        self.assertEqual(summary_blocker["actual"], 17)

    def test_verifier_enforces_canonical_atlas_pipeline_order(self) -> None:
        source = REPO_ROOT / "Docs/reference/skills-sdk-platform-atlas.html"
        with tempfile.TemporaryDirectory() as tmpdir:
            drifted = Path(tmpdir) / "drifted-pipeline.html"
            drifted.write_text(
                source.read_text(encoding="utf-8").replace(
                    'data-pipeline-step="proof_oss_local"',
                    'data-pipeline-step="proof_oss_cloud"',
                    1,
                ),
                encoding="utf-8",
            )

            payload = verify_capability_docs_projection(REPO_ROOT, artifact_path=drifted)

        self.assertEqual(payload["status"], "blocked")
        order_blocker = next(
            blocker for blocker in payload["blockers"] if blocker["code"] == "pipeline_step_order_mismatch"
        )
        self.assertEqual(order_blocker["expected"], list(CANONICAL_ATLAS_PIPELINE_STEPS))
        self.assertNotEqual(order_blocker["actual"], order_blocker["expected"])

    def test_verifier_returns_blocked_receipt_for_parse_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            invalid = Path(tmpdir) / "invalid.html"
            invalid.write_bytes(b"\xff")

            payload = verify_capability_docs_projection(REPO_ROOT, artifact_path=invalid)

        self.assertEqual(payload["status"], "blocked")
        blocker_codes = {blocker["code"] for blocker in payload["blockers"]}
        self.assertIn("projection_parse_failed", blocker_codes)


if __name__ == "__main__":
    unittest.main()
