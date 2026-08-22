#!/usr/bin/env python3
"""Verify `bin/ask` stays parse/dispatch focused."""

from __future__ import annotations

import argparse
import ast
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ASK_PATH = REPO_ROOT / "Infrastructure" / "bin" / "ask"
PYTHON_SUFFIX = ".py"
def parse_args() -> argparse.Namespace:
    """
    Create and parse command-line arguments for verifying the ask CLI modularity.
    
    Adds a `--max-lines` option to control the maximum allowed line count for Infrastructure/bin/ask (default 1900).
    
    Returns:
        argparse.Namespace: Parsed arguments with attribute `max_lines` (int) specifying the maximum allowed line count for Infrastructure/bin/ask.
    """
    parser = argparse.ArgumentParser(description="Validate ask CLI modularity constraints.")
    parser.add_argument(
        "--max-lines",
        type=int,
        default=1900,
        help="Maximum allowed line count for Infrastructure/bin/ask.",
    )
    parser.add_argument("--changed-files", nargs="*", default=(), help="Repo-relative changed files to shape-check.")
    parser.add_argument("--baseline-ref", help="Git revision used as the pre-change shape baseline.")
    parser.add_argument("--staged-source", action="store_true", help="Read changed Python source from the Git index.")
    parser.add_argument("--max-file-lines", type=int, default=800, help="Maximum lines for new Python files.")
    parser.add_argument("--max-function-lines", type=int, default=40, help="Maximum lines for new or worsened functions.")
    parser.add_argument("--max-complexity", type=int, default=12, help="Maximum cyclomatic complexity for new or worsened functions.")
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


def _repo_path(path_text: str) -> Path:
    return (REPO_ROOT / path_text).resolve()


def _git_output(args: list[str]) -> str:
    command = ["git", *args]
    result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"git shape-baseline command failed ({detail})")
    return result.stdout


def _git_lines(args: list[str]) -> list[str]:
    return [line.strip() for line in _git_output(args).splitlines() if line.strip()]


def _default_baseline_ref(*, staged_source: bool = False) -> str | None:
    if staged_source:
        return "HEAD"
    for candidate in ("origin/main", "main", "HEAD^"):
        result = subprocess.run(
            ["git", "merge-base", "HEAD", candidate],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return None


def _shape_baseline(
    path: Path | None = None,
    baseline_ref: str = "HEAD",
    *,
    staged_source: bool = False,
) -> dict[str, object]:
    diff_args = ["diff"]
    if staged_source:
        diff_args.append("--cached")
    diff_args.extend(("--name-only", "--diff-filter=D", baseline_ref, "--"))
    deleted = [
        item
        for item in _git_lines(diff_args)
        if item.endswith(PYTHON_SUFFIX)
    ]
    siblings: list[str] = []
    if path is not None:
        relative = path.relative_to(REPO_ROOT).as_posix()
        parent = Path(relative).parent.as_posix()
        siblings = [
            item
            for item in _git_lines(["ls-tree", "-r", "--name-only", baseline_ref, "--", parent])
            if item.endswith(PYTHON_SUFFIX)
        ]
    baseline_paths = dict.fromkeys([*deleted, *siblings])
    head_text = {item: _git_output(["show", f"{baseline_ref}:{item}"]) for item in baseline_paths}
    return {"deleted_python_paths": deleted, "sibling_python_paths": siblings, "head_text": head_text}


def _baseline_head_text(path: Path, baseline: dict[str, object]) -> str | None:
    relpath = path.relative_to(REPO_ROOT).as_posix()
    head_text = baseline.get("head_text", {})
    return head_text.get(relpath) if isinstance(head_text, dict) else None


def _deleted_python_paths(baseline: dict[str, object]) -> list[Path]:
    raw_paths = baseline.get("deleted_python_paths", [])
    paths: list[Path] = []
    for line in raw_paths if isinstance(raw_paths, list) else []:
        candidate = _repo_path(str(line).strip())
        if candidate.suffix == PYTHON_SUFFIX:
            paths.append(candidate)
    return paths


def _oversized_sibling_paths(
    path: Path,
    baseline: dict[str, object],
    max_file_lines: int = 800,
) -> list[Path]:
    sibling_paths = baseline.get("sibling_python_paths", [])
    head_text = baseline.get("head_text", {})
    paths: list[Path] = []
    for line in sibling_paths if isinstance(sibling_paths, list) else []:
        candidate = _repo_path(str(line).strip())
        if candidate == path or not candidate.is_file():
            continue
        relative = candidate.relative_to(REPO_ROOT).as_posix()
        text = head_text.get(relative) if isinstance(head_text, dict) else None
        if text is not None and len(text.splitlines()) > max_file_lines:
            paths.append(candidate)
    return paths


def _moved_function_metrics(
    path: Path,
    baseline: dict[str, object] | None = None,
    current: str | None = None,
) -> dict[str, tuple[int, int]]:
    """Use unique names or exact syntax matches in sibling modules as move baselines."""
    baseline = baseline or _shape_baseline(path)
    candidates: dict[str, list[tuple[tuple[int, int], str]]] = {}
    baseline_paths = [
        *_deleted_python_paths(baseline),
        *_oversized_sibling_paths(path, baseline),
    ]
    for deleted_path in dict.fromkeys(baseline_paths):
        if deleted_path.parent != path.parent:
            continue
        text = _baseline_head_text(deleted_path, baseline)
        if text is None:
            continue
        for name, record in _function_fingerprint_metrics(text, source="baseline").items():
            candidates.setdefault(name, []).append(record)
    moved = {name: values[0][0] for name, values in candidates.items() if len(values) == 1}
    if current is None:
        return moved
    for name, (_, fingerprint) in _function_fingerprint_metrics(current).items():
        exact_metrics = {
            metrics
            for metrics, candidate_fingerprint in candidates.get(name, [])
            if candidate_fingerprint == fingerprint
        }
        if len(exact_metrics) == 1:
            moved[name] = exact_metrics.pop()
    return moved


def _complexity(node: ast.AST) -> int:
    score = 1
    decision_nodes = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp, ast.Assert, ast.comprehension)
    match_node = getattr(ast, "Match", None)
    for child in ast.walk(node):
        if isinstance(child, decision_nodes):
            score += 1
        elif isinstance(child, ast.BoolOp):
            score += max(1, len(child.values) - 1)
        elif match_node is not None and isinstance(child, match_node):
            score += len(child.cases)
    return score


