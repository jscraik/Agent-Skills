from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.package_verify import (  # noqa: E402
    _portable_blocker_validation,
    verify_skill_directory,
)
from ask.skills_sdk.portable_adapter import PortableAdapterBlocker  # noqa: E402
from ask.cli_output import compact_package_verify_payload  # noqa: E402
from skills_sdk.models import MantraAssessment  # noqa: E402


def _git(directory: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(directory), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _initialize_from_current_repository(root: Path) -> None:
    _git(root, "init", "-q")
    _git(root, "fetch", "-q", str(REPO_ROOT), "HEAD")
    _git(root, "reset", "-q", "--hard", "FETCH_HEAD")


def _write_skill(root: Path, *, declared_name: str = "example-skill") -> Path:
    skill_root = root / "Skills" / "example-skill"
    skill_root.mkdir(parents=True, exist_ok=True)
    (skill_root / "SKILL.md").write_text(
        "\n".join(
            (
                "---",
                f"name: {declared_name}",
                "description: Validate this package when testing the portable SDK adapter.",
                "short_description: Portable validation fixture.",
                "interface: cli",
                "dependencies: []",
                "policy: read-only",
                "scope: fixture",
                "plugin_id: fixture",
                "version: 1.0.0",
                "compatible_roles: [agent]",
                "runtime_needs: []",
                "maturity: stable",
                "provenance: [internal]",
                "share_readiness: private",
                "owner: tests",
                "source_kind: canonical-source",
                "metadata: {}",
                "---",
                "",
                "# Example",
                "",
            )
        ),
        encoding="utf-8",
    )
    return skill_root


def test_non_git_legacy_fixture_remains_supported(tmp_path: Path) -> None:
    skill_root = _write_skill(tmp_path)

    receipt = verify_skill_directory(
        tmp_path,
        skill_root / "SKILL.md",
        "Skills/example-skill",
        trusted_sources={"internal"},
    )

    assert receipt["portable_sdk_validation"]["status"] == "not_run"
    assert not any(
        item["rule_id"].startswith("portable_sdk_") for item in receipt["blockers"]
    )


def test_git_owned_directory_contains_json_portable_evidence(tmp_path: Path) -> None:
    _initialize_from_current_repository(tmp_path)
    skill_root = _write_skill(tmp_path)

    receipt = verify_skill_directory(
        tmp_path,
        skill_root / "SKILL.md",
        "Skills/example-skill",
        trusted_sources={"internal"},
    )

    portable = receipt["portable_sdk_validation"]
    assert portable["status"] == "pass"
    assert portable["source"]["source_revision"] == _git(tmp_path, "rev-parse", "HEAD")
    assert portable["result"]["schema_version"] == "skill-package-validation/v1"
    assert portable["result"]["mutation_performed"] is False


def test_sdk_finding_is_added_without_dropping_host_blockers(tmp_path: Path) -> None:
    _initialize_from_current_repository(tmp_path)
    skill_root = _write_skill(tmp_path, declared_name="different-name")

    receipt = verify_skill_directory(
        tmp_path,
        skill_root / "SKILL.md",
        "Skills/example-skill",
        trusted_sources={"internal"},
    )

    rule_ids = {item["rule_id"] for item in receipt["blockers"]}
    assert receipt["portable_sdk_validation"]["status"] == "blocked"
    assert any(rule_id.startswith("portable_sdk_") for rule_id in rule_ids)
    assert receipt["status"] == "blocked"


def test_adapter_dependency_direction_points_only_into_standalone_sdk() -> None:
    adapter = (
        REPO_ROOT
        / "Infrastructure"
        / "scripts"
        / "lib"
        / "ask"
        / "skills_sdk"
        / "portable_adapter.py"
    ).read_text(encoding="utf-8")

    assert "from skills_sdk." in adapter
    assert "ask.skills_sdk.ir" not in adapter
    assert "ask.skills_sdk.package_build" not in adapter


def test_default_cli_payload_keeps_decision_sized_portable_evidence(
    tmp_path: Path,
) -> None:
    _initialize_from_current_repository(tmp_path)
    skill_root = _write_skill(tmp_path)
    verification = verify_skill_directory(
        tmp_path,
        skill_root / "SKILL.md",
        "Skills/example-skill",
        trusted_sources={"internal"},
    )
    data = {"skill_package_verification": verification}

    compact_package_verify_payload(data)

    compact = data["skill_package_verification"]
    assert compact["checks"]
    assert compact["portable_sdk_validation"]["status"] == "pass"
    assert compact["portable_sdk_validation"]["result"] == {
        "schema_version": "skill-package-validation/v1",
        "candidate": verification["portable_sdk_validation"]["result"]["candidate"],
        "status": "pass",
        "findings": [],
        "mutation_performed": False,
    }
    assert "files" not in compact["portable_sdk_validation"]["result"]


def test_adapter_contract_names_owner_direction_and_retirement() -> None:
    contract_path = (
        REPO_ROOT
        / "Infrastructure"
        / "config"
        / "skills-sdk"
        / "portable-validation-adapter.v1.json"
    )
    contract = json.loads(contract_path.read_text(encoding="utf-8"))

    assert contract["source_owner"]["repository"] == "jscraik/skills-sdk"
    assert contract["source_owner"]["revision"] == (
        "373c2cc0f39980004d42848d5d1082e02440cdd1"
    )
    assert contract["dependency_direction"] == (
        "Agent-Skills host adapter -> Skills SDK public API"
    )
    assert contract["current_callers"] == [
        "ask.skills_sdk.package_verify.verify_skill_directory"
    ]
    assert contract["temporary_adapter"] is True
    assert contract["retirement_condition"]


def test_ownership_language_keeps_agent_skills_transitional() -> None:
    language = (REPO_ROOT / "UBIQUITOUS_LANGUAGE.md").read_text(encoding="utf-8")

    assert "transitional `agent-skills` repository" in language
    assert "**Skills SDK** supplies the portable lifecycle implementation" in language
    assert "Preserve `agent-skills` as the Skills SDK implementation" not in language


def test_adapter_mantra_assessments_bind_exact_implementation_candidates() -> None:
    assessments_root = (
        REPO_ROOT / "Infrastructure" / "config" / "skills-sdk" / "assessments"
    )
    names = (
        "portable-validation-adapter.v1.json",
        "portable-validation-adapter-race-repair.v1.json",
    )

    for name in names:
        assessment = json.loads(
            (assessments_root / name).read_text(encoding="utf-8")
        )
        mantra = MantraAssessment.model_validate(assessment["mantra"])
        archive = subprocess.run(
            [
                "git",
                "-C",
                str(REPO_ROOT),
                "archive",
                "--format=tar",
                mantra.source_revision,
                "--",
                *assessment["assessed_paths"],
            ],
            check=True,
            capture_output=True,
        ).stdout

        assert assessment["schema_version"] == "sdk-tranche-mantra-assessment/v1"
        assert assessment["digest_algorithm"] == "git-archive-tar-sha256"
        assert hashlib.sha256(archive).hexdigest() == mantra.content_sha256
        assert mantra.overall.value == "pass"


def test_host_adapter_blocker_uses_repo_relative_path(tmp_path: Path) -> None:
    skill_md = tmp_path / "Skills" / "example-skill" / "SKILL.md"
    skill_md.parent.mkdir(parents=True)

    evidence = _portable_blocker_validation(
        PortableAdapterBlocker(
            "source_owner_mismatch",
            "package source does not belong to the expected Git owner",
        ),
        tmp_path,
        skill_md,
    )

    assert evidence["blockers"][0]["path"] == "Skills/example-skill"


def test_symlinked_external_package_is_rejected_by_owner_boundary(
    tmp_path: Path,
) -> None:
    host_root = tmp_path / "host"
    external_root = tmp_path / "external"
    host_root.mkdir()
    external_root.mkdir()
    _initialize_from_current_repository(host_root)
    _initialize_from_current_repository(external_root)
    external_skill = _write_skill(external_root)
    linked_skill = host_root / "Skills" / "example-skill"
    linked_skill.parent.mkdir(parents=True, exist_ok=True)
    linked_skill.symlink_to(external_skill, target_is_directory=True)

    receipt = verify_skill_directory(
        host_root,
        linked_skill / "SKILL.md",
        "Skills/example-skill",
        trusted_sources={"internal"},
    )

    portable = receipt["portable_sdk_validation"]
    assert portable["status"] == "blocked"
    assert portable["source"] is None
    assert portable["result"] is None
    assert any(
        blocker["rule_id"] == "portable_sdk_source_owner_mismatch"
        for blocker in receipt["blockers"]
    )
