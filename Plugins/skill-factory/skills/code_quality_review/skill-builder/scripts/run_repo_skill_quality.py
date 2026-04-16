#!/usr/bin/env python3
"""Repo-wide skill quality runner (tiered structure + optional eval scorecards)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess as sp
import sys
from pathlib import Path
from typing import Any, Dict, List

from skill_graph_inventory import discover_inventory_skills, load_inventory_policy


_FM_DELIM = re.compile(r"^\s*---\s*$")
_YAML_NAME_LINE = re.compile(r"^\s*name\s*:\s*(.+?)\s*$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run repo-wide skill quality checks.")
    p.add_argument("--root", default=".", help="Repo root")
    p.add_argument("--reports-dir", default="Infrastructure/artifacts/skills", help="Scorecard output directory")
    p.add_argument("--tier2-mode", choices=["warn", "fail", "off"], default="warn")
    p.add_argument("--run-evals", action="store_true", help="Run run_skill_evals.py for each skill")
    p.add_argument("--runner", default="codex", help="Single-run eval runner.")
    p.add_argument("--runners", action="append", default=[], help="Explicit eval runner list (repeatable or comma-separated).")
    p.add_argument("--dual-run", action="store_true", help="When running evals, execute Codex+Claude-Kimi dual-run")
    p.add_argument("--codex-fallback-profile", default="d", help="Pass through to run_skill_evals.py codex fallback profile.")
    p.add_argument("--capture-jsonl", action="store_true", help="When running evals, capture Codex JSONL")
    p.add_argument("--sandbox", default="read-only", choices=["read-only", "workspace-write", "danger-full-access"])
    p.add_argument(
        "--claude-settings",
        default=None,
        help="DEPRECATED: plain `claude` runner was removed. Use --claude-kimi-settings / --claude-zai-settings.",
    )
    p.add_argument("--claude-kimi-settings", default=None, help="Path to pass through as --claude-kimi-settings.")
    p.add_argument("--claude-zai-settings", default=None, help="Path to pass through as --claude-zai-settings.")
    p.add_argument("--claude-kimi-command", default=None, help="Path/name to pass through as --claude-kimi-command.")
    p.add_argument("--claude-zai-command", default=None, help="Path/name to pass through as --claude-zai-command.")
    p.add_argument("--baseline-file", default=None, help="Optional baseline JSON of known structure failures.")
    p.add_argument("--write-baseline", action="store_true", help="Write/update baseline JSON from current structure failures.")
    p.add_argument(
        "--benchmark-mode",
        choices=["off", "warn", "fail"],
        default="warn",
        help="Portfolio benchmark enforcement mode.",
    )
    p.add_argument(
        "--benchmark-config",
        default="Skills/skill-builder/Infrastructure/references/benchmark-policy.json",
        help="Portfolio benchmark policy JSON path.",
    )
    p.add_argument(
        "--benchmark-output-json",
        default="Infrastructure/artifacts/industry-benchmark-latest.json",
        help="Where to write benchmark JSON output.",
    )
    p.add_argument(
        "--sarif-out",
        default=None,
        help="Optional aggregate SARIF output path (default: <reports-dir>/skill-structure-gates.sarif).",
    )
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p.parse_args()


def find_skill_dirs(root: Path) -> List[Path]:
    policy = load_inventory_policy(root)
    inventory_skills = discover_inventory_skills(root, policy)
    return sorted({row.skill_md.parent.resolve() for row in inventory_skills})


def run_cmd(cmd: List[str], cwd: Path) -> sp.CompletedProcess[str]:
    return sp.run(cmd, cwd=cwd, text=True, capture_output=True)


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
    except (OSError, RuntimeError, ValueError):
        return str(skill)


def load_canonical_skill_name(skill: Path) -> str:
    skill_md = skill / "SKILL.md"
    try:
        raw = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return skill.name

    lines = raw.splitlines()
    if not lines:
        return skill.name

    start_idx = None
    for index, line in enumerate(lines):
        if line.strip():
            start_idx = index
            break
    if start_idx is None or not _FM_DELIM.match(lines[start_idx]):
        return skill.name

    end_idx = None
    for index in range(start_idx + 1, len(lines)):
        if _FM_DELIM.match(lines[index]):
            end_idx = index
            break
    if end_idx is None:
        return skill.name

    for line in lines[start_idx + 1 : end_idx]:
        match = _YAML_NAME_LINE.match(line)
        if not match:
            continue
        value = match.group(1).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1].strip()
        return value or skill.name
    return skill.name


def report_dir_for_skill(root: Path, reports_dir: str, skill: Path) -> Path:
    return (root / reports_dir / load_canonical_skill_name(skill)).resolve()


def _load_json_file(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_file(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def merge_sarif_reports(paths: List[Path], destination: Path) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [],
    }
    source_paths: List[str] = []
    for path in paths:
        if not path.exists():
            continue
        payload = _load_json_file(path)
        runs = payload.get("runs")
        if isinstance(runs, list):
            merged["runs"].extend(runs)
            source_paths.append(str(path))
    _write_json_file(destination, merged)
    return {
        "path": str(destination),
        "run_count": len(merged["runs"]),
        "source_paths": source_paths,
    }


def main() -> int:
    args = parse_args()
    if args.claude_settings:
        print(
            "ERROR: --claude-settings is deprecated because plain `claude` runner was removed. "
            "Use --claude-kimi-settings or --claude-zai-settings.",
            file=sys.stderr,
        )
        return 1
    root = Path(args.root).expanduser().resolve()
    scripts = root / "Plugins" / "skill-factory" / "skills" / "code_quality_review" / "skill-builder" / "scripts"

    skill_gate_py = scripts / "skill_gate.py"
    run_evals_py = scripts / "run_skill_evals.py"
    ci_gate_py = scripts / "ci_skill_quality_gate.py"
    benchmark_py = scripts / "benchmark_skill_portfolio.py"
    py = choose_python()

    skills = find_skill_dirs(root)
    structure_failures = []
    structure_reports: List[Path] = []
    structure_sarif_reports: List[Path] = []
    eval_junit_reports: List[Path] = []
    reports_root = (root / args.reports_dir).resolve()

    for skill in skills:
        skill_reports_dir = report_dir_for_skill(root, args.reports_dir, skill)
        skill_reports_dir.mkdir(parents=True, exist_ok=True)
        structure_report_path = skill_reports_dir / "structure-gate.json"
        structure_sarif_path = skill_reports_dir / "structure-gate.sarif"
        proc = run_cmd(
            [
                py,
                str(skill_gate_py),
                str(skill),
                "--format",
                "json",
                "--output",
                str(structure_report_path),
                "--sarif-out",
                str(structure_sarif_path),
            ],
            root,
        )
        if structure_report_path.exists():
            structure_reports.append(structure_report_path)
        if structure_sarif_path.exists():
            structure_sarif_reports.append(structure_sarif_path)
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
            except (json.JSONDecodeError, OSError, UnicodeDecodeError):
                baseline_allowed = []

    if args.run_evals:
        for skill in skills:
            skill_reports_dir = report_dir_for_skill(root, args.reports_dir, skill)
            skill_reports_dir.mkdir(parents=True, exist_ok=True)
            scorecard_path = (skill_reports_dir / "latest-scorecard.json").resolve()
            junit_path = (skill_reports_dir / "latest-junit.xml").resolve()
            cmd = [
                py,
                str(run_evals_py),
                str(skill),
                "--runner",
                args.runner,
                "--codex-fallback-profile",
                args.codex_fallback_profile,
                "--reports-dir",
                args.reports_dir,
                "--tier2-mode",
                args.tier2_mode,
                "--sandbox",
                args.sandbox,
                "--scorecard-out",
                str(scorecard_path),
                "--junit-out",
                str(junit_path),
            ]
            for runner in args.runners:
                cmd.extend(["--runners", runner])
            if args.dual_run:
                cmd.append("--dual-run")
            if args.capture_jsonl:
                cmd.append("--capture-jsonl")
            if args.claude_kimi_settings:
                cmd.extend(["--claude-kimi-settings", args.claude_kimi_settings])
            if args.claude_zai_settings:
                cmd.extend(["--claude-zai-settings", args.claude_zai_settings])
            if args.claude_kimi_command:
                cmd.extend(["--claude-kimi-command", args.claude_kimi_command])
            if args.claude_zai_command:
                cmd.extend(["--claude-zai-command", args.claude_zai_command])

            proc = run_cmd(cmd, root)
            if scorecard_path.exists():
                scorecards.append(scorecard_path)
            if junit_path.exists():
                eval_junit_reports.append(junit_path)

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

    benchmark_result = None
    benchmark_failed = False
    if args.benchmark_mode != "off":
        benchmark_cmd = [
            py,
            str(benchmark_py),
            "--root",
            str(root),
            "--config",
            str(args.benchmark_config),
            "--mode",
            args.benchmark_mode,
            "--format",
            "json",
            "--output-json",
            str(args.benchmark_output_json),
        ]
        proc = run_cmd(benchmark_cmd, root)
        if proc.stdout.strip():
            try:
                benchmark_result = json.loads(proc.stdout)
            except json.JSONDecodeError:
                benchmark_result = {"parse_error": "invalid_json", "stdout": proc.stdout}
        if proc.returncode != 0:
            benchmark_failed = True
            eval_failures.append(
                {"skill": "portfolio-benchmark", "stdout": proc.stdout, "stderr": proc.stderr}
            )

    aggregate_sarif = None
    if structure_sarif_reports:
        aggregate_sarif_path = (
            Path(args.sarif_out).expanduser().resolve()
            if args.sarif_out
            else (reports_root / "skill-structure-gates.sarif")
        )
        aggregate_sarif = merge_sarif_reports(structure_sarif_reports, aggregate_sarif_path)

    repo_artifact_index_path = reports_root / "repo-quality-artifacts.json"
    repo_artifact_index = {
        "schema_version": "1.0",
        "generated_by": "run_repo_skill_quality.py",
        "reports_root": str(reports_root),
        "structure_reports": [str(p) for p in structure_reports],
        "structure_sarif_reports": [str(p) for p in structure_sarif_reports],
        "aggregate_sarif": str(aggregate_sarif_path) if structure_sarif_reports else None,
        "scorecards": [str(p) for p in scorecards],
        "eval_junit_reports": [str(p) for p in eval_junit_reports],
        "benchmark_output_json": str(args.benchmark_output_json),
    }
    _write_json_file(repo_artifact_index_path, repo_artifact_index)

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
        "structure_reports": [str(p) for p in structure_reports],
        "structure_sarif_reports": [str(p) for p in structure_sarif_reports],
        "aggregate_sarif": repo_artifact_index["aggregate_sarif"],
        "scorecards": [str(p) for p in scorecards],
        "eval_junit_reports": [str(p) for p in eval_junit_reports],
        "repo_artifact_index": str(repo_artifact_index_path),
        "scorecard_gate": gate_result,
        "benchmark_mode": args.benchmark_mode,
        "benchmark_config": str(args.benchmark_config),
        "benchmark_output_json": str(args.benchmark_output_json),
        "benchmark_result": benchmark_result,
        "benchmark_failed": benchmark_failed,
        "sarif_summary": aggregate_sarif,
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
        print(f"Structure SARIF reports: {len(payload['structure_sarif_reports'])}")
        print(f"Eval JUnit reports: {len(payload['eval_junit_reports'])}")
        if payload["aggregate_sarif"]:
            print(f"Aggregate SARIF: {payload['aggregate_sarif']}")
        if args.benchmark_mode != "off":
            print(f"Benchmark mode: {payload['benchmark_mode']}")
            print(f"Benchmark failed: {payload['benchmark_failed']}")
        print(f"RESULT: {'PASS' if payload['passed'] else 'FAIL'}")

    return 0 if payload["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
