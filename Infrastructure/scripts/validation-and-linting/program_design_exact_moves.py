"""Exact top-level move recognition for the program-design ratchet."""

from __future__ import annotations

import ast
import subprocess
from collections import Counter
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path, PurePosixPath


class MoveBaselineUnavailable(RuntimeError):
    """Raised when baseline siblings cannot be inspected."""


def _is_extraction_scaffolding(node: ast.stmt) -> bool:
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return True
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
        return True
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else (node.target,)
        return any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets)
    return False


def _normalize_docstring_whitespace(node: ast.AST) -> None:
    """Normalize layout-only docstring whitespace before move comparison."""

    containers = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    for candidate in ast.walk(node):
        if not isinstance(candidate, containers) or not candidate.body:
            continue
        first = candidate.body[0]
        if not (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            continue
        first.value.value = "\n".join(
            line.expandtabs(4).rstrip() for line in first.value.value.splitlines()
        )


def _top_level_move_fingerprints(source_text: str) -> Counter[str]:
    tree = ast.parse(source_text)
    _normalize_docstring_whitespace(tree)
    return Counter(
        ast.dump(node, include_attributes=False)
        for node in tree.body
        if not _is_extraction_scaffolding(node)
    )


@lru_cache(maxsize=128)
def baseline_sibling_sources(revision: str, parent: str, repo_root: Path) -> tuple[str, ...]:
    """Read direct Python siblings from *parent* at *revision*."""

    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", revision, "--", parent],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if listing.returncode != 0:
        detail = listing.stderr.strip() or "baseline sibling listing failed"
        raise MoveBaselineUnavailable(f"baseline sibling lookup failed for {parent}: {detail}")

    sources: list[str] = []
    for relpath in listing.stdout.splitlines():
        candidate = PurePosixPath(relpath)
        if candidate.parent.as_posix() != parent or candidate.suffix not in {".py", ".pyw"}:
            continue
        result = subprocess.run(
            ["git", "show", f"{revision}:{relpath}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or "baseline sibling could not be read"
            raise MoveBaselineUnavailable(f"baseline sibling lookup failed for {relpath}: {detail}")
        sources.append(result.stdout)
    return tuple(sources)


def exact_move_baseline(
    path: Path,
    current_text: str,
    revision: str,
    *,
    repo_root: Path,
    baseline_sources: Callable[[str, str], tuple[str, ...]],
) -> str | None:
    """Return *current_text* only when it is an exact extraction from one baseline sibling."""

    try:
        current_nodes = _top_level_move_fingerprints(current_text)
    except SyntaxError:
        return None
    if not current_nodes:
        return None

    parent = PurePosixPath(path.relative_to(repo_root).as_posix()).parent.as_posix()
    for source_text in baseline_sources(revision, parent):
        try:
            baseline_nodes = _top_level_move_fingerprints(source_text)
        except SyntaxError:
            continue
        if all(baseline_nodes[fingerprint] >= count for fingerprint, count in current_nodes.items()):
            return current_text
    return None


__all__ = ["MoveBaselineUnavailable", "baseline_sibling_sources", "exact_move_baseline"]
