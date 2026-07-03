#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"
sys.path.insert(0, str(LIB_DIR))

from ask.skills_sdk.scenario_registry_guardrails import validate_no_direct_registry_scenario_use  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Block direct shared scenario registry references unless SDK adaptation receipts exist."
    )
    parser.add_argument("skill_path", help="Path to a skill directory or SKILL.md")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args(argv)

    raw_path = Path(args.skill_path)
    skill_dir = raw_path.parent if raw_path.name == "SKILL.md" else raw_path
    if not skill_dir.is_absolute():
        skill_dir = REPO_ROOT / skill_dir
    try:
        receipt = validate_no_direct_registry_scenario_use(skill_dir)
    except Exception as exc:  # noqa: BLE001 - preserve the validator JSON contract.
        receipt = {
            "schema_version": "skills-sdk.no-direct-registry-scenario-use.v0",
            "status": "error",
            "skill_path": skill_dir.as_posix(),
            "checks": [],
            "blockers": [
                {
                    "id": "validator_exception",
                    "status": "error",
                    "severity": "blocker",
                    "message": "Validator raised before producing a receipt.",
                    "evidence": [f"{type(exc).__name__}: {exc}"],
                }
            ],
        }
    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    elif receipt["status"] == "pass":
        print("no direct registry scenario use detected")
    else:
        for blocker in receipt["blockers"]:
            print(f"{blocker['id']}: {', '.join(blocker['evidence'])}")
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
