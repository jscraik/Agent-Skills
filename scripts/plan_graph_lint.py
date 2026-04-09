#!/usr/bin/env python3
"""
Validate markdown plan files that include fenced YAML task-graph blocks.

Contract:
tasks:
  - id: T1
    title: ...
    depends_on: []
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    already_reexec = os.environ.get("PLAN_GRAPH_PYYAML_REEXEC") == "1"
    if preferred.exists() and not already_reexec:
        env = dict(os.environ)
        env["PLAN_GRAPH_PYYAML_REEXEC"] = "1"
        os.execve(str(preferred), [str(preferred), __file__, *sys.argv[1:]], env)
    print("ERROR: PyYAML is required for plan graph linting.", file=sys.stderr)
    raise SystemExit(1)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def extract_task_graphs(markdown: str) -> List[Dict[str, Any]]:
    graphs: List[Dict[str, Any]] = []
    in_fence = False
    block_lines: List[str] = []

    for line in markdown.splitlines():
        stripped = line.strip()
        if not in_fence:
            if stripped.startswith("```"):
                in_fence = True
                block_lines = []
            continue

        if stripped.startswith("```"):
            block = "\n".join(block_lines)
            if "tasks:" in block:
                try:
                    loaded = yaml.safe_load(block)
                except Exception:  # noqa: BLE001
                    loaded = None
                if isinstance(loaded, dict) and "tasks" in loaded:
                    graphs.append(loaded)
            in_fence = False
            block_lines = []
            continue

        block_lines.append(line)

    return graphs


def _task_id(task: Dict[str, Any]) -> str:
    raw = task.get("id")
    return raw.strip() if isinstance(raw, str) else ""


def _depends(task: Dict[str, Any]) -> List[str]:
    raw = task.get("depends_on")
    if raw is None:
        return []
    if not isinstance(raw, list):
        return []
    out: List[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def detect_cycle(ids: Set[str], deps: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
    visiting: Set[str] = set()
    visited: Set[str] = set()
    parent: Dict[str, str] = {}

    def dfs(node: str) -> Tuple[bool, List[str]]:
        visiting.add(node)
        for nxt in deps.get(node, []):
            if nxt not in ids:
                continue
            if nxt in visited:
                continue
            if nxt in visiting:
                cycle = [nxt]
                cur = node
                while cur != nxt and cur in parent:
                    cycle.append(cur)
                    cur = parent[cur]
                cycle.append(nxt)
                cycle.reverse()
                return True, cycle
            parent[nxt] = node
            hit, cycle = dfs(nxt)
            if hit:
                return True, cycle
        visiting.remove(node)
        visited.add(node)
        return False, []

    for nid in sorted(ids):
        if nid in visited:
            continue
        hit, cycle = dfs(nid)
        if hit:
            return True, cycle
    return False, []


def validate_graph(graph: Dict[str, Any]) -> List[str]:
    errs: List[str] = []
    tasks = graph.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return ["`tasks` must be a non-empty list."]

    ids: Set[str] = set()
    duplicates: Set[str] = set()
    deps_map: Dict[str, List[str]] = {}

    for idx, raw in enumerate(tasks, start=1):
        if not isinstance(raw, dict):
            errs.append(f"tasks[{idx}] must be a mapping/object.")
            continue
        tid = _task_id(raw)
        if not tid:
            errs.append(f"tasks[{idx}] missing non-empty `id`.")
            continue
        if "depends_on" not in raw:
            errs.append(f"{tid}: missing required `depends_on`.")
        depends = _depends(raw)
        if "depends_on" in raw and not isinstance(raw.get("depends_on"), list):
            errs.append(f"{tid}: `depends_on` must be a list.")
        if tid in ids:
            duplicates.add(tid)
        ids.add(tid)
        deps_map[tid] = depends
        if tid in depends:
            errs.append(f"{tid}: self-dependency is not allowed.")

    if duplicates:
        errs.append(f"duplicate task id(s): {', '.join(sorted(duplicates))}.")

    for tid, depends in deps_map.items():
        unknown = sorted([d for d in depends if d not in ids])
        if unknown:
            errs.append(f"{tid}: unknown dependency id(s): {', '.join(unknown)}.")

    has_cycle, cycle = detect_cycle(ids, deps_map)
    if has_cycle:
        errs.append(f"dependency cycle detected: {' -> '.join(cycle)}.")

    return errs


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint markdown task-graph contract files.")
    parser.add_argument("path", help="Path to plan markdown file.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        print(f"[FAIL] file not found: {path}", file=sys.stderr)
        return 1

    text = read_text(path)
    graphs = extract_task_graphs(text)
    if not graphs:
        print(f"[FAIL] {path}: no YAML task graph block with `tasks:` found.", file=sys.stderr)
        return 2

    failures: List[str] = []
    for i, graph in enumerate(graphs, start=1):
        errs = validate_graph(graph)
        if errs:
            failures.append(f"graph #{i}:")
            failures.extend([f"  - {e}" for e in errs])

    if failures:
        print(f"[FAIL] {path}: task graph lint failed", file=sys.stderr)
        for line in failures:
            print(line, file=sys.stderr)
        return 2

    print(f"[OK] {path}: task graph lint passed ({len(graphs)} graph block(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
