#!/usr/bin/env python3
"""Check rooted skill projection parity across home targets and runtime list."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_REPRESENTATIVE_SKILLS = ("chronicle", "desktop-commander-guide", "find-skills")
SCHEMA_VERSION = "skill-projection-parity/v1"

sys.path.insert(0, str(SCRIPT_DIR / "lifecycle-and-sync"))
from rooted_projection_runtime import build_user_relink_plan  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to inspect.",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="Home directory that should expose the rooted skill symlinks.",
    )
    parser.add_argument(
        "--ask-bin",
        default=str(REPO_ROOT / "bin" / "ask"),
        help="ask command to invoke for preview and runtime checks.",
    )
    parser.add_argument(
        "--representative-skill",
        action="append",
        dest="representative_skills",
        help="Skill handle that must appear in the runtime list. Repeatable.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the parity report as JSON.",
    )
    return parser.parse_args()


def _read_json_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"{' '.join(command)} exited with {completed.returncode}: {completed.stderr.strip()}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{' '.join(command)} did not return valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{' '.join(command)} returned a non-object JSON payload")
    if payload.get("status") != "success":
        raise RuntimeError(f"{' '.join(command)} returned status {payload.get('status')!r}")
    return payload


def _target_report(home: Path, repo_root: Path) -> dict[str, Any]:
    expected_root = (repo_root / ".agents" / "skills").resolve()
    target_paths = [home / ".agents" / "skills", home / ".codex" / "skills"]
    relink_plan = build_user_relink_plan(repo_root / ".agents" / "skills", home=home)
    results: list[dict[str, Any]] = []
    for target in target_paths:
        entry: dict[str, Any] = {"path": str(target)}
        if not target.exists() and not target.is_symlink():
            entry.update({"status": "fail", "reason": "missing"})
            results.append(entry)
            continue
        if not target.is_symlink():
            entry.update({"status": "fail", "reason": "not_symlink"})
            results.append(entry)
            continue
        current_target = os.readlink(target)
        resolved = (target.parent / current_target).resolve()
        entry.update(
            {
                "status": "pass" if resolved == expected_root else "fail",
                "target": current_target,
                "resolved": str(resolved),
                "expected": str(expected_root),
            }
        )
        if resolved != expected_root:
            entry["reason"] = "wrong_target"
        results.append(entry)
    return {
        "status": "pass" if all(item["status"] == "pass" for item in results) else "fail",
        "expected_root": str(expected_root),
        "relink_plan": relink_plan,
        "results": results,
    }


def _runtime_list_report(ask_bin: str, representative_skills: tuple[str, ...]) -> dict[str, Any]:
    payload = _read_json_command([ask_bin, "skills", "list", "--json", "--robot"])
    skills = (payload.get("data") or {}).get("skills", [])
    if not isinstance(skills, list):
        raise RuntimeError("skills list payload is missing data.skills")
    skill_names = {
        str(skill.get("name"))
        for skill in skills
        if isinstance(skill, dict) and isinstance(skill.get("name"), str)
    }
    missing = [name for name in representative_skills if name not in skill_names]
    return {
        "status": "pass" if not missing else "fail",
        "command": [ask_bin, "skills", "list", "--json", "--robot"],
        "checked": list(representative_skills),
        "missing": missing,
        "skill_count": len(skill_names),
    }


def _preview_report(ask_bin: str) -> dict[str, Any]:
    payload = _read_json_command(
        [ask_bin, "skills", "sync", "--scope", "workspace", "--projection", "rooted", "--dry-run", "--json"]
    )
    return {
        "status": "pass",
        "command": [
            ask_bin,
            "skills",
            "sync",
            "--scope",
            "workspace",
            "--projection",
            "rooted",
            "--dry-run",
            "--json",
        ],
        "preview_status": payload.get("status"),
    }


def build_report(
    *,
    repo_root: Path = REPO_ROOT,
    home: Path | None = None,
    ask_bin: str = str(REPO_ROOT / "bin" / "ask"),
    representative_skills: tuple[str, ...] = DEFAULT_REPRESENTATIVE_SKILLS,
) -> dict[str, Any]:
    home = home if home is not None else Path.home()
    target_report = _target_report(home, repo_root)
    try:
        preview_report = _preview_report(ask_bin)
        runtime_report = _runtime_list_report(ask_bin, representative_skills)
    except RuntimeError as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "blocked",
            "blocker_class": "runtime_unavailable",
            "reason": str(exc),
            "target_report": target_report,
            "first_action": "Fix the projection runtime lane and rerun the parity checker.",
            "validation_commands": [
                f"Command: {ask_bin} skills sync --scope workspace --projection rooted --dry-run --json",
                f"Command: {ask_bin} skills list --json --robot",
            ],
        }

    status = "pass"
    reasons: list[str] = []
    if target_report["status"] != "pass":
        status = "fail"
        reasons.append("home skill targets do not resolve to the rooted runtime projection")
    if preview_report["status"] != "pass":
        status = "fail"
        reasons.append("rooted projection preview did not succeed")
    if runtime_report["status"] != "pass":
        status = "fail"
        reasons.append("runtime skill list is missing representative skills")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "blocker_class": None if status == "pass" else "parity_drift",
        "first_action": "Repair the rooted skill projection targets before retrying the parity gate.",
        "repo_root": str(repo_root),
        "home": str(home),
        "target_report": target_report,
        "preview_report": preview_report,
        "runtime_report": runtime_report,
        "validation_commands": [
            f"Command: {ask_bin} skills sync --scope workspace --projection rooted --dry-run --json",
            f"Command: {ask_bin} skills list --json --robot",
        ],
        "reasons": reasons,
    }


def main() -> int:
    args = parse_args()
    representative_skills = tuple(args.representative_skills or DEFAULT_REPRESENTATIVE_SKILLS)
    report = build_report(
        repo_root=args.repo_root,
        home=args.home,
        ask_bin=args.ask_bin,
        representative_skills=representative_skills,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"[skill-projection-parity] schema: {report['schema_version']}")
        print(f"[skill-projection-parity] status: {report['status']}")
        print(f"[skill-projection-parity] repo_root: {report['repo_root']}")
        print(f"[skill-projection-parity] home: {report['home']}")
        if report["status"] != "pass":
            for reason in report.get("reasons", []):
                print(f"- {reason}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
