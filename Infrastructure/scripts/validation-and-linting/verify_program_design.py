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
refactoring slice but do not make an unrelated change fail. New or worsened
findings fail until the owning change removes them.
"""

from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
import program_design_exact_moves as _exact_moves  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
MAX_PUBLIC_PARAMETERS = 5
PRODUCTION_PREFIXES = (
    "Infrastructure/bin/",
    "Infrastructure/scripts/",
    "Plugins/",
    "Skills/",
    "skills-system/",
)
EXCLUDED_PARTS: frozenset[str] = frozenset(
    {".venv", "__pycache__", "fixtures", "references", "tests", "test", "testing"}
)
BROAD_EXCEPTION_NAMES: frozenset[str] = frozenset({"Exception", "BaseException"})
MUTABLE_VALUE_NODES = (
    ast.Dict,
    ast.DictComp,
    ast.List,
    ast.ListComp,
    ast.Set,
    ast.SetComp,
)
MUTABLE_CONSTRUCTOR_NAMES: frozenset[str] = frozenset(
    {"Counter", "bytearray", "defaultdict", "deque", "dict", "list", "set"}
)
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


BaselineUnavailable = _exact_moves.MoveBaselineUnavailable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate changed Python program design.")
    parser.add_argument(
        "--changed-files",
        nargs="*",
        default=(),
        help="Repo-relative changed files to inspect; omitted means all tracked production Python files.",
    )
    parser.add_argument(
        "--max-public-parameters",
        type=int,
        default=MAX_PUBLIC_PARAMETERS,
        help="Maximum public function parameters before a new/worsened design finding.",
    )
    parser.add_argument(
        "--baseline-ref",
        default=None,
        help=(
            "Git revision used as the pre-change baseline; head-source validation "
            "defaults to the tracked upstream, otherwise the merge-base with the PR base."
        ),
    )
    parser.add_argument(
        "--staged-source",
        action="store_true",
        help="Read staged index blobs for staged paths; use only for staged pre-commit validation.",
    )
    parser.add_argument(
        "--source-ref",
        default=None,
        help="Read changed source blobs from this Git revision instead of the worktree.",
    )
    return parser.parse_args()


def _is_python_entrypoint(path: Path, *, source_text: str | None = None) -> bool:
    try:
        first_line = (source_text if source_text is not None else path.read_text(encoding="utf-8")).splitlines()[0]
    except (OSError, IndexError, UnicodeError):
        return False
    return first_line.startswith("#!") and "python" in first_line.lower()


def _is_production_python(
    relpath: str, *, path: Path | None = None, source_text: str | None = None
) -> bool:
    if not relpath.startswith(PRODUCTION_PREFIXES) or relpath.startswith("Plugins/cache/"):
        return False
    if not relpath.endswith((".py", ".pyw")) and (
        path is None or not _is_python_entrypoint(path, source_text=source_text)
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


def _is_staticmethod(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(
        (isinstance(decorator, ast.Name) and decorator.id == "staticmethod")
        or (isinstance(decorator, ast.Attribute) and decorator.attr == "staticmethod")
        for decorator in node.decorator_list
    )


def _parameter_count(node: ast.FunctionDef | ast.AsyncFunctionDef, *, bound_method: bool = False) -> int:
    positional = list(node.args.posonlyargs) + list(node.args.args)
    if bound_method and positional and positional[0].arg in {"self", "cls"}:
        positional = positional[1:]
    count = len(positional) + len(node.args.kwonlyargs)
    if node.args.vararg is not None:
        count += 1
    if node.args.kwarg is not None:
        count += 1
    return count


def _boolean_flag_findings(
    node: ast.FunctionDef | ast.AsyncFunctionDef, qualified_name: str
) -> list[Finding]:
    findings: list[Finding] = []
    positional = list(node.args.posonlyargs) + list(node.args.args)
    positional_defaults = [None] * (len(positional) - len(node.args.defaults)) + list(node.args.defaults)
    findings.extend(_boolean_default_findings(qualified_name, positional, positional_defaults))
    findings.extend(_boolean_default_findings(qualified_name, node.args.kwonlyargs, node.args.kw_defaults))
    return findings


def _boolean_default_findings(
    qualified_name: str,
    arguments: list[ast.arg],
    defaults: list[ast.expr | None],
) -> list[Finding]:
    findings: list[Finding] = []
    if len(arguments) != len(defaults):
        raise ValueError("argument and default lists must have the same length")
    for argument, default in zip(arguments, defaults):
        if isinstance(default, ast.Constant) and isinstance(default.value, bool):
            findings.append(
                Finding(
                    argument.lineno,
                    f"{qualified_name}:{argument.arg}",
                    f"{qualified_name}({argument.arg}=bool)",
                )
            )
    return findings


def _broad_exceptions(tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        for name in _exception_names(node.type):
            if name in BROAD_EXCEPTION_NAMES or name == "bare":
                findings.append(
                    Finding(
                        node.lineno,
                        name,
                        f"except {name}",
                    )
                )
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
    if isinstance(node, ast.Starred):
        return _target_names(node.value)
    if isinstance(node, (ast.Tuple, ast.List)):
        names: list[str] = []
        for element in node.elts:
            names.extend(_target_names(element))
        return names
    return []


def _is_mutable_value(value: ast.expr | None) -> bool:
    if isinstance(value, MUTABLE_VALUE_NODES):
        return True
    if isinstance(value, ast.Tuple):
        return any(_is_mutable_value(element) for element in value.elts)
    if not isinstance(value, ast.Call):
        return False
    if isinstance(value.func, ast.Name):
        constructor_name = value.func.id
    elif isinstance(value.func, ast.Attribute):
        constructor_name = value.func.attr
    else:
        return False
    return constructor_name in MUTABLE_CONSTRUCTOR_NAMES


def _mutable_target_names(target: ast.expr, value: ast.expr | None) -> list[str]:
    if (
        isinstance(target, (ast.Tuple, ast.List))
        and isinstance(value, (ast.Tuple, ast.List))
        and len(target.elts) == len(value.elts)
    ):
        names: list[str] = []
        for target_element, value_element in zip(target.elts, value.elts, strict=True):
            names.extend(_mutable_target_names(target_element, value_element))
        return names
    if _is_mutable_value(value):
        return _target_names(target)
    return []


class _ModuleMutableStateVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_definition_time(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_definition_time(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        defaults = (
            *node.args.defaults,
            *(default for default in node.args.kw_defaults if default is not None),
        )
        for default in defaults:
            self.visit(default)

    def visit_ClassDef(self, _node: ast.ClassDef) -> None:
        self.generic_visit(_node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._record(node, node.targets, node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._record(node, [node.target], node.value)
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self._record(node, [node.target], node.value)
        self.generic_visit(node)

    def _visit_definition_time(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        expressions = (
            *node.decorator_list,
            node.returns,
            *node.args.defaults,
            *(default for default in node.args.kw_defaults if default is not None),
        )
        for expression in expressions:
            if expression is not None:
                self.visit(expression)

    def _record(self, node: ast.AST, targets: list[ast.expr], value: ast.expr | None) -> None:
        for target in targets:
            for name in _mutable_target_names(target, value):
                if name == "__all__":
                    continue
                self.findings.append(Finding(node.lineno, name, f"module mutable state {name}"))


def _mutable_module_state(tree: ast.Module) -> list[Finding]:
    visitor = _ModuleMutableStateVisitor()
    visitor.visit(tree)
    return visitor.findings


class _PublicFunctionCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.scope: tuple[str, ...] = ()
        self.functions: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef, bool]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if node.name.startswith("_"):
            return
        previous_scope = self.scope
        self.scope = (*previous_scope, node.name)
        for statement in node.body:
            self.visit(statement)
        self.scope = previous_scope

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record(node)

    def _record(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if node.name.startswith("_") and not (node.name.startswith("__") and node.name.endswith("__")):
            return
        qualified_name = ".".join((*self.scope, node.name))
        self.functions.append((qualified_name, node, bool(self.scope) and not _is_staticmethod(node)))


def _public_functions(tree: ast.Module) -> list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef, bool]]:
    collector = _PublicFunctionCollector()
    collector.visit(tree)
    return collector.functions


def _metrics(text: str) -> DesignMetrics:
    tree = ast.parse(text)
    public_parameters: dict[str, tuple[int, int]] = {}
    boolean_flags: list[Finding] = []
    for qualified_name, node, bound_method in _public_functions(tree):
        public_parameters[qualified_name] = (_parameter_count(node, bound_method=bound_method), node.lineno)
        boolean_flags.extend(_boolean_flag_findings(node, qualified_name))
    return DesignMetrics(
        public_parameters=public_parameters,
        boolean_flags=tuple(boolean_flags),
        broad_exceptions=tuple(_broad_exceptions(tree)),
        global_statements=tuple(_global_statements(tree)),
        mutable_module_state=tuple(_mutable_module_state(tree)),
    )


def _validate_baseline_ref(revision: str) -> None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{revision}^{{commit}}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "revision could not be resolved"
        raise BaselineUnavailable(f"baseline revision {revision!r} is unavailable: {detail}")


@lru_cache(maxsize=8)
def _rename_map(revision: str, *, staged: bool) -> dict[str, str]:
    command = ["git", "diff", "--find-renames", "--name-status"]
    command.extend(["--cached", revision] if staged else [revision, "HEAD"])
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "rename map could not be inspected"
        raise BaselineUnavailable(f"baseline rename lookup failed: {detail}")
    mapping: dict[str, str] = {}
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) >= 3 and fields[0].startswith("R"):
            mapping[fields[2]] = fields[1]
    return mapping


@lru_cache(maxsize=1)
def _staged_paths() -> frozenset[str]:
    changed = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT", "--"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if changed.returncode != 0:
        detail = changed.stderr.strip() or "staged file list could not be read"
        raise BaselineUnavailable(f"staged source lookup failed: {detail}")
    index = subprocess.run(
        ["git", "ls-files", "--stage", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if index.returncode != 0:
        detail = index.stderr.strip() or "Git index could not be read"
        raise BaselineUnavailable(f"staged source lookup failed: {detail}")
    regular_paths = {
        path
        for entry in index.stdout.split("\0")
        for metadata, separator, path in (entry.partition("\t"),)
        if separator and metadata.partition(" ")[0] in {"100644", "100755"}
    }
    return frozenset(path for path in changed.stdout.splitlines() if path in regular_paths)


def _current_source_text(
    path: Path,
    *,
    staged_source: bool = False,
    source_ref: str | None = None,
) -> str:
    relpath = path.relative_to(REPO_ROOT).as_posix()
    if source_ref is not None:
        revision_path = f"{source_ref}:{relpath}"
        error_prefix = "source revision"
    elif not staged_source or relpath not in _staged_paths():
        return path.read_text(encoding="utf-8")
    else:
        revision_path = f":{relpath}"
        error_prefix = "staged source"
    result = subprocess.run(
        ["git", "show", revision_path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or f"{error_prefix} file could not be read"
        raise BaselineUnavailable(f"{error_prefix} lookup failed for {relpath}: {detail}")
    return result.stdout


def _baseline_path(relpath: str, revision: str) -> str:
    staged_path = _rename_map(revision, staged=True).get(relpath)
    if staged_path and _is_production_baseline_path(staged_path, revision):
        return staged_path
    renamed_path = _rename_map(revision, staged=False).get(relpath)
    if renamed_path and _is_production_baseline_path(renamed_path, revision):
        return renamed_path
    return relpath


def _is_production_baseline_path(relpath: str, revision: str) -> bool:
    path = REPO_ROOT / relpath
    source_text = None
    if not relpath.endswith((".py", ".pyw")):
        result = subprocess.run(
            ["git", "show", f"{revision}:{relpath}"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return False
        source_text = result.stdout
    return _is_production_python(relpath, path=path, source_text=source_text)


def _git_revision_text(path: Path, revision: str) -> str | None:
    relpath = path.relative_to(REPO_ROOT).as_posix()
    baseline_path = _baseline_path(relpath, revision)
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}:{baseline_path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if exists.returncode != 0:
        return None
    result = subprocess.run(
        ["git", "show", f"{revision}:{baseline_path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "baseline file could not be read"
        raise BaselineUnavailable(f"baseline file lookup failed for {baseline_path}: {detail}")
    return result.stdout


def _baseline_sibling_sources(revision: str, parent: str) -> tuple[str, ...]:
    return _exact_moves.baseline_sibling_sources(revision, parent, REPO_ROOT)


def _exact_move_baseline(path: Path, current_text: str, revision: str) -> str | None:
    return _exact_moves.exact_move_baseline(
        path, current_text, revision, repo_root=REPO_ROOT, baseline_sources=_baseline_sibling_sources
    )


def _new_findings(current: tuple[Finding, ...], baseline: tuple[Finding, ...]) -> list[Finding]:
    def identity(item: Finding) -> tuple[str, str]:
        return item.key, item.detail

    baseline_remaining = Counter(identity(item) for item in baseline)
    findings: list[Finding] = []
    for item in sorted(current, key=lambda finding: (finding.line, finding.key)):
        item_identity = identity(item)
        if baseline_remaining[item_identity] > 0:
            baseline_remaining[item_identity] -= 1
            continue
        findings.append(item)
    return findings


def _check_smells(
    relpath: str,
    current: DesignMetrics,
    baseline: DesignMetrics,
) -> list[str]:
    checks = (
        ("boolean flag argument", current.boolean_flags, baseline.boolean_flags),
        ("broad exception handler", current.broad_exceptions, baseline.broad_exceptions),
        ("global statement", current.global_statements, baseline.global_statements),
        ("module mutable state", current.mutable_module_state, baseline.mutable_module_state),
    )
    issues: list[str] = []
    for label, current_findings, baseline_findings in checks:
        for finding in _new_findings(current_findings, baseline_findings):
            issues.append(f"{relpath}:{finding.line}:{label}: {finding.detail}")
    return issues


def _check_source(
    relpath: str,
    current_text: str,
    baseline_text: str | None,
    *,
    max_public_parameters: int = MAX_PUBLIC_PARAMETERS,
) -> list[str]:
    try:
        current = _metrics(current_text)
    except SyntaxError as exc:
        return [f"{relpath}:{exc.lineno}: program-design could not parse changed Python ({exc.msg})"]
    if not baseline_text:
        baseline = DesignMetrics({}, (), (), (), ())
    else:
        try:
            baseline = _metrics(baseline_text)
        except SyntaxError as exc:
            return [
                f"{relpath}:{exc.lineno}: program-design baseline could not parse pre-change Python ({exc.msg})"
            ]
    issues: list[str] = []

    for name, (count, line) in sorted(current.public_parameters.items()):
        baseline_count = baseline.public_parameters.get(name, (0, 0))[0]
        if (
            count > max_public_parameters
            and count > baseline_count
        ):
            issues.append(
                f"{relpath}:{line}:{name} public interface is too wide ({count} parameters > {max_public_parameters})"
            )

    issues.extend(_check_smells(relpath, current, baseline))
    return issues


def _is_changed_production_python(
    normalized: str,
    path: Path,
    staged_paths: frozenset[str],
    *,
    staged_source: bool,
    source_ref: str | None,
) -> bool:
    parts = Path(normalized).parts
    if not normalized.startswith(PRODUCTION_PREFIXES) or normalized.startswith("Plugins/cache/") or set(parts) & EXCLUDED_PARTS or any(part.startswith("test_") for part in parts):
        return False
    is_staged = normalized in staged_paths
    if not path.is_file() and not is_staged and source_ref is None:
        return False
    source_text = None
    if not normalized.endswith((".py", ".pyw")):
        try:
            source_text = _current_source_text(path, staged_source=staged_source, source_ref=source_ref)
        except UnicodeDecodeError:
            source_text = ""
    return _is_production_python(normalized, path=path, source_text=source_text)


def _changed_candidate(
    normalized: str,
    staged_paths: frozenset[str],
    *,
    staged_source: bool,
) -> Path | None:
    relative = Path(normalized)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    if staged_source and normalized not in staged_paths:
        return None
    candidate = REPO_ROOT / normalized
    return candidate if staged_source else candidate.resolve()


def _changed_paths(
    changed_files: tuple[str, ...], *, staged_source: bool = False, source_ref: str | None = None
) -> list[Path]:
    if not changed_files:
        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if tracked.returncode != 0:
            detail = tracked.stderr.strip() or "tracked file list could not be read"
            raise BaselineUnavailable(f"production file discovery failed: {detail}")
        changed_files = tuple(line for line in tracked.stdout.splitlines() if line)
    staged_paths = _staged_paths() if staged_source else frozenset()
    paths: list[Path] = []
    for relpath in changed_files:
        normalized = relpath.removeprefix("./")
        path = _changed_candidate(normalized, staged_paths, staged_source=staged_source)
        if path is None:
            continue
        try:
            path.relative_to(REPO_ROOT)
        except ValueError:
            continue
        if _is_changed_production_python(
            normalized, path, staged_paths, staged_source=staged_source, source_ref=source_ref
        ):
            paths.append(path)
    return sorted(set(paths))


def _default_baseline_ref(*, staged_source: bool = False, source_ref: str | None = None) -> str | None:
    if staged_source:
        return "HEAD"
    if source_ref == "HEAD":
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "@{upstream}^{commit}"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return "@{upstream}"
    base_branch = os.environ.get("GITHUB_BASE_REF")
    candidates = [f"origin/{base_branch}"] if base_branch else []
    candidates.extend(("origin/main", "HEAD^"))
    for candidate in candidates:
        result = subprocess.run(
            ["git", "merge-base", "HEAD", candidate],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return None


def _scan_paths(
    changed_files: tuple[str, ...],
    baseline_ref: str,
    max_public_parameters: int,
    *,
    staged_source: bool,
    source_ref: str | None,
) -> tuple[int, list[str]]:
    issues: list[str] = []
    paths = _changed_paths(changed_files, staged_source=staged_source, source_ref=source_ref)
    for path in paths:
        relpath = path.relative_to(REPO_ROOT).as_posix()
        current_text = _current_source_text(
            path, staged_source=staged_source, source_ref=source_ref
        )
        baseline_text = _git_revision_text(path, baseline_ref)
        if baseline_text is None:
            baseline_text = _exact_move_baseline(path, current_text, baseline_ref)
        issues.extend(
            _check_source(
                relpath,
                current_text,
                baseline_text,
                max_public_parameters=max_public_parameters,
            )
        )
    return len(paths), issues


def main() -> int:
    args = parse_args()
    changed_files = tuple(args.changed_files)
    baseline_ref = args.baseline_ref or _default_baseline_ref(staged_source=args.staged_source, source_ref=args.source_ref)
    if not baseline_ref:
        print("Program design verification blocked: baseline revision could not be determined")
        return 1
    try:
        _validate_baseline_ref(baseline_ref)
    except BaselineUnavailable as exc:
        print(f"Program design verification blocked: {exc}")
        return 1
    try:
        scanned, issues = _scan_paths(
            changed_files,
            baseline_ref,
            max(1, int(args.max_public_parameters)),
            staged_source=args.staged_source,
            source_ref=args.source_ref,
        )
    except BaselineUnavailable as exc:
        print(f"Program design verification blocked: {exc}")
        return 1
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
