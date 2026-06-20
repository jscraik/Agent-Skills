from __future__ import annotations

import builtins
import json
import os
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.package_build import build_package_digest_receipt  # noqa: E402
from ask.skills_sdk.package_hardening import build_package_hardening_receipt  # noqa: E402
from ask.skills_sdk.signing_intent import SigningIntentError, build_signing_intent_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import (  # noqa: E402
    validate_robot_envelope,
    validate_signing_intent_receipt,
)


FIXTURE_SKILL = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill"
FIXTURE_POLICY = (
    REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/signing-policy.json"
)


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


class TestSkillsSdkSigningIntent(unittest.TestCase):
    def _package_receipts(self) -> tuple[dict, dict]:
        package_receipt = build_package_digest_receipt(
            REPO_ROOT,
            source_path=FIXTURE_SKILL / "SKILL.md",
            query=FIXTURE_SKILL.as_posix(),
        )
        hardening_receipt = build_package_hardening_receipt(package_receipt)
        return package_receipt, hardening_receipt

    def test_builder_emits_non_mutating_signing_intent(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()

        payload = build_signing_intent_receipt(
            policy_path=FIXTURE_POLICY,
            package_receipt=package_receipt,
            hardening_receipt=hardening_receipt,
        )
        model = validate_signing_intent_receipt(payload)

        self.assertEqual(model.schema_version, "skills-sdk.signing-intent-receipt.v0")
        self.assertEqual(model.status, "ready")
        self.assertEqual(model.package_id, "skills-sdk-valid-fixture")
        self.assertEqual(model.package_digest, package_receipt["package_digest"])
        self.assertFalse(model.signature_requested)
        self.assertFalse(model.signing_performed)
        self.assertFalse(model.key_material_accessed)
        self.assertFalse(model.artifact_emitted)
        self.assertFalse(model.mutation_performed)

    def test_builder_blocks_unpinned_package_digest(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()
        policy = deepcopy(json.loads(FIXTURE_POLICY.read_text(encoding="utf-8")))
        policy["allowed_package_digests"] = ["sha256:" + ("0" * 64)]

        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            with self.assertRaises(SigningIntentError) as raised:
                build_signing_intent_receipt(
                    policy_path=policy_path,
                    package_receipt=package_receipt,
                    hardening_receipt=hardening_receipt,
                )

        receipt = validate_signing_intent_receipt(raised.exception.receipt)
        self.assertEqual(receipt.status, "blocked")
        self.assertEqual(receipt.blockers[0].id, "package_digest_pinned")
        self.assertFalse(receipt.signing_performed)
        self.assertFalse(receipt.key_material_accessed)

    def test_builder_blocks_schema_invalid_policy(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()
        policy = deepcopy(json.loads(FIXTURE_POLICY.read_text(encoding="utf-8")))
        del policy["policy_id"]

        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            with self.assertRaises(SigningIntentError) as raised:
                build_signing_intent_receipt(
                    policy_path=policy_path,
                    package_receipt=package_receipt,
                    hardening_receipt=hardening_receipt,
                )

        receipt = validate_signing_intent_receipt(raised.exception.receipt)
        self.assertEqual(receipt.status, "blocked")
        self.assertIn("policy_contract_valid", {blocker.id for blocker in receipt.blockers})
        self.assertFalse(receipt.signing_performed)
        self.assertFalse(receipt.key_material_accessed)

    def test_fallback_contract_blocks_unknown_policy_fields(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()
        policy = deepcopy(json.loads(FIXTURE_POLICY.read_text(encoding="utf-8")))
        policy["private_key"] = "must-not-enter-receipts"
        real_import = builtins.__import__

        def import_without_pydantic(name: str, *args: object, **kwargs: object) -> object:
            if name == "pydantic":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            with mock.patch("builtins.__import__", side_effect=import_without_pydantic):
                with self.assertRaises(SigningIntentError) as raised:
                    build_signing_intent_receipt(
                        policy_path=policy_path,
                        package_receipt=package_receipt,
                        hardening_receipt=hardening_receipt,
                    )

        receipt = validate_signing_intent_receipt(raised.exception.receipt)
        contract_blocker = next(blocker for blocker in receipt.blockers if blocker.id == "policy_contract_valid")
        self.assertIn("private_key:extra_forbidden", contract_blocker.evidence)
        self.assertFalse(receipt.key_material_accessed)

    def test_fallback_contract_blocks_invalid_acceptance_trace(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()
        policy = deepcopy(json.loads(FIXTURE_POLICY.read_text(encoding="utf-8")))
        policy["acceptance_trace"] = ["BAD"]
        real_import = builtins.__import__

        def import_without_pydantic(name: str, *args: object, **kwargs: object) -> object:
            if name == "pydantic":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            with mock.patch("builtins.__import__", side_effect=import_without_pydantic):
                with self.assertRaises(SigningIntentError) as raised:
                    build_signing_intent_receipt(
                        policy_path=policy_path,
                        package_receipt=package_receipt,
                        hardening_receipt=hardening_receipt,
                    )

        receipt = validate_signing_intent_receipt(raised.exception.receipt)
        contract_blocker = next(blocker for blocker in receipt.blockers if blocker.id == "policy_contract_valid")
        self.assertIn("acceptance_trace.0:literal_error", contract_blocker.evidence)
        self.assertFalse(receipt.signing_performed)
        self.assertFalse(receipt.key_material_accessed)

    def test_fallback_contract_blocks_malformed_list_entries(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()
        policy = deepcopy(json.loads(FIXTURE_POLICY.read_text(encoding="utf-8")))
        policy["allowed_algorithms"] = ["cosign-keyless", 123]
        real_import = builtins.__import__

        def import_without_pydantic(name: str, *args: object, **kwargs: object) -> object:
            if name == "pydantic":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            with mock.patch("builtins.__import__", side_effect=import_without_pydantic):
                with self.assertRaises(SigningIntentError) as raised:
                    build_signing_intent_receipt(
                        policy_path=policy_path,
                        package_receipt=package_receipt,
                        hardening_receipt=hardening_receipt,
                    )

        receipt = validate_signing_intent_receipt(raised.exception.receipt)
        contract_blocker = next(blocker for blocker in receipt.blockers if blocker.id == "policy_contract_valid")
        self.assertIn("allowed_algorithms.1:string_type", contract_blocker.evidence)
        self.assertFalse(receipt.signing_performed)
        self.assertFalse(receipt.key_material_accessed)

    def test_fallback_contract_blocks_blank_list_entries(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()
        policy = deepcopy(json.loads(FIXTURE_POLICY.read_text(encoding="utf-8")))
        policy["allowed_package_ids"] = ["skills-sdk-valid-fixture", ""]
        real_import = builtins.__import__

        def import_without_pydantic(name: str, *args: object, **kwargs: object) -> object:
            if name == "pydantic":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            with mock.patch("builtins.__import__", side_effect=import_without_pydantic):
                with self.assertRaises(SigningIntentError) as raised:
                    build_signing_intent_receipt(
                        policy_path=policy_path,
                        package_receipt=package_receipt,
                        hardening_receipt=hardening_receipt,
                    )

        receipt = validate_signing_intent_receipt(raised.exception.receipt)
        contract_blocker = next(blocker for blocker in receipt.blockers if blocker.id == "policy_contract_valid")
        self.assertIn("allowed_package_ids.1:string_too_short", contract_blocker.evidence)
        self.assertFalse(receipt.signing_performed)
        self.assertFalse(receipt.key_material_accessed)

    def test_fallback_contract_handles_incompatible_pydantic_imports(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()
        policy = deepcopy(json.loads(FIXTURE_POLICY.read_text(encoding="utf-8")))
        policy["acceptance_trace"] = ["BAD"]
        real_import = builtins.__import__

        def import_with_incompatible_contracts(name: str, *args: object, **kwargs: object) -> object:
            if name == "ask.skills_sdk.signing_contracts":
                raise ImportError("pydantic v2 symbols unavailable")
            return real_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            with mock.patch("builtins.__import__", side_effect=import_with_incompatible_contracts):
                with self.assertRaises(SigningIntentError) as raised:
                    build_signing_intent_receipt(
                        policy_path=policy_path,
                        package_receipt=package_receipt,
                        hardening_receipt=hardening_receipt,
                    )

        receipt = validate_signing_intent_receipt(raised.exception.receipt)
        contract_blocker = next(blocker for blocker in receipt.blockers if blocker.id == "policy_contract_valid")
        self.assertIn("acceptance_trace.0:literal_error", contract_blocker.evidence)

    def test_builder_blocks_hardening_failure(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()
        hardening_receipt["status"] = "blocked"

        with self.assertRaises(SigningIntentError) as raised:
            build_signing_intent_receipt(
                policy_path=FIXTURE_POLICY,
                package_receipt=package_receipt,
                hardening_receipt=hardening_receipt,
            )

        receipt = validate_signing_intent_receipt(raised.exception.receipt)
        self.assertEqual(receipt.status, "blocked")
        self.assertIn("package_hardening_passed", {blocker.id for blocker in receipt.blockers})
        self.assertFalse(receipt.artifact_emitted)

    def test_public_cli_builds_signing_intent_receipt(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "package",
                "signing-intent",
                "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
                "--policy",
                "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/signing-policy.json",
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
        payload = envelope.data["skills_sdk_package_signing_intent"]
        self.assertIsInstance(payload, dict)
        receipt = validate_signing_intent_receipt(payload["receipt"])

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(receipt.status, "ready")
        self.assertEqual(receipt.policy_path, "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/signing-policy.json")
        self.assertFalse(payload["signing_performed"])
        self.assertFalse(payload["key_material_accessed"])
        self.assertFalse(payload["artifact_emitted"])
        self.assertIn("./bin/ask sdk package signing-intent", payload["validation_commands"][0])

    def test_public_cli_blocks_policy_mismatch(self) -> None:
        policy = deepcopy(json.loads(FIXTURE_POLICY.read_text(encoding="utf-8")))
        policy["allowed_package_ids"] = ["different-package"]
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "Infrastructure/bin/ask",
                    "sdk",
                    "package",
                    "signing-intent",
                    "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
                    "--policy",
                    str(policy_path),
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

        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_package_signing_intent"]
        self.assertEqual(envelope.status, "error")
        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["signing_performed"])
        self.assertFalse(payload["key_material_accessed"])


if __name__ == "__main__":
    unittest.main()
