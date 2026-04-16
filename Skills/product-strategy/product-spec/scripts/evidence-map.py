#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from typing import List, Tuple

HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+(.*)\s*$")
EVIDENCE_LINE_RE = re.compile(r"(?im)^\s*Evidence:\s+|^\s*Evidence gap:\s+")


def split_blocks(text: str) -> List[Tuple[int, List[str]]]:
    blocks: List[Tuple[int, List[str]]] = []
    lines = text.split("\n")
    buf: List[str] = []
    start_line = 1
    in_code = False
    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and line.strip() == "":
            if buf:
                blocks.append((start_line, buf))
                buf = []
            start_line = i + 1
            continue
        if not buf:
            start_line = i
        buf.append(line)
    if buf:
        blocks.append((start_line, buf))
    return blocks


def is_substantive_block(lines: List[str]) -> bool:
    text = "\n".join(lines).strip()
    if not text:
        return False
    if text.startswith("#"):
        return False
    if re.match(r"^\|.*\|$", text):
        return False
    if all(line.strip().startswith("|") or line.strip().startswith("-|") for line in text.split("\n")):
        return False
    return True


def append_missing_evidence(text: str, gap_line: str) -> str:
    out_lines: List[str] = []
    for _, block in split_blocks(text):
        if not is_substantive_block(block):
            out_lines.extend(block)
            out_lines.append("")
            continue
        if not EVIDENCE_LINE_RE.search("\n".join(block)):
            block.append(gap_line)
        out_lines.extend(block)
        out_lines.append("")
    return "\n".join(out_lines).rstrip() + "\n"


def extract_heading_map(text: str) -> List[Tuple[int, str]]:
    headings: List[Tuple[int, str]] = []
    for m in HEADING_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        title = m.group(2).strip()
        headings.append((line, title))
    return headings


def nearest_heading(headings: List[Tuple[int, str]], line_no: int) -> str:
    current = "(no heading)"
    for line, title in headings:
        if line <= line_no:
            current = title
        else:
            break
    return current


def build_evidence_map(text: str) -> str:
    headings = extract_heading_map(text)
    rows: List[Tuple[str, str]] = []
    for line_no, block in split_blocks(text):
        joined = "\n".join(block)
        for m in re.finditer(r"(?im)^\s*Evidence:\s+(.+)$", joined):
            section = nearest_heading(headings, line_no)
            refs = [r.strip() for r in m.group(1).split(",") if r.strip()]
            for ref in refs:
                rows.append((section, ref))
    lines = ["| Section / Claim | Evidence | Confidence | Notes |", "|---|---|---|---|"]
    if not rows:
        lines.append("| (none) | (none) | Low | No evidence lines found. |")
        return "\n".join(lines)
    for section, ref in rows:
        lines.append(f"| {section} | {ref} | Medium | Auto-collected from Evidence lines. |")
    return "\n".join(lines)


def replace_section(text: str, heading: str, new_body: str) -> str:
    pattern = re.compile(rf"(?m)^(##\s+{re.escape(heading)}\s*)$")
    match = pattern.search(text)
    if not match:
        return text.rstrip() + f"\n\n## {heading}\n{new_body}\n"
    start = match.end()
    next_h2 = re.search(r"(?m)^##\s+", text[start:])
    end = start + next_h2.start() if next_h2 else len(text)
    return text[:start] + "\n" + new_body + text[end:]


def main() -> int:
    ap = argparse.ArgumentParser(description="Append missing Evidence lines and build an Evidence Map table.")
    ap.add_argument("--input", required=True, help="Input Markdown file")
    ap.add_argument("--in-place", action="store_true", help="Write changes back to the input file")
    ap.add_argument("--append-missing", action="store_true", help="Append Evidence gap lines to paragraphs missing evidence")
    ap.add_argument("--gap-line", default="Evidence gap: missing source", help="Line to append for missing evidence")
    ap.add_argument("--update-map", action="store_true", help="Replace or add the Evidence Map section")
    args = ap.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 1

    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

    if args.append_missing:
        text = append_missing_evidence(text, args.gap_line)

    if args.update_map:
        evidence_table = build_evidence_map(text)
        text = replace_section(text, "Evidence Map", evidence_table)

    if args.in_place:
        path.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
