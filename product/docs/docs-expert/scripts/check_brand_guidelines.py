#!/usr/bin/env python3
"""Audit brand-guideline compliance in a target repository.

Profiles:
- docs-expert (default): checks BrAInwav signature and required assets.
- repo: neutral checks for watermark misuse, optional custom signature/assets.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from typing import Any

DEFAULT_DOCS_EXPERT = {
    "brand_name": "brAInwav",
    "tagline": "from demo to duty",
    "signature_assets": ["brand/brand-mark.webp"],
    "required_assets": [
        "brand/brand-mark.webp",
        "brand/brand-mark@2x.webp",
    ],
    "allow_ascii": True,
    "require_signature": True,
}


def read_file(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def resolve(path: str, base: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(base, path))


def find_watermark_usage(text: str) -> list[str]:
    patterns = [
        r"!\[[^\]]*\]\([^\)]*watermark[^\)]*\)",
        r"<img[^>]+src=['\"][^'\"]*watermark[^'\"]*['\"]",
        r"(class|id)=['\"][^'\"]*watermark[^'\"]*['\"]",
    ]
    hits: list[str] = []
    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        hits.extend(matches)
    return hits


def parse_config(path: str) -> dict[str, Any]:
    config_path = os.path.abspath(path)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Brand config not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def check_signature(
    readme_text: str,
    brand_name: str | None,
    tagline: str | None,
    signature_assets: list[str],
    allow_ascii: bool,
) -> tuple[bool, str]:
    lowered = readme_text.lower()

    has_brand = True
    if brand_name:
        has_brand = brand_name.lower() in lowered

    has_tagline = True
    if tagline:
        has_tagline = tagline.lower() in lowered

    has_image = False
    if signature_assets:
        has_image = any(asset.lower() in lowered for asset in signature_assets)

    has_alt = True
    if brand_name:
        marker = brand_name.lower()
        has_alt = f'alt="{marker}"' in lowered or f"alt='{marker}'" in lowered

    if has_image and has_alt and has_brand and has_tagline:
        return True, "image"

    if allow_ascii and has_brand and has_tagline:
        return True, "ascii"

    return False, "missing"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit repository brand signature/assets and watermark rules.",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to repo root (default: current directory)",
    )
    parser.add_argument(
        "--readme",
        default=None,
        help="Override README path (default: <repo>/README.md)",
    )
    parser.add_argument(
        "--docs",
        action="append",
        default=[],
        help="Additional doc paths to scan for watermark usage (repeatable)",
    )
    parser.add_argument(
        "--profile",
        choices=("repo", "docs-expert"),
        default="docs-expert",
        help="Brand profile mode: docs-expert (default) or repo (neutral/custom).",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Optional JSON config path for custom brand settings.",
    )
    parser.add_argument("--brand-name", default=None, help="Expected brand display name.")
    parser.add_argument("--tagline", default=None, help="Expected brand tagline.")
    parser.add_argument(
        "--signature-asset",
        action="append",
        default=[],
        help="Asset path expected in README signature (repeatable).",
    )
    parser.add_argument(
        "--required-asset",
        action="append",
        default=[],
        help="Asset path that must exist and be non-empty (repeatable).",
    )
    parser.add_argument(
        "--allow-ascii-signature",
        action="store_true",
        help="Allow plain-text signature mode in README.",
    )
    parser.add_argument(
        "--require-signature",
        action="store_true",
        help="Return non-zero if the signature is missing.",
    )
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo)
    readme_path = args.readme or os.path.join(repo_root, "README.md")
    doc_paths = [readme_path]
    for doc in args.docs:
        doc_paths.append(resolve(doc, repo_root))

    profile: dict[str, Any] = {
        "brand_name": None,
        "tagline": None,
        "signature_assets": [],
        "required_assets": [],
        "allow_ascii": False,
        "require_signature": False,
    }

    if args.profile == "docs-expert":
        profile.update(DEFAULT_DOCS_EXPERT)

    if args.config:
        profile.update(parse_config(resolve(args.config, repo_root)))

    if args.brand_name is not None:
        profile["brand_name"] = args.brand_name
    if args.tagline is not None:
        profile["tagline"] = args.tagline
    if args.signature_asset:
        profile["signature_assets"] = args.signature_asset
    if args.required_asset:
        profile["required_assets"] = args.required_asset
    if args.allow_ascii_signature:
        profile["allow_ascii"] = True
    if args.require_signature:
        profile["require_signature"] = True

    failures: list[str] = []
    notes: list[str] = []

    readme_text = read_file(readme_path)
    if readme_text is None:
        failures.append(f"README not found: {readme_path}")
    elif profile["require_signature"]:
        ok, mode = check_signature(
            readme_text,
            profile.get("brand_name"),
            profile.get("tagline"),
            profile.get("signature_assets", []),
            bool(profile.get("allow_ascii")),
        )
        if not ok:
            failures.append("README signature missing for selected brand profile")
        else:
            notes.append(f"README signature detected: {mode}")
    else:
        notes.append("Signature check skipped (signature not required)")

    missing_required: list[str] = []
    empty_required: list[str] = []
    for asset in profile.get("required_assets", []):
        asset_path = resolve(asset, repo_root)
        if not os.path.exists(asset_path):
            missing_required.append(asset)
        elif os.path.getsize(asset_path) == 0:
            empty_required.append(asset)

    if missing_required:
        failures.append("Missing required brand assets: " + ", ".join(missing_required))
    if empty_required:
        failures.append("Required brand assets are empty: " + ", ".join(empty_required))

    print("Brand compliance check")
    print(f"- Repo: {repo_root}")
    print(f"- README: {readme_path}")
    print(f"- Profile: {args.profile}")

    for note in notes:
        print(f"- Note: {note}")

    for doc_path in doc_paths:
        doc_text = read_file(doc_path)
        if doc_text is None:
            if doc_path != readme_path:
                failures.append(f"Doc not found: {doc_path}")
            continue
        hits = find_watermark_usage(doc_text)
        if hits:
            failures.append(f"Possible watermark usage in {doc_path}")

    if failures:
        print("- Status: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("- Status: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
