from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.portable_adapter import (  # noqa: E402
    PortableAdapterBlocker,
    PortableAdapterSuccess,
    PortableSource,
    SkillValidationPolicy,
    resolve_portable_source,
    run_portable_validation,
)
from skills_sdk.models.packaging import PackageReceiptV2  # noqa: E402
from skills_sdk.models.validation import SkillPackageValidation  # noqa: E402


def _git(directory: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(directory), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _skill_repository(tmp_path: Path, *, name: str = "example-skill") -> tuple[Path, str]:
    repository = tmp_path / "source"
    skill_root = repository / "skills" / name
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Validate this example skill.\n---\n\n# Example\n",
        encoding="utf-8",
    )
    _git(repository, "init", "-q")
    _git(repository, "config", "user.name", "Fixture")
    _git(repository, "config", "user.email", "fixture@example.invalid")
    _git(repository, "add", ".")
    _git(repository, "commit", "-q", "--no-gpg-sign", "-m", "fixture")
    return skill_root, _git(repository, "rev-parse", "HEAD")


def _tree_snapshot(root: Path) -> dict[str, tuple[bytes, int, int]]:
    return {
        path.relative_to(root).as_posix(): (path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _mutate_after_first_validation(
    monkeypatch: pytest.MonkeyPatch,
    mutation: Callable[[], None],
) -> None:
    from ask.skills_sdk import portable_adapter

    real_validate = portable_adapter.validate_skill_package
    calls = 0

    def mutate_after_capture(
        package_root: Path,
        *,
        source_revision: str,
        policy: SkillValidationPolicy | None = None,
    ) -> SkillPackageValidation:
        nonlocal calls
        result = real_validate(
            package_root,
            source_revision=source_revision,
            policy=policy,
        )
        calls += 1
        if calls == 1:
            mutation()
        return result

    monkeypatch.setattr(portable_adapter, "validate_skill_package", mutate_after_capture)


def _change_revision_after_final_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    from ask.skills_sdk import portable_adapter

    real_validate = portable_adapter.validate_skill_package
    real_git_output = portable_adapter._git_output
    state = {"calls": 0, "final_scan_complete": False}

    def final_validation(
        package_root: Path,
        *,
        source_revision: str,
        policy: SkillValidationPolicy | None = None,
    ) -> SkillPackageValidation:
        state["calls"] += 1
        result = real_validate(
            package_root,
            source_revision=source_revision,
            policy=policy,
        )
        state["final_scan_complete"] = state["calls"] == 2
        return result

    def revision_after_scan(directory: Path, *arguments: str) -> str | None:
        if arguments == ("rev-parse", "HEAD") and state["final_scan_complete"]:
            return "f" * 40
        return real_git_output(directory, *arguments)

    monkeypatch.setattr(portable_adapter, "validate_skill_package", final_validation)
    monkeypatch.setattr(portable_adapter, "_git_output", revision_after_scan)


def test_resolves_the_source_owners_revision(tmp_path: Path) -> None:
    skill_root, revision = _skill_repository(tmp_path)

    result = resolve_portable_source(skill_root)

    assert isinstance(result, PortableSource)
    assert result.owner_root == skill_root.parents[1]
    assert result.source_revision == revision
    assert result.dirty is False


def test_ignores_ambient_git_discovery_overrides(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill_root, revision = _skill_repository(tmp_path)
    foreign_repository = tmp_path / "foreign"
    foreign_repository.mkdir()
    _git(foreign_repository, "init", "-q")
    monkeypatch.setenv("GIT_DIR", str(foreign_repository / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(skill_root.parents[1]))

    result = resolve_portable_source(skill_root)

    assert isinstance(result, PortableSource)
    assert result.source_revision == revision


def test_path_escape_during_status_resolution_returns_a_typed_blocker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill_root, _revision = _skill_repository(tmp_path)
    from ask.skills_sdk import portable_adapter

    monkeypatch.setattr(portable_adapter, "_is_within", lambda _path, _root: True)
    monkeypatch.setattr(portable_adapter, "_is_dirty", lambda _root, _path: None)

    result = resolve_portable_source(skill_root)

    assert result == PortableAdapterBlocker(
        "source_status_unavailable",
        "package source status could not be determined",
    )


def test_dirty_probe_rejects_a_path_outside_the_owner(tmp_path: Path) -> None:
    from ask.skills_sdk.portable_adapter import _is_dirty

    owner = tmp_path / "owner"
    outside = tmp_path / "outside"
    owner.mkdir()
    outside.mkdir()

    assert _is_dirty(owner, outside) is None


def test_rejects_a_mismatched_expected_owner(tmp_path: Path) -> None:
    skill_root, _revision = _skill_repository(tmp_path)

    result = resolve_portable_source(skill_root, expected_owner_root=tmp_path / "different")

    assert result == PortableAdapterBlocker(
        "source_owner_mismatch",
        "package source does not belong to the expected Git owner",
    )


def test_rejects_a_non_git_source_without_fabricating_revision(tmp_path: Path) -> None:
    skill_root = tmp_path / "example-skill"
    skill_root.mkdir()

    result = resolve_portable_source(skill_root)

    assert result == PortableAdapterBlocker(
        "source_not_git",
        "package source is not in a Git worktree",
    )


def test_validation_reports_dirty_state_but_remains_read_only(tmp_path: Path) -> None:
    skill_root, revision = _skill_repository(tmp_path)
    (skill_root / "README.md").write_text("dirty\n", encoding="utf-8")

    result = run_portable_validation(skill_root, operation="validate")

    assert isinstance(result, PortableAdapterSuccess)
    assert isinstance(result.payload, SkillPackageValidation)
    assert result.source.dirty is True
    assert result.payload.candidate.source_revision == revision
    assert result.payload.mutation_performed is False


def test_build_blocks_dirty_source_before_sdk_packaging(tmp_path: Path) -> None:
    skill_root, _revision = _skill_repository(tmp_path)
    (skill_root / "README.md").write_text("dirty\n", encoding="utf-8")

    result = run_portable_validation(skill_root, operation="build")

    assert result == PortableAdapterBlocker(
        "source_not_immutable",
        "package build requires a clean Git-owned source",
    )


def test_build_returns_candidate_bound_sdk_receipt(tmp_path: Path) -> None:
    skill_root, revision = _skill_repository(tmp_path)

    result = run_portable_validation(skill_root, operation="build")

    assert isinstance(result, PortableAdapterSuccess)
    assert isinstance(result.payload, PackageReceiptV2)
    assert result.payload.schema_version == "package-receipt/v2"
    assert result.payload.candidate.source_revision == revision
    assert result.payload.manifest is not None
    assert result.payload.manifest.candidate == result.payload.candidate
    assert result.payload.package_digest is not None
    assert result.payload.status == "built"
    assert result.payload.mutation_performed is False


def test_build_blocks_ignored_package_content(tmp_path: Path) -> None:
    skill_root, _revision = _skill_repository(tmp_path)
    (skill_root.parents[1] / ".gitignore").write_text("skills/example-skill/generated.txt\n", encoding="utf-8")
    _git(skill_root.parents[1], "add", ".gitignore")
    _git(skill_root.parents[1], "commit", "-q", "--no-gpg-sign", "-m", "ignore generated")
    (skill_root / "generated.txt").write_text("ignored\n", encoding="utf-8")

    result = run_portable_validation(skill_root, operation="build")

    assert result == PortableAdapterBlocker(
        "source_not_immutable",
        "package build requires a clean Git-owned source",
    )


def test_build_rechecks_cleanliness_after_source_resolution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill_root, revision = _skill_repository(tmp_path)
    from ask.skills_sdk import portable_adapter

    real_resolve = portable_adapter.resolve_portable_source

    def mutate_after_resolution(
        source_path: Path,
        *,
        expected_owner_root: Path | None = None,
    ) -> PortableSource | PortableAdapterBlocker:
        source = real_resolve(
            source_path,
            expected_owner_root=expected_owner_root,
        )
        assert isinstance(source, PortableSource)
        (skill_root / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Changed after resolution.\n---\n",
            encoding="utf-8",
        )
        return source

    monkeypatch.setattr(portable_adapter, "resolve_portable_source", mutate_after_resolution)

    result = run_portable_validation(skill_root, operation="build")

    assert _git(skill_root, "rev-parse", "HEAD") == revision
    assert result == PortableAdapterBlocker(
        "source_changed_during_validation",
        "package source content changed during SDK delegation",
    )


def test_validation_rechecks_status_after_source_resolution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill_root, revision = _skill_repository(tmp_path)
    from ask.skills_sdk import portable_adapter

    real_resolve = portable_adapter.resolve_portable_source

    def mutate_after_resolution(
        source_path: Path,
        *,
        expected_owner_root: Path | None = None,
    ) -> PortableSource | PortableAdapterBlocker:
        source = real_resolve(source_path, expected_owner_root=expected_owner_root)
        assert isinstance(source, PortableSource)
        (skill_root / "README.md").write_text("dirty after resolution\n", encoding="utf-8")
        return source

    monkeypatch.setattr(portable_adapter, "resolve_portable_source", mutate_after_resolution)

    result = run_portable_validation(skill_root, operation="validate")

    assert _git(skill_root, "rev-parse", "HEAD") == revision
    assert result == PortableAdapterBlocker(
        "source_changed_during_validation",
        "package source content changed during SDK delegation",
    )


def test_build_blocks_when_the_final_status_probe_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill_root, _revision = _skill_repository(tmp_path)
    from ask.skills_sdk import portable_adapter

    statuses: Iterator[bool | None] = iter([False, None])
    monkeypatch.setattr(portable_adapter, "_is_dirty", lambda _root, _path: next(statuses))

    result = run_portable_validation(skill_root, operation="build")

    assert result == PortableAdapterBlocker(
        "source_status_unavailable",
        "package source status could not be determined",
    )


@pytest.mark.parametrize("operation", ["validate", "build"])
def test_delegation_rejects_a_revision_change(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    skill_root, revision = _skill_repository(tmp_path)
    from ask.skills_sdk import portable_adapter

    real_git_output = portable_adapter._git_output
    revisions: Iterator[str] = iter([revision, "f" * 40])

    def changing_git_output(directory: Path, *arguments: str) -> str | None:
        if arguments == ("rev-parse", "HEAD"):
            return next(revisions)
        return real_git_output(directory, *arguments)

    monkeypatch.setattr(portable_adapter, "_git_output", changing_git_output)

    result = run_portable_validation(skill_root, operation=operation)  # type: ignore[arg-type]

    assert result == PortableAdapterBlocker(
        "source_changed_during_validation",
        "package source revision changed during SDK delegation",
    )


def test_delegation_rechecks_revision_after_the_final_validation_scan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill_root, revision = _skill_repository(tmp_path)
    _change_revision_after_final_validation(monkeypatch)

    result = run_portable_validation(skill_root, operation="validate")

    assert revision == _git(skill_root, "rev-parse", "HEAD")
    assert result == PortableAdapterBlocker(
        "source_changed_during_validation",
        "package source revision changed during SDK delegation",
    )


@pytest.mark.parametrize("operation", ["validate", "build"])
def test_delegation_rejects_an_uncommitted_content_change(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    skill_root, revision = _skill_repository(tmp_path)
    _mutate_after_first_validation(
        monkeypatch,
        lambda: (skill_root / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Changed after capture.\n---\n\n# Changed\n",
            encoding="utf-8",
        ),
    )

    result = run_portable_validation(skill_root, operation=operation)  # type: ignore[arg-type]

    assert _git(skill_root, "rev-parse", "HEAD") == revision
    assert result == PortableAdapterBlocker(
        "source_changed_during_validation",
        "package source content changed during SDK delegation",
    )


def test_validation_rejects_a_dirty_to_dirty_content_change(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill_root, revision = _skill_repository(tmp_path)
    changed = skill_root / "README.md"
    changed.write_text("first dirty state\n", encoding="utf-8")
    _mutate_after_first_validation(
        monkeypatch,
        lambda: changed.write_text("second dirty state\n", encoding="utf-8"),
    )

    result = run_portable_validation(skill_root, operation="validate")

    assert _git(skill_root, "rev-parse", "HEAD") == revision
    assert result == PortableAdapterBlocker(
        "source_changed_during_validation",
        "package source content changed during SDK delegation",
    )


def test_validation_rejects_an_untracked_file_added_during_delegation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill_root, revision = _skill_repository(tmp_path)
    _mutate_after_first_validation(
        monkeypatch,
        lambda: (skill_root / "generated.txt").write_text("untracked\n", encoding="utf-8"),
    )

    result = run_portable_validation(skill_root, operation="validate")

    assert _git(skill_root, "rev-parse", "HEAD") == revision
    assert result == PortableAdapterBlocker(
        "source_changed_during_validation",
        "package source content changed during SDK delegation",
    )


def test_rejects_an_unsupported_operation(tmp_path: Path) -> None:
    skill_root, _revision = _skill_repository(tmp_path)

    with pytest.raises(ValueError, match="unsupported portable operation"):
        run_portable_validation(skill_root, operation="publish")  # type: ignore[arg-type]


@pytest.mark.parametrize("operation", ["validate", "build"])
def test_delegation_does_not_mutate_package_files(tmp_path: Path, operation: str) -> None:
    skill_root, _revision = _skill_repository(tmp_path)
    before = _tree_snapshot(skill_root)

    result = run_portable_validation(skill_root, operation=operation)  # type: ignore[arg-type]

    assert isinstance(result, PortableAdapterSuccess)
    assert _tree_snapshot(skill_root) == before
