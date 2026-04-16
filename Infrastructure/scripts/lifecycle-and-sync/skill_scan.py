#!/usr/bin/env python3
"""Fast shared scanner for repository skill metadata and quality checks."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOTS = ("auth", "backend", "frontend", "github", "interview", "product", "utilities")
ORDERED_TYPES = (
    "library_api_reference",
    "product_verification",
    "data_fetch_analysis",
    "team_automation",
    "scaffolding_templates",
    "code_quality_review",
    "ci_cd_deployment",
    "runbook",
    "infrastructure_ops",
)
REQUIRED_HEADINGS = (
    "When to use",
    "Required inputs",
    "Deliverables",
    "Failure mode",
    "Gotchas",
)


@dataclass
class SkillFile:
    path: Path
    relative_path: str
    skill_dir: Path
    skill_type: str
    line_count: int
    code_fence_count: int
    headings: set[str]


def iter_skill_files() -> Iterable[Path]:
    for root_name in ROOTS:
        root = REPO_ROOT / root_name
        if not root.is_dir():
            continue
        yield from sorted(root.rglob("SKILL.md"))


def frontmatter_block(text: str) -> list[str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return []
    block: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            return block
        block.append(line)
    return []


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = frontmatter_block(text)
    parsed: dict[str, str] = {}
    current_key: str | None = None
    current_indent = 0
    metadata_key: str | None = None

    for raw_line in lines:
        if not raw_line.strip():
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            current_indent = indent
            metadata_key = None
            parsed[current_key] = value.strip().strip("\"'")
            continue

        if current_key == "metadata" and indent > current_indent and ":" in line:
            key, value = line.split(":", 1)
            metadata_key = key.strip()
            parsed[f"metadata.{metadata_key}"] = value.strip().strip("\"'")
            continue

        if metadata_key and current_key == "metadata" and indent > current_indent:
            existing = parsed.get(f"metadata.{metadata_key}", "")
            parsed[f"metadata.{metadata_key}"] = " ".join(
                part for part in (existing, line.strip("\"'")) if part
            ).strip()
            continue

        if current_key and indent > current_indent:
            existing = parsed.get(current_key, "")
            parsed[current_key] = " ".join(
                part for part in (existing, line.strip("\"'")) if part
            ).strip()

    return parsed


def extract_headings(text: str) -> set[str]:
    headings: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if not match:
            continue
        heading = re.sub(r"\s+\(.+\)\s*$", "", match.group(1).strip())
        headings.add(heading)
    return headings


def load_skill(path: Path) -> SkillFile:
    text = path.read_text(encoding="utf-8", errors="ignore")
    parsed = parse_frontmatter(text)
    skill_type = parsed.get("metadata.skill-type") or parsed.get("metadata.skill_type") or ""
    return SkillFile(
        path=path,
        relative_path=path.relative_to(REPO_ROOT).as_posix(),
        skill_dir=path.parent,
        skill_type=skill_type,
        line_count=text.count("\n") + (0 if not text or text.endswith("\n") else 1),
        code_fence_count=sum(1 for line in text.splitlines() if line.startswith("```")),
        headings=extract_headings(text),
    )


def all_skills() -> list[SkillFile]:
    return [load_skill(path) for path in iter_skill_files()]


def title_case(value: str) -> str:
    return " ".join(word.capitalize() for word in value.replace("_", " ").split())


def cmd_lint_progressive_disclosure(mode: str) -> int:
    skills = all_skills()
    errors = 0
    warnings = 0

    def emit(severity: str, rel_path: str, message: str) -> None:
        nonlocal errors, warnings
        if severity == "error":
            print(f"ERROR {rel_path}: {message}")
            errors += 1
        else:
            print(f"WARN  {rel_path}: {message}")
            warnings += 1

    for skill in skills:
        if skill.line_count > 360:
            emit("error", skill.relative_path, f"SKILL.md exceeds hard cap (lines={skill.line_count}, cap=360)")
        elif skill.line_count > 320:
            emit("warn", skill.relative_path, f"SKILL.md exceeds target length (lines={skill.line_count}, target=320)")
            if not (skill.skill_dir / "references").is_dir():
                emit("error", skill.relative_path, "length > 320 without Infrastructure/references/ for progressive disclosure")

        if skill.code_fence_count >= 6 and not (skill.skill_dir / "scripts").is_dir():
            emit("error", skill.relative_path, f"many code fences ({skill.code_fence_count}) but Infrastructure/scripts/ directory is missing")
        elif skill.code_fence_count >= 4 and not (skill.skill_dir / "scripts").is_dir():
            emit("warn", skill.relative_path, f"consider moving embedded mechanics to Infrastructure/scripts/ (code fences={skill.code_fence_count})")

        for heading in REQUIRED_HEADINGS:
            if heading not in skill.headings:
                severity = "error" if mode == "strict" else "warn"
                emit(severity, skill.relative_path, f"missing recommended section heading: ## {heading}")

    print(f"Checked files: {len(skills)}")
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")
    print(f"Mode: {mode}")
    if mode == "strict" and errors > 0:
        return 1
    print("Progressive disclosure lint passed")
    return 0


def cmd_lint_skill_types() -> int:
    skills = all_skills()
    missing = 0
    invalid = 0
    allowed = set(ORDERED_TYPES)

    for skill in skills:
        if not skill.skill_type:
            print(f"MISSING skill type: {skill.relative_path}")
            missing += 1
            continue
        if skill.skill_type not in allowed:
            print(f"INVALID skill type: {skill.relative_path} -> {skill.skill_type}")
            invalid += 1

    print(f"Checked files: {len(skills)}")
    print(f"Missing: {missing}")
    print(f"Invalid: {invalid}")
    if missing > 0 or invalid > 0:
        return 1
    print("skill-type lint passed")
    return 0


def cmd_write_skill_type_index(output: Path) -> int:
    skills = all_skills()
    counts = {skill_type: 0 for skill_type in ORDERED_TYPES}
    grouped: dict[str, list[tuple[str, str]]] = {skill_type: [] for skill_type in ORDERED_TYPES}
    invalid: list[tuple[str, str, str]] = []
    total_tagged = 0

    for skill in skills:
        if not skill.skill_type:
            continue
        rel_dir = skill.skill_dir.relative_to(REPO_ROOT).as_posix()
        category = str(Path(rel_dir).parent).replace("\\", "/")
        name = skill.skill_dir.name
        if skill.skill_type in counts:
            counts[skill.skill_type] += 1
            total_tagged += 1
            grouped[skill.skill_type].append((name, category))
        else:
            invalid.append((name, category, skill.skill_type))

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fh:
        fh.write("# Skill Type Index\n\n")
        fh.write("Generated from `metadata.skill-type` tags in skill frontmatter.\n\n")
        fh.write("## Table of Contents\n")
        fh.write("- [Summary](#summary)\n")
        fh.write("- [Validation Notes](#validation-notes)\n")
        fh.write("- [Canonical Values](#canonical-values)\n")
        fh.write("- [Semantic Types](#semantic-types)\n\n")
        fh.write("## Summary\n\n")
        for skill_type in ORDERED_TYPES:
            fh.write(f"- `{skill_type}`: {counts[skill_type]}\n")
        fh.write(f"- `invalid`: {len(invalid)}\n")
        fh.write(f"- `total_tagged`: {total_tagged}\n\n")
        fh.write("## Validation Notes\n\n")
        fh.write(f"- Source scope: `{' '.join(ROOTS)}`.\n")
        fh.write("- Companion mode: sandbox-safe (no protected runtime path mutations).\n")
        fh.write("- Validation command:\n")
        fh.write("  - `bash Infrastructure/scripts/validation-and-linting/lint_skill_types.sh`\n\n")
        fh.write("## Canonical Values\n\n")
        for skill_type in ORDERED_TYPES:
            fh.write(f"- `{skill_type}`\n")
        fh.write("\n## Semantic Types\n\n")
        for skill_type in ORDERED_TYPES:
            fh.write(f"### {title_case(skill_type)}\n\n")
            items = sorted(grouped[skill_type])
            if items:
                for name, category in items:
                    fh.write(f"- {name} ({category})\n")
            else:
                fh.write("- _No tagged skills yet._\n")
            fh.write("\n")
        if invalid:
            fh.write("## Invalid Tags\n\n")
            for name, category, skill_type in sorted(invalid):
                fh.write(f"- {name} ({category}) [{skill_type}]\n")
            fh.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fast repository skill scanner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    progressive = subparsers.add_parser("lint-progressive-disclosure")
    progressive.add_argument("--mode", choices=("strict", "warn"), default="warn")

    subparsers.add_parser("lint-skill-types")

    index = subparsers.add_parser("write-skill-type-index")
    index.add_argument("--output", type=Path, required=True)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "lint-progressive-disclosure":
        return cmd_lint_progressive_disclosure(args.mode)
    if args.command == "lint-skill-types":
        return cmd_lint_skill_types()
    if args.command == "write-skill-type-index":
        return cmd_write_skill_type_index(args.output)
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
