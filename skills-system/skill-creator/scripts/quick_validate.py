#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import re
import sys
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
TOP_LEVEL_LIST_KEYS = {"allowed-tools"}


class FrontmatterError(ValueError):
    """Raised when SKILL.md frontmatter cannot be parsed by the quick validator."""


def _parse_scalar(raw_value):
    value = raw_value.strip()
    if not value:
        return {}
    if value[0:1] in {'"', "'"}:
        quote = value[0]
        if not value.endswith(quote) or len(value) == 1:
            raise FrontmatterError("unterminated quoted scalar")
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        items = value[1:-1].strip()
        if not items:
            return []
        return [item.strip().strip('"').strip("'") for item in items.split(",")]
    if value in {"true", "false"}:
        return value == "true"
    if value in {"True", "False"}:
        return value == "True"
    return value


def _parse_frontmatter(frontmatter_text):
    """Parse the small YAML subset allowed in SKILL.md frontmatter.

    The quick validator only needs top-level keys, scalar `name` and
    `description`, and optional nested/list metadata. Keeping this parser local
    avoids making basic skill validation depend on PyYAML in the ambient
    `python3` environment.
    """
    fields = {}
    current_map = None
    current_list_key = None

    for line_number, line in enumerate(frontmatter_text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" in line:
            raise FrontmatterError(f"line {line_number}: tabs are not allowed in YAML frontmatter")

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if stripped.startswith("- "):
            item = _parse_scalar(stripped[2:])
            if current_map and current_list_key:
                target = fields.setdefault(current_map, {})
                if not isinstance(target, dict):
                    raise FrontmatterError(f"line {line_number}: list item has no mapping parent")
                values = target.setdefault(current_list_key, [])
                if not isinstance(values, list):
                    raise FrontmatterError(f"line {line_number}: list item parent is not a list")
                values.append(item)
                continue
            if current_map and isinstance(fields.get(current_map), list):
                fields[current_map].append(item)
                continue
            raise FrontmatterError(f"line {line_number}: list item has no list parent")

        if ":" not in line:
            raise FrontmatterError(f"line {line_number}: expected 'key: value'")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise FrontmatterError(f"line {line_number}: empty key")

        if indent:
            if not current_map:
                raise FrontmatterError(f"line {line_number}: nested key has no parent")
            parent = fields.setdefault(current_map, {})
            if not isinstance(parent, dict):
                raise FrontmatterError(f"line {line_number}: nested parent is not a mapping")
            value = raw_value.strip()
            if value:
                parent[key] = _parse_scalar(value)
                current_list_key = None
            else:
                parent[key] = []
                current_list_key = key
            continue

        current_map = None
        current_list_key = None
        value = raw_value.strip()
        if value:
            fields[key] = _parse_scalar(value)
        else:
            fields[key] = [] if key in TOP_LEVEL_LIST_KEYS else {}
            current_map = key

    return fields


def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    try:
        frontmatter = _parse_frontmatter(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except FrontmatterError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    allowed_properties = {"name", "description", "license", "allowed-tools", "metadata"}

    unexpected_keys = set(frontmatter.keys()) - allowed_properties
    if unexpected_keys:
        allowed = ", ".join(sorted(allowed_properties))
        unexpected = ", ".join(sorted(unexpected_keys))
        return (
            False,
            f"Unexpected key(s) in SKILL.md frontmatter: {unexpected}. Allowed properties are: {allowed}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return (
                False,
                f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)",
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return (
                False,
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
            )
        if len(name) > MAX_SKILL_NAME_LENGTH:
            return (
                False,
                f"Name is too long ({len(name)} characters). "
                f"Maximum is {MAX_SKILL_NAME_LENGTH} characters.",
            )

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        if "<" in description or ">" in description:
            return False, "Description cannot contain angle brackets (< or >)"
        if len(description) > 1024:
            return (
                False,
                f"Description is too long ({len(description)} characters). Maximum is 1024 characters.",
            )

    return True, "Skill is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
