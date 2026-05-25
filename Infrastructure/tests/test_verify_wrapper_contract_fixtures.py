from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "verify_wrapper_contract_fixtures.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("verify_wrapper_contract_fixtures", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load verify_wrapper_contract_fixtures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifyWrapperContractFixturesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = _load_module()

    def _run_main(self, *args: str) -> list[str]:
        completed: list[str] = []

        def record_runtime_separation(repo_root: Path, timeout_seconds: int) -> None:
            self.assertEqual(repo_root, REPO_ROOT)
            self.assertEqual(timeout_seconds, 45)
            completed.append("runtime-separation")

        def record_runtime_proof(repo_root: Path, timeout_seconds: int, *, handle: str, evidence_dir: str) -> None:
            self.assertEqual(repo_root, REPO_ROOT)
            self.assertEqual(timeout_seconds, 45)
            completed.append(f"runtime-proof:{handle}:{evidence_dir}")

        with (
            mock.patch.object(sys, "argv", ["verify_wrapper_contract_fixtures.py", *args]),
            mock.patch.object(self.module, "_assert_runtime_separation_fixtures", record_runtime_separation),
            mock.patch.object(self.module, "_assert_runtime_proof_fixtures", record_runtime_proof),
            mock.patch.dict("os.environ", {}, clear=True),
            mock.patch("builtins.print"),
        ):
            self.assertEqual(self.module.main(), 0)
        return completed

    def test_no_flag_runs_all_public_wrapper_fixtures(self) -> None:
        self.assertEqual(
            self._run_main(),
            ["runtime-separation", "runtime-proof:he-heartbeat:/tmp/jsc-364-wrapper-codex-parity"],
        )

    def test_runtime_separation_flag_preserves_legacy_fixture_scope(self) -> None:
        self.assertEqual(self._run_main("--runtime-separation"), ["runtime-separation"])

    def test_runtime_proof_flag_runs_only_proof_plane_fixtures(self) -> None:
        self.assertEqual(
            self._run_main("--runtime-proof"),
            ["runtime-proof:he-heartbeat:/tmp/jsc-364-wrapper-codex-parity"],
        )

    def test_runtime_proof_fixture_target_can_be_overridden(self) -> None:
        self.assertEqual(
            self._run_main(
                "--runtime-proof",
                "--runtime-proof-handle",
                "simplify",
                "--runtime-proof-evidence-dir",
                "/tmp/custom-proof",
            ),
            ["runtime-proof:simplify:/tmp/custom-proof"],
        )

    def test_conformance_blocked_runtime_envelope_may_exit_nonzero(self) -> None:
        calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime={"blockers": [{"rule_id": "live_config_layer_stack"}]},
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            self.module._assert_runtime_proof_fixtures(
                REPO_ROOT,
                45,
                handle="he-heartbeat",
                evidence_dir="/tmp/proof",
            )

        conformance_calls = [call for call in calls if call[0][1:4] == ["skills", "conformance", "run"]]
        self.assertEqual(len(conformance_calls), 1)
        self.assertFalse(conformance_calls[0][1])

    def test_conformance_rejects_unknown_live_parity_status(self) -> None:
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(live_parity_status="maybe-live")

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, "live_parity_status is invalid"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-heartbeat", evidence_dir="/tmp/proof")

    def test_conformance_rejects_non_object_blocked_runtime(self) -> None:
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime=[],
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, "blocked_runtime is not an object"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-heartbeat", evidence_dir="/tmp/proof")

    def test_conformance_rejects_blocked_runtime_without_blockers(self) -> None:
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime={"blockers": []},
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, "must be a non-empty list"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-heartbeat", evidence_dir="/tmp/proof")

    def test_conformance_rejects_truthy_non_list_blockers(self) -> None:
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime={"blockers": "cache-miss"},
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, "must be a non-empty list"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-heartbeat", evidence_dir="/tmp/proof")

    def test_conformance_rejects_non_object_blocker_entries(self) -> None:
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime={"blockers": ["cache-miss"]},
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, r"blockers\[0\] is not an object"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-heartbeat", evidence_dir="/tmp/proof")

    def test_conformance_rejects_error_envelope_with_valid_nested_payload(self) -> None:
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime={"blockers": [{"rule_id": "live_config_layer_stack"}]},
            conformance_envelope_status="error",
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, "returned error envelope"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-heartbeat", evidence_dir="/tmp/proof")

    def test_assert_path_reports_missing_path(self) -> None:
        self.assertEqual(self.module._assert_path({"data": {"proof": "ok"}}, "cmd", ["data", "proof"]), "ok")
        with self.assertRaisesRegex(SystemExit, "cmd missing path: data.missing"):
            self.module._assert_path({"data": {}}, "cmd", ["data", "missing"])

    def test_assert_string_field_rejects_empty_and_unexpected_values(self) -> None:
        payload = {"data": {"status": "pass", "empty": ""}}
        self.assertEqual(self.module._assert_string_field(payload, "cmd", ["data", "status"], "pass"), "pass")
        with self.assertRaisesRegex(SystemExit, "is not a non-empty string"):
            self.module._assert_string_field(payload, "cmd", ["data", "empty"])
        with self.assertRaisesRegex(SystemExit, "expected 'blocked'"):
            self.module._assert_string_field(payload, "cmd", ["data", "status"], "blocked")

    def _runtime_proof_envelope_stub(
        self,
        *,
        live_parity_status: str,
        blocked_runtime: object | None = None,
        conformance_envelope_status: str = "success",
    ) -> tuple[list[tuple[list[str], bool]], object]:
        calls: list[tuple[list[str], bool]] = []
        blocked_runtime = {"blockers": []} if blocked_runtime is None else blocked_runtime

        def fake_assert_envelope(
            repo_root: Path,
            command: list[str],
            timeout_seconds: int,
            *,
            require_success: bool = True,
        ) -> dict:
            calls.append((command, require_success))
            self.assertEqual(repo_root, REPO_ROOT)
            self.assertEqual(timeout_seconds, 45)
            if command[1:4] == ["skills", "explain", "he-heartbeat"]:
                return {
                    "data": {
                        "explanation": {
                            "reachability": {"proof_command": "./bin/ask skills proof he-heartbeat --json --robot"},
                            "next_command": "./bin/ask skills proof he-heartbeat --json --robot",
                        }
                    }
                }
            if command[1:4] == ["skills", "proof", "he-heartbeat"]:
                return {
                    "data": {
                        "proof": {
                            "schema_version": "command-handle-proof.v2",
                            "status": "fail",
                            "gates": {},
                            "gate_policy": {},
                        }
                    }
                }
            return {
                "status": conformance_envelope_status,
                "data": {
                    "skills_conformance": {
                        "schema_version": "skills-conformance-evidence.v1",
                        "model_contract_status": "pass",
                        "live_parity_status": live_parity_status,
                        "blocked_runtime": blocked_runtime,
                    }
                }
            }

        return calls, fake_assert_envelope


if __name__ == "__main__":
    unittest.main()
