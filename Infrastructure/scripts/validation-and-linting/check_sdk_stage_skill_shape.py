#!/usr/bin/env python3
"""Validate SDK-created deterministic stage skill heading and context shape."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only in stripped runtimes
    yaml = None


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

SYNAIPSE_STAGE_NAMES = {
    "strategy",
    "reframe",
    "brainstorm",
    "trace-plan",
    "tracker-plan",
    "slice-spec",
    "execution-plan",
    "work",
    "review",
    "eval-report",
    "reconcile",
    "reinforce",
}

REFERENCE_STATUS_VALUES = {
    "adopted",
    "needs_synaipse_rewrite",
    "legacy_context_only",
    "archive_candidate",
    "remove_candidate",
}

LEGACY_REFERENCE_TERMS = (
    "Harness Engineering",
    "he-plan",
    "he-spec",
    "he-linear-plan",
    "he-code-review",
    "he-work",
    "he-strategy",
    "he-reframe",
    "he-brainstorm",
    "he-eval-report",
    "he-reconcile",
    "he-reinforce",
    "he-router",
    "he-phase-work",
    "he-fix-bugs",
    "he-heartbeat",
    "he-improve",
)

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


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


def load_yaml(path: Path) -> dict:
    if yaml is None:
        fail("PyYAML is required for SDK stage source-context validation")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))  # type: ignore[union-attr]
    if not isinstance(payload, dict):
        fail(f"{path} must contain a YAML mapping")
    return payload


def relative_markdown_links(path: Path) -> list[str]:
    links: list[str] = []
    for match in MARKDOWN_LINK_RE.finditer(path.read_text(encoding="utf-8")):
        target = match.group(1).strip()
        if not target or target.startswith(("#", "http://", "https://", "mailto:", "plugin://")):
            continue
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        target = target.split("#", 1)[0]
        if target:
            links.append(target)
    return links


def validate_copied_reference_links(root: Path, reference_path: Path) -> None:
    for target in relative_markdown_links(reference_path):
        resolved = (reference_path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            fail(
                f"{reference_path.relative_to(root)} has link escaping repository: {target}"
            )
        if not resolved.exists():
            fail(
                f"{reference_path.relative_to(root)} has broken Markdown link: {target}"
            )


def validate_synaipse_reference_quality(root: Path) -> None:
    index_path = (
        root
        / "Plugins/synaipse-harness/references/upstream/harness-engineering-context.yaml"
    )
    if not index_path.exists():
        return

    payload = load_yaml(index_path)
    copied_root = root / "Plugins/synaipse-harness/references/upstream/harness-engineering"
    references = payload.get("references")
    quality_audit = payload.get("quality_audit")
    if not isinstance(quality_audit, dict):
        fail(f"{index_path.relative_to(root)} missing quality_audit metadata")
    if not isinstance(references, list) or not references:
        fail(f"{index_path.relative_to(root)} must list copied references")
    if payload.get("reference_count") != len(references):
        fail(
            f"{index_path.relative_to(root)} reference_count must equal listed references"
        )

    indexed_paths: set[str] = set()
    markdown_count = 0
    rewrite_needed = 0
    for row in references:
        if not isinstance(row, dict):
            fail(f"{index_path.relative_to(root)} references entries must be mappings")
        ref_path_text = row.get("path")
        if not isinstance(ref_path_text, str):
            fail(f"{index_path.relative_to(root)} reference missing path")
        indexed_paths.add(ref_path_text)
        ref_path = root / ref_path_text
        if not ref_path.exists():
            fail(f"{index_path.relative_to(root)} points at missing reference: {ref_path_text}")
        try:
            ref_path.resolve().relative_to(copied_root.resolve())
        except ValueError:
            fail(f"{ref_path_text} must stay inside SynAIpse copied upstream reference root")

        status = row.get("adoption_status")
        if status not in REFERENCE_STATUS_VALUES:
            fail(f"{ref_path_text} has invalid or missing adoption_status: {status!r}")
        stage_map = row.get("stage_map")
        if not isinstance(stage_map, list) or not stage_map:
            fail(f"{ref_path_text} must declare at least one SynAIpse stage_map entry")
        invalid_stages = sorted(stage for stage in stage_map if stage not in SYNAIPSE_STAGE_NAMES)
        if invalid_stages:
            fail(f"{ref_path_text} has invalid SynAIpse stage_map entries: {invalid_stages}")

        notes = row.get("quality_notes")
        if not isinstance(notes, dict):
            fail(f"{ref_path_text} missing quality_notes")
        stale_terms = notes.get("stale_terms")
        if not isinstance(stale_terms, list):
            fail(f"{ref_path_text} quality_notes.stale_terms must be a list")
        if notes.get("accuracy_certification") not in {
            "structure_and_links_only",
            "not_certified",
        }:
            fail(f"{ref_path_text} has invalid quality_notes.accuracy_certification")

        detected_text = ref_path_text
        if ref_path.suffix == ".md":
            markdown_count += 1
            detected_text += "\n" + ref_path.read_text(encoding="utf-8")
            validate_copied_reference_links(root, ref_path)
            if notes.get("link_check") != "passed":
                fail(f"{ref_path_text} Markdown reference must record link_check: passed")
        elif notes.get("link_check") != "not_markdown":
            fail(f"{ref_path_text} non-Markdown reference must record link_check: not_markdown")
        detected_terms = sorted(term for term in LEGACY_REFERENCE_TERMS if term in detected_text)

        if sorted(stale_terms) != detected_terms:
            fail(
                f"{ref_path_text} stale_terms drifted: expected {detected_terms}, "
                f"got {sorted(stale_terms)}"
            )
        if detected_terms and status == "adopted":
            fail(f"{ref_path_text} cannot be adopted while legacy HE terms remain")
        if status == "needs_synaipse_rewrite":
            rewrite_needed += 1
            if not row.get("rewrite_reason"):
                fail(f"{ref_path_text} needs_synaipse_rewrite requires rewrite_reason")

    actual_paths = {
        path.relative_to(root).as_posix()
        for path in copied_root.rglob("*")
        if path.is_file()
    }
    missing_from_index = sorted(actual_paths - indexed_paths)
    stale_index_rows = sorted(indexed_paths - actual_paths)
    if missing_from_index or stale_index_rows:
        fail(
            f"{index_path.relative_to(root)} copied reference index drifted: "
            f"missing_from_index={missing_from_index}, stale_index_rows={stale_index_rows}"
        )

    if markdown_count == 0:
        fail("SynAIpse copied upstream reference audit found no Markdown references")
    if rewrite_needed == 0:
        fail("SynAIpse copied upstream reference audit must classify legacy rewrites explicitly")


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

    validate_synaipse_reference_quality(root)

    print(f"[sdk-stage-shape] SDK stage skill shape passed ({len(skill_dirs)} skill(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
