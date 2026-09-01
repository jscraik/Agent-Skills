from __future__ import annotations

import importlib
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

package_build_compat = importlib.import_module("ask.skills_sdk.package_build_compat")
portable_adapter = importlib.import_module("ask.skills_sdk.portable_adapter")
packaging_models = importlib.import_module("skills_sdk.models.packaging")
validation_models = importlib.import_module("skills_sdk.models.validation")

build_package_projection = package_build_compat.build_package_projection
PortableAdapterBlocker = portable_adapter.PortableAdapterBlocker
PortableAdapterSuccess = portable_adapter.PortableAdapterSuccess
PortableSource = portable_adapter.PortableSource
PackageReceiptBlocker = packaging_models.PackageReceiptBlocker
PackageReceiptV2 = packaging_models.PackageReceiptV2
SkillPackageValidation = validation_models.SkillPackageValidation


def _git(directory: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(directory), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _skill_repository(tmp_path: Path) -> tuple[Path, str]:
    repository = tmp_path / "source"
    skill_root = repository / "skills" / "example-skill"
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        "---\nname: example-skill\ndescription: Validate this example skill.\n---\n\n# Example\n",
        encoding="utf-8",
    )
    _git(repository, "init", "-q")
    _git(repository, "config", "user.name", "Fixture")
    _git(repository, "config", "user.email", "fixture@example.invalid")
    _git(repository, "add", ".")
    _git(repository, "commit", "-q", "--no-gpg-sign", "-m", "fixture")
    return skill_root, _git(repository, "rev-parse", "HEAD")


def _projection(skill_root: Path):
    return build_package_projection(
        skill_root,
        query="example-skill",
        canonical_source_path="skills/example-skill/SKILL.md",
        validation_command="./bin/ask sdk package build example-skill --json --robot",
    )


def _blocked_receipt() -> PackageReceiptV2:
    timestamp = datetime(2026, 8, 31, tzinfo=UTC)
    return PackageReceiptV2(
        schema_version="package-receipt/v2",
        receipt_id="blocked-fixture",
        lane="validation",
        status="blocked",
        started_at=timestamp,
        finished_at=timestamp,
        evidence=("SKILL.md",),
        blocker=PackageReceiptBlocker(
            code="invalid_source_revision",
            message="source revision is invalid",
            evidence_refs=(),
        ),
    )


def _mock_success(receipt: object, tmp_path: Path) -> PortableAdapterSuccess:
    source = PortableSource(tmp_path, tmp_path, "a" * 40, False)
    payload = cast(SkillPackageValidation | PackageReceiptV2, receipt)
    return PortableAdapterSuccess("build", source, payload)


def test_build_accepts_current_sdk_package_receipt_v2(tmp_path: Path) -> None:
    skill_root, _revision = _skill_repository(tmp_path)

    projection = _projection(skill_root)
    receipt = PackageReceiptV2.model_validate(projection.payload["receipt"])

    assert receipt.schema_version == "package-receipt/v2"
    assert receipt.status == "built"
    assert receipt.mutation_performed is False


def test_v2_build_binds_candidate_manifest_and_digest(tmp_path: Path) -> None:
    skill_root, revision = _skill_repository(tmp_path)

    projection = _projection(skill_root)
    receipt = PackageReceiptV2.model_validate(projection.payload["receipt"])

    assert receipt.candidate is not None
    assert receipt.manifest is not None
    assert receipt.manifest.candidate == receipt.candidate
    assert receipt.candidate.source_revision == revision
    assert len(receipt.candidate.content_sha256) == 64
    assert receipt.package_digest is not None
    assert len(receipt.package_digest) == 64
    assert list(receipt.included_files) == [item.path for item in receipt.manifest.files]


def test_build_preserves_current_sdk_blocked_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ask.skills_sdk import package_build_compat

    receipt = _blocked_receipt()
    monkeypatch.setattr(
        package_build_compat,
        "run_portable_validation",
        lambda *_args, **_kwargs: _mock_success(receipt, tmp_path),
    )

    projection = _projection(tmp_path)
    embedded = PackageReceiptV2.model_validate(projection.payload["receipt"])

    assert projection.payload["status"] == "blocked"
    assert embedded.blocker == receipt.blocker
    assert embedded.candidate is None
    assert embedded.manifest is None
    assert embedded.package_digest is None
    assert embedded.mutation_performed is False


