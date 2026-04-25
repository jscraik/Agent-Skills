#!/usr/bin/env python3
"""Generate rooted runtime skill-set entrypoints."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from selection_policy import ROOT_SKILL_SET_NAMES, policy_identity
from skillset_model import ROOT_SKILL_SET_METADATA, modules_by_skill_set, build_skill_modules, rel, repo_root

TEMPLATE = repo_root() / "Infrastructure" / "templates" / "root-skill-set" / "SKILL.md.j2"
DEFAULT_OUTPUT_DIR = repo_root() / ".agents" / "skills"
MAX_DESCRIPTION_WORDS = 35
MAX_BODY_WORDS = 250


def word_count(text: str) -> int:
    """
    Count non-empty whitespace-separated tokens in the given text.
    
    Parameters:
        text (str): Input string to evaluate; tokens are produced by splitting on any whitespace.
    
    Returns:
        int: Number of tokens after splitting on whitespace and excluding tokens that are empty or only whitespace.
    """
    return len([word for word in text.split() if word.strip()])


def render_template(skill_set_name: str, metadata: dict[str, str]) -> str:
    """
    Render the SKILL.md template for a root skill-set using provided metadata.
    
    Parameters:
    	skill_set_name (str): Root skill-set identifier (used for `{{ skill_set_name }}` and to generate `{{ title }}` by replacing hyphens with spaces and title-casing).
    	metadata (dict[str, str]): Mapping providing values for template tokens:
    		- "description": substituted for `{{ short_mutually_exclusive_description }}`
    		- "scope": substituted for `{{ scope }}`
    		- "exclusions": substituted for `{{ exclusions }}`
    
    Returns:
    	rendered (str): The template text with all known tokens replaced by their corresponding values from `skill_set_name` and `metadata`.
    """
    title = skill_set_name.replace("-", " ").title()
    template = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{{ skill_set_name }}": skill_set_name,
        "{{ short_mutually_exclusive_description }}": metadata["description"],
        "{{ title }}": title,
        "{{ scope }}": metadata["scope"],
        "{{ exclusions }}": metadata["exclusions"],
    }
    rendered = template
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)
    return rendered


def build_roots(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    """
    Generate a report of rendered root skill-set entrypoints and validate their lengths.
    
    Renders the SKILL.md template for each root skill-set name, counts words in each root's short description and rendered body, groups modules by root, and records any length violations.
    
    Returns:
        report (dict): A dictionary with the following keys:
            - status (str): "pass" if no violations, otherwise "fail".
            - projection_mode (str): Always "rooted".
            - policy_identity (str): Identity string from the selection policy.
            - root_count (int): Number of root entries processed.
            - roots (list[dict]): List of root records, each containing:
                - name (str): Root skill-set name.
                - path (str): Relative path where SKILL.md would be written.
                - description_words (int): Word count of the short description.
                - body_words (int): Word count of the rendered SKILL.md body.
                - module_count (int): Number of modules associated with this root.
                - content (str): Rendered SKILL.md body.
            - unmapped (Any): Modules returned as unmapped by build_skill_modules().
            - violations (list[dict]): List of violation records; each contains:
                - code (str): Violation code, e.g. "ROOT_DESCRIPTION_TOO_LONG" or "ROOT_BODY_TOO_LONG".
                - name (str): Affected root skill-set name.
                - words (int): The offending word count.
    """
    modules, unmapped = build_skill_modules()
    grouped = modules_by_skill_set(modules)
    roots = []
    violations: list[dict[str, Any]] = []
    for name in ROOT_SKILL_SET_NAMES:
        metadata = ROOT_SKILL_SET_METADATA[name]
        body = render_template(name, metadata)
        description_words = word_count(metadata["description"])
        body_words = word_count(body)
        root_path = output_dir / name / "SKILL.md"
        root = {
            "name": name,
            "path": rel(root_path),
            "description_words": description_words,
            "body_words": body_words,
            "module_count": len(grouped.get(name, [])),
            "content": body,
        }
        roots.append(root)
        if description_words > MAX_DESCRIPTION_WORDS:
            violations.append({"code": "ROOT_DESCRIPTION_TOO_LONG", "name": name, "words": description_words})
        if body_words > MAX_BODY_WORDS:
            violations.append({"code": "ROOT_BODY_TOO_LONG", "name": name, "words": body_words})
    return {
        "status": "pass" if not violations else "fail",
        "projection_mode": "rooted",
        "policy_identity": policy_identity(),
        "root_count": len(roots),
        "roots": roots,
        "unmapped": unmapped,
        "violations": violations,
    }


def write_roots(report: dict[str, Any], output_dir: Path, *, repo_root_path: Path | None = None) -> list[dict[str, str]]:
    # Verify output_dir is inside the expected repository subtree before any mutations.
    """
    Write SKILL.md files for each root in the report into the specified output directory and return a list of write records.
    
    Parameters:
        report (dict[str, Any]): Report produced by build_roots; must contain a "roots" iterable where each root is a mapping with at least "name" (directory name) and "content" (file contents).
        output_dir (Path): Target base directory under which per-root subdirectories will be created (e.g., <output_dir>/<root_name>/SKILL.md).
        repo_root_path (Path | None): Optional repository root override used to validate that `output_dir` resides under the expected `.agents/skills` subtree. If None, the repository root is determined automatically.
    
    Returns:
        list[dict[str, str]]: A list of records for each written file, each containing `path` (relative path string) and `action` (e.g., `"write"`).
    
    Raises:
        ValueError: If `output_dir` is not located within the expected repository subtree (.agents/skills) relative to `repo_root_path` or the detected repository root.
    """
    repository_root = repo_root_path or repo_root()
    expected_base = repository_root / ".agents" / "skills"
    resolved_output = output_dir.resolve()
    resolved_expected = expected_base.resolve()
    try:
        resolved_output.relative_to(resolved_expected)
    except ValueError as exc:
        raise ValueError(
            f"Output directory {output_dir} is outside the expected repository subtree {expected_base}. "
            f"Aborting write to avoid deleting arbitrary paths."
        ) from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    writes: list[dict[str, str]] = []
    for root in report["roots"]:
        target_dir = output_dir / root["name"]
        if target_dir.exists() or target_dir.is_symlink():
            if target_dir.is_symlink() or target_dir.is_file():
                target_dir.unlink()
            elif target_dir.is_dir():
                shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "SKILL.md"
        target.write_text(root["content"], encoding="utf-8")
        writes.append({"path": rel(target), "action": "write"})
    return writes


def public_report(report: dict[str, Any]) -> dict[str, Any]:
    """
    Return a copy of the report with the `content` field removed from each root entry.
    
    Parameters:
        report (dict[str, Any]): Report dictionary produced by build_roots, containing a "roots" list of per-root dictionaries.
    
    Returns:
        dict[str, Any]: A shallow copy of `report` where each item in `report["roots"]` has had its `"content"` key omitted.
    """
    return {
        **report,
        "roots": [
            {key: value for key, value in root.items() if key != "content"}
            for root in report["roots"]
        ],
    }


def main() -> int:
    """
    Run the CLI to build rooted skill-set SKILL.md files and emit a report.
    
    Builds a report for all root skill sets, optionally writes generated SKILL.md files to the specified output directory when `--write` is provided (skipped if `--dry-run`), and prints either a JSON payload (`--json`) or a human-readable summary with violation lines. If `--write` is requested and the report contains violations, the write is aborted; when `--json` is set the public report is printed before aborting.
    
    Returns:
        int: Process exit code: `0` when the report status is "pass", `1` otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_roots(args.output_dir)
    writes: list[dict[str, str]] = []
    if args.write and not args.dry_run:
        if report["status"] != "pass":
            if args.json:
                print(json.dumps(public_report(report), indent=2, sort_keys=True))
            return 1
        writes = write_roots(report, args.output_dir)
    payload = {**public_report(report), "writes": writes, "dry_run": bool(args.dry_run or not args.write)}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"root skill sets: {payload['status']} ({payload['root_count']} roots)")
        for violation in payload["violations"]:
            print(f"- {violation['code']}: {violation.get('name')}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
