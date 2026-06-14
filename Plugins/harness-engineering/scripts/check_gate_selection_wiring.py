#!/usr/bin/env python3
"""Validate HE gate selection contract wiring across skills and evals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SNIPPETS = {
    "references/gate-selection-contract.md": [
        "gate_profile:",
        "risk_class: trivial|standard|domain_sensitive|architecture_sensitive|closure_sensitive|security_sensitive|mixed",
        "Do not let `mixed` load every adjacent contract.",
    ],
    "references/deferred-context-index.md": [
        "references/gate-selection-contract.md",
        "smallest gate profile",
    ],
    "references/lifecycle-exit-contract.md": [
        "gate_profile:",
        "Do not load broad domain, strategy, refactor, Linear, security, specialist, or eval gates unless",
        "Do not claim release confidence while lifecycle evals time out",
    ],
    "skills/he-reconcile/SKILL.md": [
        "gate selection contract",
        "smallest sufficient gate profile",
        "references/gate-selection-contract.md",
    ],
    "skills/he-spec/SKILL.md": [
        "gate selection contract",
        "minimum proof into acceptance criteria",
        "references/gate-selection-contract.md",
    ],
    "skills/he-code-review/SKILL.md": [
        "over-broad gate profiles as readiness findings",
        "references/gate-selection-contract.md",
    ],
    "skills/he-eval-report/SKILL.md": [
        "closure-sensitive slices",
        "release-confidence or Linear completion recommendations",
        "references/gate-selection-contract.md",
    ],
}

REQUIRED_EVAL_IDS = {
    "skills/he-reconcile/references/evals.yaml": [
        "gate-selection-trivial-docs-negative",
        "gate-selection-mixed-smallest-set",
    ],
    "skills/he-spec/references/evals.yaml": [
        "gate-selection-minimum-proof",
        "no-domain-for-trivial-work",
    ],
    "skills/he-code-review/references/evals.yaml": [
        "overbroad-gate-profile-finding",
        "keyword-only-specialist-rejected",
    ],
    "skills/he-eval-report/references/evals.yaml": [
        "release-confidence-timeout-block",
        "security-sensitive-proof-required",
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
