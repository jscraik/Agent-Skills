#!/usr/bin/env python3
"""Verify `bin/ask` stays parse/dispatch focused."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ASK_PATH = REPO_ROOT / "bin" / "ask"


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the modularity verifier.
    
    Parameters:
        None
    
    Returns:
        args (argparse.Namespace): Parsed arguments with attribute `max_lines` (int) specifying the maximum allowed line count for bin/ask (default 1700).
    """
    parser = argparse.ArgumentParser(description="Validate ask CLI modularity constraints.")
    parser.add_argument(
        "--max-lines",
        type=int,
        default=1900,
        help="Maximum allowed line count for bin/ask.",
    )
    return parser.parse_args()


def _imported_modules(tree: ast.AST) -> set[str]:
    """
    Collect the module names referenced by import statements in the given AST.
    
    Parameters:
        tree (ast.AST): The parsed AST to analyse.
    
    Returns:
        modules (set[str]): A set of module name strings found in `import` and `from ... import` statements. For `from . import ...` (or other relative imports without a module name) the empty string `""` is included.
    """
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


def _command_imports_ok(modules: set[str]) -> bool:
    """
    Check that the required ask command modules are present in the provided set of imported module names.
    
    Parameters:
        modules (set[str]): Module name strings extracted from the AST of a Python file.
    
    Returns:
        bool: `True` if `ask.commands.skills`, `ask.commands.repo` and `ask.commands.plugins` are all present in `modules`, `False` otherwise.
    """
    required = {
        "ask.commands.skills",
        "ask.commands.repo",
        "ask.commands.plugins",
    }
    return all(module in modules for module in required)


def _forbidden_imports(modules: set[str]) -> list[str]:
    """
    Identify imported module names that match forbidden prefixes (`subprocess`, `requests`).
    
    Parameters:
        modules (set[str]): Set of imported module names extracted from an AST.
    
    Returns:
        list[str]: Sorted list of module names from `modules` that are equal to a forbidden prefix or start with a forbidden prefix followed by a dot.
    """
    forbidden_prefixes = ("subprocess", "requests")
    found: list[str] = []
    for module in modules:
        for prefix in forbidden_prefixes:
            if module == prefix or module.startswith(prefix + "."):
                found.append(module)
                break
    return sorted(found)


def main() -> int:
    """
    Verify modularity constraints of the bin/ask entrypoint and report any violations.
    
    Checks include a configurable maximum line count, presence of required command imports, and absence of forbidden direct-execution modules. Prints a summary line and any issues; returns an exit code indicating the result.
    
    Returns:
        int: `0` if all checks pass, `1` if the entrypoint is missing or any check fails.
    """
    args = parse_args()
    if not ASK_PATH.exists():
        print(f"Missing ask entrypoint: {ASK_PATH}")
        return 1

    text = ASK_PATH.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    try:
        tree = ast.parse(text, filename=str(ASK_PATH))
    except SyntaxError as exc:
        print(f"ask_cli_modularity: parse_failed file={ASK_PATH} line={exc.lineno} msg={exc.msg}")
        return 1
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
