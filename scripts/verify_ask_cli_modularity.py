#!/usr/bin/env python3
"""Verify `bin/ask` stays parse/dispatch focused."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ASK_PATH = REPO_ROOT / "bin" / "ask"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate ask CLI modularity constraints.")
    parser.add_argument(
        "--max-lines",
        type=int,
        default=1700,
        help="Maximum allowed line count for bin/ask.",
    )
    return parser.parse_args()


def _imported_modules(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


def _command_imports_ok(modules: set[str]) -> bool:
    required = {
        "ask.commands.skills",
        "ask.commands.repo",
        "ask.commands.plugins",
    }
    return all(module in modules for module in required)


def _forbidden_imports(modules: set[str]) -> list[str]:
    forbidden_prefixes = ("subprocess", "requests")
    found: list[str] = []
    for module in modules:
        for prefix in forbidden_prefixes:
            if module == prefix or module.startswith(prefix + "."):
                found.append(module)
                break
    return sorted(found)


def main() -> int:
    args = parse_args()
    if not ASK_PATH.exists():
        print(f"Missing ask entrypoint: {ASK_PATH}")
        return 1

    text = ASK_PATH.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    tree = ast.parse(text, filename=str(ASK_PATH))
    modules = _imported_modules(tree)

    issues: list[str] = []
    if line_count > max(1, int(args.max_lines)):
        issues.append(
            f"bin/ask exceeds max line budget ({line_count} > {args.max_lines})"
        )
    if not _command_imports_ok(modules):
        issues.append("bin/ask must import ask.commands.skills, ask.commands.repo, and ask.commands.plugins")
    forbidden = _forbidden_imports(modules)
    if forbidden:
        issues.append(f"bin/ask imports forbidden direct execution modules: {', '.join(forbidden)}")

    print(f"ask_cli_modularity: lines={line_count} max={args.max_lines}")
    if issues:
        print("Modularity verification failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Modularity verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
