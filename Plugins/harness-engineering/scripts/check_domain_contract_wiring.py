#!/usr/bin/env python3
"""Validate DDD/domain-model contract wiring across HE lifecycle surfaces."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DOMAIN_REFERENCES = (
    "domain-context-contract.md",
    "domain-model-routing.md",
    "ubiquitous-language-contract.md",
    "domain-model-production-contract.md",
)
REQUIRED_DOMAIN_SKILLS = {
    "he-brainstorm": ("domain-context-contract.md", "domain-model-production-contract.md"),
    "he-spec": DOMAIN_REFERENCES,
    "he-plan": DOMAIN_REFERENCES,
    "he-work": ("domain-context-contract.md", "domain-model-production-contract.md"),
    "he-code-review": ("domain-context-contract.md", "domain-model-production-contract.md"),
    "he-eval-report": ("domain-context-contract.md", "domain-model-production-contract.md"),
    "he-strategy": ("domain-model-production-contract.md",),
    "he-reconcile": ("domain-model-routing.md", "domain-model-production-contract.md"),
}
REQUIRED_REFERENCE_TERMS = {
    "references/domain-context-contract.md": (
        "domain-model-production-contract.md",
        "UBIQUITOUS.md",
        "Production Model Integrity",
        "bounded context",
        "aggregate invariants",
    ),
    "references/domain-model-routing.md": (
        "UBIQUITOUS.md",
        ".harness/decisions/ADR-###-<slug>.md",
        "folded `he-deepen-spec` mode",
        "folded `he-technical-review` mode",
        "production-grade",
        "domain-model-production-contract.md",
    ),
    "references/ubiquitous-language-contract.md": (
        "UBIQUITOUS.md",
        "UBIQUITOUS-MAP.md",
        "request_user_input",
        ".harness/decisions/ADR-###-<slug>.md",
    ),
    "references/domain-model-production-contract.md": (
        "domain_model:",
        "bounded_context",
        "core_domain_relevance",
        "aggregate",
        "closure_impact",
    ),
    "references/lifecycle-exit-contract.md": (
        "domain_model:",
        "closure_impact",
        "domain_model.status",
    ),
    "references/deferred-context-index.md": (
        "references/ubiquitous-language-contract.md",
        "references/domain-model-production-contract.md",
    ),
}
REQUIRED_EVAL_TERMS = {
    "skills/he-reconcile/references/evals.yaml": ("production-domain-inferred-route",),
    "skills/he-brainstorm/references/evals.yaml": (
        "domain-survivor-selection",
        "ubiquitous-domain-interview",
    ),
    "skills/he-spec/references/evals.yaml": ("domain-model-acceptance-gate",),
    "skills/he-plan/references/evals.yaml": ("aggregate-boundary-plan",),
    "skills/he-work/references/evals.yaml": ("implementation-domain-drift-stop",),
    "skills/he-code-review/references/evals.yaml": ("model-code-test-language-mismatch",),
    "skills/he-eval-report/references/evals.yaml": ("domain-model-integrity-closure",),
    "skills/he-strategy/references/evals.yaml": (
        "domain-vision-core",
        "sparse-adr-three-part-threshold",
    ),
}
REQUIRED_EVAL_REPORT_SURFACES = {
    "skills/he-eval-report/references/eval-report-contract.md": ("domain model integrity",),
    "skills/he-eval-report/references/eval-report-template.md": ("Domain Model Integrity Check",),
    "skills/he-eval-report/references/eval-report-schema.json": ("Domain Model Integrity Check",),
}


def read(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    for rel_path, terms in REQUIRED_REFERENCE_TERMS.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing domain reference surface: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{rel_path} missing domain term: {term}")

    for skill_name, references in sorted(REQUIRED_DOMAIN_SKILLS.items()):
        skill_path = root / "skills" / skill_name / "SKILL.md"
        if not skill_path.exists():
            errors.append(f"missing required domain skill: {skill_name}")
            continue
        skill_text = skill_path.read_text(encoding="utf-8")
        for reference in references:
            if reference not in skill_text:
                errors.append(f"{skill_name} does not reference {reference}")

    routing_text = read(root, "references/domain-model-routing.md")
    if "Use `he-deepen-spec` when" in routing_text:
        errors.append("domain-model-routing uses stale direct he-deepen-spec route")
    if "Use `he-code-review` or `he-technical-review`" in routing_text:
        errors.append("domain-model-routing uses stale direct he-technical-review route")

    for rel_path, terms in REQUIRED_EVAL_TERMS.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing domain eval surface: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{rel_path} missing domain eval case: {term}")

    for rel_path, terms in REQUIRED_EVAL_REPORT_SURFACES.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing domain eval report surface: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{rel_path} missing domain eval report term: {term}")

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
