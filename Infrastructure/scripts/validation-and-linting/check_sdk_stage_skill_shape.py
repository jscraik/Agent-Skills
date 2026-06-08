#!/usr/bin/env python3
"""Validate SDK-created deterministic stage skill heading shape."""

from __future__ import annotations

import re
import sys
from pathlib import Path


EXPECTED_STAGE_HEADINGS = [
    "Stage Contract",
    "When to use",
    "When not to use",
    "Required inputs",
    "Deliverables",
    "Preconditions",
    "Procedure",
    "Allowed writes",
    "Forbidden writes",
    "Exit criteria",
    "Validation",
    "Handoff",
    "Failure modes",
    "Execution boundaries",
    "Gotchas",
    "Examples",
    "References",
]

REQUIRED_COMPANION_FILES = [
    Path("references/contract.yaml"),
    Path("references/evals.yaml"),
    Path("references/task-profile.json"),
    Path("references/source-context.yaml"),
    Path("agents/openai.yaml"),
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def frontmatter(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        return ""
    end = raw.find("\n---", 4)
    if end == -1:
        return ""
    return raw[4:end]


def markdown_h2_headings(path: Path) -> list[str]:
    headings: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"##\s+(.+?)\s*", line)
        if match:
            headings.append(match.group(1))
    return headings


def sdk_stage_skill_dirs(root: Path) -> list[Path]:
    skill_dirs: list[Path] = []
    for skill_md in root.glob("**/SKILL.md"):
        relative = skill_md.relative_to(root)
        if any(part in {".agents", ".skillsets", "cache"} for part in relative.parts):
            continue
        if "sdk_stage:" in frontmatter(skill_md):
            skill_dirs.append(skill_md.parent)
    return sorted(skill_dirs)


def fail(message: str) -> None:
    print(f"[sdk-stage-shape] ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    root = repo_root()
    skill_dirs = sdk_stage_skill_dirs(root)
    if not skill_dirs:
        fail("no SDK stage skills with metadata.sdk_stage were found")

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        headings = markdown_h2_headings(skill_md)
        if headings != EXPECTED_STAGE_HEADINGS:
            fail(
                f"{skill_md.relative_to(root)} headings drifted: "
                f"expected {EXPECTED_STAGE_HEADINGS}, got {headings}"
            )

        frontmatter_text = frontmatter(skill_md)
        if "command_visibility: orchestrator" not in frontmatter_text:
            fail(f"{skill_md.relative_to(root)} missing command_visibility: orchestrator")
        if "lifecycle_state: active" not in frontmatter_text:
            fail(f"{skill_md.relative_to(root)} missing lifecycle_state: active")

        for companion in REQUIRED_COMPANION_FILES:
            if not (skill_dir / companion).exists():
                fail(f"{skill_dir.relative_to(root)} missing {companion}")

        skill_text = skill_md.read_text(encoding="utf-8")
        if "./references/source-context.yaml" not in skill_text:
            fail(f"{skill_md.relative_to(root)} must link references/source-context.yaml")

        source_context = skill_dir / "references/source-context.yaml"
        source_text = source_context.read_text(encoding="utf-8")
        upstream_index = (
            root
            / "Plugins/synaipse-harness/references/upstream/harness-engineering-context.yaml"
        )
        if skill_md.relative_to(root).parts[:2] == ("Plugins", "synaipse-harness"):
            if not upstream_index.exists():
                fail("synaipse-harness missing copied Harness Engineering context index")
            if "Plugins/synaipse-harness/references/upstream/harness-engineering-context.yaml" not in source_text:
                fail(
                    f"{source_context.relative_to(root)} must point at the copied "
                    "SynAIpse-owned Harness Engineering context index"
                )
            copied_domain_model = (
                root
                / "Plugins/synaipse-harness/references/upstream/harness-engineering/domain-model-routing.md"
            )
            if not copied_domain_model.exists():
                fail("synaipse-harness missing copied domain-model-routing.md")
        required_source_markers = (
            "schema_version:",
            "skill:",
            "stage:",
            "template:",
            "original_references:",
            "load_when:",
            "provenance_policy:",
        )
        missing_markers = [marker for marker in required_source_markers if marker not in source_text]
        if missing_markers:
            fail(
                f"{source_context.relative_to(root)} missing source context markers: "
                f"{missing_markers}"
            )

    print(f"[sdk-stage-shape] SDK stage skill shape passed ({len(skill_dirs)} skill(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
