from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "verify_wrapper_contract_fixtures.py"


def _load_module():
    """
    Load and execute the verify_wrapper_contract_fixtures.py script as a module and return it.
    
    Returns:
        module (module): The loaded module object for verify_wrapper_contract_fixtures.
    
    Raises:
        RuntimeError: If the module spec or its loader cannot be created from SCRIPT_PATH.
    """
    spec = importlib.util.spec_from_file_location("verify_wrapper_contract_fixtures", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load verify_wrapper_contract_fixtures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifyWrapperContractFixturesTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Load the target script module into the test instance and assign it to self.module for use by the tests.
        """
        self.module = _load_module()

    def _run_main(self, *args: str) -> list[str]:
        """
        Run the loaded module's main() as if invoked from the command line with the given arguments, while mocking environment, print, and the module's runtime fixture assertion functions to record which fixture planes were executed.
        
        Parameters:
            *args (str): Command-line arguments to pass to the script (excluding the script name).
        
        Returns:
            completed (list[str]): Ordered list of recorded fixture invocations. Entries are either
                "runtime-separation" or "runtime-proof:{handle}:{evidence_dir}".
        """
        completed: list[str] = []

        def record_runtime_separation(repo_root: Path, timeout_seconds: int) -> None:
            """
            Callback used by tests to validate that the runtime-separation fixture was invoked.
            
            Asserts that `repo_root` equals the test's `REPO_ROOT` and `timeout_seconds` equals 45, then records the invocation by appending "runtime-separation" to the surrounding `completed` list.
            """
            self.assertEqual(repo_root, REPO_ROOT)
            self.assertEqual(timeout_seconds, 45)
            completed.append("runtime-separation")

        def record_runtime_proof(repo_root: Path, timeout_seconds: int, *, handle: str, evidence_dir: str) -> None:
            """
            Record a runtime-proof fixture invocation and validate the test call parameters.
            
            Asserts that `repo_root` equals `REPO_ROOT` and `timeout_seconds` equals 45, then appends
            the string "runtime-proof:{handle}:{evidence_dir}" to the surrounding `completed` list.
            
            Parameters:
                repo_root (Path): Repository root path expected to be `REPO_ROOT`.
                timeout_seconds (int): Timeout value expected to be 45.
                handle (str): Runtime-proof handle used in the recorded entry.
                evidence_dir (str): Evidence directory used in the recorded entry.
            """
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
        completed = self._run_main()

        self.assertEqual(completed[0], "runtime-separation")
        self.assertRegex(
            completed[1],
            r"^runtime-proof:he-phase-work:/tmp/jsc-364-wrapper-codex-parity-.+",
        )

    def test_runtime_separation_flag_preserves_legacy_fixture_scope(self) -> None:
        self.assertEqual(self._run_main("--runtime-separation"), ["runtime-separation"])

    def test_runtime_proof_flag_runs_only_proof_plane_fixtures(self) -> None:
        self.assertRegex(
            self._run_main("--runtime-proof")[0],
            r"^runtime-proof:he-phase-work:/tmp/jsc-364-wrapper-codex-parity-.+",
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

    def test_run_json_ignores_darwin_confstr_warning_preamble(self) -> None:
        proc = mock.Mock()
        proc.returncode = 0
        proc.stdout = (
            "python3: warning: confstr() failed with code 5: couldn't get path of "
            'DARWIN_USER_TEMP_DIR; using /tmp instead\n{"status":"success"}\n'
        )

        with mock.patch.object(self.module.subprocess, "run", return_value=proc):
            exit_code, payload = self.module._run_json(REPO_ROOT, ["ask"], 45)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload, {"status": "success"})

    def test_run_json_rejects_unknown_stdout_preamble(self) -> None:
        proc = mock.Mock()
        proc.returncode = 0
        proc.stdout = 'unexpected warning\n{"status":"success"}\n'

        with mock.patch.object(self.module.subprocess, "run", return_value=proc):
            with self.assertRaisesRegex(SystemExit, "ask did not emit JSON"):
                self.module._run_json(REPO_ROOT, ["ask"], 45)

    def test_conformance_blocked_runtime_envelope_may_exit_nonzero(self) -> None:
        """
        Verifies that runtime conformance may be allowed to fail when a blocked runtime envelope contains a blocker for the live config layer.
        
        Sets up a fake `_assert_envelope` that returns a conformance envelope with `live_parity_status="blocked_runtime"`
        and a `blocked_runtime` object containing a blocker whose `rule_id` is `live_config_layer_stack`, runs the runtime-proof
        fixtures, and asserts that exactly one conformance invocation occurred and its `require_success` flag is `False`.
        """
        calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime={"blockers": [{"rule_id": "live_config_layer_stack", "message": "Live config layer is unavailable."}]},
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            self.module._assert_runtime_proof_fixtures(
                REPO_ROOT,
                45,
                handle="he-phase-work",
                evidence_dir="/tmp/proof",
            )

        conformance_calls = [call for call in calls if call[0][1:4] == ["skills", "conformance", "run"]]
        self.assertEqual(len(conformance_calls), 1)
        self.assertFalse(conformance_calls[0][1])

    def test_conformance_rejects_unknown_live_parity_status(self) -> None:
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(live_parity_status="maybe-live")

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, "live_parity_status is invalid"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-phase-work", evidence_dir="/tmp/proof")

    def test_conformance_rejects_non_object_blocked_runtime(self) -> None:
        """
        Verifies that a conformance envelope with a non-object `blocked_runtime` causes the runtime-proof fixture check to exit with an error.
        
        Sets up a stubbed `_assert_envelope` that returns `live_parity_status="blocked_runtime"` and `blocked_runtime` as a list, patches the module's `_assert_envelope`, and asserts that `_assert_runtime_proof_fixtures(...)` raises `SystemExit` with the message "blocked_runtime is not an object".
        """
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime=[],
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, "blocked_runtime is not an object"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-phase-work", evidence_dir="/tmp/proof")

    def test_conformance_rejects_blocked_runtime_without_blockers(self) -> None:
        """
        Verify that _assert_runtime_proof_fixtures raises a SystemExit when a conformance envelope indicates `live_parity_status` is "blocked_runtime" but the `blocked_runtime` object contains an empty `blockers` list.
        
        This test patches the envelope assertion to return a blocked_runtime payload with `blockers: []` and asserts the raised SystemExit message matches "must be a non-empty list".
        """
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime={"blockers": []},
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, "must be a non-empty list"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-phase-work", evidence_dir="/tmp/proof")

    def test_conformance_rejects_truthy_non_list_blockers(self) -> None:
        """
        Verify that _assert_runtime_proof_fixtures rejects a blocked_runtime whose 'blockers' field is a truthy non-list value.
        
        Asserts that calling the fixture with `blocked_runtime={"blockers": "cache-miss"}` raises SystemExit with a message matching "must be a non-empty list".
        """
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime={"blockers": "cache-miss"},
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, "must be a non-empty list"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-phase-work", evidence_dir="/tmp/proof")

    def test_conformance_rejects_non_object_blocker_entries(self) -> None:
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime={"blockers": ["cache-miss"]},
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, r"blockers\[0\] is not an object"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-phase-work", evidence_dir="/tmp/proof")

    def test_conformance_rejects_error_envelope_with_valid_nested_payload(self) -> None:
        _calls, fake_assert_envelope = self._runtime_proof_envelope_stub(
            live_parity_status="blocked_runtime",
            blocked_runtime={"blockers": [{"rule_id": "live_config_layer_stack"}]},
            conformance_envelope_status="error",
        )

        with mock.patch.object(self.module, "_assert_envelope", fake_assert_envelope):
            with self.assertRaisesRegex(SystemExit, "returned error envelope"):
                self.module._assert_runtime_proof_fixtures(REPO_ROOT, 45, handle="he-phase-work", evidence_dir="/tmp/proof")

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
        """
        Create a test stub that records envelope assertions and returns a fake `_assert_envelope` implementation.
        
        Parameters:
            live_parity_status (str): Value to embed in the returned conformance payload's `live_parity_status` field.
            blocked_runtime (object | None): Value to embed in the conformance payload's `blocked_runtime` field; defaults to `{"blockers": []}` when omitted.
            conformance_envelope_status (str): Top-level `status` to use for the conformance envelope payload.
        
        Returns:
            tuple[list[tuple[list[str], bool]], callable]: A pair where the first element is a list that will be appended with `(command, require_success)` for each invocation, and the second element is a callable `fake_assert_envelope(repo_root, command, timeout_seconds, *, require_success=True)` that performs basic assertions on its `repo_root` and `timeout_seconds` arguments and returns deterministic fake envelope payloads based on the supplied `command`.
        """
        calls: list[tuple[list[str], bool]] = []
        blocked_runtime = {"blockers": []} if blocked_runtime is None else blocked_runtime

        def fake_assert_envelope(
            repo_root: Path,
            command: list[str],
            timeout_seconds: int,
            *,
            require_success: bool = True,
        ) -> dict:
            """
            Create a test stub for _assert_envelope that records the call and returns synthetic envelope payloads based on the invoked command.
            
            This function appends (command, require_success) to the enclosing `calls` list and asserts that `repo_root` equals REPO_ROOT and `timeout_seconds` equals 45. For commands whose slice command[1:4] equals ["skills", "explain", "he-phase-work"] it returns an explanation payload containing `reachability.proof_command` and `next_command`. For commands whose slice equals ["skills", "proof", "he-phase-work"] it returns a proof payload with `schema_version`, `status`, `gates` and `gate_policy`. For all other commands it returns a conformance-style envelope whose top-level `status` is taken from the surrounding `conformance_envelope_status` and whose `data.skills_conformance` includes `schema_version`, `model_contract_status`, `live_parity_status`, and `blocked_runtime`.
            
            Parameters:
                repo_root (Path): Repository root path expected to match REPO_ROOT.
                command (list[str]): The command array used to select the returned synthetic payload.
                timeout_seconds (int): Timeout value expected to be 45.
                require_success (bool): Flag recorded with the call; defaults to True.
            
            Returns:
                dict: A synthetic envelope dictionary matching one of the explanation, proof, or conformance payload shapes described above.
            """
            calls.append((command, require_success))
            self.assertEqual(repo_root, REPO_ROOT)
            self.assertEqual(timeout_seconds, 45)
            if command[1:4] == ["skills", "explain", "he-phase-work"]:
                return {
                    "data": {
                        "explanation": {
                            "reachability": {"proof_command": "./bin/ask skills proof he-phase-work --json --robot"},
                            "next_command": "./bin/ask skills proof he-phase-work --json --robot",
                        }
                    }
                }
            if command[1:4] == ["skills", "proof", "he-phase-work"]:
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
