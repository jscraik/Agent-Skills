#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path> [--resources scripts,references,assets] [--examples] [--interface key=value]

Examples:
    init_skill.py my-new-skill --path skills/public
    init_skill.py my-new-skill --path skills/public --resources scripts,references
    init_skill.py my-api-helper --path skills/private --resources scripts --examples
    init_skill.py custom-skill --path /custom/location
    init_skill.py my-skill --path skills/public --interface short_description="Short UI label"
"""

import argparse
import re
import sys
from pathlib import Path

from generate_openai_yaml import write_openai_yaml

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES = {"scripts", "references", "assets"}

SKILL_TEMPLATE = """---
name: {skill_name}
description: "Use when a request maps directly to the {skill_name} workflow and needs deterministic, evidence-backed outputs."
---

# {skill_title}

## Overview

This skill provides a focused execution path for {skill_title} tasks with clear inputs, explicit outputs, and validation-first delivery.

## When to use

- Trigger when the user asks for {skill_title}-specific work with concrete artifacts.
- Route elsewhere when another skill has a tighter contract for the request.

## Inputs

- User objective and success criteria.
- Required files, paths, or repository context.
- Constraints (time, safety, tooling, and validation requirements).

## Workflow

1. Confirm scope and gather the minimum context required to proceed safely.
2. Run the narrowest proof or probe first.
3. Execute the implementation path with deterministic commands.
4. Validate outputs and summarize evidence.

## Deliverables

- Concrete output artifacts with exact paths.
- Commands executed and validation results.
- Any blockers, root cause, and next safest action.

## Validation

- Run the smallest relevant checks first, then broaden only as needed.
- Stop at first failing gate and report the failure before continuing.

## Failure mode

- If required context is missing or unsafe actions are requested, pause and ask one targeted clarification.
- If tooling fails, provide a concrete fallback command path.

## Gotchas

- Avoid broad edits before proving the smallest path works.
- Keep outputs deterministic and file-path explicit.

## Resources

- `scripts/`: executable helpers for repeatable operations.
- `references/`: detailed docs loaded when needed.
- `assets/`: templates and files used in produced outputs.

## Examples

- Triggering prompt: "Run {skill_name} on this repo and provide validated outputs."
- Non-triggering prompt: "Give me unrelated brainstorming ideas without execution."

"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example helper script for {skill_name}

This helper validates inputs and prints a deterministic execution summary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run {skill_name} helper")
    parser.add_argument("--input", default="", help="Optional input path")
    parser.add_argument("--output", default="./artifacts/{skill_name}-summary.json", help="Output summary path")
    parser.add_argument("--dry-run", action="store_true", help="Print intended actions without writing files")
    return parser.parse_args()


def main():
    args = parse_args()
    output_path = Path(args.output).expanduser()
    payload = {{
        "skill": "{skill_name}",
        "input": args.input or None,
        "mode": "dry-run" if args.dry_run else "execute",
        "status": "ok",
    }}
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")
    print(f"Wrote summary to {{output_path}}")

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

Use this file for durable domain context that is too large for `SKILL.md`.

## Recommended Sections

- Scope and non-scope
- Overview
- Invariants and safety constraints
- Step-by-step operational workflow
- Validation checklist
- Troubleshooting
- Links to related docs/scripts
"""

EXAMPLE_ASSET = """# Example Asset File

Use this location for templates or files consumed by generated outputs.

## Asset Rules

