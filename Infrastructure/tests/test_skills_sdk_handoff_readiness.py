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

from ask.skills_sdk.handoff_readiness import build_handoff_readiness_receipt  # noqa: E402
from ask.skills_sdk.handoff_readiness_contracts import validate_handoff_readiness_receipt  # noqa: E402


FIXTURE_SKILL = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
REQUIRED_LANES = ("deterministic_local_gates", "oss-local", "oss-cloud", "tessl-local-proof", "tessl-live-dry-run")


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


def _run_ask(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _readiness_receipt_payload(lane_id: str) -> dict[str, object]:
    if lane_id in {"oss-local", "oss-cloud"}:
        return {"status": "pass", "codex_profile": lane_id, "codex_exec_invoked": True, "case_count": 3}
    if lane_id == "tessl-local-proof":
        return {
            "status": "success",
            "data": {"skills_sdk_eval_tessl_local_proof": {"receipt": {
                "schema_version": "skills-sdk.tessl-local-proof.v1",
                "status": "pass",
                "execute": True,
            }}},
        }
    if lane_id == "tessl-live-dry-run":
        return {
            "status": "success",
            "data": {
                "tessl_eval": {
                    "status": "pass",
                    "live_private": True,
                    "dry_run": True,
                }
            },
        }
    return {"status": "pass"}


def _readiness_lane_command(lane_id: str) -> str:
    commands = {
        "deterministic_local_gates": "./bin/ask skills package verify Skills/example --json --robot",
        "oss-local": (
            "./bin/ask sdk eval run Skills/example --runner internal "
            "--mode smoke --codex-profile oss-local --json --robot"
        ),
        "oss-cloud": (
            "./bin/ask sdk eval run Skills/example --runner internal "
            "--mode smoke --codex-profile oss-cloud --json --robot"
        ),
        "tessl-local-proof": (
            "./bin/ask sdk eval tessl-local-proof --skill Skills/example "
            "--workspace jscraik --execute --json --robot"
        ),
        "tessl-live-dry-run": (
            "./bin/ask evals run Skills/example --tessl-live-private "
            "--tessl-workspace jscraik --tessl-live-dry-run --json --robot"
        ),
    }
    return commands[lane_id]


def _write_readiness_bundle(temp_dir: Path, *, status: str = "pass") -> Path:
    lanes = []
    for lane_id in REQUIRED_LANES:
        receipt_path = temp_dir / f"{lane_id}.json"
        receipt_path.write_text(json.dumps(_readiness_receipt_payload(lane_id)) + "\n", encoding="utf-8")
        lanes.append({
            "id": lane_id,
            "status": status,
            "command": _readiness_lane_command(lane_id),
            "receipt_path": str(receipt_path),
        })
    readiness_path = temp_dir / "eval-handoff-readiness.json"
    readiness_path.write_text(
        json.dumps({
            "schema_version": "skills-sdk.eval-handoff-readiness-input.v1",
            "candidate_id": "fixture-candidate",
            "lanes": lanes,
        }),
        encoding="utf-8",
    )
    return readiness_path


def _write_tessl_score_receipt(
    path: Path,
    *,
    feedback_status: str = "closed",
    regressions: list[dict[str, object]] | None = None,
    usage_percent: float = 95.0,
    scenario_count: int = 3,
) -> Path:
    regressions = regressions or []
    path.write_text(
        json.dumps({
            "data": {
                "skills_sdk_eval_tessl_score": {
                    "status": "preview",
                    "ready": not regressions and feedback_status != "open" and usage_percent >= 90.0,
                    "receipt": {
                        "status": "preview",
                        "blocker_class": None,
                        "feedback_loop": {
                            "status": feedback_status,
                            "regression_count": len(regressions),
                            "regression_paths": [str(item.get("path")) for item in regressions],
                        },
                        "score_summary": {
                            "scenario_count": scenario_count,
                            "usage_percent": usage_percent,
                            "baseline_percent": 70.0,
                            "regressions": regressions,
                        },
                    },
                }
            }
        }),
        encoding="utf-8",
    )
    return path


def _write_raw_tessl_score_receipt(path: Path, *, scenario_count: int = 3) -> Path:
    path.write_text(
        json.dumps({
            "schema_version": "skills-sdk.tessl-score-receipt.v0",
            "status": "preview",
            "feedback_loop": {"status": "closed", "regression_count": 0},
            "score_summary": {
                "scenario_count": scenario_count,
                "usage_percent": 95.0,
                "baseline_percent": 70.0,
                "regressions": [],
            },
        }),
        encoding="utf-8",
    )
    return path


class TestSkillsSdkHandoffReadiness(unittest.TestCase):
    def test_missing_readiness_artifact_blocks_live_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=Path(temp_dir) / "missing.json",
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        blocker_ids = {blocker["id"] for blocker in receipt["blockers"]}
        self.assertIn("readiness_artifact_present", blocker_ids)
        self.assertIn("lane_present", blocker_ids)

    def test_complete_readiness_artifact_allows_live_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            readiness_path = _write_readiness_bundle(Path(temp_dir))
            tessl_score = _write_tessl_score_receipt(Path(temp_dir) / "tessl-score.json")
            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
                tessl_score_path=tessl_score,
            )

        self.assertEqual(receipt["status"], "preview")
        self.assertTrue(receipt["ready_for_live_tessl"])
        self.assertEqual(receipt["blockers"], [])
        self.assertEqual(receipt["tessl_score_summary"]["usage_percent"], 95.0)
        validate_handoff_readiness_receipt(receipt)

    def test_handoff_readiness_blocks_open_tessl_feedback_loop(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            tessl_score = _write_tessl_score_receipt(temp_path / "tessl-score.json", feedback_status="open")
            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
                tessl_score_path=tessl_score,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        self.assertIn("tessl_feedback_loop_closed", {blocker["id"] for blocker in receipt["blockers"]})
        self.assertTrue(any("Tessl score feedback loop" in action for action in receipt["required_next_actions"]))
        self.assertFalse(any(action.startswith("Run live Tessl") for action in receipt["required_next_actions"]))
        validate_handoff_readiness_receipt(receipt)

    def test_handoff_readiness_blocks_tessl_baseline_wins(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            tessl_score = _write_tessl_score_receipt(
                temp_path / "tessl-score.json",
                regressions=[{"path": "reader-testing", "usage_score": 0, "baseline_score": 2}],
            )
            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
                tessl_score_path=tessl_score,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        self.assertIn("tessl_baseline_wins_absent", {blocker["id"] for blocker in receipt["blockers"]})
        validate_handoff_readiness_receipt(receipt)

    def test_handoff_readiness_blocks_sub_90_tessl_usage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            tessl_score = _write_tessl_score_receipt(temp_path / "tessl-score.json", usage_percent=89.9)
            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
                tessl_score_path=tessl_score,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        self.assertIn("tessl_usage_threshold_met", {blocker["id"] for blocker in receipt["blockers"]})
        validate_handoff_readiness_receipt(receipt)

    def test_handoff_readiness_blocks_smoke_only_oss_release_proof(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            for lane_id in ("oss-local", "oss-cloud"):
                (temp_path / f"{lane_id}.json").write_text(
                    json.dumps({"status": "pass", "codex_profile": lane_id, "codex_exec_invoked": True, "case_count": 2}),
                    encoding="utf-8",
                )
            tessl_score = _write_tessl_score_receipt(temp_path / "tessl-score.json", scenario_count=5)
            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
                tessl_score_path=tessl_score,
            )

        self.assertEqual(receipt["status"], "blocked")
        blocker_ids = {blocker["id"] for blocker in receipt["blockers"]}
        self.assertIn("oss-local_release_scenario_count_matches_tessl", blocker_ids)
        self.assertIn("oss-cloud_release_scenario_count_matches_tessl", blocker_ids)
        validate_handoff_readiness_receipt(receipt)

    def test_handoff_readiness_accepts_raw_tessl_score_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            tessl_score = _write_raw_tessl_score_receipt(temp_path / "tessl-score.json")
            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
                tessl_score_path=tessl_score,
            )

        self.assertEqual(receipt["status"], "preview")
        self.assertTrue(receipt["ready_for_live_tessl"])
        self.assertEqual(receipt["tessl_score_summary"]["scenario_count"], 3)
        validate_handoff_readiness_receipt(receipt)

    def test_handoff_readiness_compares_oss_to_release_set_universe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            for lane_id in ("oss-local", "oss-cloud"):
                (temp_path / f"{lane_id}.json").write_text(
                    json.dumps({
                        "status": "pass",
                        "codex_profile": lane_id,
                        "codex_exec_invoked": True,
                        "case_count": 20,
                        "scenario_set_case_ids": [f"case-{index}" for index in range(20)],
                        "release_set_minimum": 20,
                    }),
                    encoding="utf-8",
                )
            tessl_score = _write_tessl_score_receipt(temp_path / "tessl-score.json", scenario_count=32)
            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
                tessl_score_path=tessl_score,
            )

        self.assertEqual(receipt["status"], "preview")
        blocker_ids = {blocker["id"] for blocker in receipt["blockers"]}
        self.assertNotIn("oss-local_release_scenario_count_matches_tessl", blocker_ids)
        self.assertNotIn("oss-cloud_release_scenario_count_matches_tessl", blocker_ids)
        validate_handoff_readiness_receipt(receipt)

    def test_handoff_readiness_command_requires_preview(self) -> None:
        process = _run_ask(
            "sdk",
            "eval",
            "handoff-readiness",
            "--skill",
            FIXTURE_SKILL,
            "--json",
            "--robot",
        )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("require --preview", envelope["errors"][0]["message"])

    def test_handoff_readiness_command_builds_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            readiness_path = _write_readiness_bundle(Path(temp_dir))
            process = _run_ask(
                "sdk",
                "eval",
                "handoff-readiness",
                "--skill",
                FIXTURE_SKILL,
                "--receipt-json",
                str(readiness_path),
                "--preview",
                "--json",
                "--robot",
            )

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_handoff_readiness"]
        self.assertEqual(payload["status"], "preview")
        self.assertTrue(payload["ready_for_live_tessl"])

    def test_handoff_readiness_blocks_wrong_oss_profile_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            wrong_receipt = temp_path / "oss-local.json"
            wrong_receipt.write_text(json.dumps({"status": "pass", "codex_profile": "oss-cloud"}), encoding="utf-8")

            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        semantic_blockers = [blocker for blocker in receipt["blockers"] if blocker["id"] == "lane_receipt_semantics_valid"]
        self.assertTrue(semantic_blockers)
        self.assertIn("expected=oss-local with codex_exec_invoked=true", semantic_blockers[0]["evidence"])

    def test_handoff_readiness_blocks_oss_receipt_without_codex_exec_proof(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            weak_receipt = temp_path / "oss-local.json"
            weak_receipt.write_text(json.dumps({"status": "pass", "codex_profile": "oss-local"}), encoding="utf-8")

            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        semantic_blockers = [blocker for blocker in receipt["blockers"] if blocker["id"] == "lane_receipt_semantics_valid"]
        self.assertTrue(semantic_blockers)
        self.assertIn("codex_exec_invoked=False", semantic_blockers[0]["evidence"])

    def test_handoff_readiness_blocks_failed_lane_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            blocked_receipt = temp_path / "oss-cloud.json"
            blocked_receipt.write_text(json.dumps({"status": "blocked", "codex_profile": "oss-cloud"}), encoding="utf-8")

            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        semantic_blockers = [blocker for blocker in receipt["blockers"] if blocker["id"] == "lane_receipt_semantics_valid"]
        self.assertTrue(semantic_blockers)
        self.assertIn("status=blocked", semantic_blockers[0]["evidence"])

    def test_handoff_readiness_accepts_nested_sdk_eval_run_receipt_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            oss_local_receipt = temp_path / "oss-local.json"
            oss_local_receipt.write_text(
                json.dumps({
                    "status": "success",
                    "data": {
                        "skills_sdk_eval_run": {
                            "receipt": {
                                "status": "pass",
                                "lane": "oss-local",
                                "profile": "oss-local",
                                "codex_profile": "oss-local",
                                "codex_exec_invoked": True,
                            }
                        }
                    },
                }),
                encoding="utf-8",
            )

            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "preview")
        self.assertTrue(receipt["ready_for_live_tessl"])

    def test_handoff_readiness_blocks_preview_only_tessl_local_proof(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            payload = json.loads(readiness_path.read_text(encoding="utf-8"))
            for lane in payload["lanes"]:
                if lane["id"] == "tessl-local-proof":
                    lane["command"] = (
                        "./bin/ask sdk eval tessl-local-proof "
                        "--skill Skills/example --workspace jscraik --preview --json --robot"
                    )
                    receipt_path = Path(lane["receipt_path"])
                    receipt_path.write_text(
                        json.dumps({
                            "status": "success",
                            "data": {
                                "skills_sdk_eval_tessl_local_proof": {
                                    "receipt": {
                                        "schema_version": "skills-sdk.tessl-local-proof.v1",
                                        "status": "preview",
                                        "execute": False,
                                    }
                                }
                            },
                        }),
                        encoding="utf-8",
                    )
            readiness_path.write_text(json.dumps(payload), encoding="utf-8")

            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        semantic_blockers = [blocker for blocker in receipt["blockers"] if blocker["id"] == "lane_receipt_semantics_valid"]
        self.assertTrue(semantic_blockers)
        self.assertIn("expected=command includes tessl-local-proof --execute", semantic_blockers[0]["evidence"])

    def test_handoff_readiness_blocks_tessl_dry_run_command_without_dry_run_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            payload = json.loads(readiness_path.read_text(encoding="utf-8"))
            for lane in payload["lanes"]:
                if lane["id"] == "tessl-live-dry-run":
                    receipt_path = Path(lane["receipt_path"])
                    receipt_path.write_text(
                        json.dumps({
                            "status": "success",
                            "data": {
                                "tessl_eval": {
                                    "status": "pass",
                                    "live_private": True,
                                    "dry_run": False,
                                }
                            },
                        }),
                        encoding="utf-8",
                    )
            readiness_path.write_text(json.dumps(payload), encoding="utf-8")

            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        semantic_blockers = [blocker for blocker in receipt["blockers"] if blocker["id"] == "lane_receipt_semantics_valid"]
        self.assertTrue(semantic_blockers)
        self.assertIn(
            "expected=command includes --tessl-live-dry-run and receipt records tessl_eval.dry_run=true",
            semantic_blockers[0]["evidence"],
        )
        self.assertIn("tessl_live_dry_run=False", semantic_blockers[0]["evidence"])

    def test_handoff_readiness_blocks_preview_only_oss_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            oss_receipt = temp_path / "oss-local.json"
            oss_receipt.write_text(
                json.dumps({"status": "preview", "codex_profile": "oss-local"}),
                encoding="utf-8",
            )

            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        semantic_blockers = [blocker for blocker in receipt["blockers"] if blocker["id"] == "lane_receipt_semantics_valid"]
        self.assertTrue(semantic_blockers)
        self.assertIn("status=preview", semantic_blockers[0]["evidence"])

    def test_handoff_readiness_routes_failed_oss_local_receipt_to_repair_first(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            oss_receipt = temp_path / "oss-local.json"
            oss_receipt.write_text(
                json.dumps({
                    "status": "error",
                    "receipt": {
                        "status": "fail",
                        "codex_profile": "oss-local",
                        "codex_exec_invoked": True,
                        "case_count": 20,
                        "failed_count": 7,
                    },
                }),
                encoding="utf-8",
            )

            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        self.assertFalse(receipt["next_gate_allowed"])
        self.assertEqual(receipt["blocked_next_gates"], ["oss-cloud", "tessl-dry-run", "tessl-live"])
        oss_local_lane = next(lane for lane in receipt["lanes"] if lane["id"] == "oss-local")
        self.assertEqual(oss_local_lane["declared_status"], "pass")
        self.assertEqual(oss_local_lane["status"], "blocked")
        semantic_blockers = [blocker for blocker in receipt["blockers"] if blocker["id"] == "lane_receipt_semantics_valid"]
        self.assertTrue(semantic_blockers)
        self.assertIn("status=error", semantic_blockers[0]["evidence"])
        self.assertIn("Repair the oss-local release-lane failures", receipt["required_next_actions"][0])
        self.assertIn("before oss-cloud", receipt["required_next_actions"][0])
        self.assertIn("do not run live Tessl", receipt["required_next_actions"][0])
        validate_handoff_readiness_receipt(receipt)

    def test_handoff_readiness_blocks_placeholder_lane_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            payload = json.loads(readiness_path.read_text(encoding="utf-8"))
            for lane in payload["lanes"]:
                if lane["id"] == "oss-local":
                    lane["command"] = (
                        "./bin/ask sdk eval ab-judge-score "
                        "--run-receipt <teach-ab-run-receipt.json> "
                        "--judge-profile oss-local --execute --json --robot"
                    )
            readiness_path.write_text(json.dumps(payload), encoding="utf-8")

            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        command_blockers = [blocker for blocker in receipt["blockers"] if blocker["id"] == "lane_command_recorded"]
        self.assertTrue(command_blockers)
        self.assertIn("<teach-ab-run-receipt.json>", command_blockers[0]["evidence"][0])
        self.assertIn("Replace placeholder lane commands", receipt["required_next_actions"][0])
        self.assertIn("--codex-profile oss-local", receipt["required_next_actions"][1])
        self.assertIn("A/B judge route", receipt["required_next_actions"][2])

    def test_handoff_readiness_routes_oss_local_runtime_blocker_to_diagnostic_continuation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            readiness_path = _write_readiness_bundle(temp_path)
            payload = json.loads(readiness_path.read_text(encoding="utf-8"))
            for lane in payload["lanes"]:
                if lane["id"] == "oss-local":
                    lane["status"] = "blocked"
                    lane["blocker"] = "blocked_runtime: oss-local produced no receipt before timeout"
                    lane.pop("receipt_path")
            readiness_path.write_text(json.dumps(payload), encoding="utf-8")

            receipt = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=readiness_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_tessl"])
        self.assertIn("run oss-cloud as a diagnostic continuation", receipt["required_next_actions"][0])
        self.assertIn("keep live Tessl blocked", receipt["required_next_actions"][0])


if __name__ == "__main__":
    unittest.main()
