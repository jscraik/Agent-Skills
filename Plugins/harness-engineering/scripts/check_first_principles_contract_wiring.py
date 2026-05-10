#!/usr/bin/env python3
"""Validate HE first-principles contract wiring across skills and evals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SNIPPETS = {
    "references/first-principles-contract.md": [
        "first_principles_check:",
        "verified_failure:",
        "fundamental_constraint:",
        "assumption_being_challenged:",
        "smallest_effective_mechanism:",
        "analogy_or_template_rejected:",
        "proof_required:",
        "decision_type: Type 1|Type 2",
        "outcome: proceed|ask|defer|reject|delete_or_collapse",
        "Headless Mode",
    ],
    "references/deferred-context-index.md": [
        "references/first-principles-contract.md",
        "first_principles_check with verified failure",
    ],
    "skills/he-brainstorm/SKILL.md": [
        "first-principles contract",
        "references/first-principles-contract.md",
    ],
    "skills/he-strategy/SKILL.md": [
        "first-principles contract",
        "references/first-principles-contract.md",
    ],
    "skills/he-spec/SKILL.md": [
        "first-principles contract",
        "references/first-principles-contract.md",
    ],
    "skills/he-plan/SKILL.md": [
        "first-principles contract",
        "references/first-principles-contract.md",
    ],
    "skills/he-linear-plan/SKILL.md": [
        "first-principles contract",
        "references/first-principles-contract.md",
    ],
    "skills/he-eval-report/SKILL.md": [
        "first-principles contract",
        "references/first-principles-contract.md",
    ],
    "skills/he-code-review/SKILL.md": [
        "first-principles contract",
        "references/first-principles-contract.md",
    ],
}

REQUIRED_EVAL_IDS = {
    "skills/he-brainstorm/references/evals.yaml": [
        "first-principles-brainstorm-survivor-selection",
    ],
    "skills/he-strategy/references/evals.yaml": [
        "first-principles-rejects-template-copying",
    ],
    "skills/he-spec/references/evals.yaml": [
        "first-principles-spec-smallest-mechanism",
    ],
    "skills/he-plan/references/evals.yaml": [
        "first-principles-routes-type1-to-proof",
        "first-principles-allows-type2-fast-path",
    ],
    "skills/he-linear-plan/references/evals.yaml": [
        "first-principles-compresses-linear-noise",
    ],
    "skills/he-eval-report/references/evals.yaml": [
        "first-principles-eval-closure-challenge",
    ],
    "skills/he-code-review/references/evals.yaml": [
        "first-principles-review-flags-false-sophistication",
    ],
    "references/lifecycle-tracer-evals.yaml": [
        "first-principles-records-assumptions-headless",
    ],
}


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative_path, snippets in REQUIRED_SNIPPETS.items():
        path = root / relative_path
        if not path.exists():
            errors.append(f"missing required file: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{relative_path} missing snippet: {snippet}")

    for relative_path, case_ids in REQUIRED_EVAL_IDS.items():
        path = root / relative_path
        if not path.exists():
            errors.append(f"missing eval file: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for case_id in case_ids:
            if f"id: {case_id}" not in text:
                errors.append(f"{relative_path} missing eval case id: {case_id}")

    forbidden_skill = root / "skills" / "he-first-principles"
    if forbidden_skill.exists():
        errors.append("unexpected standalone skill exists: skills/he-first-principles")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=PLUGIN_ROOT,
        help="Harness Engineering plugin root.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors = validate(args.root)
    result = {
        "schema_version": 1,
        "plugin_root": str(args.root),
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
