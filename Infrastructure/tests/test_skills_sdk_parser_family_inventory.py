from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from ask.skills_sdk.parser_family_inventory import (  # noqa: E402
    PARSER_FAMILY_IDS,
    _discover_compatibility_examples,
    _receipt_policy,
    _requires_concrete_fixture,
    build_parser_family_inventory_receipt,
)
from ask.command_metadata import COMMAND_EXAMPLES, VALID_ACTIONS  # noqa: E402
from helpers.schema_validator import _validate_schema_subset  # noqa: E402


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-parser-family-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _snapshot_files(root: Path) -> list[tuple[str, bytes]]:
    return sorted(
        (path.relative_to(root).as_posix(), path.read_bytes())
        for path in root.rglob("*")
        if path.is_file()
    )


class TestSkillsSdkParserFamilyInventory(unittest.TestCase):
    def test_inventory_proves_registration_dispatch_and_policy_without_execution(self) -> None:
        receipt = build_parser_family_inventory_receipt(REPO_ROOT)

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["family_count"], len(PARSER_FAMILY_IDS))
        self.assertEqual({family["id"] for family in receipt["families"]}, set(PARSER_FAMILY_IDS))
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["command_execution_performed"])
        self.assertTrue(
            all(
                (REPO_ROOT / family["registration_owner"]["path"]).is_file()
                and (REPO_ROOT / family["dispatch_owner"]["path"]).is_file()
                for family in receipt["families"]
            )
        )
        self.assertTrue(all(family["receipt_policy"]["disposition"] for family in receipt["families"]))
        self.assertTrue(all(family["caller_consequence"] for family in receipt["families"]))
        self.assertEqual(
            {family["receipt_policy"]["disposition"] for family in receipt["families"]},
            {"authority_bound_mutation", "explicit_run_receipt", "preview_replay"},
        )
        eval_family = next(family for family in receipt["families"] if family["id"] == "eval")
        self.assertEqual(eval_family["receipt_policy"]["disposition"], "authority_bound_mutation")
        self.assertTrue(eval_family["receipt_policy"]["requires_concrete_fixture"])

        missing_examples = {
            family["id"]
            for family in receipt["families"]
            if not family["compatibility_examples"]
        }
        self.assertEqual(missing_examples, set())
        compatibility_check = next(
            check for check in receipt["checks"] if check["id"] == "missing_compatibility_examples"
        )
        self.assertEqual(compatibility_check["status"], "pass")

    def test_registered_edge_families_have_concrete_command_metadata_examples(self) -> None:
        edge_families = {"start", "route-map", "plugin", "improve"}

        self.assertTrue(edge_families.issubset(set(VALID_ACTIONS["sdk"])))
        for family_id in edge_families:
            examples = COMMAND_EXAMPLES[("sdk", family_id)]
            self.assertTrue(examples, family_id)
            self.assertTrue(all("<" not in example and ">" not in example for example in examples))
            self.assertTrue(any(example.startswith("ask sdk ") for example in examples))

    def test_improve_example_replays_against_repo_fixture_without_writes(self) -> None:
        command = COMMAND_EXAMPLES[("sdk", "improve")][0]
        process = _run_metadata_example(command)

        self.assertEqual(process.returncode, 0, process.stderr)
        receipt = json.loads(process.stdout)["data"]["skills_sdk_project_improve"]["receipt"]
        self.assertEqual(receipt["status"], "pass")
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["source_mutation_performed"])

    def test_cli_emits_non_mutating_parser_family_receipt_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runtime_root = Path(directory)
            env = _isolated_runtime_env(runtime_root)
            before_runtime = _snapshot_files(runtime_root)
            before_status = _git_status()
            process = _run_parser_family_cli(env)
            after_runtime = _snapshot_files(runtime_root)

        self.assert_non_mutating_receipt(process)
        self.assertEqual(after_runtime, before_runtime)
        self.assertEqual(_git_status(), before_status)

    def assert_non_mutating_receipt(self, process: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(process.returncode, 0, process.stderr)
        receipt = json.loads(process.stdout)["data"]["skills_sdk_parser_family_inventory"]["receipt"]
        self.assertEqual(receipt["status"], "pass")
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["command_execution_performed"])

    def test_policy_keeps_authority_and_fixture_requirements_separate(self) -> None:
        self.assertTrue(_requires_concrete_fixture(["ask sdk eval regression-plan --view-json <run-id> --preview"]))
        self.assertEqual(
            _receipt_policy("eval", ["ask sdk eval regression-plan --view-json <run-id> --preview"]),
            "authority_bound_mutation",
        )
        self.assertFalse(_requires_concrete_fixture(["ask sdk check fixture --prompt 'a>b'"]))

    def test_command_metadata_discovery_rejects_unrelated_strings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            metadata_path = Path(directory) / "command_metadata.py"
            metadata_path.write_text(
                "COMMAND_EXAMPLES = {('sdk', 'check'): ['skills-sdk check fixture --preview']}\n"
                "DOC = 'skills-sdk plugin hidden --preview'\n",
                encoding="utf-8",
            )
            examples = _discover_compatibility_examples(REPO_ROOT, metadata_path=metadata_path)

        self.assertEqual(examples["check"], ["skills-sdk check fixture --preview"])
        self.assertEqual(examples["plugin"], [])

    def test_parity_drift_keeps_blocked_receipt_schema_valid(self) -> None:
        registered = build_parser_family_inventory_receipt(REPO_ROOT)["families"]
        registered_map = {
            family["id"]: family["registration_owner"] for family in registered
        }
        dispatched_map = {
            family["id"]: family["dispatch_owner"] for family in registered
        }
        registered_map.pop("start")
        dispatched_map.pop("check")
        with patch(
            "ask.skills_sdk.parser_family_inventory._discover_registered_families",
            return_value=registered_map,
        ), patch(
            "ask.skills_sdk.parser_family_inventory._discover_dispatch_families",
            return_value=dispatched_map,
        ):
            receipt = build_parser_family_inventory_receipt(REPO_ROOT)

        schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/parser-family-inventory-receipt.v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        _validate_schema_subset(schema, receipt, {schema_path.name: schema})
        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(receipt["families"][0]["registration_owner"]["path"].startswith("<unresolved-"))
        self.assertTrue(receipt["families"][1]["dispatch_owner"]["path"].startswith("<unresolved-"))

    def test_receipt_matches_its_schema(self) -> None:
        receipt = build_parser_family_inventory_receipt(REPO_ROOT)
        schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/parser-family-inventory-receipt.v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        _validate_schema_subset(schema, receipt, {schema_path.name: schema})


def _isolated_runtime_env(runtime_root: Path) -> dict[str, str]:
    env = _command_env()
    for key, suffix in {
        "XDG_CACHE_HOME": "xdg-cache",
        "XDG_STATE_HOME": "xdg-state",
        "MISE_CACHE_DIR": "mise-cache",
        "MISE_STATE_DIR": "mise-state",
        "UV_CACHE_DIR": "uv-cache",
    }.items():
        env[key] = str(runtime_root / suffix)
    return env


def _run_parser_family_cli(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "evidence",
            "parser-families",
            "--preview",
            "--json",
            "--robot",
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _run_metadata_example(command: str) -> subprocess.CompletedProcess[str]:
    argv = shlex.split(command)
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *argv[1:]],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _git_status() -> str:
    return subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout


if __name__ == "__main__":
    unittest.main()