def test_build_rejects_unexpected_sdk_payload_type(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ask.skills_sdk import package_build_compat

    monkeypatch.setattr(
        package_build_compat,
        "run_portable_validation",
        lambda *_args, **_kwargs: _mock_success(object(), tmp_path),
    )

    with pytest.raises(TypeError, match="unexpected payload"):
        _projection(tmp_path)


def test_build_projection_maps_package_receipt_v2(tmp_path: Path) -> None:
    skill_root, revision = _skill_repository(tmp_path)

    projection = _projection(skill_root)
    payload = projection.payload
    receipt = PackageReceiptV2.model_validate(payload["receipt"])

    assert payload["status"] == receipt.status
    assert receipt.candidate is not None
    assert receipt.manifest is not None
    assert payload["package_id"] == receipt.candidate.package_id
    assert payload["source_revision"] == revision
    assert payload["source_digest"] == receipt.candidate.content_sha256
    assert payload["version"] == receipt.manifest.version
    assert payload["package_digest"] == receipt.package_digest
    assert payload["included_files"] == list(receipt.included_files)
    assert payload["excluded_files"] == list(receipt.excluded_files)


def test_blocked_v2_projection_preserves_typed_blocker_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ask.skills_sdk import package_build_compat

    receipt = _blocked_receipt()
    monkeypatch.setattr(
        package_build_compat,
        "run_portable_validation",
        lambda *_args, **_kwargs: _mock_success(receipt, tmp_path),
    )

    projection = _projection(tmp_path)
    embedded = projection.payload["receipt"]
    assert isinstance(embedded, dict)

    assert projection.error_message == "source revision is invalid"
    assert embedded["blocker"] == {
        "code": "invalid_source_revision",
        "message": "source revision is invalid",
        "evidence_refs": [],
    }
    assert "blocked" in projection.payload["agent_summary"]


def test_host_adapter_blocker_projection_stays_distinct_from_sdk_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ask.skills_sdk import package_build_compat

    blocker = PortableAdapterBlocker("source_not_git", "source is not Git-owned")
    monkeypatch.setattr(
        package_build_compat,
        "run_portable_validation",
        lambda *_args, **_kwargs: blocker,
    )

    projection = _projection(tmp_path)

    assert projection.payload["status"] == "blocked"
    assert projection.payload["adapter_blocker"] == {
        "code": "source_not_git",
        "message": "source is not Git-owned",
    }
    assert "receipt" not in projection.payload
    assert "package_digest" not in projection.payload
    assert projection.payload["mutation_performed"] is False


def test_package_build_cli_payload_remains_decision_sized_and_v2_bound(
    tmp_path: Path,
) -> None:
    skill_root, _revision = _skill_repository(tmp_path)

    payload = _projection(skill_root).payload

    assert payload["schema_version"] == "skills-sdk-package-build.v1"
    assert payload["facade_command"] == "skills-sdk package build"
    assert payload["validation_commands"] == [
        "./bin/ask sdk package build example-skill --json --robot"
    ]
    assert payload["receipt"]["schema_version"] == "package-receipt/v2"
    assert str(tmp_path) not in str(payload)
    assert "produced digest identity" in payload["agent_summary"]


def test_source_change_blocker_cannot_project_a_built_v2_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ask.skills_sdk import package_build_compat

    blocker = PortableAdapterBlocker(
        "source_changed_during_validation",
        "package source content changed during SDK delegation",
    )
    monkeypatch.setattr(
        package_build_compat,
        "run_portable_validation",
        lambda *_args, **_kwargs: blocker,
    )

    projection = _projection(tmp_path)

    assert projection.payload["status"] == "blocked"
    assert projection.payload["adapter_blocker"]["code"] == (
        "source_changed_during_validation"
    )
    assert "receipt" not in projection.payload
    assert projection.payload["mutation_performed"] is False


def test_projection_contract_declares_v1_receipt_compatibility_boundary(
    tmp_path: Path,
) -> None:
    skill_root, _revision = _skill_repository(tmp_path)

    payload = _projection(skill_root).payload

    assert payload["schema_version"] == "skills-sdk-package-build.v1"
    assert payload["receipt"]["schema_version"] == "package-receipt/v2"
