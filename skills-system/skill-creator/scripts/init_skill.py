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
from datetime import date
from pathlib import Path

from generate_openai_yaml import write_openai_yaml

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 220
MIN_DESCRIPTION_LENGTH = 35
ALLOWED_RESOURCES = {"scripts", "references", "assets"}
DESCRIPTION_TASK_VERBS = {
    "audit",
    "auditing",
    "build",
    "building",
    "create",
    "creating",
    "debug",
    "debugging",
    "design",
    "designing",
    "diagnose",
    "diagnosing",
    "evaluate",
    "evaluating",
    "fix",
    "fixing",
    "generate",
    "generating",
    "harden",
    "hardening",
    "install",
    "installing",
    "migrate",
    "migrating",
    "needs",
    "package",
    "packaging",
    "plan",
    "planning",
    "publish",
    "publishing",
    "refactor",
    "refactoring",
    "repair",
    "repairing",
    "review",
    "reviewing",
    "route",
    "routing",
    "scaffold",
    "scaffolding",
    "test",
    "testing",
    "triage",
    "triaging",
    "update",
    "updating",
    "validate",
    "validating",
}
DESCRIPTION_WAFFLE_TERMS = {
    "best-in-class",
    "comprehensive",
    "cutting-edge",
    "designed to",
    "easy-to-use",
    "empower",
    "game-changing",
    "guide for",
    "helps",
    "innovative",
    "leverage",
    "powerful",
    "robust",
    "seamless",
    "specialized knowledge",
    "state-of-the-art",
    "streamline",
    "this skill",
    "world-class",
}

from init_skill_templates import (
    CONTRACT_TEMPLATE,
    EVALS_TEMPLATE,
    EXAMPLE_ASSET,
    EXAMPLE_REFERENCE,
    EXAMPLE_SCRIPT,
    SKILL_TEMPLATE,
    SOURCE_CONTEXT_TEMPLATE,
    TASK_PROFILE_TEMPLATE,
)

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


def validate_description(description):
    """Validate frontmatter description for immediate agent routing."""
    description = description.strip()
    if not description:
        return "Description is required."
    if len(description) < MIN_DESCRIPTION_LENGTH:
        return (
            f"Description is too short ({len(description)} characters). "
            f"Minimum is {MIN_DESCRIPTION_LENGTH} characters."
        )
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return (
            f"Description is too long ({len(description)} characters). "
            f"Maximum is {MAX_DESCRIPTION_LENGTH} characters."
        )
    if "\n" in description or "\r" in description:
        return "Description must be a single line."
    if not description.startswith("Use when "):
        return 'Description must start with "Use when " and state the triggering task.'
    lowered = description.lower()
    for term in sorted(DESCRIPTION_WAFFLE_TERMS):
        if term in lowered:
            return f"Description contains waffle term '{term}'. Use concrete trigger language."
    words = set(re.findall(r"[a-z][a-z-]*", lowered))
    if not words.intersection(DESCRIPTION_TASK_VERBS):
        return "Description must include a concrete task verb such as create, audit, fix, test, or validate."
    sentence_marks = sum(description.count(mark) for mark in ".!?")
    if sentence_marks > 1:
        return "Description must be one concise trigger sentence."
    if "<" in description or ">" in description:
        return "Description cannot contain angle brackets (< or >)."
    return None


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


def create_sdk_contract_files(skill_dir, skill_name, skill_title, last_reviewed):
    """Create the SDK-required progressive-disclosure files."""
    references_dir = skill_dir / "references"
    references_dir.mkdir(exist_ok=True)
    required_files = {
        "contract.yaml": CONTRACT_TEMPLATE.replace("__SKILL_NAME__", skill_name),
        "evals.yaml": EVALS_TEMPLATE.replace("__SKILL_NAME__", skill_name),
        "task-profile.json": (
            TASK_PROFILE_TEMPLATE.replace("__SKILL_NAME__", skill_name)
            .replace("__SKILL_TITLE__", skill_title)
            .replace("__LAST_REVIEWED__", last_reviewed)
        ),
        "source-context.yaml": SOURCE_CONTEXT_TEMPLATE.replace("__SKILL_NAME__", skill_name),
    }
    for filename, content in required_files.items():
        path = references_dir / filename
        if path.exists():
            continue
        path.write_text(content, encoding="utf-8")
        print(f"[OK] Created references/{filename}")


def init_skill(
    skill_name,
    path,
    resources,
    include_examples,
    interface_overrides,
    description,
    owner,
    review_cadence,
):
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
    last_reviewed = date.today().isoformat()
    skill_content = SKILL_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title,
        description=description,
        owner=owner,
        review_cadence=review_cadence,
        last_reviewed=last_reviewed,
    )

    skill_md_path = skill_dir / "SKILL.md"
    try:
        skill_md_path.write_text(skill_content, encoding="utf-8")
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

    # Create SDK package contract files
    try:
        create_sdk_contract_files(skill_dir, skill_name, skill_title, last_reviewed)
    except Exception as e:
        print(f"[ERROR] Error creating SDK contract files: {e}")
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
    print("1. Review SKILL.md and tighten the workflow for the real use case")
    if resources:
        if include_examples:
            print("2. Customize or delete the example files in scripts/, references/, and assets/")
        else:
            print("2. Add resources to scripts/, references/, and assets/ as needed")
    else:
        print("2. Create resource directories only if needed (scripts/, references/, assets/)")
    print("3. Review references/contract.yaml, references/evals.yaml, and references/task-profile.json")
    print("4. Update agents/openai.yaml if the UI metadata should differ")
    print("5. Run quick_validate.py, generate_openai_yaml.py, and the repo ask eval wrapper")
    print(
        "6. Forward-test complex skills with realistic user requests to ensure they work as intended"
    )

    return skill_dir


def main():
    parser = argparse.ArgumentParser(
        description="Create a new skill directory with a SKILL.md template.",
    )
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Output directory for the skill")
    parser.add_argument(
        "--description",
        required=True,
        help='Concise trigger sentence starting with "Use when " for SKILL.md frontmatter',
    )
    parser.add_argument(
        "--owner",
        required=True,
        help="Responsible owner for lifecycle metadata",
    )
    parser.add_argument(
        "--review-cadence",
        default="quarterly",
        help="Lifecycle review cadence, for example monthly or quarterly",
    )
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

    description = args.description.strip()
    description_error = validate_description(description)
    if description_error:
        print(f"[ERROR] Invalid --description: {description_error}")
        print(
            '   Example: --description "Use when a repo needs skill-package validation, eval coverage, or release-readiness evidence."'
        )
        sys.exit(1)

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

    result = init_skill(
        skill_name,
        path,
        resources,
        args.examples,
        args.interface,
        description,
        args.owner,
        args.review_cadence,
    )

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
