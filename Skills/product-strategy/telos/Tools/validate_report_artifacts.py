"""Fail-closed validation for the five TELOS report input artifacts."""

from __future__ import annotations

import errno
import json
import os
import stat
from shutil import copyfile, rmtree
import sys
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "findings.json",
    "recommendations.json",
    "roadmap.json",
    "methodology.json",
    "narrative.json",
)
COMPLETION_MARKER = ".telos-artifacts-complete"
COMPLETION_MARKER_BYTES = b"TELOS_REPORT_ARTIFACTS_COMPLETE_V1\n"
LEVELS = frozenset(("low", "medium", "high"))
EPISTEMIC_STATUSES = frozenset(("observation", "inference", "unknown"))


def _required(mapping: dict[str, Any], keys: set[str], name: str) -> None:
    missing = sorted(keys - mapping.keys())
    if missing:
        raise ValueError(f"{name} missing required fields: {', '.join(missing)}")


def _strings(value: Any, name: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{name} must be an array of strings")


def _text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _validate_findings(value: Any) -> None:
    findings = _object(value, "findings.json")
    _required(findings, {"findings"}, "findings.json")
    if not isinstance(findings["findings"], list):
        raise ValueError("findings.json.findings must be an array")
    for index, finding in enumerate(findings["findings"]):
        item = _object(finding, f"finding[{index}]")
        _required(
            item,
            {
                "id",
                "title",
                "description",
                "evidence",
                "source",
                "severity",
                "epistemicStatus",
                "qualifiers",
            },
            f"finding[{index}]",
        )
        for key in ("id", "title", "description", "evidence", "source"):
            _text(item[key], f"finding[{index}].{key}")
        if item["severity"] not in {"critical", "high", "medium", "low"}:
            raise ValueError(f"finding[{index}].severity is invalid")
        if item["epistemicStatus"] not in EPISTEMIC_STATUSES:
            raise ValueError(f"finding[{index}].epistemicStatus is invalid")
        _strings(item["qualifiers"], f"finding[{index}].qualifiers")


def _validate_recommendations(value: Any) -> None:
    recommendations = _object(value, "recommendations.json")
    _required(recommendations, {"recommendations"}, "recommendations.json")
    if not isinstance(recommendations["recommendations"], list):
        raise ValueError("recommendations.json.recommendations must be an array")
    for index, recommendation in enumerate(recommendations["recommendations"]):
        item = _object(recommendation, f"recommendation[{index}]")
        _required(item, {"id", "title", "description", "priority"}, f"recommendation[{index}]")
        for key in ("id", "title", "description"):
            _text(item[key], f"recommendation[{index}].{key}")
        if item["priority"] not in {"immediate", "short-term", "long-term"}:
            raise ValueError(f"recommendation[{index}].priority is invalid")


def _validate_roadmap(value: Any) -> None:
    roadmap = _object(value, "roadmap.json")
    _required(roadmap, {"phases"}, "roadmap.json")
    if not isinstance(roadmap["phases"], list):
        raise ValueError("roadmap.json.phases must be an array")
    for index, phase in enumerate(roadmap["phases"]):
        item = _object(phase, f"phase[{index}]")
        _required(item, {"phase", "title", "description", "duration"}, f"phase[{index}]")
        for key in ("phase", "title", "description", "duration"):
            _text(item[key], f"phase[{index}].{key}")


def _validate_methodology(value: Any) -> None:
    methodology = _object(value, "methodology.json")
    _required(methodology, {"interviewCount", "roles"}, "methodology.json")
    if not isinstance(methodology["interviewCount"], int) or isinstance(methodology["interviewCount"], bool):
        raise ValueError("methodology.json.interviewCount must be an integer")
    _strings(methodology["roles"], "methodology.json.roles")


def _validate_narrative(value: Any) -> None:
    narrative = _object(value, "narrative.json")
    scalar_keys = ("reportDate", "context", "clientAsk", "currentState", "whyNow", "timelinePressures", "goodNews", "targetStateDescription", "commitmentRequired")
    list_keys = ("existentialRisks", "competitiveThreats", "requirements", "keyCapabilities", "successMetrics", "immediateSteps", "decisionPoints")
    _required(narrative, set(scalar_keys) | set(list_keys) | {"riskMatrix"}, "narrative.json")
    for key in scalar_keys:
        _text(narrative[key], f"narrative.json.{key}")
    for key in list_keys:
        _strings(narrative[key], f"narrative.json.{key}")
    if not isinstance(narrative["riskMatrix"], list):
        raise ValueError("narrative.json.riskMatrix must be an array")
    for index, risk in enumerate(narrative["riskMatrix"]):
        item = _object(risk, f"riskMatrix[{index}]")
        _required(item, {"risk", "probability", "impact", "mitigation"}, f"riskMatrix[{index}]")
        for key in ("risk", "probability", "impact", "mitigation"):
            _text(item[key], f"riskMatrix[{index}].{key}")
        if item["probability"] not in LEVELS or item["impact"] not in LEVELS:
            raise ValueError(f"riskMatrix[{index}] probability and impact must be low, medium, or high")


def _validate_artifacts(artifacts: dict[str, Any]) -> None:
    validators = (
        ("findings.json", _validate_findings),
        ("recommendations.json", _validate_recommendations),
        ("roadmap.json", _validate_roadmap),
        ("methodology.json", _validate_methodology),
        ("narrative.json", _validate_narrative),
    )
    for filename, validator in validators:
        validator(artifacts[filename])


def _validate_artifact_names(directory: Path, *, published: bool = False) -> None:
    actual_names = {path.name for path in directory.iterdir()}
    expected_names = set(REQUIRED_FILES)
    if published:
        expected_names.add(COMPLETION_MARKER)
    missing = sorted(expected_names - actual_names)
    unexpected = sorted(actual_names - expected_names)
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected: {', '.join(unexpected)}")
        raise ValueError(f"artifact directory must contain exactly the five required files ({'; '.join(details)})")


def _validate_artifact_files(paths: dict[str, Path]) -> None:
    for filename, path in paths.items():
        if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"missing, empty, or symlinked required artifact: {filename}")


