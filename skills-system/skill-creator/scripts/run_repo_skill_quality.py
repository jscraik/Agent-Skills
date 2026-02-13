#!/usr/bin/env python3
"""Repo-wide skill quality runner (tiered structure + optional eval scorecards)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run repo-wide skill quality checks.")
    p.add_argument("--root", default=".", help="Repo root")
    p.add_argument("--reports-dir", default="artifacts/reports/skills", help="Scorecard output directory")
    p.add_argument("--tier2-mode", choices=["warn", "fail", "off"], default="warn")
    p.add_argument("--run-evals", action="store_true", help="Run run_skill_evals.py for each skill")
    p.add_argument("--dual-run", action="store_true", help="When running evals, execute Codex+Claude dual-run")
    p.add_argument("--capture-jsonl", action="store_true", help="When running evals, capture Codex JSONL")
    p.add_argument("--sandbox", default="read-only", choices=["read-only", "workspace-write", "danger-full-access"])
    p.add_argument("--baseline-file", default=None, help="Optional baseline JSON of known structure failures.")
    p.add_argument("--write-baseline", action="store_true", help="Write/update baseline JSON from current structure failures.")
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p.parse_args()


def find_skill_dirs(root: Path) -> List[Path]:
    out: List[Path] = []
    for skill_md in root.rglob("SKILL.md"):
        s = str(skill_md)
        if "/.git/" in s or "/_archive/" in s or "/assets/template/.codex/skills/" in s:
            continue
        if any(part in skill_md.parts for part in {"artifacts", "reports", "templates"}):
            continue
        out.append(skill_md.parent)
    return sorted(set(out))


def run_cmd(cmd: List[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def choose_python() -> str:
    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    if preferred.exists():
        return str(preferred)
    return sys.executable


def rel_skill(root: Path, skill: Path) -> str:
    try:
        rel = skill.resolve().relative_to(root.resolve())
        text = str(rel)
        return "." if text == "" else text
    except Exception:
        return str(skill)


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    scripts = root / "utilities" / "skill-creator" / "scripts"

    skill_gate_py = scripts / "skill_gate.py"
    run_evals_py = scripts / "run_skill_evals.py"
    ci_gate_py = scripts / "ci_skill_quality_gate.py"
    py = choose_python()

    skills = find_skill_dirs(root)
    structure_failures = []

    for skill in skills:
        proc = run_cmd([py, str(skill_gate_py), str(skill), "--format", "json"], root)
        if proc.returncode != 0:
            structure_failures.append({"skill": rel_skill(root, skill), "stdout": proc.stdout, "stderr": proc.stderr})

    scorecards: List[Path] = []
    eval_failures = []

    baseline_allowed: List[str] = []
    if args.baseline_file:
        baseline_path = Path(args.baseline_file).expanduser().resolve()
        if baseline_path.exists():
            try:
                baseline_obj = json.loads(baseline_path.read_text(encoding="utf-8"))
                if isinstance(baseline_obj, dict) and isinstance(baseline_obj.get("allowed_structure_failures"), list):
                    baseline_allowed = [str(x) for x in baseline_obj["allowed_structure_failures"]]
            except Exception:
                baseline_allowed = []

    if args.run_evals:
        for skill in skills:
            cmd = [
                py,
                str(run_evals_py),
                str(skill),
                "--reports-dir",
                args.reports_dir,
                "--tier2-mode",
                args.tier2_mode,
                "--sandbox",
                args.sandbox,
                "--scorecard-out",
                str((root / args.reports_dir / skill.name / "latest-scorecard.json").resolve()),
            ]
            if args.dual_run:
                cmd.append("--dual-run")
            if args.capture_jsonl:
                cmd.append("--capture-jsonl")

            proc = run_cmd(cmd, root)
            scorecard_path = (root / args.reports_dir / skill.name / "latest-scorecard.json").resolve()
            if scorecard_path.exists():
                scorecards.append(scorecard_path)

            if proc.returncode != 0:
                eval_failures.append({"skill": rel_skill(root, skill), "stdout": proc.stdout, "stderr": proc.stderr})

    gate_result = None
    if scorecards:
        cmd = [py, str(ci_gate_py), "--tier2-mode", args.tier2_mode, "--format", "json"] + [str(p) for p in scorecards]
        proc = run_cmd(cmd, root)
        gate_result = json.loads(proc.stdout) if proc.stdout.strip() else None
        if proc.returncode != 0:
            eval_failures.append({"skill": "scorecard-gate", "stdout": proc.stdout, "stderr": proc.stderr})

    current_structure_failures = [x["skill"] for x in structure_failures]
    new_structure_failures = sorted(set(current_structure_failures) - set(baseline_allowed))
    resolved_structure_failures = sorted(set(baseline_allowed) - set(current_structure_failures))

    if args.write_baseline and args.baseline_file:
        baseline_path = Path(args.baseline_file).expanduser().resolve()
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_payload = {
            "allowed_structure_failures": sorted(set(current_structure_failures)),
            "generated_by": "run_repo_skill_quality.py",
        }
        baseline_path.write_text(json.dumps(baseline_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    payload = {
        "skills": len(skills),
        "structure_failures": len(structure_failures),
        "new_structure_failures": len(new_structure_failures),
        "resolved_structure_failures": len(resolved_structure_failures),
        "eval_failures": len(eval_failures),
        "structure_failure_details": structure_failures,
        "new_structure_failure_skills": new_structure_failures,
        "resolved_structure_failure_skills": resolved_structure_failures,
        "baseline_allowed_structure_failures": baseline_allowed,
        "eval_failure_details": eval_failures,
        "scorecards": [str(p) for p in scorecards],
        "scorecard_gate": gate_result,
        "passed": len(new_structure_failures) == 0 and len(eval_failures) == 0,
    }

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Skills scanned: {payload['skills']}")
        print(f"Structure failures: {payload['structure_failures']}")
        if args.baseline_file:
            print(f"New structure failures vs baseline: {payload['new_structure_failures']}")
            print(f"Resolved structure failures vs baseline: {payload['resolved_structure_failures']}")
        print(f"Eval failures: {payload['eval_failures']}")
        print(f"RESULT: {'PASS' if payload['passed'] else 'FAIL'}")

    return 0 if payload["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
