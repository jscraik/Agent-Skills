from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skills_sdk.models.packaging import PackageReceipt

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.package_build import build_package_digest_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import (  # noqa: E402
    validate_package_digest_receipt,
    validate_robot_envelope,
)

FIXTURE_SKILL = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


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


def _write_project_local_skill(project_root: Path) -> Path:
    skill_root = project_root / ".codex" / "skills" / "x-content-writer"
    skill_root.mkdir(parents=True)
    (project_root / "AGENTS.md").write_text("# X-writer Canary\n", encoding="utf-8")
    (project_root / "skills-sdk.json").write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.project.v1",
                "project": {"id": "x-writer-canary", "name": "X-writer Canary"},
                "skill_sources": [
                    {
                        "root": ".codex/skills",
                        "kind": "canonical_project_source",
                        "standard": "agent-skills",
                        "write_policy": "sdk_managed",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (skill_root / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: x-content-writer",
                "description: Project-local canary writer skill.",
                "---",
                "",
                "# X Content Writer",
                "",
                "Draft only from project-local evidence.",
            ]
        ),
        encoding="utf-8",
    )
    return skill_root


def _commit_project(project_root: Path) -> str:
    commands = (
        ("init", "-q"),
        ("config", "user.name", "Test Author"),
        ("config", "user.email", "test@example.invalid"),
        ("config", "commit.gpgsign", "false"),
        ("add", "."),
        ("commit", "-q", "-m", "test: seed package"),
    )
    for arguments in commands:
        subprocess.run(
            ["git", "-C", str(project_root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
    return subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _write_valid_project_skill(project_root: Path) -> Path:
    skill_root = project_root / ".codex" / "skills" / "skills-sdk-valid-fixture"
    shutil.copytree(FIXTURE_SKILL, skill_root)
    (project_root / "AGENTS.md").write_text("# Package Owner\n", encoding="utf-8")
    (project_root / "skills-sdk.json").write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.project.v1",
                "project": {"id": "package-owner", "name": "Package Owner"},
                "skill_sources": [
                    {
                        "root": ".codex/skills",
                        "kind": "canonical_project_source",
                        "standard": "agent-skills",
                        "write_policy": "sdk_managed",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return skill_root


def _run_package_build_cli(skill_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "package",
            "build",
            str(skill_root / "SKILL.md"),
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


class TestSkillsSdkPackageBuild(unittest.TestCase):
    def test_public_cli_blocks_package_without_immutable_git_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "x-writer-canary"
            skill_root = _write_project_local_skill(project_root)
            completed = _run_package_build_cli(skill_root)

        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_package_build"]

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["adapter_blocker"]["code"], "source_not_git")
        self.assertFalse(payload["mutation_performed"])

    def test_public_cli_builds_project_local_package_identity_from_declared_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "x-writer-canary"
            skill_root = _write_project_local_skill(project_root)
            source_revision = _commit_project(project_root)
            completed = _run_package_build_cli(skill_root)

        self.assertEqual(completed.returncode, 0, completed.stdout or completed.stderr)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_package_build"]
        receipt = PackageReceipt.model_validate(payload["receipt"])

        self.assertEqual(payload["status"], "built")
        self.assertEqual(receipt.candidate.package_id, "x-content-writer")
        self.assertEqual(receipt.candidate.source_revision, source_revision)
        self.assertEqual(receipt.schema_version, "package-receipt/v1")
        self.assertEqual(payload["included_files"], ["SKILL.md"])
        self.assertEqual(
            Path(str(payload["canonical_source_path"])).resolve(),
            (skill_root / "SKILL.md").resolve(),
        )

    def test_builder_emits_non_mutating_package_digest_receipt(self) -> None:
        payload = build_package_digest_receipt(
            REPO_ROOT,
            source_path=FIXTURE_SKILL / "SKILL.md",
            query=FIXTURE_SKILL.as_posix(),
        )
        model = validate_package_digest_receipt(payload)

        self.assertEqual(model.schema_version, "skills-sdk.package-digest-receipt.v0")
        self.assertEqual(model.package_id, "skills-sdk-valid-fixture")
        self.assertEqual(model.manifest.skill_ir_schema_version, "skills-sdk.skill-ir.v0")
        self.assertFalse(model.mutation_performed)
        self.assertEqual(
            model.included_files,
            [
                "Infrastructure/tests/fixtures/skills_sdk/valid_skill/README.md",
                "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md",
            ],
        )
        self.assertTrue(model.package_digest.startswith("sha256:"))

    def test_public_cli_builds_package_identity_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "package-owner"
            skill_root = _write_valid_project_skill(project_root)
            source_revision = _commit_project(project_root)
            completed = _run_package_build_cli(skill_root)

        self.assertEqual(completed.returncode, 0, completed.stdout or completed.stderr)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_package_build"]
        self.assertIsInstance(payload, dict)
        receipt = PackageReceipt.model_validate(payload["receipt"])

        self.assertEqual(payload["status"], "built")
        self.assertEqual(payload["package_digest"], receipt.package_digest)
        self.assertEqual(payload["source_revision"], source_revision)
        self.assertEqual(
            payload["included_files"],
            [
                "README.md",
                "SKILL.md",
            ],
        )
        self.assertEqual(receipt.schema_version, "package-receipt/v1")
        self.assertFalse(payload["mutation_performed"])
        self.assertIn("./bin/ask sdk package build", payload["validation_commands"][0])

    def test_public_cli_blocks_missing_skill_source(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "package",
                "build",
                "Infrastructure/tests/fixtures/skills_sdk/missing",
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
        payload = envelope.data["skills_sdk_package_build"]

        self.assertEqual(envelope.status, "error")
        self.assertEqual(envelope.errors[0].code, "ERR_VALIDATION")
        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["mutation_performed"])


if __name__ == "__main__":
    unittest.main()
