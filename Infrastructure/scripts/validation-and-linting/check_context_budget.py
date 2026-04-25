#!/usr/bin/env python3
"""Validate context-budgeted skill-tree projection artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
LIFECYCLE_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"
if str(LIFECYCLE_DIR) not in sys.path:
    sys.path.insert(0, str(LIFECYCLE_DIR))

from generate_root_skill_sets import build_roots  # type: ignore  # noqa: E402
from generate_skillset_manifests import build_manifest_report  # type: ignore  # noqa: E402
from selection_policy import ROOT_SKILL_SET_NAMES, policy_identity  # type: ignore  # noqa: E402
from skillset_model import file_hash  # type: ignore  # noqa: E402

CONFIG_PATH = REPO_ROOT / "Infrastructure" / "GOVERNANCE" / "context-budget.yaml"
DEFAULTS = {
    "runtime_projection": {
        "max_root_skill_sets": 10,
        "max_root_description_words_total": 350,
        "max_root_body_words_each": 250,
        "max_visible_flat_skills_in_hybrid": 5,
    },
    "routing": {
        "max_candidates_returned": 3,
        "forbid_full_manifest_output": True,
        "forbid_unrelated_skillset_load": True,
    },
    "modules": {
        "max_loaded_modules_per_task": 3,
        "max_module_body_words": 900,
    },
    "workouts": {"max_skill_context_tokens": 1500},
}


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    if not path.is_file():
        return DEFAULTS
    try:
        import yaml  # type: ignore
    except ImportError:
        # PyYAML not installed; return defaults
        return DEFAULTS

    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
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
        if item.is_dir() and not item.name.startswith(".") and (item / "SKILL.md").exists()
    )


def validate_written_manifest_provenance(
    *,
    skillsets_dir: Optional[Path] = None,
    repo_root_path: Path = REPO_ROOT,
) -> list[dict[str, Any]]:
    """Validate generated `.skillsets/**` files are owned, current, and provenance-rich."""
    skillsets_dir = skillsets_dir or repo_root_path / ".skillsets"
    if not skillsets_dir.exists():
        return []
    violations: list[dict[str, Any]] = []
    allowed_manifest_paths = {
        Path(".skillsets") / skill_set / "manifest.jsonl"
        for skill_set in ROOT_SKILL_SET_NAMES
    }
    for path in sorted(skillsets_dir.rglob("*")):
        if path.is_dir():
            continue
        try:
            rel_path = path.relative_to(repo_root_path)
        except ValueError:
            try:
                rel_path = Path(".skillsets") / path.relative_to(skillsets_dir)
            except ValueError:
                continue
        if rel_path not in allowed_manifest_paths:
            violations.append({
                "code": "UNOWNED_SKILLSET_FILE",
                "path": rel_path.as_posix(),
                "message": ".skillsets may contain only generated <root>/manifest.jsonl files",
            })
            continue
        expected_skill_set = rel_path.parts[1]
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                violations.append({
                    "code": "INVALID_SKILLSET_MANIFEST_JSON",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "message": str(exc),
                })
                continue
            if not isinstance(row, dict):
                violations.append({
                    "code": "INVALID_SKILLSET_MANIFEST_ROW_TYPE",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "row_type": type(row).__name__,
                    "message": "manifest rows must be JSON objects",
                })
                continue
            provenance = row.get("provenance")
            source_path = row.get("source_path")
            if row.get("skill_set") != expected_skill_set:
                violations.append({
                    "code": "SKILLSET_ROW_OWNERSHIP_MISMATCH",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "expected": expected_skill_set,
                    "actual": row.get("skill_set"),
                })
            if not isinstance(source_path, str) or not source_path.endswith("/SKILL.md"):
                violations.append({
                    "code": "SKILLSET_SOURCE_PATH_INVALID",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "source_path": source_path,
                })
                continue
            source_parts = Path(source_path).parts
            is_canonical_source = (
                len(source_parts) >= 3
                and ".." not in source_parts
                and source_parts[0] == "Skills"
            ) or (
                len(source_parts) >= 4
                and ".." not in source_parts
                and source_parts[0] == "Plugins"
                and source_parts[2] == "skills"
            )
            if not is_canonical_source:
                violations.append({
                    "code": "SKILLSET_SOURCE_PATH_NOT_CANONICAL",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "source_path": source_path,
                })
                continue
            source_file = repo_root_path / source_path
            if not source_file.is_file():
                violations.append({
                    "code": "SKILLSET_SOURCE_PATH_MISSING",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "source_path": source_path,
                })
                continue
            if not isinstance(provenance, dict):
                violations.append({
                    "code": "SKILLSET_PROVENANCE_MISSING",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                })
                continue
            required = {"generator", "projection_mode", "policy_identity", "source_revision", "source_sha256"}
            missing = sorted(key for key in required if not provenance.get(key))
            if missing:
                violations.append({
                    "code": "SKILLSET_PROVENANCE_INCOMPLETE",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "missing": missing,
                })
            if provenance.get("projection_mode") != "rooted":
                violations.append({
                    "code": "SKILLSET_PROVENANCE_MODE_MISMATCH",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "projection_mode": provenance.get("projection_mode"),
                })
            if provenance.get("source_sha256") and provenance.get("source_sha256") != file_hash(source_file):
                violations.append({
                    "code": "SKILLSET_SOURCE_HASH_STALE",
                    "path": rel_path.as_posix(),
                    "line": line_no,
                    "source_path": source_path,
                })
    return violations


def validate_context_budget(*, projection_mode: str = "flat") -> dict[str, Any]:
    config = load_config()
    root_report = build_roots()
    manifest_report = build_manifest_report()
    runtime_entries = first_level_runtime_entries()
    violations: list[dict[str, Any]] = []
    runtime_config = config["runtime_projection"]
    routing_config = config["routing"]

    if root_report["root_count"] > int(runtime_config["max_root_skill_sets"]):
        violations.append({
            "code": "TOO_MANY_ROOT_SKILL_SETS",
            "message": "root skill-set count exceeds budget",
            "count": root_report["root_count"],
            "max": runtime_config["max_root_skill_sets"],
        })
    total_description_words = sum(root["description_words"] for root in root_report["roots"])
    if total_description_words > int(runtime_config["max_root_description_words_total"]):
        violations.append({
            "code": "ROOT_DESCRIPTIONS_TOO_LONG",
            "message": "combined root descriptions exceed budget",
            "words": total_description_words,
            "max": runtime_config["max_root_description_words_total"],
        })
    overlong_bodies = [
        {"name": root["name"], "words": root["body_words"]}
        for root in root_report["roots"]
        if root["body_words"] > int(runtime_config["max_root_body_words_each"])
    ]
    if overlong_bodies:
        violations.append({"code": "ROOT_BODY_TOO_LONG", "roots": overlong_bodies})
    if int(routing_config["max_candidates_returned"]) > 3:
        violations.append({"code": "ROUTER_CANDIDATE_BUDGET_TOO_HIGH"})
    if projection_mode == "rooted":
        allowed = set(ROOT_SKILL_SET_NAMES) | {"codex-primary-runtime"}
        latent_first_level = [name for name in runtime_entries if name not in allowed]
        if latent_first_level:
            violations.append({
                "code": "LATENT_SKILLS_EXPOSED_FIRST_LEVEL",
                "skills": latent_first_level,
            })
    if manifest_report["violations"]:
        violations.extend(manifest_report["violations"])
    violations.extend(validate_written_manifest_provenance())
    manifest_paths = [manifest["path"] for manifest in manifest_report["manifests"]]
    missing_manifest_files = [path for path in manifest_paths if not (REPO_ROOT / path).is_file()]
    if projection_mode == "rooted" and missing_manifest_files:
        violations.append({
            "code": "MANIFEST_FILES_MISSING",
            "paths": missing_manifest_files,
        })
    return {
        "status": "pass" if not violations else "fail",
        "projection_mode": projection_mode,
        "policy_identity": policy_identity(),
        "config_path": str(CONFIG_PATH.relative_to(REPO_ROOT)),
        "root_count": root_report["root_count"],
        "root_description_words_total": total_description_words,
        "runtime_entries": runtime_entries,
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
