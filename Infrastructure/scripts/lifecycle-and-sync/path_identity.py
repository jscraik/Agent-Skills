#!/usr/bin/env python3
"""
Small path identity helpers for shell sync scripts.

The sync shell uses this module when string comparison is too brittle, for
example when macOS resolves differently-cased spellings of the same directory.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def is_same_or_child(canonical: Path, candidate: Path) -> bool:
    """
    Return whether candidate resolves to canonical or a child of canonical.

    The samefile check handles symlinks and case-insensitive filesystems when
    both paths exist. The lower-case fallback keeps behavior stable for already
    removed or partially-resolved paths.
    """
    canonical_real = Path(os.path.realpath(canonical))
    candidate_real = Path(os.path.realpath(candidate))

    try:
        if os.path.samefile(canonical_real, candidate_real):
            return True
    except OSError:
        pass

    canonical_text = str(canonical_real).rstrip(os.sep).lower()
    candidate_text = str(candidate_real).lower()
    return candidate_text == canonical_text or candidate_text.startswith(canonical_text + os.sep)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Path identity helpers for sync scripts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    same_or_child = subparsers.add_parser(
        "is-same-or-child",
        help="Exit 0 when candidate resolves to canonical or a child of it.",
    )
    same_or_child.add_argument("canonical", type=Path)
    same_or_child.add_argument("candidate", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "is-same-or-child":
        return 0 if is_same_or_child(args.canonical, args.candidate) else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
