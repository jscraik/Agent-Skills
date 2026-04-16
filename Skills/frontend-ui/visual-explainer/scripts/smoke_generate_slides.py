#!/usr/bin/env python3
"""Smoke test for slide-deck generation with section-coverage checks."""

from __future__ import annotations

import argparse
import json
import re
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Outline:
    title: str
    sections: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a smoke-test slide deck from markdown and verify all sections are covered."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Source markdown file to convert into slide skeleton.",
    )
    parser.add_argument(
        "--output-dir",
        default="~/.agent/diagrams",
        help="Output directory for generated HTML (default: ~/.agent/diagrams).",
    )
    parser.add_argument(
        "--open",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Open the generated file in the browser (default: true).",
    )
    return parser.parse_args()


def extract_outline(path: Path) -> Outline:
    text = path.read_text(encoding="utf-8", errors="replace")
    title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem)
    sections = [
        m.group(1).strip()
        for m in re.finditer(r"^##\s+(.+)$", text, flags=re.MULTILINE)
        if m.group(1).strip().lower() != "table of contents"
    ]
    if not sections:
        raise ValueError("No level-2 sections found in source markdown.")
    return Outline(title=title, sections=sections)


def build_html(outline: Outline, source: Path) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    slides = [
        f"""
<section class="slide hero">
  <div class="badge">Smoke Test · generate-slides</div>
  <h1>{outline.title}</h1>
  <p class="sub">Source: <code>{source}</code></p>
  <p class="sub">Generated: {generated_at}</p>
</section>
""",
        """
<section class="slide">
  <h2>Coverage map</h2>
  <p>All source sections are included below.</p>
  <ol class="cols">
"""
        + "\n".join(f"    <li>{section}</li>" for section in outline.sections)
        + """
  </ol>
</section>
""",
    ]

    for section in outline.sections:
        slides.append(
            f"""
<section class="slide">
  <h2>{section}</h2>
  <p class="sub">Section preserved from source for slide-mode coverage fidelity.</p>
</section>
"""
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{outline.title} · Slides Smoke Test</title>
<style>
:root {{
  --bg: #0b1020;
  --surface: #111833;
  --surface2: #1a2550;
  --text: #e8ecff;
  --muted: #aab6e6;
  --accent: #66d9ef;
  --border: rgba(255,255,255,0.12);
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: Inter, system-ui, -apple-system, sans-serif; }}
.slide {{ min-height: 100dvh; padding: 56px; border-bottom: 1px solid var(--border); display: flex; flex-direction: column; justify-content: center; gap: 14px; background: radial-gradient(circle at 85% 15%, rgba(102,217,239,0.15), transparent 42%), var(--surface); }}
.hero {{ background: radial-gradient(circle at 15% 20%, rgba(245,158,11,0.20), transparent 44%), radial-gradient(circle at 82% 18%, rgba(102,217,239,0.16), transparent 38%), var(--surface2); }}
h1 {{ font-size: clamp(32px, 5vw, 58px); line-height: 1.05; margin: 0; max-width: 16ch; }}
h2 {{ font-size: clamp(28px, 4vw, 44px); line-height: 1.1; margin: 0; }}
.sub {{ color: var(--muted); font-size: 18px; margin: 0; }}
.badge {{ display: inline-block; width: fit-content; padding: 8px 12px; border-radius: 999px; border: 1px solid var(--border); background: rgba(255,255,255,0.06); color: var(--accent); font-weight: 700; letter-spacing: 0.02em; }}
ol {{ margin: 0; padding-left: 24px; font-size: 20px; line-height: 1.45; }}
ol.cols {{ columns: 2; column-gap: 40px; }}
li {{ margin: 6px 0; break-inside: avoid; }}
code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: var(--accent); }}
@media (max-width: 900px) {{
  .slide {{ padding: 40px 24px; }}
  ol.cols {{ columns: 1; }}
}}
</style>
</head>
<body>
{''.join(slides)}
</body>
</html>
"""


def verify_coverage(sections: list[str], html: str) -> tuple[int, list[str]]:
    missing = [section for section in sections if section not in html]
    return len(sections) - len(missing), missing


def maybe_open(path: Path, should_open: bool) -> bool:
    if not should_open:
        return False
    return bool(webbrowser.open(path.resolve().as_uri()))


def main() -> int:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    outline = extract_outline(source)
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = output_dir / f"{source.stem}-slides-smoke-{timestamp}.html"

    html = build_html(outline, source)
    output_path.write_text(html, encoding="utf-8")

    covered, missing = verify_coverage(outline.sections, html)
    opened = maybe_open(output_path, args.open)

    summary = {
        "source": str(source),
        "output": str(output_path),
        "sections_total": len(outline.sections),
        "sections_covered": covered,
        "missing_sections": missing,
        "slides": len(re.findall(r'<section class="slide', html)),
        "opened": opened,
    }
    print(json.dumps(summary, indent=2))

    if missing:
        return 1
    if args.open and not opened:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
