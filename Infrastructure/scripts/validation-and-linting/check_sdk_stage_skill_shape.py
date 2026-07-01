#!/usr/bin/env python3
"""Validate SDK-created deterministic stage skill heading and context shape."""

from __future__ import annotations

import re
import sys
import json
import subprocess
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only in stripped runtimes
    yaml = None


EXPECTED_STAGE_HEADINGS = [
    "When to use",
    "Required inputs",
    "Deliverables",
    "Procedure",
    "Validation",
    "Handoff",
    "Failure modes",
    "Gotchas",
    "References",
]

REQUIRED_YAML_KEYS = {
    Path("references/contract.yaml"): {
        "schema_version",
        "skill",
        "stage",
        "preconditions",
        "allowed_writes",
        "forbidden_writes",
        "execution_boundaries",
        "exit_criteria",
    },
    Path("references/evals.yaml"): {
        "schema_version",
        "skill",
        "stage",
        "eval_scenarios",
        "success_criteria",
    },
    Path("references/source-context.yaml"): {
        "schema_version",
        "skill",
        "stage",
        "template",
        "original_references",
        "references",
        "load_when",
        "provenance_policy",
        "allowed_claims",
        "forbidden_claims",
        "freshness",
        "context_budget",
    },
    Path("agents/openai.yaml"): {
        "schema_version",
        "skill",
        "stage",
        "role",
        "instructions",
        "tool_policy",
        "output_contract",
    },
}

REQUIRED_JSON_KEYS = {
    Path("references/task-profile.json"): {
        "schema_version",
        "skill",
        "stage",
        "task_type",
        "inputs",
        "outputs",
        "validation_profile",
    },
}

REQUIRED_COMPANION_FILES = [
    *REQUIRED_YAML_KEYS.keys(),
    *REQUIRED_JSON_KEYS.keys(),
]

SOURCE_CONTEXT_REFERENCE_KEYS = {
    "path",
    "kind",
    "provenance",
    "load_when",
    "allowed_claims",
    "forbidden_claims",
    "freshness",
    "context_budget",
    "claim_scope",
    "bounded_unit",
}

REFERENCE_KINDS = {
    "expert_viewpoint",
    "evidence_packet",
    "prior_art",
    "runbook",
    "rubric",
    "substantial_context",
    "composite_runbook",
    "stage_companion",
    "upstream_pack_export",
}

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
    "he-phase-work",
    "he-fix-bugs",
    "he-improve",
)

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")

REFERENCE_AUDIT_CERTIFICATIONS = {
    "structure_and_links_only",
    "not_certified",
}


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
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        payload = load_yaml_with_ruby(path, text)
    else:
        payload = yaml.safe_load(text)  # type: ignore[union-attr]
    if not isinstance(payload, dict):
        fail(f"{path} must contain a YAML mapping")
    return payload


