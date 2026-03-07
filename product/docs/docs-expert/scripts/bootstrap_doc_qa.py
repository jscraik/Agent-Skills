#!/usr/bin/env python3
"""Install docs QA baseline files in a target repository.

This script bootstraps missing lint and brand baseline files so docs QA checks
can run instead of being skipped.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MARKDOWNLINT_CANDIDATES = (
    ".markdownlint-cli2.yaml",
    ".markdownlint-cli2.yml",
    ".markdownlint.yaml",
    ".markdownlint.yml",
    ".markdownlint.jsonc",
)

MARKDOWNLINT_BASELINE = """config:
  default: true
  MD013: false
  MD033: false

globs:
  - "**/*.md"

ignores:
  - ".git/**"
  - "node_modules/**"
  - "dist/**"
  - "build/**"
"""

VALE_INI_BASELINE = """StylesPath = .vale/styles
MinAlertLevel = suggestion
Vocab = Docs

[*.md]
BasedOnStyles = Docs
"""

VALE_STYLE_BASELINE = """extends: existence
message: "Avoid punctuation in headings unless required."
level: suggestion
scope: heading
nonword: true
tokens:
  - '[.!?]$'
"""

BRAND_README_BASELINE = """# Brand Assets

This folder stores repository brand assets and usage notes.

## What to include
- Official logo/mark assets approved by this repository's brand owner
- Signature usage rules for README/docs (if applicable)
- Accessibility notes for alt text and contrast

## Notes
- Do not import fallback brand assets when official brand assets already exist.
"""

BRAND_CONSTRAINTS_BASELINE = """# Branding Constraints

- Source of truth order:
  1) repository-specific brand guidelines
  2) org-level brand docs
  3) docs-expert fallback profile (only if approved)

- Use the documentation signature in root README only when branding applies.
- Do not use watermark overlays in technical docs.
- Keep signature assets in this directory.
"""

README_SIGNATURE_SNIPPET = """---

<img
  src="./brand/brand-mark.webp"
  srcset="./brand/brand-mark.webp 1x, ./brand/brand-mark@2x.webp 2x"
  alt="brAInwav"
  height="28"
  align="left"
/>

<br clear="left" />

**brAInwav**
_from demo to duty_
"""


def write_text(
    path: Path,
    content: str,
    apply: bool,
    force: bool,
    summary: dict[str, list[str]],
) -> None:
    if path.exists() and not force:
        summary["existing"].append(str(path))
        return
    if not apply:
        summary["planned"].append(str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    summary["created"].append(str(path))


def copy_asset(
    src: Path,
    dst: Path,
    apply: bool,
    force: bool,
    summary: dict[str, list[str]],
) -> None:
    if dst.exists() and not force:
        summary["existing"].append(str(dst))
        return
    if not apply:
        summary["planned"].append(str(dst))
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    summary["created"].append(str(dst))


def ensure_lint_baseline(
    repo_root: Path,
    apply: bool,
    force: bool,
    summary: dict[str, list[str]],
) -> None:
    has_markdownlint = any((repo_root / candidate).exists() for candidate in MARKDOWNLINT_CANDIDATES)
    if not has_markdownlint:
        write_text(repo_root / ".markdownlint-cli2.yaml", MARKDOWNLINT_BASELINE, apply, force, summary)

    write_text(repo_root / ".vale.ini", VALE_INI_BASELINE, apply, force, summary)
    write_text(repo_root / ".vale/styles/Docs/HeadingPunctuation.yml", VALE_STYLE_BASELINE, apply, force, summary)


def ensure_brand_baseline(
    repo_root: Path,
    apply: bool,
    force: bool,
    insert_signature: bool,
    brand_profile: str,
    summary: dict[str, list[str]],
) -> None:
    brand_dir = repo_root / "brand"

    write_text(brand_dir / "README.md", BRAND_README_BASELINE, apply, force, summary)
    write_text(brand_dir / "constraints.md", BRAND_CONSTRAINTS_BASELINE, apply, force, summary)

    if brand_profile == "none":
        summary["warnings"].append("Brand bootstrap skipped (--brand-profile none)")
        return

    if brand_profile == "repo":
        if insert_signature:
            summary["warnings"].append(
                "Skipped README signature insertion in repo profile: signature content must come from official repo brand guidance."
            )
        return

    skill_root = Path(__file__).resolve().parent.parent
    assets_dir = skill_root / "assets/brand"
    for filename in (
        "brand-mark.webp",
        "brand-mark@2x.webp",
        "brand-mark.png",
        "brand-mark@2x.png",
    ):
        src = assets_dir / filename
        dst = brand_dir / filename
        if not src.exists():
            summary["warnings"].append(f"Missing skill asset: {src}")
            continue
        copy_asset(src, dst, apply, force, summary)

    if not insert_signature:
        return

    readme = repo_root / "README.md"
    if not readme.exists():
        summary["warnings"].append("README.md not found; skipped signature insertion")
        return

    content = readme.read_text(encoding="utf-8")
    if "brand/brand-mark.webp" in content:
        summary["existing"].append(str(readme) + " (signature)")
        return

    if not apply:
        summary["planned"].append(str(readme) + " (append signature)")
        return

    readme.write_text(content.rstrip() + "\n\n" + README_SIGNATURE_SNIPPET + "\n", encoding="utf-8")
    summary["created"].append(str(readme) + " (signature appended)")


def print_section(label: str, values: list[str]) -> None:
    if not values:
        return
    print(f"- {label}:")
    for value in values:
        print(f"  - {value}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install missing docs QA baseline files in a repository.",
    )
    parser.add_argument("--repo", default=".", help="Target repository root (default: current directory)")
    parser.add_argument("--apply", action="store_true", help="Write changes (default is dry-run)")
    parser.add_argument("--force", action="store_true", help="Overwrite baseline files when they already exist")
    parser.add_argument("--skip-lint", action="store_true", help="Do not install lint baselines")
    parser.add_argument("--skip-brand", action="store_true", help="Do not install brand baselines")
    parser.add_argument(
        "--brand-profile",
        choices=("repo", "docs-expert", "none"),
        default="repo",
        help="Brand baseline mode: repo (default, neutral), docs-expert (fallback assets), or none.",
    )
    parser.add_argument(
        "--insert-readme-signature",
        action="store_true",
        help="Append docs signature snippet to README.md when missing",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    summary: dict[str, list[str]] = {
        "created": [],
        "planned": [],
        "existing": [],
        "warnings": [],
    }

    if not repo_root.exists() or not repo_root.is_dir():
        print(f"ERROR: Repo path does not exist or is not a directory: {repo_root}")
        return 1

    if not args.skip_lint:
        ensure_lint_baseline(repo_root, args.apply, args.force, summary)

    if not args.skip_brand:
        ensure_brand_baseline(
            repo_root,
            args.apply,
            args.force,
            args.insert_readme_signature,
            args.brand_profile,
            summary,
        )

    print("Docs QA bootstrap")
    print(f"- Repo: {repo_root}")
    print(f"- Mode: {'apply' if args.apply else 'dry-run'}")
    print(f"- Brand profile: {args.brand_profile}")
    print_section("Planned", summary["planned"])
    print_section("Created", summary["created"])
    print_section("Existing", summary["existing"])
    print_section("Warnings", summary["warnings"])

    if not summary["planned"] and not summary["created"]:
        print("- Status: nothing to do")
    elif args.apply:
        print("- Status: applied")
    else:
        print("- Status: dry-run complete")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
