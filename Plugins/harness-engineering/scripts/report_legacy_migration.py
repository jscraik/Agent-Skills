#!/usr/bin/env python3
"""Report how HE skills map to the current Skill Factory operator shape."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SOFT_LINE_BUDGET = 140
REQUIRED_EVALS = {
    "happy-operator-path",
    "edge-missing-inputs-proceed",
    "pressure-no-governance-bloat",
    "pressure-live-not-archive",
    "negative-neighboring-lane",
}


def skill_rows(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for skill in sorted((root / "skills").glob("*/SKILL.md")):
        skill_dir = skill.parent
        contract = skill_dir / "references" / "contract.yaml"
        evals = skill_dir / "references" / "evals.yaml"
        skill_text = skill.read_text(encoding="utf-8")
        contract_text = contract.read_text(encoding="utf-8") if contract.exists() else ""
        eval_text = evals.read_text(encoding="utf-8") if evals.exists() else ""
        active_text = "\n".join(
            line for line in (skill_text + "\n" + contract_text).splitlines()
            if not line.lstrip().startswith("prompt:")
        )
        missing_evals = sorted(case for case in REQUIRED_EVALS if f"id: {case}" not in eval_text)
        rows.append({
            "skill": skill_dir.name,
            "skill_path": str(skill.relative_to(root.parent.parent)),
            "lines": len(skill_text.splitlines()),
            "hot_path_status": "review" if len(skill_text.splitlines()) > SOFT_LINE_BUDGET else "ok",
            "operator_contract": "present" if "operator_contract:" in contract_text else "missing",
            "missing_operator_evals": missing_evals,
            "reference_mentions": len(re.findall(r"references/|\.\./\.\./references/", skill_text)),
            "archive_authority_risk": any(token in active_text.lower() for token in ("budget-archive", "deferred-store")),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    rows = skill_rows(root)
    result = {
        "schema_version": 1,
        "root": str(root),
        "status": "pass",
        "summary": {
            "checked_skills": len(rows),
            "hot_path_review": sum(1 for row in rows if row["hot_path_status"] == "review"),
            "missing_operator_contract": sum(1 for row in rows if row["operator_contract"] != "present"),
            "skills_with_missing_operator_evals": sum(1 for row in rows if row["missing_operator_evals"]),
            "archive_authority_risks": sum(1 for row in rows if row["archive_authority_risk"]),
        },
        "skills": rows,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
