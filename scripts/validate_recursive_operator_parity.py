#!/usr/bin/env python3
"""Validate operator action parity between plan contract and loop runtime.

Fails when action primitives declared in the plan's Agent-Native capability map
are missing from:
1) CLI action parser choices
2) runtime action handlers in main()
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Iterable, Set


SECTION_HEADER_PREFIX = "### Agent-Native Capability Map"
ACTION_PATTERN = re.compile(r"([a-z_]+)\s*\(")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate recursive loop operator action parity")
    p.add_argument(
        "--plan-file",
        default="docs/plans/2026-02-19-feat-recursive-skill-self-improvement-loop-plan.md",
        help="Path to plan markdown with Agent-Native capability map",
    )
    p.add_argument(
        "--loop-script",
        default="utilities/skill-creator/scripts/recursive_skill_loop.py",
        help="Path to recursive loop runtime script",
    )
    p.add_argument("--json", action="store_true", help="Emit JSON report")
    return p.parse_args()


def _iter_capability_rows(lines: Iterable[str]) -> Iterable[str]:
    in_section = False
    for raw in lines:
        line = raw.rstrip("\n")
        if line.strip().startswith(SECTION_HEADER_PREFIX):
            in_section = True
            continue
        if in_section:
            if line.startswith("### "):
                break
            if line.startswith("|"):
                yield line


def declared_run_actions_from_plan(plan_text: str) -> Set[str]:
    actions: Set[str] = set()
    for row in _iter_capability_rows(plan_text.splitlines()):
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        # Skip markdown separator row
        if all(c and set(c) <= {"-"} for c in cells):
            continue
        capability_cell = cells[1]
        for match in ACTION_PATTERN.finditer(capability_cell):
            action = match.group(1)
            if action.endswith("_run"):
                actions.add(action)
    return actions


def parser_actions_from_ast(tree: ast.AST) -> Set[str]:
    actions: Set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue
        if not node.args:
            continue
        first = node.args[0]
        if not isinstance(first, ast.Constant) or first.value != "action":
            continue
        for kw in node.keywords:
            if kw.arg != "choices":
                continue
            if isinstance(kw.value, (ast.List, ast.Tuple, ast.Set)):
                for elt in kw.value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        actions.add(elt.value)
    return actions


def handled_actions_from_main_ast(tree: ast.AST) -> Set[str]:
    actions: Set[str] = set()

    main_fn = None
    for node in tree.body if isinstance(tree, ast.Module) else []:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            main_fn = node
            break
    if main_fn is None:
        return actions

    for node in ast.walk(main_fn):
        # Explicit comparisons: if args.action == "start_run"
        if isinstance(node, ast.Compare):
            if len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
                left = node.left
                if (
                    isinstance(left, ast.Attribute)
                    and left.attr == "action"
                    and isinstance(left.value, ast.Name)
                    and left.value.id == "args"
                ):
                    for comparator in node.comparators:
                        if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                            actions.add(comparator.value)

        # Dispatch calls: queue_terminal_action(action="abort_run", ...)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "queue_terminal_action":
                for kw in node.keywords:
                    if kw.arg == "action" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                        actions.add(kw.value.value)

    return actions


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan_file).resolve()
    script_path = Path(args.loop_script).resolve()

    if not plan_path.exists():
        print(f"ERROR: plan file not found: {plan_path}", file=sys.stderr)
        return 2
    if not script_path.exists():
        print(f"ERROR: loop script not found: {script_path}", file=sys.stderr)
        return 2

    plan_actions = declared_run_actions_from_plan(plan_path.read_text(encoding="utf-8"))
    tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=str(script_path))
    parser_actions = parser_actions_from_ast(tree)
    handled_actions = handled_actions_from_main_ast(tree)

    missing_in_parser = sorted(plan_actions - parser_actions)
    missing_in_handlers = sorted(plan_actions - handled_actions)
    ok = not missing_in_parser and not missing_in_handlers and bool(plan_actions)

    report = {
        "ok": ok,
        "plan_file": str(plan_path),
        "loop_script": str(script_path),
        "declared_actions": sorted(plan_actions),
        "parser_actions": sorted(parser_actions),
        "handled_actions": sorted(handled_actions),
        "missing_in_parser": missing_in_parser,
        "missing_in_handlers": missing_in_handlers,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("[operator-parity] declared:", ", ".join(report["declared_actions"]) or "(none)")
        print("[operator-parity] parser:", ", ".join(report["parser_actions"]) or "(none)")
        print("[operator-parity] handlers:", ", ".join(report["handled_actions"]) or "(none)")
        if missing_in_parser:
            print("[operator-parity] missing in parser:", ", ".join(missing_in_parser))
        if missing_in_handlers:
            print("[operator-parity] missing in handlers:", ", ".join(missing_in_handlers))

    if not plan_actions:
        print("[operator-parity] ERROR: no *_run actions found in capability map section", file=sys.stderr)
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