def _function_metrics(
    text: str,
    *,
    source: str = "current",
) -> dict[str, tuple[int, int]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        if source == "baseline":
            return {}
        raise
    metrics: dict[str, tuple[int, int]] = {}

    class _FunctionVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.qualifiers: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.qualifiers.append(node.name)
            self.generic_visit(node)
            self.qualifiers.pop()

        def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            qualified_name = ".".join([*self.qualifiers, node.name])
            end_lineno = getattr(node, "end_lineno", node.lineno)
            metrics[qualified_name] = (end_lineno - node.lineno + 1, _complexity(node))
            self.qualifiers.append(node.name)
            self.generic_visit(node)
            self.qualifiers.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._visit_function(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._visit_function(node)

    _FunctionVisitor().visit(tree)
    return metrics


def _function_fingerprint_metrics(
    text: str,
    *,
    source: str = "current",
) -> dict[str, tuple[tuple[int, int], str]]:
    """Return function metrics bound to normalized syntax for exact move detection."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        if source == "baseline":
            return {}
        raise
    records: dict[str, tuple[tuple[int, int], str]] = {}

    class _FingerprintVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.qualifiers: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.qualifiers.append(node.name)
            self.generic_visit(node)
            self.qualifiers.pop()

        def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            name = ".".join([*self.qualifiers, node.name])
            end_lineno = getattr(node, "end_lineno", node.lineno)
            metrics = (end_lineno - node.lineno + 1, _complexity(node))
            records[name] = (metrics, ast.dump(node, include_attributes=False))
            self.qualifiers.append(node.name)
            self.generic_visit(node)
            self.qualifiers.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._visit_function(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._visit_function(node)

    _FingerprintVisitor().visit(tree)
    return records


def _changed_python_paths(paths: tuple[str, ...]) -> list[Path]:
    python_paths: list[Path] = []
    for path_text in paths:
        if path_text.endswith(PYTHON_SUFFIX):
            path = _repo_path(path_text)
            if path.exists() and path.is_file():
                python_paths.append(path)
    return sorted(set(python_paths))


def _current_source(path: Path, *, staged_source: bool = False) -> str:
    if not staged_source:
        return path.read_text(encoding="utf-8")
    relpath = path.relative_to(REPO_ROOT).as_posix()
    return _git_output(["show", f":{relpath}"])


def _check_file_size(path: Path, current: str, baseline: str | None, args: argparse.Namespace, issues: list[str]) -> None:
    relpath = path.relative_to(REPO_ROOT).as_posix()
    line_count = len(current.splitlines())
    baseline_line_count = len(baseline.splitlines()) if baseline is not None else 0
    if line_count <= args.max_file_lines:
        return
    if line_count > baseline_line_count:
        issues.append(f"{relpath} exceeds file line budget ({line_count} > {args.max_file_lines})")


def _check_function_shape(
    path: Path,
    current: str,
    baseline: str | None,
    args: argparse.Namespace,
    issues: list[str],
    shape_baseline: dict[str, object] | None = None,
) -> None:
    relpath = path.relative_to(REPO_ROOT).as_posix()
    current_metrics = _function_metrics(current, source="current")
    baseline_metrics = (
        _function_metrics(baseline, source="baseline")
        if baseline is not None
        else _moved_function_metrics(path, shape_baseline, current)
    )
    for name, (line_count, complexity) in sorted(current_metrics.items()):
        old_lines, old_complexity = baseline_metrics.get(name, (0, 0))
        if line_count > args.max_function_lines and line_count > old_lines:
            issues.append(f"{relpath}:{name} exceeds function line budget ({line_count} > {args.max_function_lines})")
        if complexity > args.max_complexity and complexity > old_complexity:
            issues.append(f"{relpath}:{name} exceeds complexity budget ({complexity} > {args.max_complexity})")


def _check_python_shape(args: argparse.Namespace) -> list[str]:
    issues: list[str] = []
    staged_source = bool(getattr(args, "staged_source", False))
    baseline_ref = getattr(args, "baseline_ref", None) or _default_baseline_ref(staged_source=staged_source)
    if not baseline_ref:
        return ["shape baseline unavailable: baseline revision could not be determined"]
    baseline_by_parent: dict[Path, dict[str, object]] = {}
    for path in _changed_python_paths(tuple(args.changed_files)):
        try:
            current = _current_source(path, staged_source=staged_source)
            shape_baseline = baseline_by_parent.get(path.parent)
            if shape_baseline is None:
                shape_baseline = _shape_baseline(path, baseline_ref, staged_source=staged_source)
                baseline_by_parent[path.parent] = shape_baseline
            baseline = _baseline_head_text(path, shape_baseline)
            _check_file_size(path, current, baseline, args, issues)
            _check_function_shape(path, current, baseline, args, issues, shape_baseline)
        except RuntimeError as exc:
            issues.append(f"{path.relative_to(REPO_ROOT).as_posix()} shape baseline unavailable: {exc}")
            break
    return issues


def _check_ask_entrypoint(args: argparse.Namespace) -> list[str] | None:
    if not ASK_PATH.exists():
        print(f"Missing ask entrypoint: {ASK_PATH}")
        return None
    text = ASK_PATH.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    try:
        tree = ast.parse(text, filename=str(ASK_PATH))
    except SyntaxError as exc:
        print(f"ask_cli_modularity: parse_failed file={ASK_PATH} line={exc.lineno} msg={exc.msg}")
        return None
    issues = _check_ask_modules(tree, line_count, args)
    print(f"ask_cli_modularity: lines={line_count} max={args.max_lines}")
    return issues


def _check_ask_modules(tree: ast.AST, line_count: int, args: argparse.Namespace) -> list[str]:
    modules = _imported_modules(tree)
    issues: list[str] = []
    if line_count > max(1, int(args.max_lines)):
        issues.append(f"Infrastructure/bin/ask exceeds max line budget ({line_count} > {args.max_lines})")
    if not _command_imports_ok(modules):
        issues.append("Infrastructure/bin/ask must import ask.commands.skills, ask.commands.repo, and ask.commands.plugins")
    forbidden = _forbidden_imports(modules)
    if forbidden:
        issues.append(f"Infrastructure/bin/ask imports forbidden direct execution modules: {', '.join(forbidden)}")
    return issues


def main() -> int:
    """
    Verify modularity constraints of the Infrastructure/bin/ask entrypoint and report any violations.
    
    Checks a configurable maximum line count, required command imports, and absence of forbidden direct-execution modules. Prints a summary line and any issues.
    
    Returns:
        int: `0` if all checks pass, `1` if the entrypoint is missing, parsing fails, or any check fails.
    """
    args = parse_args()
    issues = _check_ask_entrypoint(args)
    if issues is None:
        return 1
    issues.extend(_check_python_shape(args))
    if issues:
        print("Modularity verification failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Modularity verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
