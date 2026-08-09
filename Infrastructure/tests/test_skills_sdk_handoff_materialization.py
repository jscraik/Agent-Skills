from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.handoff_materialization import (  # noqa: E402
    HandoffMaterializationRequest,
    materialize_handoff_bundle,
    record_tessl_dry_run,
)
from ask.skills_sdk.handoff_capture import (  # noqa: E402
    HANDOFF_CAPTURE_SCHEMA_VERSION,
    HandoffCaptureRequest,
    capture_handoff_lane,
)
from ask.skills_sdk.handoff_readiness import (  # noqa: E402
    build_candidate_identity,
    build_handoff_readiness_receipt,
    build_tessl_dry_run_admission,
)


FIXTURE_SKILL = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
PRE_TESSL_LANES = (
    "mechanical_validation",
    "security_risk_modes",
    "scenario_quality",
    "scorer_quality",
    "scorer_calibration",
    "deterministic_local_gates",
    "oss-local",
    "oss-cloud",
    "tessl-local-proof",
)


def _source_payload(lane_id: str, candidate: dict[str, str]) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": HANDOFF_CAPTURE_SCHEMA_VERSION,
        "status": "pass",
        "lane": lane_id,
        "candidate": candidate,
        "issued_at": datetime.now(UTC).isoformat(),
    }
    if lane_id in {"oss-local", "oss-cloud"}:
        payload["data"] = {"skills_sdk_eval_run": {"receipt": {
            "status": "pass",
            "codex_profile": lane_id,
            "codex_exec_invoked": True,
            "cases": [{"case_id": f"{lane_id}-case", "status": "pass"}],
            "untrusted_debug_detail": "must-not-enter-handoff-evidence",
        }}}
        return payload
    if lane_id == "tessl-local-proof":
        payload["data"] = {"skills_sdk_eval_tessl_local_proof": {"receipt": {
            "schema_version": "skills-sdk.tessl-local-proof.v1",
            "status": "pass",
            "execute": True,
        }}}
        return payload
    return payload


def _inputs(root: Path) -> list[str]:
    candidate = build_candidate_identity(REPO_ROOT, REPO_ROOT / FIXTURE_SKILL)
    receipts: list[str] = []
    for lane_id in PRE_TESSL_LANES:
        source = root / f"source-{lane_id}.json"
        receipts.append(f"{lane_id}={source}")
        payload = _source_payload(lane_id, candidate)
        payload["commands"] = [_command(lane_id)]
        source.write_text(json.dumps(payload), encoding="utf-8")
    return receipts


def _stale_source_payload(lane_id: str) -> dict[str, object]:
    payload = _source_payload(
        lane_id,
        build_candidate_identity(REPO_ROOT, REPO_ROOT / FIXTURE_SKILL),
    )
    payload["issued_at"] = "2000-01-01T00:00:00+00:00"
    return payload


def _command(lane_id: str) -> str:
    commands = {
        "mechanical_validation": "./bin/ask skills audit Skills/example --level strict --json --robot && ./bin/ask skills package verify Skills/example --json --robot",
        "security_risk_modes": "./bin/ask sdk security risk-modes Skills/example --preview --json --robot",
        "scenario_quality": "./bin/ask sdk eval scenario-quality Skills/example --preview --json --robot",
        "scorer_quality": "./bin/ask sdk eval scorer-quality Skills/example --preview --json --robot",
        "scorer_calibration": "./bin/ask sdk eval scorer-calibration Skills/example --preview --json --robot",
        "deterministic_local_gates": (
            "./bin/ask sdk eval run Skills/example --runner internal --mode smoke "
            "--codex-profile oss-local --json --robot"
        ),
        "oss-local": "./bin/ask sdk eval run Skills/example --runner internal --mode release --codex-profile oss-local --json --robot",
        "oss-cloud": "./bin/ask sdk eval run Skills/example --runner internal --mode release --codex-profile oss-cloud --json --robot",
        "tessl-local-proof": "./bin/ask sdk eval tessl-local-proof --skill Skills/example --workspace jscraik --execute --json --robot",
    }
    return commands[lane_id]


def _request(
    *,
    evidence_root: Path,
    lane_receipts: list[str],
    operation: Literal["preview", "execute"],
) -> HandoffMaterializationRequest:
    return HandoffMaterializationRequest(
        skill=FIXTURE_SKILL,
        evidence_root=evidence_root,
        lane_receipts=tuple(lane_receipts),
        operation=operation,
    )


