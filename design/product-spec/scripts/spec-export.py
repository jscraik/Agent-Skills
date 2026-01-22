#!/usr/bin/env python3
import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Heading:
    level: int
    title: str
    start_idx: int
    end_idx: int


HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+(.*)\s*$")


def parse_headings(text: str) -> List[Heading]:
    headings: List[Heading] = []
    for m in HEADING_RE.finditer(text):
        hashes = m.group(1)
        title = m.group(2).strip()
        headings.append(Heading(level=len(hashes), title=title, start_idx=m.start(), end_idx=m.end()))
    return headings


def find_heading(headings: List[Heading], pattern: str) -> Optional[Heading]:
    for h in headings:
        if re.search(pattern, h.title, flags=re.IGNORECASE):
            return h
    return None


def section_text(text: str, headings: List[Heading], heading: Heading) -> str:
    start = heading.end_idx
    end = len(text)
    for h in headings:
        if h.start_idx <= heading.start_idx:
            continue
        if h.level <= heading.level:
            end = h.start_idx
            break
    return text[start:end]


def parse_inline_list(value: str) -> List[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [v.strip().strip("\"'") for v in inner.split(",") if v.strip()]
    if "," in value:
        return [v.strip().strip("\"'") for v in value.split(",") if v.strip()]
    if value:
        return [value.strip().strip("\"'")]
    return []


def parse_metadata_value(value: str) -> Dict[str, Any]:
    value = value.strip()
    if not value:
        return {}
    if value.startswith("{") and value.endswith("}"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}
    return {}


def parse_template_metadata(text: str) -> Dict[str, Any]:
    headings = parse_headings(text)
    h = find_heading(headings, r"\bTemplate Metadata\b")
    if not h:
        raise ValueError("Missing 'Template Metadata' section.")

    sec = section_text(text, headings, h)
    data: Dict[str, Any] = {
        "name": "",
        "description": "",
        "title_template": "",
        "acceptance_criteria": [],
        "priority": "medium",
        "variables": [],
        "metadata": {},
    }

    field_re = re.compile(r"(?im)^\s*-\s+\*\*(.+?):\*\*\s*(.*)$")
    current_field: Optional[str] = None
    for line in sec.splitlines():
        m = field_re.match(line)
        if m:
            field = m.group(1).strip().lower()
            value = m.group(2).strip()
            current_field = field
            if field == "name":
                data["name"] = value
            elif field == "description":
                data["description"] = value
            elif field == "title_template":
                data["title_template"] = value
            elif field == "acceptance_criteria":
                data["acceptance_criteria"] = []
            elif field == "priority":
                data["priority"] = value or "medium"
            elif field == "variables":
                data["variables"] = parse_inline_list(value)
            elif field == "metadata":
                data["metadata"] = parse_metadata_value(value)
            else:
                current_field = None
            continue

        if current_field == "acceptance_criteria":
            item = re.sub(r"^\s*[-*]\s*", "", line).strip()
            if item:
                data["acceptance_criteria"].append(item)

    return data


def validate_template_metadata(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not data.get("name"):
        errors.append("Template Metadata: 'name' is required.")
    if not data.get("description"):
        errors.append("Template Metadata: 'description' is required.")
    title_template = data.get("title_template", "")
    if not title_template:
        errors.append("Template Metadata: 'title_template' is required.")
    elif "{" not in title_template or "}" not in title_template:
        errors.append("Template Metadata: 'title_template' must include {variable} placeholders.")
    acceptance = data.get("acceptance_criteria", [])
    if not acceptance:
        errors.append("Template Metadata: 'acceptance_criteria' must include at least one item.")
    if "variables" not in data or data["variables"] is None:
        errors.append("Template Metadata: 'variables' must exist (can be empty).")
    if "metadata" not in data or data["metadata"] is None:
        errors.append("Template Metadata: 'metadata' must exist (can be empty).")
    if not data.get("priority"):
        errors.append("Template Metadata: 'priority' is required (default 'medium').")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Export Template Metadata from a spec to JSON.")
    ap.add_argument("file", help="Markdown spec file to parse")
    ap.add_argument("--out", help="Output JSON path (defaults to stdout)")
    ap.add_argument("--validate", action="store_true", help="Validate required fields and exit non-zero on failure")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    try:
        data = parse_template_metadata(text)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.validate:
        errors = validate_template_metadata(data)
        if errors:
            for e in errors:
                print(f"error: {e}", file=sys.stderr)
            return 1
        return 0

    output = json.dumps(data, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
        return 0

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
