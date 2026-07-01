#!/usr/bin/env python3
"""Verify `bin/ask` stays parse/dispatch focused."""

from __future__ import annotations

import argparse
import ast
import subprocess
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ASK_PATH = REPO_ROOT / "Infrastructure" / "bin" / "ask"
PYTHON_SUFFIX = ".py"
LEGACY_SHAPE_DEBT = {
    "Infrastructure/scripts/lib/ask/commands/evals.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing eval command extraction debt",
        "expires": "2026-07-31",
    },
    "Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py": {
        "owner": "skill-factory",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing plugin eval runner extraction debt",
        "expires": "2026-07-31",
    },
    "Plugins/skill-factory/scripts/skill-builder/skill_gate.py": {
        "owner": "skill-factory",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing plugin gate extraction debt",
        "expires": "2026-07-31",
    },
    "Plugins/skill-factory/scripts/skill-builder/test_run_skill_evals.py": {
        "owner": "skill-factory",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing plugin eval regression suite debt",
        "expires": "2026-07-31",
    },
    "Plugins/skill-factory/scripts/skill-builder/test_skill_gate_contract_evals.py": {
        "owner": "skill-factory",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing plugin gate regression suite debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/scripts/lib/ask/commands/skills_impl.py": {
        "owner": "ask-cli",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing skills command extraction debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/scripts/lib/ask/skill_review_dashboard.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing skill review dashboard extraction debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing package contract extraction debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing typed contract extraction debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/scripts/lifecycle-and-sync/route_skillset.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing routed skillset extraction debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py": {
        "owner": "skill-factory",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing skill authoring benchmark extraction debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/tests/test_ask_cli_impl.py": {
        "owner": "ask-cli",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing ask CLI regression suite debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/tests/test_ask_evals_command.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing eval command regression suite debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/tests/test_ask_skills_package_contract.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing package contract regression suite debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/tests/test_ask_skills_package.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing package verification regression suite debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/tests/test_pr_skills_sdk_artifacts.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing SDK artifact regression suite debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/tests/test_skills_sdk_scenario_quality.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing scenario quality regression suite debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/tests/test_skills_sdk_ab_judge_score.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing A/B judge score regression suite debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/tests/test_skills_sdk_schema_spine.py": {
        "owner": "skills-sdk",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing schema spine regression suite debt",
        "expires": "2026-07-31",
    },
    "skills-system/skill-creator/scripts/init_skill.py": {
        "owner": "skill-factory",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing skill creator scaffold extraction debt",
        "expires": "2026-07-31",
    },
    "Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/test_skill_gate.py": {
        "owner": "skill-factory",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing code-quality skill gate regression suite debt",
        "expires": "2026-07-31",
    },
    "Infrastructure/tests/test_ask_skills_errors.py": {
        "owner": "ask-cli",
        "rule_id": "ask-cli-shape-budget",
        "ticket": "JSC-SDK-SPINE",
        "reason": "pre-existing skills error regression suite debt",
        "expires": "2026-07-31",
    },
}
LEGACY_SHAPE_DEBT_PATHS = frozenset(LEGACY_SHAPE_DEBT)
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


def _git_head_text(path: Path) -> str | None:
    relpath = path.relative_to(REPO_ROOT).as_posix()
    result = subprocess.run(
        ["git", "show", f"HEAD:{relpath}"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


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


def _function_metrics(text: str, *, relpath: str, source: str, issues: list[str]) -> dict[str, tuple[int, int]]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        if source == "baseline":
            return {}
        raise
    metrics: dict[str, tuple[int, int]] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_lineno = getattr(node, "end_lineno", node.lineno)
            metrics[node.name] = (end_lineno - node.lineno + 1, _complexity(node))
    return metrics


def _changed_python_paths(paths: tuple[str, ...]) -> list[Path]:
    python_paths: list[Path] = []
    for path_text in paths:
        if path_text.endswith(PYTHON_SUFFIX):
            path = _repo_path(path_text)
            if path.exists() and path.is_file():
                python_paths.append(path)
    return sorted(set(python_paths))


def _check_file_size(path: Path, current: str, baseline: str | None, args: argparse.Namespace, issues: list[str]) -> None:
    relpath = path.relative_to(REPO_ROOT).as_posix()
    if relpath in LEGACY_SHAPE_DEBT_PATHS:
        return
    line_count = len(current.splitlines())
    baseline_line_count = len(baseline.splitlines()) if baseline is not None else 0
    if line_count <= args.max_file_lines:
        return
    if line_count > baseline_line_count:
        issues.append(f"{relpath} exceeds file line budget ({line_count} > {args.max_file_lines})")


def _check_function_shape(path: Path, current: str, baseline: str | None, args: argparse.Namespace, issues: list[str]) -> None:
    relpath = path.relative_to(REPO_ROOT).as_posix()
    if relpath in LEGACY_SHAPE_DEBT_PATHS:
        return
    current_metrics = _function_metrics(current, relpath=relpath, source="current", issues=issues)
    baseline_metrics = _function_metrics(baseline, relpath=relpath, source="baseline", issues=issues) if baseline is not None else {}
    for name, (line_count, complexity) in sorted(current_metrics.items()):
        old_lines, old_complexity = baseline_metrics.get(name, (0, 0))
        if line_count > args.max_function_lines and line_count > old_lines:
            issues.append(f"{relpath}:{name} exceeds function line budget ({line_count} > {args.max_function_lines})")
        if complexity > args.max_complexity and complexity > old_complexity:
            issues.append(f"{relpath}:{name} exceeds complexity budget ({complexity} > {args.max_complexity})")


def _check_python_shape(args: argparse.Namespace) -> list[str]:
    issues: list[str] = []
    issues.extend(_check_legacy_shape_debt_metadata())
    for path in _changed_python_paths(tuple(args.changed_files)):
        current = path.read_text(encoding="utf-8")
        baseline = _git_head_text(path)
        _check_file_size(path, current, baseline, args, issues)
        _check_function_shape(path, current, baseline, args, issues)
    return issues


def _check_legacy_shape_debt_metadata() -> list[str]:
    issues: list[str] = []
    required_fields = ("owner", "rule_id", "ticket", "reason", "expires")
    today = date.today()
    for relpath, metadata in sorted(LEGACY_SHAPE_DEBT.items()):
        missing = [field for field in required_fields if not metadata.get(field)]
        if missing:
            issues.append(f"{relpath} legacy shape debt missing waiver field(s): {', '.join(missing)}")
            continue
        try:
            expires = date.fromisoformat(metadata["expires"])
        except ValueError:
            issues.append(f"{relpath} legacy shape debt has invalid expires date: {metadata['expires']}")
            continue
        if expires < today:
            issues.append(f"{relpath} legacy shape debt expired on {metadata['expires']}")
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
