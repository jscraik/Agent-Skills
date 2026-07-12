from __future__ import annotations

import hashlib
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


_AUTHORITY_FAMILY_IDS = ("eval", "trust", "plugin", "improve", "install", "rollback", "uninstall", "knowledge")
_AUTHORITY_SCHEMA_VERSIONS = {
    "skills_sdk_eval_ab_preview": "skills-sdk.ab-preview-receipt.v0",
    "skills_sdk_trust_decide": "skills-sdk.trust-decision-receipt.v0",
    "skills_sdk_plugin_review": "skills-sdk-plugin-review.v0",
    "skills_sdk_project_improve": "skills-sdk.project-improvement-receipt.v0",
    "skills_sdk_install_preview": "skills-sdk.install-preview.v1",
    "skills_sdk_project_rollback": "skills-sdk.project-cleanup-receipt.v1",
    "skills_sdk_project_uninstall": "skills-sdk.project-cleanup-receipt.v1",
    "knowledge_ingest": "skills-sdk-knowledge-ingest.v1",
}
_AUTHORITY_REPLAY_CASES = {
    "eval": {
        "receipt_key": "skills_sdk_eval_ab_preview",
        "command_token": "eval ab-preview",
        "fixture_paths": (
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill",
            "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/deterministic-eval-pass.json",
        ),
        "expected_status": "preview",
    },
    "trust": {
        "receipt_key": "skills_sdk_trust_decide",
        "command_token": "trust decide",
        "fixture_paths": ("Infrastructure/tests/fixtures/skills_sdk/valid_skill",),
        "expected_status": "preview",
    },
    "plugin": {
        "receipt_key": "skills_sdk_plugin_review",
        "command_token": "plugin review",
        "fixture_paths": ("Infrastructure/tests/fixtures/skills_sdk/valid_skill",),
        "expected_status": "preview",
    },
    "improve": {
        "receipt_key": "skills_sdk_project_improve",
        "command_token": "improve",
        "fixture_paths": ("Infrastructure/tests/fixtures/skills_sdk/parser_family_project",),
        "expected_status": "pass",
    },
    "install": {
        "receipt_key": "skills_sdk_install_preview",
        "command_token": "install Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",
        "fixture_paths": ("Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",),
        "expected_status": "preview",
    },
    "rollback": {
        "receipt_key": "skills_sdk_project_rollback",
        "command_token": "rollback --receipt Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",
        "fixture_paths": ("Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",),
        "expected_status": "preview",
    },
    "uninstall": {
        "receipt_key": "skills_sdk_project_uninstall",
        "command_token": "uninstall authority-replay-fixture --project-root Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",
        "fixture_paths": ("Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",),
        "expected_status": "preview",
    },
    "knowledge": {
        "receipt_key": "knowledge_ingest",
        "command_token": "knowledge ingest --extraction Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",
        "fixture_paths": ("Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",),
        "expected_status": "preview",
    },
}