def _artifact_paths(directory: Path, *, published: bool = False) -> dict[str, Path]:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("artifact directory must be a real directory, not a symlink")
    _validate_artifact_names(directory, published=published)
    paths = {filename: directory / filename for filename in REQUIRED_FILES}
    _validate_artifact_files(paths)
    if published:
        marker = directory / COMPLETION_MARKER
        if marker.is_symlink() or not marker.is_file() or marker.read_bytes() != COMPLETION_MARKER_BYTES:
            raise ValueError("published artifact directory has an invalid completion marker")
    return paths


def _validate_json_artifacts(paths: dict[str, Path]) -> None:
    artifacts: dict[str, Any] = {}
    for filename, path in paths.items():
        try:
            artifacts[filename] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid JSON artifact: {filename}") from exc
    _validate_artifacts(artifacts)


def validate_artifacts(directory: Path) -> None:
    """Validate an unmarked source/draft set of exactly five JSON files."""
    _validate_json_artifacts(_artifact_paths(directory))


def validate_published_artifacts(directory: Path) -> None:
    """Validate a consumable set, including its final completion marker."""
    _validate_json_artifacts(_artifact_paths(directory, published=True))


def _producer_destination(
    source_directory: Path, artifact_directory: Path
) -> tuple[Path, Path, Path]:
    source = source_directory.resolve()
    destination = artifact_directory.absolute().resolve()
    if source_directory.is_symlink() or not source.is_dir():
        raise ValueError("producer source must be a real directory")
    if destination == source or destination in source.parents or source in destination.parents:
        raise ValueError("producer source and output must be separate directories")
    if artifact_directory.exists() or artifact_directory.is_symlink():
        raise ValueError("producer output directory already exists")
    parent = destination.parent
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("producer output parent must be a real directory")
    return source, destination, parent


def _reserve_destination(destination: Path) -> None:
    """Reserve a new destination without replacing an external race winner."""
    try:
        os.mkdir(destination)
    except FileExistsError as exc:
        raise ValueError("producer output directory already exists") from exc


