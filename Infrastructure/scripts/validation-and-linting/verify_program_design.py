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
import os
import subprocess
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType


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
    {".venv", "__pycache__", "fixtures", "references", "tests", "test"}
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
MUTABLE_CONSTRUCTOR_NAMES: frozenset[str] = frozenset({"bytearray", "defaultdict", "dict", "list", "set"})
PROGRAM_DESIGN_WAIVERS: Mapping[str, Mapping[str, str]] = MappingProxyType({})
WAIVER_FIELDS = ("owner", "rule_id", "ticket", "reason", "expires")
PUBLIC_DUNDER_NAMES = frozenset({"__init__", "__new__"})


@dataclass(frozen=True)
class Finding:
    """A source location and stable key for one design smell."""

    line: int
    key: str
    detail: str
    waiver_key: str | None = None

    @property
    def effective_waiver_key(self) -> str:
        return self.waiver_key or self.key


@dataclass(frozen=True)
class DesignMetrics:
    """AST-derived metrics used by the ratchet."""

    public_parameters: dict[str, tuple[int, int]]
    boolean_flags: tuple[Finding, ...]
    broad_exceptions: tuple[Finding, ...]
    global_statements: tuple[Finding, ...]
    mutable_module_state: tuple[Finding, ...]


class BaselineUnavailable(RuntimeError):
    """Raised when the requested Git baseline cannot be inspected."""


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
        help="Git revision used as the pre-change baseline; defaults to the merge-base with the PR base.",
    )
    parser.add_argument(
        "--staged-source",
        action="store_true",
        help="Read staged index blobs for staged paths; use only for staged pre-commit validation.",
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
                        f"{name}@{node.lineno}:{node.col_offset}",
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
        for target_element, value_element in zip(target.elts, value.elts):
            names.extend(_mutable_target_names(target_element, value_element))
        return names
    if _is_mutable_value(value):
        return _target_names(target)
    return []


class _ModuleMutableStateVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def visit_FunctionDef(self, _node: ast.FunctionDef) -> None:
        return None

    def visit_AsyncFunctionDef(self, _node: ast.AsyncFunctionDef) -> None:
        return None

    def visit_ClassDef(self, _node: ast.ClassDef) -> None:
        return None

    def visit_Assign(self, node: ast.Assign) -> None:
        self._record(node, node.targets, node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._record(node, [node.target], node.value)
        self.generic_visit(node)

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
        if node.name.startswith("_") and node.name not in PUBLIC_DUNDER_NAMES:
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
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "--"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "staged file list could not be read"
        raise BaselineUnavailable(f"staged source lookup failed: {detail}")
    return frozenset(line for line in result.stdout.splitlines() if line)


def _current_source_text(path: Path, *, staged_source: bool = False) -> str:
    relpath = path.relative_to(REPO_ROOT).as_posix()
    if not staged_source or relpath not in _staged_paths():
        return path.read_text(encoding="utf-8")
    result = subprocess.run(
        ["git", "show", f":{relpath}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "staged file could not be read"
        raise BaselineUnavailable(f"staged source lookup failed for {relpath}: {detail}")
    return result.stdout


def _baseline_path(relpath: str, revision: str) -> str:
    staged_path = _rename_map(revision, staged=True).get(relpath)
    if staged_path:
        return staged_path
    return _rename_map(revision, staged=False).get(relpath, relpath)


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


def _check_waiver_metadata(
    waivers: Mapping[str, Mapping[str, str]] | None,
    *,
    validation_date: date,
) -> list[str]:
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
        if expires < validation_date:
            issues.append(f"{key} program-design waiver expired on {metadata['expires']}")
    return issues


def _is_waived(
    relpath: str,
    rule_id: str,
    finding: Finding | str,
    waivers: Mapping[str, Mapping[str, str]] | None,
) -> bool:
    finding_key = finding.effective_waiver_key if isinstance(finding, Finding) else finding
    return f"{relpath}:{rule_id}:{finding_key}" in (waivers or PROGRAM_DESIGN_WAIVERS)


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
    waivers: Mapping[str, Mapping[str, str]] | None,
) -> list[str]:
    checks = (
        ("boolean flag argument", "boolean-flag", current.boolean_flags, baseline.boolean_flags),
        ("broad exception handler", "broad-exception", current.broad_exceptions, baseline.broad_exceptions),
        ("global statement", "global-state", current.global_statements, baseline.global_statements),
        ("module mutable state", "mutable-module-state", current.mutable_module_state, baseline.mutable_module_state),
    )
    issues: list[str] = []
    for label, rule_id, current_findings, baseline_findings in checks:
        for finding in _new_findings(current_findings, baseline_findings):
            if _is_waived(relpath, rule_id, finding, waivers):
                continue
            issues.append(f"{relpath}:{finding.line}:{label}: {finding.detail}")
    return issues


def _check_source(
    relpath: str,
    current_text: str,
    baseline_text: str | None,
    *,
    max_public_parameters: int = MAX_PUBLIC_PARAMETERS,
    waivers: Mapping[str, Mapping[str, str]] | None = None,
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
            and not _is_waived(relpath, "public-interface", name, waivers)
        ):
            issues.append(
                f"{relpath}:{line}:{name} public interface is too wide ({count} parameters > {max_public_parameters})"
            )

    issues.extend(_check_smells(relpath, current, baseline, waivers))
    return issues


def _is_changed_production_python(
    normalized: str,
    path: Path,
    staged_paths: frozenset[str],
    *,
    staged_source: bool,
) -> bool:
    is_staged = normalized in staged_paths
    if not path.is_file() and not is_staged:
        return False
    source_text = None
    if not normalized.endswith((".py", ".pyw")):
        try:
            source_text = _current_source_text(path, staged_source=staged_source)
        except UnicodeDecodeError:
            source_text = ""
    return _is_production_python(normalized, path=path, source_text=source_text)


def _changed_paths(changed_files: tuple[str, ...], *, staged_source: bool = False) -> list[Path]:
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
        candidate = REPO_ROOT / normalized
        path = candidate.resolve()
        try:
            path.relative_to(REPO_ROOT)
        except ValueError:
            continue
        if _is_changed_production_python(normalized, path, staged_paths, staged_source=staged_source):
            paths.append(path)
    return sorted(set(paths))


def _default_baseline_ref() -> str | None:
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
) -> tuple[int, list[str]]:
    issues: list[str] = []
    paths = _changed_paths(changed_files, staged_source=staged_source)
    for path in paths:
        relpath = path.relative_to(REPO_ROOT).as_posix()
        baseline_text = _git_revision_text(path, baseline_ref)
        issues.extend(
            _check_source(
                relpath,
                _current_source_text(path, staged_source=staged_source),
                baseline_text,
                max_public_parameters=max_public_parameters,
            )
        )
    return len(paths), issues


def main() -> int:
    args = parse_args()
    changed_files = tuple(args.changed_files)
    metadata_issues = _check_waiver_metadata(
        None,
        validation_date=date.today(),
    )
    if metadata_issues:
        print("Program design waiver metadata failed:")
        for issue in metadata_issues:
            print(f"- {issue}")
        return 1
    baseline_ref = args.baseline_ref or _default_baseline_ref()
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