_NEGATIVE_AUTHORITY_REPLAY_CASES = (
    (
        "eval_missing_fixture",
        "ask sdk eval ab-preview --skill-a Infrastructure/tests/fixtures/skills_sdk/valid_skill --skill-b Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill --fixture Infrastructure/tests/fixtures/skills_sdk/missing-eval.json --preview --json --robot",
        "skills_sdk_eval_ab_preview",
        "fixture_missing",
        ("Infrastructure/tests/fixtures/skills_sdk/valid_skill", "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"),
    ),
    (
        "trust_missing_source",
        "ask sdk trust decide Infrastructure/tests/fixtures/skills_sdk/missing_skill --decision trust --reason 'fixture passed local checks' --owner skills-sdk-tests --preview --json --robot",
        "skills_sdk_trust_decide",
        "canonical source is missing",
        ("Infrastructure/tests/fixtures/skills_sdk/valid_skill",),
    ),
    (
        "install_missing_source",
        "ask sdk install Infrastructure/tests/fixtures/skills_sdk/missing_skill --preview --json --robot",
        "skills_sdk_install_preview",
        "missing",
        ("Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",),
    ),
    (
        "plugin_missing_description",
        "ask sdk plugin create negative-skill --kind skill --category agent-ops --preview --json --robot",
        "skills_sdk_plugin_create",
        "description",
        ("Infrastructure/tests/fixtures/skills_sdk/valid_skill",),
    ),
    (
        "improve_missing_project",
        "ask sdk improve Infrastructure/tests/fixtures/skills_sdk/parser_family_project/skills/parser-family-example/SKILL.md --project-root Infrastructure/tests/fixtures/skills_sdk/missing-project --preview --json --robot",
        "skills_sdk_project_improve",
        "invalid_project_root",
        ("Infrastructure/tests/fixtures/skills_sdk/parser_family_project",),
    ),
    (
        "rollback_missing_receipt",
        "ask sdk rollback --receipt Infrastructure/tests/fixtures/skills_sdk/authority_replay_project/.harness/receipts/skills-sdk/install/missing.json --preview --json --robot",
        "skills_sdk_project_rollback",
        "missing_receipt",
        ("Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",),
    ),
    (
        "uninstall_unknown_skill",
        "ask sdk uninstall missing-skill --project-root Infrastructure/tests/fixtures/skills_sdk/authority_replay_project --preview --json --robot",
        "skills_sdk_project_uninstall",
        "unknown_skill_id",
        ("Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",),
    ),
    (
        "knowledge_missing_skill",
        "ask sdk knowledge ingest --extraction Infrastructure/tests/fixtures/skills_sdk/authority_replay_project/knowledge-extraction --skill Infrastructure/tests/fixtures/skills_sdk/missing-skill --preview --json --robot",
        None,
        "skill must point at",
        ("Infrastructure/tests/fixtures/skills_sdk/authority_replay_project",),
    ),
)


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

    def test_authority_replay_selection_is_separate_from_inventory_status(self) -> None:
        selection = build_parser_family_inventory_receipt(REPO_ROOT)["authority_replay_selection"]
        self.assertEqual(selection["status"], "planned")
        self.assertEqual(selection["authority_family_count"], 8)
        self.assertEqual(selection["selected_count"], 8)
        self.assertEqual(selection["blocked_count"], 0)
        selected = {
            row["id"]: row
            for row in selection["families"]
            if row["status"] == "selected_preview"
        }
        self.assertEqual(set(selected), set(_AUTHORITY_FAMILY_IDS))
        self.assertTrue(all(row["command"].startswith("ask sdk ") for row in selected.values()))
        self.assertTrue(all("--preview" in row["command"] for row in selected.values()))
        self.assertIn("repository-owned fixture", selection["selection_policy"][1])
        self.assertIn("Infrastructure/tests/fixtures/skills_sdk/", selected["eval"]["command"])
        self.assertIn("--fixture", selected["eval"]["command"])
        self.assertEqual(selection["blockers"], [])

    def test_authority_replay_previews_emit_receipts_without_mutation(self) -> None:
        for family_id, case in _AUTHORITY_REPLAY_CASES.items():
            preview_commands = [
                command
                for command in COMMAND_EXAMPLES[("sdk", family_id)]
                if "--preview" in shlex.split(command) and case["command_token"] in command
            ]
            self.assertGreaterEqual(len(preview_commands), 1, family_id)
            for command in preview_commands:
                with self.subTest(family_id=family_id, command=command):
                    _assert_authority_replay_preview(self, command, case)

    def test_authority_replay_negative_inputs_block_without_mutation(self) -> None:
        for case_id, command, receipt_key, blocker, fixture_paths in _NEGATIVE_AUTHORITY_REPLAY_CASES:
            with self.subTest(case_id=case_id):
                _assert_negative_authority_replay(
                    self,
                    command=command,
                    receipt_key=receipt_key,
                    blocker=blocker,
                    fixture_paths=fixture_paths,
                )

    def test_owned_cleanup_fixture_receipts_match_install_and_lockfile_schemas(self) -> None:
        fixture_root = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/authority_replay_project"
        install_schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json"
        lockfile_schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json"
        install_schema = json.loads(install_schema_path.read_text(encoding="utf-8"))
        lockfile_schema = json.loads(lockfile_schema_path.read_text(encoding="utf-8"))
        install_receipt = json.loads(
            (fixture_root / ".harness/receipts/skills-sdk/install/authority-replay-fixture.json").read_text(
                encoding="utf-8"
            )
        )
        lockfile = json.loads((fixture_root / "skills.lock.json").read_text(encoding="utf-8"))

        _validate_schema_subset(install_schema, install_receipt, {install_schema_path.name: install_schema})
        _validate_schema_subset(
            lockfile_schema,
            lockfile,
            {lockfile_schema_path.name: lockfile_schema, install_schema_path.name: install_schema},
        )
        self.assertEqual(
            (fixture_root / "skills/authority-replay-fixture/SKILL.md").read_bytes(),
            (fixture_root / ".agents/skills/authority-replay-fixture/SKILL.md").read_bytes(),
        )

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

    def test_retained_authority_replay_artifact_matches_current_selection(self) -> None:
        artifact_path = REPO_ROOT / ".harness/evidence/handoff/skills-sdk-parser-families/authority-parser-replay-selection.json"
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        selection = build_parser_family_inventory_receipt(REPO_ROOT)["authority_replay_selection"]

        _assert_retained_artifact_core(self, artifact, selection)
        _assert_retained_artifact_replays(self, artifact)


