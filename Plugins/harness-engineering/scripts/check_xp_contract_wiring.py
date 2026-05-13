#!/usr/bin/env python3
"""Validate XP operating contract wiring across HE lifecycle surfaces."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


XP_REFERENCE = "xp-operating-contract.md"
XP_REQUIRED_SKILLS = {
    "he-eval-report",
    "he-linear-plan",
    "he-phase-work",
    "he-plan",
    "he-refactor",
    "he-strategy",
    "he-work",
}
XP_PROOF_TERMS = {
    "baby",
    "feedback",
    "quality",
    "slack_policy",
    "story/value",
    "value basis",
}
XP_REQUIRED_SURFACES = {
    "references/plugin-eval-confidence-contract.md": (
        "d / 63",
        "rooted handle",
        "release eval lane",
        "cache sync status",
    ),
    "skills/he-eval-report/references/eval-report-contract.md": (
        "planned-proof gap",
        "proof before",
    ),
    "skills/he-eval-report/references/eval-report-template.md": (
        "planned proof check",
        "planned before implementation",
    ),
    "skills/he-linear-plan/references/linear-plan-output-contract.md": (
        "xp value filter",
        "story / value basis",
    ),
    "skills/he-linear-plan/references/contract.yaml": (
        "story_value_basis",
        "story/value basis",
    ),
    "skills/he-phase-work/references/contract.yaml": (
        "slack_policy",
    ),
    "skills/he-phase-work/references/phase-gate-contract.md": (
        "slack_policy",
        "stale",
    ),
    "skills/he-refactor/references/refactor-program-contract.md": (
        "xp migration constraint",
        "smallest reversible step",
    ),
    "skills/he-strategy/references/strategy-output-contract.md": (
        "smallest feedback-producing next slice",
        "stop or pivot",
    ),
}


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    xp_path = root / "references" / XP_REFERENCE
    if not xp_path.exists():
        errors.append(f"missing XP operating contract: references/{XP_REFERENCE}")
    else:
        xp_text = xp_path.read_text(encoding="utf-8").lower()
        for term in XP_PROOF_TERMS:
            if term not in xp_text:
                errors.append(f"XP operating contract missing proof term: {term}")

    deferred_index = root / "references" / "deferred-context-index.md"
    deferred_text = deferred_index.read_text(encoding="utf-8") if deferred_index.exists() else ""
    if XP_REFERENCE not in deferred_text:
        errors.append("deferred context index does not route XP operating contract")

    for skill_name in sorted(XP_REQUIRED_SKILLS):
        skill_path = root / "skills" / skill_name / "SKILL.md"
        if not skill_path.exists():
            errors.append(f"missing required lifecycle skill: {skill_name}")
            continue
        text = skill_path.read_text(encoding="utf-8")
        if XP_REFERENCE not in text:
            errors.append(f"{skill_name} does not reference XP operating contract")

    for rel_path, required_terms in XP_REQUIRED_SURFACES.items():
        surface_path = root / rel_path
        if not surface_path.exists():
            errors.append(f"missing XP contract surface: {rel_path}")
            continue
        surface_text = surface_path.read_text(encoding="utf-8").lower()
        for term in required_terms:
            if term not in surface_text:
                errors.append(f"{rel_path} missing XP surface term: {term}")

    tracer_path = root / "references" / "lifecycle-tracer-evals.yaml"
    tracer_text = tracer_path.read_text(encoding="utf-8") if tracer_path.exists() else ""
    for expected in (
        "tracer-xp-strategy-feedback-slice",
        "tracer-xp-linear-value-filter",
        "tracer-xp-eval-planned-proof",
        "tracer-xp-phase-work-slack",
    ):
        if expected not in tracer_text:
            errors.append(f"missing XP lifecycle tracer eval: {expected}")

    release_eval_script = root / "scripts" / "run_lifecycle_release_evals.py"
    if not release_eval_script.exists():
        errors.append("missing HE lifecycle release eval lane script")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    errors = validate(root)
    result = {
        "schema_version": 1,
        "root": str(root),
        "status": "pass" if not errors else "fail",
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for error in errors:
            print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
