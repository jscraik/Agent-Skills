#!/usr/bin/env python3
"""Ratchet low-level program-design smells in changed Python production code.

This check deliberately complements, rather than replaces, the ask CLI shape
check.  The shape check protects line count and complexity.  This check protects
four design boundaries that are cheap to identify without pretending that an
AST can judge every abstraction choice:

* public functions whose parameter list grows past the small-interface budget;
* boolean default arguments, which usually encode two responsibilities;
* newly added broad exception handlers; and
* newly added explicit or module-level mutable global state.

Existing debt is ratcheted: unchanged findings remain visible to the next
refactoring slice but do not make an unrelated change fail.  New or worsened
findings fail unless the owning change removes them or records a time-boxed
waiver in the owning review surface.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MAX_PUBLIC_PARAMETERS = 5
PRODUCTION_PREFIXES = (
    "Infrastructure/bin/",
    "Infrastructure/scripts/",
    "Plugins/",
    "skills-system/",
)
EXCLUDED_PARTS = {".venv", "__pycache__", "references", "tests", "test"}
BROAD_EXCEPTION_NAMES = {"Exception", "BaseException"}
MUTABLE_VALUE_NODES = (
    ast.Dict,
    ast.DictComp,
    ast.List,
    ast.ListComp,
    ast.Set,
    ast.SetComp,
)
PROGRAM_DESIGN_WAIVERS: dict[str, dict[str, str]] = {}
WAIVER_FIELDS = ("owner", "rule_id", "ticket", "reason", "expires")


@dataclass(frozen=True)
class Finding:
    """A source location and stable key for one design smell."""

    line: int
    key: str
    detail: str


@dataclass(frozen=True)
class DesignMetrics:
    """AST-derived metrics used by the ratchet."""

    public_parameters: dict[str, tuple[int, int]]
    boolean_flags: tuple[Finding, ...]
    broad_exceptions: tuple[Finding, ...]
    global_statements: tuple[Finding, ...]
    mutable_module_state: tuple[Finding, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate changed Python program design.")
    parser.add_argument(
        "--changed-files",
        nargs="*",
        default=(),
        help="Repo-relative changed files to inspect; omitted means no-op baseline mode.",
    )
    parser.add_argument(
        "--max-public-parameters",
        type=int,
        default=MAX_PUBLIC_PARAMETERS,
        help="Maximum public function parameters before a new/worsened design finding.",
    )
    return parser.parse_args()


def _is_production_python(relpath: str) -> bool:
    if (
        not relpath.endswith(".py")
        or not relpath.startswith(PRODUCTION_PREFIXES)
        or relpath.startswith("Plugins/cache/")
    ):
        return False
    parts = set(Path(relpath).parts)
    if parts & EXCLUDED_PARTS:
        return False
    return not any(part.startswith("test_") for part in parts)


def _exception_names(node: ast.expr | None) -> list[str]:
    if node is None:
        return ["bare"]
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [node.attr]
    if isinstance(node, ast.Tuple):
        names: list[str] = []
        for element in node.elts:
            names.extend(_exception_names(element))
        return names
    return [ast.unparse(node)]


def _parameter_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    positional = list(node.args.posonlyargs) + list(node.args.args)
    if positional and positional[0].arg in {"self", "cls"}:
        positional = positional[1:]
    count = len(positional) + len(node.args.kwonlyargs)
    if node.args.vararg is not None:
        count += 1
    if node.args.kwarg is not None:
        count += 1
    return count


def _boolean_flags(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[Finding]:
    findings: list[Finding] = []
    positional = list(node.args.posonlyargs) + list(node.args.args)
    positional_defaults = [None] * (len(positional) - len(node.args.defaults)) + list(node.args.defaults)
    for argument, default in zip(positional, positional_defaults):
        if isinstance(default, ast.Constant) and isinstance(default.value, bool):
            findings.append(Finding(argument.lineno, f"{node.name}:{argument.arg}", f"{node.name}({argument.arg}=bool)"))
    for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        if isinstance(default, ast.Constant) and isinstance(default.value, bool):
            findings.append(Finding(argument.lineno, f"{node.name}:{argument.arg}", f"{node.name}({argument.arg}=bool)"))
    return findings


def _broad_exceptions(tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        for name in _exception_names(node.type):
            if name in BROAD_EXCEPTION_NAMES or name == "bare":
                findings.append(Finding(node.lineno, name, f"except {name}"))
    return findings


def _global_statements(tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Global):
            for name in node.names:
                findings.append(Finding(node.lineno, name, f"global {name}"))
    return findings


def _target_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        names: list[str] = []
        for element in node.elts:
            names.extend(_target_names(element))
        return names
    return []


def _mutable_module_state(tree: ast.Module) -> list[Finding]:
    findings: list[Finding] = []
    for node in tree.body:
        value: ast.expr | None = None
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            value = node.value
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            value = node.value
            targets = [node.target]
        if value is None or not isinstance(value, MUTABLE_VALUE_NODES):
            continue
        for target in targets:
            for name in _target_names(target):
                # Uppercase constants and __all__ are intentionally excluded;
                # a newly added lower-case mutable binding is the useful signal.
                if name.isupper() or name == "__all__":
                    continue
                findings.append(Finding(node.lineno, name, f"module mutable state {name}"))
    return findings


def _metrics(text: str) -> DesignMetrics:
    tree = ast.parse(text)
    public_parameters: dict[str, tuple[int, int]] = {}
    boolean_flags: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("_"):
            continue
        public_parameters[node.name] = (_parameter_count(node), node.lineno)
        boolean_flags.extend(_boolean_flags(node))
    return DesignMetrics(
        public_parameters=public_parameters,
        boolean_flags=tuple(boolean_flags),
        broad_exceptions=tuple(_broad_exceptions(tree)),
        global_statements=tuple(_global_statements(tree)),
        mutable_module_state=tuple(_mutable_module_state(tree)),
    )


def _git_head_text(path: Path) -> str | None:
    relpath = path.relative_to(REPO_ROOT).as_posix()
    result = subprocess.run(
        ["git", "show", f"HEAD:{relpath}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def _check_waiver_metadata(waivers: dict[str, dict[str, str]] | None = None) -> list[str]:
    issues: list[str] = []
    for key, metadata in sorted((waivers or PROGRAM_DESIGN_WAIVERS).items()):
        missing = [field for field in WAIVER_FIELDS if not metadata.get(field)]
        if missing:
            issues.append(f"{key} program-design waiver missing field(s): {', '.join(missing)}")
            continue
        try:
            expires = date.fromisoformat(metadata["expires"])
        except ValueError:
            issues.append(f"{key} program-design waiver has invalid expires date: {metadata['expires']}")
            continue
        if expires < date.today():
            issues.append(f"{key} program-design waiver expired on {metadata['expires']}")
    return issues


def _is_waived(relpath: str, rule_id: str, waivers: dict[str, dict[str, str]] | None) -> bool:
    return f"{relpath}:{rule_id}" in (waivers or PROGRAM_DESIGN_WAIVERS)


def _new_findings(current: tuple[Finding, ...], baseline: tuple[Finding, ...]) -> list[Finding]:
    current_counts = Counter(item.key for item in current)
    baseline_counts = Counter(item.key for item in baseline)
    remaining = {key: max(0, count - baseline_counts[key]) for key, count in current_counts.items()}
    findings: list[Finding] = []
    for item in sorted(current, key=lambda finding: (finding.line, finding.key)):
        if remaining.get(item.key, 0) > 0:
            findings.append(item)
            remaining[item.key] -= 1
    return findings


def _check_smells(
    relpath: str,
    current: DesignMetrics,
    baseline: DesignMetrics,
    waivers: dict[str, dict[str, str]] | None,
) -> list[str]:
    checks = (
        ("boolean flag argument", "boolean-flag", current.boolean_flags, baseline.boolean_flags),
        ("broad exception handler", "broad-exception", current.broad_exceptions, baseline.broad_exceptions),
        ("global statement", "global-state", current.global_statements, baseline.global_statements),
        ("module mutable state", "mutable-module-state", current.mutable_module_state, baseline.mutable_module_state),
    )
    issues: list[str] = []
    for label, rule_id, current_findings, baseline_findings in checks:
        if _is_waived(relpath, rule_id, waivers):
            continue
        for finding in _new_findings(current_findings, baseline_findings):
            issues.append(f"{relpath}:{finding.line}:{label}: {finding.detail}")
    return issues


def _check_source(
    relpath: str,
    current_text: str,
    baseline_text: str | None,
    *,
    max_public_parameters: int = MAX_PUBLIC_PARAMETERS,
    waivers: dict[str, dict[str, str]] | None = None,
) -> list[str]:
    try:
        current = _metrics(current_text)
    except SyntaxError as exc:
        return [f"{relpath}:{exc.lineno}: program-design could not parse changed Python ({exc.msg})"]
    baseline = _metrics(baseline_text) if baseline_text else DesignMetrics({}, (), (), (), ())
    issues: list[str] = []

    for name, (count, line) in sorted(current.public_parameters.items()):
        baseline_count = baseline.public_parameters.get(name, (0, 0))[0]
        if (
            count > max_public_parameters
            and count > baseline_count
            and not _is_waived(relpath, "public-interface", waivers)
        ):
            issues.append(
                f"{relpath}:{line}:{name} public interface is too wide ({count} parameters > {max_public_parameters})"
            )

    issues.extend(_check_smells(relpath, current, baseline, waivers))
    return issues


def _changed_paths(changed_files: tuple[str, ...]) -> list[Path]:
    paths: list[Path] = []
    for relpath in changed_files:
        normalized = relpath.removeprefix("./")
        path = (REPO_ROOT / normalized).resolve()
        if path.is_file() and _is_production_python(normalized):
            paths.append(path)
    return sorted(set(paths))


def main() -> int:
    args = parse_args()
    changed_files = tuple(args.changed_files)
    metadata_issues = _check_waiver_metadata()
    if metadata_issues:
        print("Program design waiver metadata failed:")
        for issue in metadata_issues:
            print(f"- {issue}")
        return 1
    if not changed_files:
        print("program_design: no changed production Python files supplied; baseline ratchet pass")
        return 0

    issues: list[str] = []
    scanned = 0
    for path in _changed_paths(changed_files):
        scanned += 1
        relpath = path.relative_to(REPO_ROOT).as_posix()
        issues.extend(
            _check_source(
                relpath,
                path.read_text(encoding="utf-8"),
                _git_head_text(path),
                max_public_parameters=max(1, int(args.max_public_parameters)),
            )
        )
    print(f"program_design: scanned={scanned}")
    if issues:
        print("Program design verification failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Program design verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