- Keep assets versioned and small enough for repo policy.
- Do not store secrets, API keys, or personal data.
- Reference assets from `SKILL.md` using relative paths.
"""


def normalize_skill_name(skill_name):
    """Normalize a skill name to lowercase hyphen-case."""
    normalized = skill_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def parse_resources(raw_resources):
    if not raw_resources:
        return []
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_RESOURCES))
        print(f"[ERROR] Unknown resource type(s): {', '.join(invalid)}")
        print(f"   Allowed: {allowed}")
        sys.exit(1)
    deduped = []
    seen = set()
    for resource in resources:
        if resource not in seen:
            deduped.append(resource)
            seen.add(resource)
    return deduped


def create_resource_dirs(skill_dir, skill_name, skill_title, resources, include_examples):
    for resource in resources:
        resource_dir = skill_dir / resource
        resource_dir.mkdir(exist_ok=True)
        if resource == "scripts":
            if include_examples:
                example_script = resource_dir / "example.py"
                example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
                example_script.chmod(0o755)
                print("[OK] Created scripts/example.py")
            else:
                print("[OK] Created scripts/")
        elif resource == "references":
            if include_examples:
                example_reference = resource_dir / "api_reference.md"
                example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
                print("[OK] Created references/api_reference.md")
            else:
                print("[OK] Created references/")
        elif resource == "assets":
            if include_examples:
                example_asset = resource_dir / "example_asset.txt"
                example_asset.write_text(EXAMPLE_ASSET)
                print("[OK] Created assets/example_asset.txt")
            else:
                print("[OK] Created assets/")


def init_skill(skill_name, path, resources, include_examples, interface_overrides):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created
        resources: Resource directories to create
        include_examples: Whether to create example files in resource directories

    Returns:
        Path to created skill directory, or None if error
    """
    # Determine skill directory path
    skill_dir = Path(path).resolve() / skill_name

    # Check if directory already exists
    if skill_dir.exists():
        print(f"[ERROR] Skill directory already exists: {skill_dir}")
        return None

    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"[OK] Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"[ERROR] Error creating directory: {e}")
        return None

    # Create SKILL.md from template
    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)

    skill_md_path = skill_dir / "SKILL.md"
    try:
        skill_md_path.write_text(skill_content)
        print("[OK] Created SKILL.md")
    except Exception as e:
        print(f"[ERROR] Error creating SKILL.md: {e}")
        return None

    # Create agents/openai.yaml
    try:
        result = write_openai_yaml(skill_dir, skill_name, interface_overrides)
        if not result:
            return None
    except Exception as e:
        print(f"[ERROR] Error creating agents/openai.yaml: {e}")
        return None

    # Create resource directories if requested
    if resources:
        try:
            create_resource_dirs(skill_dir, skill_name, skill_title, resources, include_examples)
        except Exception as e:
            print(f"[ERROR] Error creating resource directories: {e}")
            return None

    # Print next steps
    print(f"\n[OK] Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Refine SKILL.md with your exact trigger boundaries, workflow, and validation gates")
    if resources:
        if include_examples:
            print("2. Customize or delete the example files in scripts/, references/, and assets/")
        else:
            print("2. Add resources to scripts/, references/, and assets/ as needed")
    else:
        print("2. Create resource directories only if needed (scripts/, references/, assets/)")
    print("3. Update agents/openai.yaml if the UI metadata should differ")
    print("4. Run the validator when ready to check the skill structure")
    print(
        "5. Forward-test complex skills with realistic user requests to ensure they work as intended"
    )

    return skill_dir


def main():
    parser = argparse.ArgumentParser(
        description="Create a new skill directory with a SKILL.md template.",
    )
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Output directory for the skill")
    parser.add_argument(
        "--resources",
        default="",
        help="Comma-separated list: scripts,references,assets",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Create example files inside the selected resource directories",
    )
    parser.add_argument(
        "--interface",
        action="append",
        default=[],
        help="Interface override in key=value format (repeatable)",
    )
    args = parser.parse_args()

    raw_skill_name = args.skill_name
    skill_name = normalize_skill_name(raw_skill_name)
    if not skill_name:
        print("[ERROR] Skill name must include at least one letter or digit.")
        sys.exit(1)
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        print(
            f"[ERROR] Skill name '{skill_name}' is too long ({len(skill_name)} characters). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH} characters."
        )
        sys.exit(1)
    if skill_name != raw_skill_name:
        print(f"Note: Normalized skill name from '{raw_skill_name}' to '{skill_name}'.")

    resources = parse_resources(args.resources)
    if args.examples and not resources:
        print("[ERROR] --examples requires --resources to be set.")
        sys.exit(1)

    path = args.path

    print(f"Initializing skill: {skill_name}")
    print(f"   Location: {path}")
    if resources:
        print(f"   Resources: {', '.join(resources)}")
        if args.examples:
            print("   Examples: enabled")
    else:
        print("   Resources: none (create as needed)")
    print()

    result = init_skill(skill_name, path, resources, args.examples, args.interface)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