def _assert_retained_artifact_core(test_case: unittest.TestCase, artifact: dict, selection: dict) -> None:
    test_case.assertEqual(artifact["schema_version"], "skills-sdk.parser-family-authority-replay-selection.v1")
    test_case.assertEqual(artifact["source_tree_digest"], _source_tree_digest(artifact["source_files"]))
    for field in ("authority_family_count", "selected_count", "blocked_count"):
        test_case.assertEqual(artifact[field], selection[field])
    test_case.assertEqual(artifact["selection_policy"], selection["selection_policy"])
    test_case.assertEqual(
        {row["family"] for row in artifact["selected_preview_commands"]},
        {row["id"] for row in selection["families"] if row["status"] == "selected_preview"},
    )
    test_case.assertEqual(
        {row["family"]: row["command"] for row in artifact["selected_preview_commands"]},
        {row["id"]: row["command"] for row in selection["families"] if row["status"] == "selected_preview"},
    )
    test_case.assertEqual(
        {row["family"] for row in artifact["blocked_fixture_families"]},
        {row["id"] for row in selection["families"] if row["status"] == "blocked_fixture"},
    )


def _assert_retained_artifact_replays(test_case: unittest.TestCase, artifact: dict) -> None:
    test_case.assertEqual(artifact["receipt_backed_replay_status"], "pass")
    test_case.assertEqual(
        {row["family"] for row in artifact["receipt_backed_replays"]},
        set(_AUTHORITY_REPLAY_CASES),
    )
    test_case.assertEqual(
        {row["family"]: row["expected_receipt_status"] for row in artifact["receipt_backed_replays"]},
        {family_id: case["expected_status"] for family_id, case in _AUTHORITY_REPLAY_CASES.items()},
    )
    negative_coverage = artifact["negative_replay_coverage"]
    test_case.assertEqual(negative_coverage["status"], "pass")
    test_case.assertEqual(
        {row["family"] for row in negative_coverage["families"]},
        set(_AUTHORITY_REPLAY_CASES),
    )
    test_case.assertTrue(
        all(
            row["expected_status"] in {"blocked", "blocked_error"}
            and "fixture_snapshot:unchanged" in row["mutation_evidence"]
            and "runtime_snapshot:unchanged" in row["mutation_evidence"]
            for row in negative_coverage["families"]
        )
    )


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


def _assert_authority_replay_preview(
    testcase: unittest.TestCase,
    command: str,
    case: dict[str, object],
) -> None:
    fixture_paths = tuple(case["fixture_paths"])
    before = {path: _snapshot_files(REPO_ROOT / path) for path in fixture_paths}
    process = _run_metadata_example(command)
    after = {path: _snapshot_files(REPO_ROOT / path) for path in fixture_paths}

    testcase.assertEqual(process.returncode, 0, process.stderr)
    testcase.assertEqual(after, before)
    payload = json.loads(process.stdout)
    result = payload["data"][case["receipt_key"]]
    receipt = result.get("receipt", result)
    testcase.assertEqual(receipt["status"], case["expected_status"])
    testcase.assertFalse(result.get("mutation_performed", False))
    _assert_authority_receipt_identity(testcase, case["receipt_key"], result, receipt)
    _assert_authority_receipt_schema(testcase, case, result, receipt)
    _assert_authority_receipt_fields(testcase, case["receipt_key"], result, receipt)


def _assert_authority_receipt_identity(
    testcase: unittest.TestCase,
    receipt_key: object,
    result: dict[str, object],
    receipt: dict[str, object],
) -> None:
    identity = result["preview"] if receipt_key == "skills_sdk_install_preview" else receipt
    if receipt_key in {"skills_sdk_plugin_review", "knowledge_ingest"}:
        identity = result
    if receipt_key == "skills_sdk_project_improve":
        identity = receipt
    testcase.assertEqual(identity["schema_version"], _AUTHORITY_SCHEMA_VERSIONS[receipt_key])


