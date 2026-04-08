#!/usr/bin/env python3
"""Run bounded observe-only smoke runs for onboarded skill profiles."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
RECURSIVE_LOOP_SCRIPT = SCRIPT_DIR / "recursive_skill_loop.py"
ALLOWED_EXECUTABLES = {"python3"}


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def discover_profiles_from_profile_index(repo_root: Path, profile_index_path: Path) -> List[Path]:
    if not profile_index_path.exists():
        raise FileNotFoundError(
            f"Missing canonical profile index: {profile_index_path}. "
            "Run validate_skill_graph_profiles.py first."
        )

    payload = json.loads(profile_index_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"profile-index.json must be a JSON object: {profile_index_path}")

    rows = payload.get("skills")
    if not isinstance(rows, list) or not rows:
        raise ValueError("profile-index.json is missing a non-empty skills[] inventory.")

    out: List[Path] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "")).strip().lower()
        profile_rel = str(row.get("profile_path", "")).strip()
        if not profile_rel or status != "valid":
            continue
        profile_path = (repo_root / profile_rel).resolve()
        rel_profile = profile_path.relative_to(repo_root).as_posix()
        if rel_profile in seen:
            continue
        seen.add(rel_profile)
        if profile_path.exists():
            out.append(profile_path)
    return sorted(out)


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


def _sanitize_lines(lines: List[str], repo_root: Path) -> List[str]:
    """Replace all occurrences of the absolute repo root with '.' in output lines."""
    root_text = str(repo_root)
    return [line.replace(root_text, ".") for line in lines]


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
        "--profile-index",
        default="artifacts/skill-graphs/onboarding/profile-index.json",
        help="Canonical profile index inventory source (repo-relative)",
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
    profile_index_path = (repo_root / args.profile_index).resolve()

    profiles = discover_profiles_from_profile_index(repo_root, profile_index_path)
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
    pass_count = sum(1 for item in results if item.get("status") == "accepted")
    fail_count = sum(1 for item in results if item.get("status") == "rejected")
    report = {
        "schema_version": "1.0",
        "generated_at": iso_now(),
        "repo_root": ".",
        "dry_run": bool(args.dry_run),
        "profile_count": len(results),
        "planned_count": planned_count,
        "executed_count": executed_count,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "results": results,
    }

    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report_out": str(report_out.relative_to(repo_root)), "fail_count": fail_count}, indent=2))
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
