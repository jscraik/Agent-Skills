from __future__ import annotations

import json
import subprocess
import unittest

from test_skills_sdk_ab_preflight import (
    SkillsSdkAbPreflightFixture,
    _CustomBoundarySignal,
    _HostileEnvelope,
    _catalog_probe_result,
)


class TestSkillsSdkAbPreflightTransport(
    SkillsSdkAbPreflightFixture,
    unittest.TestCase,
):
    def test_cloud_catalog_requires_exact_integer_zero_process_exit(self) -> None:
        class IntSubclass(int):
            pass

        invalid_values = (False, True, 0.0, "0", None, IntSubclass(0))
        for returncode in invalid_values:
            with self.subTest(returncode_type=type(returncode).__name__):
                self._assert_invalid_catalog_returncode(returncode)
        for returncode in (-9, 1, 255):
            with self.subTest(returncode=returncode):
                self._assert_nonzero_catalog_returncode(returncode)

    def test_cloud_catalog_requires_closed_transport_envelope(self) -> None:
        class StringSubclass(str):
            pass

        class MissingReturncode:
            stdout = json.dumps(self._catalog_payload())
            stderr = ""

        class RaisingAttribute:
            @property
            def returncode(self) -> int:
                raise RuntimeError("secret-like exception text")

            stdout = json.dumps(self._catalog_payload())
            stderr = ""

        valid_stdout = json.dumps(self._catalog_payload())
        cases = (
            subprocess.CompletedProcess(["op", "run"], 0, stdout=valid_stdout.encode(), stderr=""),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=bytearray(valid_stdout.encode()), stderr=""),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=memoryview(valid_stdout.encode()), stderr=""),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=None, stderr=""),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=valid_stdout, stderr=None),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=StringSubclass(valid_stdout), stderr=""),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=valid_stdout, stderr=StringSubclass("")),
            {"returncode": 0, "stdout": valid_stdout, "stderr": ""},
            (0, valid_stdout, ""),
            MissingReturncode(),
            RaisingAttribute(),
        )
        for completed in cases:
            with self.subTest(transport_type=type(completed).__name__):
                payload, failure, evidence = _catalog_probe_result(
                    ["op", "run"],
                    lambda _command, result=completed: result,  # type: ignore[arg-type,return-value]
                )
                self.assertIsNone(payload)
                self.assertEqual(failure, "invalid_probe_transport_envelope")
                self.assertEqual(evidence["probe_transport_class"], "invalid")
                self.assertNotIn("secret-like", json.dumps(evidence))

    def test_cloud_catalog_contains_hostile_attribute_base_exceptions(self) -> None:
        exception_cases = (
            KeyboardInterrupt("keyboard-secret-text"),
            SystemExit("system-secret-text"),
            GeneratorExit("generator-secret-text"),
            RuntimeError("runtime-secret-text"),
            _CustomBoundarySignal("custom-secret-text"),
        )
        valid_stdout = json.dumps(self._catalog_payload())
        for attribute in ("returncode", "stdout", "stderr"):
            for raised in exception_cases:
                with self.subTest(attribute=attribute):
                    completed = _HostileEnvelope(attribute, raised, valid_stdout)
                    payload, failure, evidence = _catalog_probe_result(
                        ["op", "run"], lambda _command, result=completed: result,
                    )
                    self.assertIsNone(payload)
                    self.assertEqual(failure, "invalid_probe_transport_envelope")
                    self.assertEqual(evidence["probe_transport_class"], "invalid")
                    self.assertEqual(
                        evidence[f"probe_{attribute}_class"],
                        "attribute_access_failure",
                    )
                    rendered = json.dumps(evidence)
                    self.assertNotIn("secret-text", rendered)
                    self.assertNotIn("BoundarySignal", rendered)

    def test_cloud_catalog_rejects_oversized_and_control_framed_stdout(self) -> None:
        valid_stdout = json.dumps(self._catalog_payload())
        cases = (
            valid_stdout + "x" * (1024 * 1024),
            "\x00" + valid_stdout,
            valid_stdout + "\t",
            valid_stdout + "\r",
            valid_stdout + "\n\n",
        )
        for stdout in cases:
            completed = subprocess.CompletedProcess(["op", "run"], 0, stdout=stdout, stderr="")
            with self.subTest(suffix=repr(stdout[-2:])):
                payload, failure, evidence = _catalog_probe_result(
                    ["op", "run"], lambda _command, result=completed: result,
                )
                self.assertIsNone(payload)
                self.assertEqual(failure, "invalid_probe_transport_envelope")
                self.assertEqual(evidence["probe_transport_class"], "invalid")

        completed = subprocess.CompletedProcess(
            ["op", "run"], 0, stdout=valid_stdout + "\n", stderr="",
        )
        payload, failure, evidence = _catalog_probe_result(
            ["op", "run"], lambda _command: completed,
        )
        self.assertIsNotNone(payload)
        self.assertIsNone(failure)
        self.assertEqual(evidence["probe_stdout_class"], "bounded_json_text")

    def _assert_invalid_catalog_returncode(self, returncode: object) -> None:
        completed = subprocess.CompletedProcess(
            ["op", "run"],
            returncode,
            stdout=json.dumps(self._catalog_payload()),
            stderr="",
        )
        fact = self._catalog_fact_for_process(completed)
        self.assertEqual(fact["status"], "blocked")
        self.assertIn("invalid_probe_transport_envelope", fact["blocker"]["reason"])
        self.assertIsInstance(json.dumps(fact), str)
        payload, failure, evidence = _catalog_probe_result(
            ["op", "run"], lambda _command: completed,
        )
        self.assertIsNone(payload)
        self.assertEqual(failure, "invalid_probe_transport_envelope")
        self.assertEqual(evidence["probe_returncode_class"], "invalid_type")

    def _assert_nonzero_catalog_returncode(self, returncode: int) -> None:
        completed = self._catalog_process(self._catalog_payload(), returncode=returncode)
        fact = self._catalog_fact_for_process(completed)
        self.assertEqual(fact["status"], "blocked")
        payload, failure, evidence = _catalog_probe_result(
            ["op", "run"], lambda _command: completed,
        )
        self.assertIsNone(payload)
        self.assertEqual(failure, "probe_exit_contract_mismatch")
        self.assertEqual(evidence["probe_exit_class"], "nonzero")
        self.assertEqual(evidence["probe_exit_code"], returncode)

    def test_cloud_catalog_rejects_malformed_or_contradictory_child_contracts(self) -> None:
        duplicate = json.dumps(self._catalog_payload()).replace(
            '"result_class": "pass"',
            '"result_class": "pass", "result_class": "pass"',
        )
        raw_cases = (
            "{}",
            duplicate,
            json.dumps(self._catalog_payload()) + " {}",
            json.dumps(self._catalog_payload(http_status=True)),
            json.dumps(self._catalog_payload(match_count=True)),
            json.dumps(self._catalog_payload(http_status=float("nan"))),
            json.dumps(self._catalog_payload(network_accessed=False)),
            json.dumps(self._catalog_payload(matched_model=None)),
            json.dumps(self._catalog_payload(catalog_digest="sha256:not-a-digest")),
            json.dumps(self._catalog_payload(result_class="model_missing", match_count=1)),
        )
        completed_cases = [
            subprocess.CompletedProcess(["op", "run"], 0, stdout=raw, stderr="")
            for raw in raw_cases
        ]
        completed_cases.append(self._catalog_process(self._catalog_payload(), stderr="unexpected"))
        for index, completed in enumerate(completed_cases):
            with self.subTest(index=index):
                fact = self._catalog_fact_for_process(completed)
                self.assertEqual(fact["status"], "blocked")
                self.assertFalse(fact["secret_value_observed"])
