#!/usr/bin/env python3
"""Validate Harness Engineering deterministic routing-map structure."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_yaml_stage_names(path: Path) -> set[str]:
    stages: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("stage: "):
            stages.add(stripped.split(":", 1)[1].strip().strip('"'))
    return stages


def validate_map(plugin_root: Path, *, run_router_samples: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    map_path = plugin_root / "references" / "routing-map.json"
    data = json.loads(map_path.read_text(encoding="utf-8"))

    rules = data.get("deterministic_decision_order", [])
    priorities = [rule.get("priority") for rule in rules]
    if priorities != sorted(priorities):
        errors.append("deterministic_decision_order priorities are not sorted")
    duplicates = sorted({priority for priority in priorities if priorities.count(priority) > 1})
    if duplicates:
        errors.append(f"duplicate routing priorities: {duplicates}")

    templates = data.get("stage_invocation_templates", {})
    expected_stages = set(templates)
    skill_stages = {
        path.parent.name
        for path in (plugin_root / "skills").glob("he-*/SKILL.md")
        if path.parent.name not in {"he-phase-heartbeat", "he-router"}
    }
    for stage in sorted(expected_stages):
        if stage not in templates:
            errors.append(f"missing stage invocation template: {stage}")
        if not (plugin_root / "skills" / stage / "SKILL.md").exists():
            errors.append(f"missing routed skill entrypoint: {stage}")
    missing_templates = sorted(skill_stages - expected_stages)
    if missing_templates:
        errors.append(f"routed skill entrypoints without stage invocation template: {missing_templates}")

    tracer_path = plugin_root / "references" / "lifecycle-tracer-evals.yaml"
    tracer_stages = load_yaml_stage_names(tracer_path)
    missing_tracers = sorted(expected_stages - tracer_stages)
    if missing_tracers:
        errors.append(f"missing lifecycle tracer stages: {missing_tracers}")

    if run_router_samples:
        route_samples = data.get("route_samples", {})
        if not route_samples:
            warnings.append("router sample execution requested but routing-map.json has no route_samples")
            return errors, warnings
        repo_root = plugin_root.parents[1]
        route_script = repo_root / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "route_skillset.py"
        for expected_stage, prompt in route_samples.items():
            result = subprocess.run(
                [sys.executable, str(route_script), "--skill-set", "harness-engineering", "--task", prompt, "--json"],
                cwd=repo_root,
                check=False,
                text=True,
                capture_output=True,
            )
            if result.returncode != 0:
                errors.append(f"route sample failed for {expected_stage}: {result.stderr.strip()}")
                continue
            selected = json.loads(result.stdout).get("selected", {}).get("id")
            if selected != expected_stage:
                errors.append(f"route sample expected {expected_stage}, got {selected}")
    else:
        warnings.append("router sample execution skipped")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin_root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--run-router-samples", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors, warnings = validate_map(args.plugin_root.resolve(), run_router_samples=args.run_router_samples)
    result = {
        "schema_version": 1,
        "plugin_root": str(args.plugin_root.resolve()),
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for error in errors:
            print(f"error: {error}")
        for warning in warnings:
            print(f"warning: {warning}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