def _assert_authority_receipt_schema(
    testcase: unittest.TestCase,
    case: dict[str, object],
    result: dict[str, object],
    receipt: dict[str, object],
) -> None:
    schema_names = {
        "skills_sdk_eval_ab_preview": "ab-preview-receipt.v0.schema.json",
        "skills_sdk_trust_decide": "trust-decision-receipt.v0.schema.json",
        "skills_sdk_install_preview": "install-preview.v1.schema.json",
        "skills_sdk_project_rollback": "project-cleanup-receipt.v1.schema.json",
        "skills_sdk_project_uninstall": "project-cleanup-receipt.v1.schema.json",
    }
    schema_name = schema_names.get(case["receipt_key"])
    if schema_name is None:
        return
    schema_dir = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk"
    schema_payload = json.loads((schema_dir / schema_name).read_text(encoding="utf-8"))
    schema_receipt = result["preview"] if case["receipt_key"] == "skills_sdk_install_preview" else receipt
    schemas = {schema_name: schema_payload}
    schemas.update(
        {
            referenced_name: json.loads((schema_dir / referenced_name).read_text(encoding="utf-8"))
            for referenced_name in (
                "eval-profile-preview-receipt.v0.schema.json",
                "lockfile-preview.v1.schema.json",
            )
        }
    )
    _validate_schema_subset(schema_payload, schema_receipt, schemas)


def _assert_negative_authority_replay(
    testcase: unittest.TestCase,
    *,
    command: str,
    receipt_key: str | None,
    blocker: str,
    fixture_paths: tuple[str, ...],
) -> None:
    before = {path: _snapshot_files(REPO_ROOT / path) for path in fixture_paths}
    with tempfile.TemporaryDirectory() as directory:
        runtime_root = Path(directory)
        before_runtime = _snapshot_files(runtime_root)
        process = _run_metadata_example(command, env=_isolated_runtime_env(runtime_root))
        after_runtime = _snapshot_files(runtime_root)
    after = {path: _snapshot_files(REPO_ROOT / path) for path in fixture_paths}

    testcase.assertNotEqual(process.returncode, 0, process.stdout)
    testcase.assertEqual(after, before)
    testcase.assertEqual(after_runtime, before_runtime)
    payload = json.loads(process.stdout)
    if receipt_key is None:
        testcase.assertIn(blocker, json.dumps(payload).lower())
        return
    result = payload["data"][receipt_key]
    testcase.assertEqual(result["status"], "blocked")
    testcase.assertIn(blocker, json.dumps(result).lower())
    testcase.assertFalse(result.get("mutation_performed", False))


def _assert_authority_receipt_fields(
    testcase: unittest.TestCase,
    receipt_key: object,
    result: dict[str, object],
    receipt: dict[str, object],
) -> None:
    if receipt_key in {"skills_sdk_project_rollback", "skills_sdk_project_uninstall"}:
        testcase.assertTrue(receipt["files_planned"])
    elif receipt_key == "knowledge_ingest":
        testcase.assertEqual(receipt["staged_preflight"]["status"], "pass")
        testcase.assertTrue(all(item["action"] == "preview" for item in receipt["copied_files"]))
    elif receipt_key == "skills_sdk_trust_decide":
        testcase.assertFalse(result["trust_store_mutated"])
    elif receipt_key == "skills_sdk_project_improve":
        testcase.assertFalse(result["source_mutation_performed"])
    elif receipt_key == "skills_sdk_eval_ab_preview":
        testcase.assertFalse(receipt["codex_exec_invoked"])
        testcase.assertFalse(receipt["network_accessed"])
    elif receipt_key == "skills_sdk_plugin_review":
        testcase.assertTrue(result["planned_commands"])
    elif receipt_key == "skills_sdk_install_preview":
        testcase.assertFalse(result["preview"]["mutation_performed"])


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


def _run_metadata_example(
    command: str,
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    argv = shlex.split(command)
    wrapper = "bin/skills-sdk" if argv[0] == "skills-sdk" else "Infrastructure/bin/ask"
    return subprocess.run(
        [sys.executable, wrapper, *argv[1:]],
        cwd=REPO_ROOT,
        env=env or _command_env(),
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


def _source_tree_digest(paths: list[str]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.encode())
        digest.update(b"\0")
        digest.update((REPO_ROOT / path).read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


if __name__ == "__main__":
    unittest.main()
