#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

TARGETS = ("portable", "codex", "claude")

SPEC_KEYS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "compatibility",
    "metadata",
}

CLAUDE_KEYS = {
    "model",
    "context",
    "hooks",
    "user-invocable",
    "disable-model-invocation",
}

TARGET_LIMITS = {
    "portable": {"name": 64, "description": 500},
    "codex": {"name": 100, "description": 500},
    "claude": {"name": 64, "description": 1024},
}


def _target_keys(target: str) -> set[str] | None:
    if target == "portable":
        return set(SPEC_KEYS)
    if target == "claude":
        return set(SPEC_KEYS) | set(CLAUDE_KEYS)
    return None


def validate_skill(skill_path: str, *, target: str = "portable"):
    """Basic validation of a skill"""
    warnings: list[str] = []
    skill_path_obj = Path(skill_path)

    if target not in TARGETS:
        return False, f"Unknown target: {target}", warnings

    skill_md = skill_path_obj / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found", warnings

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found", warnings

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format", warnings

    frontmatter_text = match.group(1)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary", warnings
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}", warnings

    allowed_properties = _target_keys(target)
    if allowed_properties is not None:
        unexpected_keys = set(frontmatter.keys()) - allowed_properties
        if unexpected_keys:
            allowed = ", ".join(sorted(allowed_properties))
            unexpected = ", ".join(sorted(unexpected_keys))
            if target == "portable":
                return (
                    False,
                    f"Unexpected key(s) in SKILL.md frontmatter: {unexpected}. Allowed properties are: {allowed}",
                    warnings,
                )
            warnings.append(
                f"Unexpected key(s) in SKILL.md frontmatter: {unexpected}. Expected keys are: {allowed}"
            )
    else:
        unexpected_keys = set(frontmatter.keys()) - SPEC_KEYS
        if unexpected_keys:
            unexpected = ", ".join(sorted(unexpected_keys))
            warnings.append(
                f"Non-standard frontmatter keys detected: {unexpected}. Codex ignores extra keys, "
                "but portable targets may not."
            )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter", warnings
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter", warnings

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}", warnings
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return (
                False,
                f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)",
                warnings,
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return (
                False,
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
                warnings,
            )
        max_name_len = TARGET_LIMITS[target]["name"]
        if len(name) > max_name_len:
            return (
                False,
                f"Name is too long ({len(name)} characters). Maximum is {max_name_len} characters.",
                warnings,
            )

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}", warnings
    description = description.strip()
    if description:
        if "<" in description or ">" in description:
            return False, "Description cannot contain angle brackets (< or >)", warnings
        max_desc_len = TARGET_LIMITS[target]["description"]
        if len(description) > max_desc_len:
            return (
                False,
                f"Description is too long ({len(description)} characters). Maximum is {max_desc_len} characters.",
                warnings,
            )

    return True, "Skill is valid!", warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Quick validation for skills.")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument(
        "--target",
        choices=TARGETS,
        default="portable",
        help="Validation target (portable, codex, claude)",
    )
    args = parser.parse_args()

    valid, message, warnings = validate_skill(args.skill_path, target=args.target)
    for warning in warnings:
        print(f"[WARN] {warning}")
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
