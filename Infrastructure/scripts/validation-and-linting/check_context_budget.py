#!/usr/bin/env python3
# pylint: disable=import-outside-toplevel,wrong-import-position,too-many-branches
"""Validate context-budgeted skill-tree projection artifacts."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
LIFECYCLE_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"
RUNTIME_SEP_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "runtime-separation"
if str(LIFECYCLE_DIR) not in sys.path:
    sys.path.insert(0, str(LIFECYCLE_DIR))
if str(RUNTIME_SEP_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SEP_DIR))

_root_skill_sets = importlib.import_module("generate_root_skill_sets")
_skillset_manifests = importlib.import_module("generate_skillset_manifests")
_projection_runtime = importlib.import_module("rooted_projection_runtime")
_selection_policy = importlib.import_module("selection_policy")
_yaml_compat = importlib.import_module("yaml_compat")
build_roots = _root_skill_sets.build_roots
build_manifest_report = _skillset_manifests.build_manifest_report
direct_runtime_names_from_manifest_report = (
    _projection_runtime.direct_runtime_names_from_manifest_report
)
ROOT_SKILL_SET_NAMES = _selection_policy.ROOT_SKILL_SET_NAMES
policy_identity = _selection_policy.policy_identity
load_yaml_mapping = _yaml_compat.load_yaml_mapping

# codex-primary-runtime is an active runtime projection directory, not a rooted
# policy skill set, but manifest provenance may legitimately point through it.
ALLOWED_FIRST_LEVEL_MANIFEST_ROOTS = set(ROOT_SKILL_SET_NAMES) | {
    "codex-primary-runtime"
}
file_hash = importlib.import_module("skillset_model").file_hash

CONFIG_PATH = REPO_ROOT / "Infrastructure" / "GOVERNANCE" / "context-budget.yaml"
DEFAULTS = {
    "runtime_projection": {
        "max_root_skill_sets": 10,
        "max_root_description_words_total": 350,
        "max_root_body_words_each": 250,
    },
    "routing": {
        "max_candidates_returned": 3,
    },
    "workouts": {"max_skill_context_tokens": 1500},
}


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    if not path.is_file():
        return json.loads(json.dumps(DEFAULTS))
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None

    try:
        loaded = (
            yaml.safe_load(path.read_text(encoding="utf-8"))
            if yaml
            else load_yaml_mapping(path)
        )
        loaded = loaded or {}
    except UnicodeDecodeError as exc:
        # Malformed encoding; re-raise to surface the error
        raise ValueError(f"Failed to load configuration from {path}: {exc}") from exc
    except Exception as exc:
        # Malformed YAML or encoding issue; re-raise to surface the error
        raise ValueError(f"Failed to load configuration from {path}: {exc}") from exc

    merged = json.loads(json.dumps(DEFAULTS))
    for section, values in loaded.items():
        if isinstance(values, dict) and isinstance(merged.get(section), dict):
            merged[section].update(values)
        else:
            merged[section] = values
    return merged


def word_count(text: str) -> int:
    return len([word for word in text.split() if word.strip()])


def first_level_runtime_entries() -> list[str]:
    skills_dir = REPO_ROOT / ".agents" / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(
        item.name
        for item in skills_dir.iterdir()
        if item.is_dir()
        and not item.name.startswith(".")
        and (item / "SKILL.md").exists()
    )


def _allowed_manifest_paths() -> set[Path]:
    paths = {
        Path(".skillsets") / skill_set / "manifest.jsonl"
        for skill_set in ROOT_SKILL_SET_NAMES
    }
    paths.add(Path(".skillsets") / "command-surface.json")
    return paths


def _relative_skillset_path(
    path: Path, skillsets_dir: Path, repo_root_path: Path
) -> Path | None:
    try:
        return path.relative_to(repo_root_path)
    except ValueError:
        try:
            return Path(".skillsets") / path.relative_to(skillsets_dir)
        except ValueError:
            return None


def _command_surface_violations(path: Path, rel_path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [
            {
                "code": "INVALID_COMMAND_SURFACE_JSON",
                "path": rel_path.as_posix(),
                "message": str(exc),
            }
        ]
    if isinstance(payload, dict) and isinstance(payload.get("handles"), list):
        return []
    return [
        {
            "code": "INVALID_COMMAND_SURFACE_SHAPE",
            "path": rel_path.as_posix(),
            "message": "command-surface.json must contain a handles array",
        }
    ]


def _canonical_source_path(row: dict[str, Any], source_path: str) -> bool:
    parts = Path(source_path).parts
    plugin_skills_index = parts.index("skills") if "skills" in parts else -1
    system_bridge = (
        row.get("scope") == "system" and len(parts) >= 3 and parts[0] == "skills-system"
    )
    first_party = len(parts) >= 3 and parts[0] == "Skills"
    plugin_source = (
        len(parts) >= 4 and parts[0] == "Plugins" and plugin_skills_index >= 2
    )
    return ".." not in parts and (first_party or plugin_source or system_bridge)


def _source_file_violations(
    row: dict[str, Any], rel_path: Path, line_no: int, repo_root_path: Path
) -> tuple[Path | None, list[dict[str, Any]]]:
    source_path = row.get("source_path")
    context = {"path": rel_path.as_posix(), "line": line_no, "source_path": source_path}
    if not isinstance(source_path, str) or not source_path.endswith("/SKILL.md"):
        return None, [{"code": "SKILLSET_SOURCE_PATH_INVALID", **context}]
    if not _canonical_source_path(row, source_path):
        return None, [{"code": "SKILLSET_SOURCE_PATH_NOT_CANONICAL", **context}]
    source_file = repo_root_path / source_path
    if not source_file.is_file():
        return None, [{"code": "SKILLSET_SOURCE_PATH_MISSING", **context}]
    try:
        source_file.resolve().relative_to(repo_root_path.resolve())
    except ValueError:
        return None, [{"code": "SKILLSET_SOURCE_PATH_ESCAPES_REPO", **context}]
    return source_file, []


def _provenance_shape_violations(
    provenance: dict[str, Any], rel_path: Path, line_no: int
) -> list[dict[str, Any]]:
    context = {"path": rel_path.as_posix(), "line": line_no}
    required = {"generator", "projection_mode", "policy_identity", "source_sha256"}
    unknown = sorted(
        key for key in provenance if key not in required | {"generated_at"}
    )
    missing = sorted(key for key in required if not provenance.get(key))
    violations: list[dict[str, Any]] = []
    if unknown:
        violations.append(
            {
                "code": "SKILLSET_PROVENANCE_UNKNOWN_KEYS",
                **context,
                "unknown_keys": unknown,
            }
        )
    if missing:
        violations.append(
            {"code": "SKILLSET_PROVENANCE_INCOMPLETE", **context, "missing": missing}
        )
    if provenance.get("projection_mode") != "rooted":
        violations.append(
            {
                "code": "SKILLSET_PROVENANCE_MODE_MISMATCH",
                **context,
                "projection_mode": provenance.get("projection_mode"),
            }
        )
    return violations


def _provenance_value_violations(
    provenance: dict[str, Any],
    source_file: Path,
    source_path: str,
    rel_path: Path,
    line_no: int,
) -> list[dict[str, Any]]:
    context = {"path": rel_path.as_posix(), "line": line_no}
    violations: list[dict[str, Any]] = []
    if provenance.get("source_sha256") and provenance.get("source_sha256") != file_hash(
        source_file
    ):
        violations.append(
            {
                "code": "SKILLSET_SOURCE_HASH_STALE",
                **context,
                "source_path": source_path,
            }
        )
    current_policy_identity = policy_identity()
    if (
        provenance.get("policy_identity")
        and provenance.get("policy_identity") != current_policy_identity
    ):
        violations.append(
            {
                "code": "SKILLSET_POLICY_IDENTITY_STALE",
                **context,
                "expected": current_policy_identity,
                "actual": provenance.get("policy_identity"),
            }
        )
    return violations


def _manifest_row_violations(
    row: dict[str, Any], rel_path: Path, line_no: int, repo_root_path: Path
) -> list[dict[str, Any]]:
    context = {"path": rel_path.as_posix(), "line": line_no}
    violations: list[dict[str, Any]] = []
    expected_skill_set = rel_path.parts[1]
    if row.get("skill_set") != expected_skill_set:
        violations.append(
            {
                "code": "SKILLSET_ROW_OWNERSHIP_MISMATCH",
                **context,
                "expected": expected_skill_set,
                "actual": row.get("skill_set"),
            }
        )
    source_file, source_violations = _source_file_violations(
        row, rel_path, line_no, repo_root_path
    )
    violations.extend(source_violations)
    if source_file is None:
        return violations
    provenance = row.get("provenance")
    if not isinstance(provenance, dict):
        violations.append({"code": "SKILLSET_PROVENANCE_MISSING", **context})
        return violations
    violations.extend(_provenance_shape_violations(provenance, rel_path, line_no))
    violations.extend(
        _provenance_value_violations(
            provenance, source_file, row["source_path"], rel_path, line_no
        )
    )
    return violations


def _manifest_file_violations(
    path: Path, rel_path: Path, repo_root_path: Path
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for line_no, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            violations.append(
                {
                    "code": "INVALID_SKILLSET_MANIFEST_JSON",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "message": str(exc),
                }
            )
            continue
        if not isinstance(row, dict):
            violations.append(
                {
                    "code": "INVALID_SKILLSET_MANIFEST_ROW_TYPE",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "row_type": type(row).__name__,
                    "message": "manifest rows must be JSON objects",
                }
            )
            continue
        violations.extend(
            _manifest_row_violations(row, rel_path, line_no, repo_root_path)
        )
    return violations


def validate_written_manifest_provenance(
    *, skillsets_dir: Optional[Path] = None, repo_root_path: Path = REPO_ROOT
) -> list[dict[str, Any]]:
    """Validate generated skillset ownership, source integrity, and provenance."""
    skillsets_dir = skillsets_dir or repo_root_path / ".skillsets"
    if not skillsets_dir.exists():
        return []
    violations: list[dict[str, Any]] = []
    allowed_paths = _allowed_manifest_paths()
    command_surface_path = Path(".skillsets") / "command-surface.json"
    for path in sorted(skillsets_dir.rglob("*")):
        if (
            path.is_dir()
            or (
                rel_path := _relative_skillset_path(path, skillsets_dir, repo_root_path)
            )
            is None
        ):
            continue
        if rel_path not in allowed_paths:
            violations.append(
                {
                    "code": "UNOWNED_SKILLSET_FILE",
                    "path": rel_path.as_posix(),
                    "message": ".skillsets may contain only generated <root>/manifest.jsonl files",
                }
            )
        elif rel_path == command_surface_path:
            violations.extend(_command_surface_violations(path, rel_path))
        else:
            violations.extend(_manifest_file_violations(path, rel_path, repo_root_path))
    return violations


def _root_budget_violations(
    root_report: dict[str, Any],
    runtime_config: dict[str, Any],
    routing_config: dict[str, Any],
) -> tuple[int, list[dict[str, Any]]]:
    violations: list[dict[str, Any]] = []
    if root_report["root_count"] > int(runtime_config["max_root_skill_sets"]):
        violations.append(
            {
                "code": "TOO_MANY_ROOT_SKILL_SETS",
                "message": "root skill-set count exceeds budget",
                "count": root_report["root_count"],
                "max": runtime_config["max_root_skill_sets"],
            }
        )
    total_description_words = sum(
        root["description_words"] for root in root_report["roots"]
    )
    if total_description_words > int(
        runtime_config["max_root_description_words_total"]
    ):
        violations.append(
            {
                "code": "ROOT_DESCRIPTIONS_TOO_LONG",
                "message": "combined root descriptions exceed budget",
                "words": total_description_words,
                "max": runtime_config["max_root_description_words_total"],
            }
        )
    overlong_bodies = [
        {"name": root["name"], "words": root["body_words"]}
        for root in root_report["roots"]
        if root["body_words"] > int(runtime_config["max_root_body_words_each"])
    ]
    if overlong_bodies:
        violations.append({"code": "ROOT_BODY_TOO_LONG", "roots": overlong_bodies})
    if int(routing_config["max_candidates_returned"]) > 3:
        violations.append({"code": "ROUTER_CANDIDATE_BUDGET_TOO_HIGH"})
    return total_description_words, violations


def _projection_violations(
    projection_mode: str,
    runtime_entries: list[str],
    manifest_report: dict[str, Any],
) -> list[dict[str, Any]]:
    if projection_mode != "rooted":
        return []
    allowed = (
        ALLOWED_FIRST_LEVEL_MANIFEST_ROOTS
        | direct_runtime_names_from_manifest_report(manifest_report)
    )
    latent = [name for name in runtime_entries if name not in allowed]
    return (
        []
        if not latent
        else [{"code": "LATENT_SKILLS_EXPOSED_FIRST_LEVEL", "skills": latent}]
    )


def _manifest_budget_violations(
    projection_mode: str,
    manifest_report: dict[str, Any],
    repo_root_path: Path = REPO_ROOT,
) -> list[dict[str, Any]]:
    violations = list(manifest_report["violations"])
    violations.extend(
        validate_written_manifest_provenance(repo_root_path=repo_root_path)
    )
    manifest_paths = [manifest["path"] for manifest in manifest_report["manifests"]]
    missing = [path for path in manifest_paths if not (repo_root_path / path).is_file()]
    if projection_mode == "rooted" and missing:
        violations.append({"code": "MANIFEST_FILES_MISSING", "paths": missing})
    return violations


def validate_context_budget(
    *, projection_mode: str = "flat", repo_root_path: Path = REPO_ROOT
) -> dict[str, Any]:
    config = load_config()
    root_report = build_roots()
    manifest_report = build_manifest_report()
    runtime_entries = first_level_runtime_entries()
    total_description_words, violations = _root_budget_violations(
        root_report, config["runtime_projection"], config["routing"]
    )
    violations.extend(
        _projection_violations(projection_mode, runtime_entries, manifest_report)
    )
    violations.extend(
        _manifest_budget_violations(
            projection_mode, manifest_report, repo_root_path=repo_root_path
        )
    )
    return {
        "status": "pass" if not violations else "fail",
        "projection_mode": projection_mode,
        "policy_identity": policy_identity(),
        "config_path": str(CONFIG_PATH.relative_to(REPO_ROOT)),
        "root_count": root_report["root_count"],
        "root_description_words_total": total_description_words,
        "runtime_entries": runtime_entries,
        "command_surface_handle_names": [],
        "manifest_count": manifest_report["manifest_count"],
        "module_count": manifest_report["module_count"],
        "unmapped_count": len(manifest_report["unmapped"]),
        "violations": violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projection", choices=("flat", "rooted"), default="flat")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_context_budget(projection_mode=args.projection)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"context budget: {report['status']} ({report['projection_mode']})")
        for violation in report["violations"]:
            print(f"- {violation['code']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
