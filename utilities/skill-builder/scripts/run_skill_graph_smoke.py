#!/usr/bin/env python3
"""Run bounded observe-only smoke runs for onboarded skill profiles."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
RECURSIVE_LOOP_SCRIPT = SCRIPT_DIR / "recursive_skill_loop.py"
DEFAULT_REPORT_OUT = Path("artifacts/skill-graphs/onboarding/smoke-report.json")
DEFAULT_DRY_RUN_REPORT_OUT = Path("artifacts/skill-graphs/onboarding/smoke-report.dry-run.json")
EXCLUDED_PREFIXES = (
    "skills/.system/",
    "utilities/recon-workbench/assets/template/.codex/skills/",
)
ALLOWED_EXECUTABLES = {"python3"}
ABSOLUTE_PATH_PATTERN = re.compile(r"(?P<path>(?<![A-Za-z0-9_.-])/(?:[^\s\"'`]|\\ )+)")


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json_dict(path: Path) -> Dict[str, object]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"Expected JSON object at {path}")
    return obj


def discover_profiles(repo_root: Path, profile_index_path: Path) -> List[Path]:
    if not profile_index_path.exists():
        raise RuntimeError(f"Missing profile index: {profile_index_path}")

    profile_index = load_json_dict(profile_index_path)
    rows = profile_index.get("skills")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"profile-index.json has no skills[] rows: {profile_index_path}")

    out: List[Path] = []
    missing: List[str] = []
    seen: set[str] = set()

    for row in rows:
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "valid")).strip().lower()
        if status not in {"valid", "active"}:
            continue

        scope_skill = str(row.get("scope_skill", "")).strip()
        if not scope_skill:
            continue
        if any(scope_skill.startswith(prefix.rstrip("/")) for prefix in EXCLUDED_PREFIXES):
            continue

        profile_rel = str(
            row.get("profile_path", f"{scope_skill}/references/task-profile.json")
        ).strip()
        if not profile_rel:
            continue
        if profile_rel in seen:
            continue
        seen.add(profile_rel)

        profile = (repo_root / profile_rel).resolve()
        try:
            rel_profile = profile.relative_to(repo_root)
        except ValueError as exc:
            raise RuntimeError(
                f"profile-index references profile_path outside repo root: {profile_rel}"
            ) from exc
        if profile.exists():
            out.append(profile)
        else:
            missing.append(rel_profile.as_posix())

    if missing:
        preview = ", ".join(sorted(missing)[:10])
        raise RuntimeError(
            f"Canonical profile-index references missing profile files ({len(missing)}): {preview}"
        )

    if not out:
        raise RuntimeError("No runnable profiles discovered from canonical profile-index.")

    return out


def _rel_or_redact(value: str, repo_root: Path) -> str:
    """Return a repo-relative posix path, or redact absolute paths that escape the root."""
    raw = value.strip()
    if not raw:
        return ""
    candidate = Path(raw)
    if candidate.is_absolute():
        try:
            return candidate.relative_to(repo_root).as_posix()
        except ValueError:
            return "<redacted-absolute-path>"
    return raw


def _sanitize_absolute_match(raw_path: str, repo_root: Path) -> str:
    candidate = Path(raw_path)
    try:
        rel = candidate.relative_to(repo_root)
    except ValueError:
        return "<redacted-absolute-path>"
    return rel.as_posix()


def _sanitize_lines(lines: List[str], repo_root: Path) -> List[str]:
    """Replace absolute paths with repo-relative paths or redacted placeholders."""
    sanitized: List[str] = []
    for line in lines:
        def _replace(match: re.Match[str]) -> str:
            mapped = _sanitize_absolute_match(match.group("path"), repo_root)
            if mapped == "<redacted-absolute-path>":
                return mapped
            return f"./{mapped}"

        replaced = line
        replaced = ABSOLUTE_PATH_PATTERN.sub(_replace, replaced)
        sanitized.append(replaced)
    return sanitized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(ROOT), help="Repository root")
    parser.add_argument(
        "--runs-out-root",
        default="artifacts/skill-graphs/runs-smoke",
        help="Out root passed into recursive_skill_loop.py",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/skill-graphs/onboarding/smoke-report.json",
        help="Smoke execution report output path",
    )
    parser.add_argument(
        "--controls-dir",
        default="artifacts/skill-graphs/controls",
        help="Controls directory for recursive loop invocation",
    )
    parser.add_argument(
        "--lessons-jsonl",
        default="artifacts/skill-graphs/lessons/canonical-lessons.jsonl",
        help="Canonical lessons JSONL path",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional cap on number of profiles to execute (0 = all)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=1,
        help="Override loop max iterations for smoke speed",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print planned profile list and write report without executing runs",
    )
    parser.add_argument(
        "--allow-dry-run-canonical-report",
        action="store_true",
        help="Allow --dry-run to overwrite canonical smoke-report.json",
    )
    parser.add_argument(
        "--profile-index",
        default="artifacts/skill-graphs/onboarding/profile-index.json",
        help="Canonical profile index used for inventory selection",
    )
    return parser.parse_args()


def check_required_run_artifacts(run_out_dir: Path) -> Tuple[List[str], Dict[str, object]]:
    required = ("run.json", "promotion_decision.json", "events.jsonl")
    missing: List[str] = []
    for name in required:
        if not (run_out_dir / name).exists():
            missing.append(name)

    details: Dict[str, object] = {}
    run_path = run_out_dir / "run.json"
    if run_path.exists():
        try:
            run_obj = json.loads(run_path.read_text(encoding="utf-8"))
            if isinstance(run_obj, dict):
                details["terminal_status"] = run_obj.get("terminal_status")
                details["stop_reason"] = run_obj.get("stop_reason")
        except json.JSONDecodeError:
            missing.append("run.json(valid_json)")

    evidence_path = run_out_dir / "evidence_packet.json"
    if evidence_path.exists():
        try:
            evidence_obj = json.loads(evidence_path.read_text(encoding="utf-8"))
            completeness = (
                evidence_obj.get("completeness", {}).get("score")
                if isinstance(evidence_obj, dict)
                else None
            )
            details["evidence_completeness"] = completeness
        except json.JSONDecodeError:
            details["evidence_completeness"] = None
    else:
        details["evidence_completeness"] = None

    return missing, details


def run_recursive_loop(command: List[str], repo_root: Path) -> subprocess.CompletedProcess[str]:
    if not command:
        raise ValueError("Command cannot be empty.")
    executable = command[0]
    if executable not in ALLOWED_EXECUTABLES:
        raise ValueError(f"Executable not allowed for smoke runner: {executable}")
    return subprocess.run(
        command,
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        check=False,
        shell=False,
    )


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    runs_out_root = (repo_root / args.runs_out_root).resolve()
    controls_dir = (repo_root / args.controls_dir).resolve()
    lessons_jsonl = (repo_root / args.lessons_jsonl).resolve()
    report_out = (repo_root / args.report_out).resolve()
    canonical_report_out = (repo_root / DEFAULT_REPORT_OUT).resolve()
    if args.dry_run and report_out == canonical_report_out and not args.allow_dry_run_canonical_report:
        report_out = (repo_root / DEFAULT_DRY_RUN_REPORT_OUT).resolve()
    profile_index_path = (repo_root / args.profile_index).resolve()

    profiles = discover_profiles(repo_root, profile_index_path)
    if args.limit and args.limit > 0:
        profiles = profiles[: args.limit]

    results: List[Dict[str, object]] = []
    for profile_path in profiles:
        rel_profile = profile_path.relative_to(repo_root).as_posix()
        command = [
            "python3",
            str(RECURSIVE_LOOP_SCRIPT),
            "--profile-file",
            str(profile_path),
            "--objective",
            f"Smoke validation for {profile_path.parent.parent.relative_to(repo_root).as_posix()}",
            "--out-root",
            str(runs_out_root),
            "--run-owner",
            "skill-graph-smoke",
            "--rollout-mode",
            "observe_only",
            "--uplift-gate-mode",
            "observe",
            "--controls-dir",
            str(controls_dir),
            "--lessons-jsonl",
            str(lessons_jsonl),
            "--max-injected-lessons",
            "1",
            "--low-confidence-threshold",
            "0.6",
            "--max-iterations",
            str(max(1, args.max_iterations)),
            "--feedback-outcome",
            "worked",
            "--feedback-note",
            "smoke validation pass",
        ]

        if args.dry_run:
            results.append(
                {
                    "profile_path": rel_profile,
                    "status": "planned",
                    "command": _sanitize_lines(command, repo_root),
                }
            )
            continue

        completed = run_recursive_loop(command, repo_root)
        execution_status = "passed" if completed.returncode == 0 else "nonzero_exit"
        run_id = ""
        out_dir = ""
        for line in (completed.stdout or "").splitlines():
            if line.startswith("[recursive-loop] run_id="):
                run_id = line.split("=", 1)[1].strip()
            if line.startswith("[recursive-loop] out_dir="):
                out_dir = line.split("=", 1)[1].strip()

        smoke_status = "rejected"
        artifact_missing: List[str] = []
        artifact_details: Dict[str, object] = {}
        if out_dir:
            out_path = Path(out_dir)
            if out_path.exists():
                artifact_missing, artifact_details = check_required_run_artifacts(out_path)
                if not artifact_missing:
                    smoke_status = "accepted"

        results.append(
            {
                "profile_path": rel_profile,
                "status": smoke_status,
                "execution_status": execution_status,
                "exit_code": completed.returncode,
                "run_id": run_id,
                "run_out_dir": _rel_or_redact(out_dir, repo_root),
                "missing_artifacts": artifact_missing,
                "artifact_details": artifact_details,
                "stdout_tail": _sanitize_lines((completed.stdout or "").splitlines()[-8:], repo_root),
                "stderr_tail": _sanitize_lines((completed.stderr or "").splitlines()[-8:], repo_root),
            }
        )

    planned_count = sum(1 for item in results if item.get("status") == "planned")
    executed_count = sum(1 for item in results if item.get("status") in {"accepted", "rejected"})
    executed_pass_count = sum(1 for item in results if item.get("status") == "accepted")
    executed_fail_count = sum(1 for item in results if item.get("status") == "rejected")
    report = {
        "schema_version": "1.0",
        "generated_at": iso_now(),
        "repo_root": ".",
        "dry_run": bool(args.dry_run),
        "profile_count": len(results),
        "planned_count": planned_count,
        "executed_count": executed_count,
        "executed_pass_count": executed_pass_count,
        "executed_fail_count": executed_fail_count,
        "pass_count": executed_pass_count,
        "fail_count": executed_fail_count,
        "results": results,
    }

    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "report_out": _rel_or_redact(str(report_out), repo_root),
                "planned_count": planned_count,
                "executed_fail_count": executed_fail_count,
            },
            indent=2,
        )
    )
    return 0 if executed_fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
