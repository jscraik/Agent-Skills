#!/usr/bin/env python3
"""Validate first-principles factory gate evidence in factory outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "desired_outcome",
    "user_specific_constraints",
    "copied_assumption_rejected",
    "fundamental_constraints",
    "smallest_effective_mechanism",
    "artifact_decision",
    "rejected_alternatives",
    "evidence_required",
    "validation_proof",
    "stop_or_pivot_condition",
)

ALLOWED_DECISIONS = (
    "BUILD_SKILL",
    "BUILD_PLUGIN",
    "ADD_HOOK",
    "ADD_MCP_TOOL",
    "ADD_APP",
    "ADD_EVAL",
    "IMPROVE_EXISTING",
    "DOCS_ONLY",
    "DO_NOT_BUILD",
)

PLACEHOLDERS = {"", '""', "''", "todo", "tbd", "not sure", "unknown"}

SKIP_PARTS = {
    ".agents",
    ".skillsets",
    "budget-archive",
    "generated",
    "runtime",
    "cache",
}

FACTORY_PREFIXES = (
    "Plugins/skill-factory/skills/",
    "Plugins/plugin-factory/skills/",
)


@dataclass(frozen=True)
class GateResult:
    path: str
    status: str
    message: str
    details: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "status": self.status,
            "message": self.message,
            "details": list(self.details),
        }


def _normalize_path(path: Path) -> str:
    return path.as_posix().lstrip("./")


def should_skip_path(path: Path) -> bool:
    rel = _normalize_path(path)
    parts = set(path.parts)
    if parts & SKIP_PARTS:
        return True
    if not is_factory_readiness_path(path):
        return True
    return not (
        rel.endswith(".md")
        or rel.endswith(".markdown")
        or rel.endswith(".yaml")
        or rel.endswith(".yml")
    )


def is_factory_readiness_path(path: Path) -> bool:
    rel = _normalize_path(path)
    return any(prefix in rel for prefix in FACTORY_PREFIXES)


def _extract_frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    return text[4:end]


def _extract_fenced_yaml(text: str) -> list[str]:
    blocks: list[str] = []
    pattern = re.compile(r"```(?:ya?ml)\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
    for match in pattern.finditer(text):
        blocks.append(match.group(1))
    return blocks


def _extract_labeled_sections(text: str) -> list[str]:
    sections: list[str] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("#"):
            continue
        heading = line.lower()
        if "first-principles gate" not in heading and "first principles gate" not in heading:
            continue
        body: list[str] = []
        for body_line in lines[index + 1 :]:
            if body_line.lstrip().startswith("#"):
                break
            body.append(body_line)
        sections.append("\n".join(body))
    return sections


def _parse_scalar(value: str) -> Any:
    stripped = value.strip()
    if stripped in {"[]", ""}:
        return [] if stripped == "[]" else ""
    if stripped.startswith("[") and stripped.endswith("]"):
        inner = stripped[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("\"'") for part in inner.split(",")]
    return stripped.strip("\"'")


def _parse_gate_mapping(block: str) -> tuple[dict[str, Any] | str | None, str | None]:
    lines = block.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("first_principles_gate:"):
            continue
        raw_value = stripped.split(":", 1)[1].strip()
        if raw_value:
            return raw_value.strip("\"'"), _parse_reason(lines)

        mapping: dict[str, Any] = {}
        for child in lines[index + 1 :]:
            if not child.startswith((" ", "\t")):
                if child.strip():
                    break
                continue
            child_stripped = child.strip()
            if ":" not in child_stripped:
                continue
            key, value = child_stripped.split(":", 1)
            mapping[key.strip()] = _parse_scalar(value)
        return mapping, _parse_reason(lines)
    return None, None


def _parse_reason(lines: list[str]) -> str | None:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("first_principles_gate_reason:"):
            return stripped.split(":", 1)[1].strip().strip("\"'")
    return None


def extract_gate(text: str) -> tuple[dict[str, Any] | str | None, str | None]:
    frontmatter = _extract_frontmatter(text)
    if frontmatter is not None:
        gate, reason = _parse_gate_mapping(frontmatter)
        if gate is not None:
            return gate, reason

    for block in _extract_fenced_yaml(text):
        gate, reason = _parse_gate_mapping(block)
        if gate is not None:
            return gate, reason

    for section in _extract_labeled_sections(text):
        gate, reason = _parse_gate_mapping("first_principles_gate:\n" + section)
        if gate is not None:
            return gate, reason

    return None, None


def _is_blank(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in PLACEHOLDERS
    if isinstance(value, list):
        return len(value) == 0
    return value is None


def validate_gate(path: Path, *, strict: bool = False) -> GateResult:
    rel = _normalize_path(path)
    if should_skip_path(path):
        return GateResult(rel, "skipped", "path is outside first-principles gate validation scope")

    if not path.exists():
        return GateResult(rel, "skipped", "path does not exist")

    text = path.read_text(encoding="utf-8")
    gate, reason = extract_gate(text)
    if gate is None:
        status = "fail" if strict and is_factory_readiness_path(path) else "warn"
        return GateResult(rel, status, "missing first_principles_gate evidence")

    if isinstance(gate, str):
        if gate == "not_applicable" and reason:
            return GateResult(rel, "pass", "first_principles_gate exemption accepted")
        status = "fail" if strict else "warn"
        return GateResult(
            rel,
            status,
            "invalid first_principles_gate exemption",
            ("not_applicable requires first_principles_gate_reason",),
        )

    missing = tuple(field for field in REQUIRED_FIELDS if field not in gate)
    invalid: list[str] = []
    if missing:
        invalid.append("missing required fields: " + ", ".join(missing))

    decision = str(gate.get("artifact_decision", "")).strip()
    if decision and decision not in ALLOWED_DECISIONS:
        invalid.append(f"invalid artifact_decision: {decision}")

    blank = tuple(field for field in REQUIRED_FIELDS if field in gate and _is_blank(gate[field]))
    if blank:
        invalid.append("blank or placeholder fields: " + ", ".join(blank))

    if invalid:
        status = "fail" if strict else "warn"
        return GateResult(rel, status, "malformed first_principles_gate evidence", tuple(invalid))

    return GateResult(rel, "pass", "first_principles_gate evidence valid")


def validate_paths(paths: list[Path], *, strict: bool = False) -> list[GateResult]:
    if not paths:
        return [GateResult("<none>", "skipped", "no paths provided")]
    return [validate_gate(path, strict=strict) for path in paths]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    results = validate_paths(args.paths, strict=args.strict)
    if args.format == "json":
        print(json.dumps({"results": [result.as_dict() for result in results]}, indent=2))
    else:
        for result in results:
            prefix = "[family-gate]"
            print(f"{prefix} first-principles gate {result.status}: {result.path}: {result.message}")
            for detail in result.details:
                print(f"{prefix}   - {detail}")

    return 1 if any(result.status == "fail" for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