def _run_ask(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    temp_root = Path(tempfile.gettempdir()) / "agent-skills-handoff-materialization"
    env.setdefault("XDG_CACHE_HOME", str(temp_root / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_root / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_root / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_root / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_root / "uv-cache"))
    return subprocess.run(
        [str(REPO_ROOT / "bin" / "ask"), *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TestSkillsSdkHandoffMaterialization(unittest.TestCase):
    def test_cli_previews_a_valid_handoff_bundle(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            lane_receipts = _inputs(root)
            arguments = [
                "sdk", "eval", "handoff-materialize", "--skill", FIXTURE_SKILL,
                "--evidence-root", str(root / "preview-candidate"),
            ]
            for receipt in lane_receipts:
                arguments.extend(["--lane-receipt", receipt])
            completed = _run_ask(*arguments, "--preview", "--json", "--robot")

        envelope = json.loads(completed.stdout)
        payload = envelope["data"]["skills_sdk_eval_handoff_materialize"]
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["status"], "preview")
        self.assertTrue(payload["ready_for_tessl_dry_run"])

    def test_materializes_current_pre_tessl_receipts_for_dry_run(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            lane_receipts = _inputs(root)
            bundle_root = root / "current-candidate"
            receipt = materialize_handoff_bundle(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=_request(
                    evidence_root=bundle_root,
                    lane_receipts=lane_receipts,
                    operation="execute",
                ),
            )
            admission = build_tessl_dry_run_admission(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=bundle_root / "eval-handoff-readiness.json",
            )
            oss_cloud_receipt = json.loads((bundle_root / "oss-cloud.json").read_text(encoding="utf-8"))
            readiness = json.loads((bundle_root / "eval-handoff-readiness.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["status"], "pass", receipt)
        self.assertTrue(receipt["mutation_performed"])
        self.assertTrue(admission["ready_for_tessl_dry_run"])
        self.assertNotIn("untrusted_debug_detail", oss_cloud_receipt)
        self.assertTrue(str(oss_cloud_receipt["source_receipt_digest"]).startswith("sha256:"))
        self.assertEqual(oss_cloud_receipt["cases"], [{"case_id": "oss-cloud-case", "status": "pass"}])
        dry_run_lane = next(lane for lane in readiness["lanes"] if lane["id"] == "tessl-live-dry-run")
        self.assertIn("--handoff-readiness", dry_run_lane["command"])
        self.assertIn(
            "eval-handoff-readiness.json",
            dry_run_lane["command"],
        )

    def test_materializes_multiple_current_oss_shards(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            lane_receipts = _inputs(root)
            extra_source = root / "source-oss-local-second-shard.json"
            payload = _source_payload(
                "oss-local",
                build_candidate_identity(REPO_ROOT, REPO_ROOT / FIXTURE_SKILL),
            )
            payload["commands"] = [
                ("./bin/ask sdk eval run Skills/example --runner internal --mode release "
                 "--codex-profile oss-local --case second-shard --json --robot")
            ]
            extra_source.write_text(json.dumps(payload), encoding="utf-8")
            lane_receipts.append(f"oss-local={extra_source}")
            bundle_root = root / "current-candidate"
            receipt = materialize_handoff_bundle(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=_request(
                    evidence_root=bundle_root,
                    lane_receipts=lane_receipts,
                    operation="execute",
                ),
            )
            oss_local_receipt = json.loads((bundle_root / "oss-local.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["status"], "pass", receipt)
        self.assertEqual(len(oss_local_receipt["source_receipt_paths"]), 2)
        self.assertEqual(len(oss_local_receipt["source_receipt_digests"]), 2)
        self.assertIn(" && ", oss_local_receipt["command"])

    def test_records_successful_dry_run_as_the_live_handoff_gate(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            bundle_root = root / "current-candidate"
            materialize_handoff_bundle(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=_request(
                    evidence_root=bundle_root,
                    lane_receipts=_inputs(root),
                    operation="execute",
                ),
            )
            receipt_path = record_tessl_dry_run(
                REPO_ROOT,
                readiness_path=bundle_root / "eval-handoff-readiness.json",
                tessl_eval={
                    "status": "pass",
                    "dry_run": True,
                    "live_private": True,
                    "workspace": "jscraik",
                    "visibility": "private",
                    "oss_scenario_parity": {"status": "pass", "staged_case_count": 8, "staged_case_ids": []},
                    "budget_preflight": {"status": "pass", "scenario_count": 8, "max_scenarios_default": 10},
                },
            )
            readiness = build_handoff_readiness_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                readiness_path=bundle_root / "eval-handoff-readiness.json",
            )
            receipt_exists = (REPO_ROOT / receipt_path).is_file()

        self.assertTrue(receipt_exists)
        self.assertTrue(readiness["ready_for_live_tessl"], readiness)

    def test_record_tessl_dry_run_rejects_non_pass_status(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            bundle_root = root / "current-candidate"
            materialize_handoff_bundle(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=_request(
                    evidence_root=bundle_root,
                    lane_receipts=_inputs(root),
                    operation="execute",
                ),
            )
            with self.assertRaises(ValueError) as ctx:
                record_tessl_dry_run(
                    REPO_ROOT,
                    readiness_path=bundle_root / "eval-handoff-readiness.json",
                    tessl_eval={
                        "status": "blocked",
                        "dry_run": True,
                        "live_private": True,
                    },
                )
        self.assertIn("successful private Tessl dry-run", str(ctx.exception))

    def test_record_tessl_dry_run_rejects_non_dry_run_result(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            bundle_root = root / "current-candidate"
            materialize_handoff_bundle(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=_request(
                    evidence_root=bundle_root,
                    lane_receipts=_inputs(root),
                    operation="execute",
                ),
            )
            with self.assertRaises(ValueError) as ctx:
                record_tessl_dry_run(
                    REPO_ROOT,
                    readiness_path=bundle_root / "eval-handoff-readiness.json",
                    tessl_eval={
                        "status": "pass",
                        "dry_run": False,
                        "live_private": True,
                    },
                )
        self.assertIn("successful private Tessl dry-run", str(ctx.exception))

    def test_record_tessl_dry_run_rejects_existing_receipt(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            bundle_root = root / "current-candidate"
            materialize_handoff_bundle(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=_request(
                    evidence_root=bundle_root,
                    lane_receipts=_inputs(root),
                    operation="execute",
                ),
            )
            tessl_eval = {
                "status": "pass",
                "dry_run": True,
                "live_private": True,
                "workspace": "jscraik",
                "visibility": "private",
                "oss_scenario_parity": {"status": "pass", "staged_case_count": 8, "staged_case_ids": []},
                "budget_preflight": {"status": "pass", "scenario_count": 8, "max_scenarios_default": 10},
            }
            record_tessl_dry_run(
                REPO_ROOT,
                readiness_path=bundle_root / "eval-handoff-readiness.json",
                tessl_eval=tessl_eval,
            )
            with self.assertRaises(ValueError) as ctx:
                record_tessl_dry_run(
                    REPO_ROOT,
                    readiness_path=bundle_root / "eval-handoff-readiness.json",
                    tessl_eval=tessl_eval,
                )
        self.assertIn("already exists", str(ctx.exception))

    def test_materializes_case_evidence_from_a_passing_captured_shard_command(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            lane_receipts = _inputs(root)
            legacy_source = root / "source-oss-cloud.json"
            payload = json.loads(legacy_source.read_text(encoding="utf-8"))
            payload["data"]["skills_sdk_eval_run"]["receipt"].pop("cases")
            payload["commands"] = [
                ("./bin/ask sdk eval run Skills/example --runner internal --mode release "
                 "--codex-profile oss-cloud --case happy-diff --case happy-polish --json --robot")
            ]
            legacy_source.write_text(json.dumps(payload), encoding="utf-8")
            receipt = materialize_handoff_bundle(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=_request(
                    evidence_root=root / "current-candidate",
                    lane_receipts=lane_receipts,
                    operation="execute",
                ),
            )
            oss_cloud = json.loads((root / "current-candidate" / "oss-cloud.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["status"], "pass", receipt)
        self.assertEqual(
            oss_cloud["cases"],
            [
                {"case_id": "happy-diff", "status": "pass"},
                {"case_id": "happy-polish", "status": "pass"},
            ],
        )

    def test_materialization_rejects_missing_pre_tessl_lane(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            lane_receipts = _inputs(root)
            receipt = materialize_handoff_bundle(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=_request(
                    evidence_root=root / "blocked-candidate",
                    lane_receipts=[item for item in lane_receipts if not item.startswith("oss-cloud=")],
                    operation="preview",
                ),
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("missing lane receipt for lane: oss-cloud", receipt["blockers"])
        self.assertIn("oss-cloud: missing receipt", receipt["blockers"])

    def test_materialization_rejects_a_receipt_outside_the_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "outside-repo.json"
            source.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
            receipt = materialize_handoff_bundle(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=_request(
                    evidence_root=REPO_ROOT / ".harness" / "evidence" / "handoff" / "outside-receipt",
                    lane_receipts=[f"{lane_id}={source}" for lane_id in PRE_TESSL_LANES],
                    operation="preview",
                ),
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("mechanical_validation: receipt must be contained by the repository", receipt["blockers"])

    def test_materialization_rejects_stale_capture_receipt(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            lane_receipts = _inputs(root)
            stale = root / "source-scorer_quality.json"
            stale.write_text(json.dumps(_stale_source_payload("scorer_quality")), encoding="utf-8")
            receipt = materialize_handoff_bundle(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=_request(
                    evidence_root=root / "stale-candidate",
                    lane_receipts=lane_receipts,
                    operation="preview",
                ),
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn(
            "scorer_quality: receipt issued_at must be current and no older than 24 hours",
            receipt["blockers"],
        )

    def test_capture_runs_one_lane_and_preserves_the_real_command_envelope(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            root = Path(temp_dir)
            source_receipt = root / "oss-cloud-source.json"

            def fake_run(arguments: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
                envelope = {
                    "status": "success",
                    "data": {"skills_sdk_eval_run": {"receipt": {
                        "status": "pass",
                        "codex_profile": "oss-cloud",
                        "codex_exec_invoked": True,
                        "cases": [{"case_id": "happy-diff", "status": "pass"}],
                    }}},
                }
                return subprocess.CompletedProcess(arguments, 0, json.dumps(envelope), "")

            receipt = capture_handoff_lane(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=HandoffCaptureRequest(
                    skill=FIXTURE_SKILL,
                    lane_id="oss-cloud",
                    receipt_path=source_receipt,
                    operation="execute",
                    cases=("happy-diff",),
                ),
                run_command=fake_run,
            )
            persisted = json.loads(source_receipt.read_text(encoding="utf-8"))

        self.assertEqual(receipt["status"], "pass")
        self.assertTrue(receipt["mutation_performed"])
        self.assertTrue(persisted["mutation_performed"])
        self.assertEqual(persisted["candidate"], build_candidate_identity(REPO_ROOT, REPO_ROOT / FIXTURE_SKILL))
        self.assertEqual(persisted["data"]["skills_sdk_eval_run"]["receipt"]["codex_profile"], "oss-cloud")
        self.assertEqual(
            persisted["data"]["skills_sdk_eval_run"]["receipt"]["cases"],
            [{"case_id": "happy-diff", "status": "pass"}],
        )
        self.assertIn("--codex-profile oss-cloud", persisted["commands"][0])
        self.assertNotIn("trace_id", persisted["command_results"][0])

    def test_capture_rejects_unbounded_oss_lane_before_running_a_child(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            receipt_path = Path(temp_dir) / "oss-local.json"
            request = HandoffCaptureRequest(
                skill=FIXTURE_SKILL,
                lane_id="oss-local",
                receipt_path=receipt_path,
                operation="execute",
            )

            receipt = capture_handoff_lane(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=request,
                run_command=self.fail,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("oss-local capture requires explicit one- or two-case shards", receipt["blockers"])

    def test_capture_rejects_oversized_oss_shards(self) -> None:
        handoff_root = REPO_ROOT / ".harness" / "evidence" / "handoff"
        handoff_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=handoff_root) as temp_dir:
            receipt_path = Path(temp_dir) / "oss-local.json"
            request = HandoffCaptureRequest(
                skill=FIXTURE_SKILL,
                lane_id="oss-local",
                receipt_path=receipt_path,
                operation="execute",
                cases=("one", "two", "three"),
            )

            receipt = capture_handoff_lane(
                REPO_ROOT,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                request=request,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("oss-local capture supports at most two cases per shard", receipt["blockers"])