def _write_completion_marker(destination: Path) -> None:
    """Atomically publish the deterministic marker as the final directory entry."""
    temporary = destination / f".{COMPLETION_MARKER}.tmp"
    try:
        with temporary.open("xb") as stream:
            stream.write(COMPLETION_MARKER_BYTES)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination / COMPLETION_MARKER)
    except OSError:
        if temporary.exists() and not temporary.is_symlink():
            temporary.unlink()
        raise


def _reservation_identity(destination: Path) -> tuple[int, int]:
    metadata = os.lstat(destination)
    if not stat.S_ISDIR(metadata.st_mode):
        raise ValueError("producer destination reservation is not a directory")
    return metadata.st_dev, metadata.st_ino


def _remove_bound_reservation(
    parent_fd: int, name: str, identity: tuple[int, int], directory_flag: int, nofollow_flag: int
) -> None:
    metadata = os.lstat(name, dir_fd=parent_fd)
    if (metadata.st_dev, metadata.st_ino) != identity or not stat.S_ISDIR(metadata.st_mode):
        return
    reservation_fd = os.open(
        name,
        os.O_RDONLY | directory_flag | nofollow_flag,
        dir_fd=parent_fd,
    )
    try:
        bound_metadata = os.fstat(reservation_fd)
        if (bound_metadata.st_dev, bound_metadata.st_ino) != identity:
            return
        try:
            rmtree(".", dir_fd=reservation_fd)
        except OSError as exc:
            if exc.errno != errno.EINVAL:
                raise
        # This platform has no safe unlink-directory-by-handle primitive. Keep
        # the now-empty reservation directory rather than racing a pathname
        # based rmdir against an external replacement.
    finally:
        os.close(reservation_fd)


def _cleanup_owned_reservation(
    destination: Path, identity: tuple[int, int]
) -> None:
    """Remove only the still-owned reservation after a failed production."""
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    nofollow_flag = getattr(os, "O_NOFOLLOW", 0)
    if not directory_flag or not nofollow_flag:
        return
    parent_fd: int | None = None
    try:
        parent_fd = os.open(
            destination.parent,
            os.O_RDONLY | directory_flag | nofollow_flag,
        )
        _remove_bound_reservation(
            parent_fd,
            destination.name,
            identity,
            directory_flag,
            nofollow_flag,
        )
    except (NotImplementedError, OSError):
        # A disappeared, swapped, or unsupported descriptor-relative path is
        # never safe to remove. The original production failure is re-raised.
        return
    finally:
        if parent_fd is not None:
            os.close(parent_fd)


def produce_artifacts(source_directory: Path, artifact_directory: Path) -> None:
    """Materialize a validated five-file set without inventing report data.

    ``source_directory`` is the caller's completed, source-grounded draft set.
    The function exclusively reserves the requested destination, copies those
    exact JSON bytes into the reserved directory, and validates the complete
    set before returning it as published. Existing destinations and nested
    source / output paths are rejected so a rerun cannot merge with prior
    evidence or replace a destination created by another process.
    """
    source, destination, _parent = _producer_destination(source_directory, artifact_directory)
    source_paths = _artifact_paths(source)
    reservation_identity: tuple[int, int] | None = None
    try:
        _reserve_destination(destination)
        reservation_identity = _reservation_identity(destination)
        for filename, source_path in source_paths.items():
            copyfile(source_path, destination / filename)
        validate_artifacts(destination)
        _write_completion_marker(destination)
        validate_published_artifacts(destination)
    except (OSError, ValueError):
        if reservation_identity is not None:
            _cleanup_owned_reservation(destination, reservation_identity)
        raise


def main(argv: list[str]) -> int:
    if len(argv) == 2:
        operation = "validate"
    elif len(argv) == 4 and argv[1] == "--produce":
        operation = "produce"
    else:
        print(
            f"usage: {argv[0]} ARTIFACT_DIRECTORY | {argv[0]} --produce DRAFT_DIRECTORY ARTIFACT_DIRECTORY",
            file=sys.stderr,
        )
        return 2
    try:
        if operation == "validate":
            validate_published_artifacts(Path(argv[1]))
        else:
            produce_artifacts(Path(argv[2]), Path(argv[3]))
    except ValueError as exc:
        print(f"report artifact validation blocked: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"report artifact producer blocked: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