def load_yaml_with_ruby(path: Path, text: str) -> dict:
    code = (
        "require 'yaml'; require 'json'; "
        "print JSON.generate(YAML.safe_load(STDIN.read, permitted_classes: [], aliases: true))"
    )
    try:
        process = subprocess.run(
            ["ruby", "-e", code],
            input=text,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        fail_yaml_runtime_unavailable(path, str(exc))
    if process.returncode != 0:
        if ruby_yaml_runtime_unavailable(process.stderr):
            fail_yaml_runtime_unavailable(path, process.stderr)
        fail(f"{path} is invalid YAML: {process.stderr.strip()}")
    try:
        payload = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        fail_yaml_runtime_unavailable(path, f"ruby returned non-JSON output: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path} must contain a YAML mapping")
    return payload


def ruby_yaml_runtime_unavailable(stderr: str) -> bool:
    lowered = stderr.lower()
    tooling_markers = (
        "mise",
        "shim",
        "trust",
        "permission denied",
        "command not found",
        "no such file or directory",
    )
    return any(marker in lowered for marker in tooling_markers)


def fail_yaml_runtime_unavailable(path: Path, stderr: str = "") -> None:
    detail = f" Ruby stderr: {stderr.strip()}" if stderr.strip() else ""
    fail(
        f"{path} requires PyYAML or runnable Ruby YAML; run through "
        f"bash Infrastructure/scripts/run-infrastructure-python.sh.{detail}"
    )


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{path} must contain a JSON object")
    return payload


def missing_keys(payload: dict, required: set[str]) -> list[str]:
    return sorted(key for key in required if key not in payload)


def validate_required_mapping(
    root: Path,
    skill_dir: Path,
    relative_path: Path,
    required: set[str],
) -> dict:
    path = skill_dir / relative_path
    if not path.exists():
        fail(f"{skill_dir.relative_to(root)} missing {relative_path}")
    payload = load_yaml(path)
    missing = missing_keys(payload, required)
    if missing:
        fail(f"{path.relative_to(root)} missing required keys: {missing}")
    return payload


def validate_required_json(
    root: Path,
    skill_dir: Path,
    relative_path: Path,
    required: set[str],
) -> dict:
    path = skill_dir / relative_path
    if not path.exists():
        fail(f"{skill_dir.relative_to(root)} missing {relative_path}")
    payload = load_json(path)
    missing = missing_keys(payload, required)
    if missing:
        fail(f"{path.relative_to(root)} missing required keys: {missing}")
    return payload


def validate_source_context_references(
    root: Path,
    skill_dir: Path,
    payload: dict,
    source_context: Path,
) -> None:
    references = payload.get("references")
    if not isinstance(references, list) or not references:
        fail(f"{source_context.relative_to(root)} references must be a non-empty list")

    for index, row in enumerate(references):
        if not isinstance(row, dict):
            fail(f"{source_context.relative_to(root)} references[{index}] must be a mapping")
        missing = missing_keys(row, SOURCE_CONTEXT_REFERENCE_KEYS)
        if missing:
            fail(
                f"{source_context.relative_to(root)} references[{index}] "
                f"missing required keys: {missing}"
            )
        kind = row.get("kind")
        if kind not in REFERENCE_KINDS:
            fail(
                f"{source_context.relative_to(root)} references[{index}] "
                f"has invalid kind: {kind!r}"
            )

        ref_path_text = row.get("path")
        if not isinstance(ref_path_text, str) or not ref_path_text.strip():
            fail(f"{source_context.relative_to(root)} references[{index}] path must be a string")

        if kind == "upstream_pack_export":
            continue

        if ref_path_text.startswith(("http://", "https://", "/")):
            fail(
                f"{source_context.relative_to(root)} references[{index}] "
                "must not require an absolute or remote runtime path"
            )

        if row.get("bounded_unit") is not True:
            fail(
                f"{source_context.relative_to(root)} references[{index}] "
                "must declare bounded_unit: true"
            )

        if ref_path_text.startswith("references/") and ref_path_text.endswith(".md"):
            local_reference = skill_dir / ref_path_text
            if not local_reference.exists():
                fail(
                    f"{source_context.relative_to(root)} references[{index}] "
                    f"points at missing SDK-local reference: {ref_path_text}"
                )


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


def _validate_quality_audit_structure(
    root: Path,
    payload: dict,
    index_path: Path,
) -> list[dict]:
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
    return references


def _validate_reference_entry(
    root: Path,
    row: dict,
    copied_root: Path,
    index_path: Path,
) -> tuple[str, bool, bool]:
    if not isinstance(row, dict):
        fail(f"{index_path.relative_to(root)} references entries must be mappings")
    ref_path_text = row.get("path")
    if not isinstance(ref_path_text, str):
        fail(f"{index_path.relative_to(root)} reference missing path")
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
    if notes.get("accuracy_certification") not in REFERENCE_AUDIT_CERTIFICATIONS:
        fail(f"{ref_path_text} has invalid quality_notes.accuracy_certification")

    detected_text = ref_path_text
    is_markdown = ref_path.suffix == ".md"
    if is_markdown:
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

    needs_rewrite = status == "needs_synaipse_rewrite"
    if needs_rewrite and not row.get("rewrite_reason"):
        fail(f"{ref_path_text} needs_synaipse_rewrite requires rewrite_reason")
    return ref_path_text, is_markdown, needs_rewrite


def validate_synaipse_reference_quality(root: Path) -> None:
    index_path = (
        root
        / "Plugins/synaipse-harness/references/upstream/harness-engineering-context.yaml"
    )
    if not index_path.exists():
        return

    payload = load_yaml(index_path)
    copied_root = root / "Plugins/synaipse-harness/references/upstream/harness-engineering"
    references = _validate_quality_audit_structure(root, payload, index_path)

    indexed_paths: set[str] = set()
    markdown_count = 0
    rewrite_needed = 0
    for row in references:
        ref_path_text, is_markdown, needs_rewrite = _validate_reference_entry(
            root,
            row,
            copied_root,
            index_path,
        )
        indexed_paths.add(ref_path_text)
        if is_markdown:
            markdown_count += 1
        if needs_rewrite:
            rewrite_needed += 1

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

        for companion, required_keys in REQUIRED_YAML_KEYS.items():
            validate_required_mapping(root, skill_dir, companion, required_keys)

        for companion, required_keys in REQUIRED_JSON_KEYS.items():
            validate_required_json(root, skill_dir, companion, required_keys)

        skill_text = skill_md.read_text(encoding="utf-8")
        if "./references/source-context.yaml" not in skill_text:
            fail(f"{skill_md.relative_to(root)} must link references/source-context.yaml")

        source_context = skill_dir / "references/source-context.yaml"
        source_payload = load_yaml(source_context)
        validate_source_context_references(root, skill_dir, source_payload, source_context)
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
        required_source_markers = tuple(f"{key}:" for key in REQUIRED_YAML_KEYS[source_context.relative_to(skill_dir)])
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
