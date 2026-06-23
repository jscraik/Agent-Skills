from __future__ import annotations

import ast
import json
import shlex
from pathlib import Path
from typing import Any, Literal

from ask.skills_sdk.capability_status import MATRIX_PATH, load_capability_matrix


CAPABILITY_EVIDENCE_SCHEMA_VERSION = "skills-sdk.capability-evidence-receipt.v0"
CAPABILITY_EVIDENCE_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/capability-evidence-receipt.v0.schema.json"
)
CAPABILITY_EVIDENCE_ACCEPTANCE_TRACE = ["PU-032", "FR-008", "SA-003", "VP-032"]
COMMAND_STARTERS = frozenset({"./bin/ask", "./bin/skills-sdk", "ask", "python3", "uv", "bash"})
EXTERNAL_MARKERS = ("github", "circleci", "tessl", "snyk", "http://", "https://")

EvidenceKind = Literal["file", "command", "schema", "receipt", "external_lane", "unknown"]
EvidenceStatus = Literal["pass", "blocked", "not_run", "unknown"]


def build_capability_evidence_receipt(repo_root: Path, *, scope: str = "capability-matrix") -> dict[str, Any]:
    if scope != "capability-matrix":
        raise ValueError("capability evidence verification currently supports only scope=capability-matrix")

    matrix = load_capability_matrix(repo_root)
    rows = [
        _evidence_row(repo_root, capability["id"], evidence_ref)
        for capability in matrix["capabilities"]
        for evidence_ref in capability["evidence_refs"]
    ]
    blockers = [row for row in rows if row["status"] in {"blocked", "unknown"}]
    not_run_count = sum(1 for row in rows if row["status"] == "not_run")
    pass_count = sum(1 for row in rows if row["status"] == "pass")
    unknown_count = sum(1 for row in rows if row["kind"] == "unknown")
    return {
        "schema_version": CAPABILITY_EVIDENCE_SCHEMA_VERSION,
        "schema_uri": CAPABILITY_EVIDENCE_SCHEMA_URI,
        "status": "blocked" if blockers else "pass",
        "operation": "capability_evidence_verify",
        "scope": scope,
        "matrix_path": MATRIX_PATH.as_posix(),
        "capability_count": len(matrix["capabilities"]),
        "evidence_ref_count": len(rows),
        "pass_count": pass_count,
        "blocked_count": len(blockers),
        "not_run_count": not_run_count,
        "unknown_count": unknown_count,
        "evidence_rows": rows,
        "blockers": blockers,
        "mutation_performed": False,
        "command_execution_performed": False,
        "acceptance_trace": CAPABILITY_EVIDENCE_ACCEPTANCE_TRACE,
        "agent_summary": _agent_summary(len(rows), pass_count, len(blockers), not_run_count),
    }


def _agent_summary(total: int, pass_count: int, blocked_count: int, not_run_count: int) -> str:
    return (
        "Capability evidence verification checked "
        f"{total} evidence ref(s): {pass_count} passed, {blocked_count} blocked, "
        f"and {not_run_count} command or external lane ref(s) were classified but not run."
    )


def _evidence_row(repo_root: Path, capability_id: str, evidence_ref: str) -> dict[str, Any]:
    kind, status, reason, evidence, lane = _classify_ref(repo_root, evidence_ref)
    return {
        "capability_id": capability_id,
        "ref": evidence_ref,
        "kind": kind,
        "status": status,
        "reason": reason,
        "evidence": evidence,
        "lane": lane,
        "executes_command": kind == "command",
    }


def _classify_ref(repo_root: Path, evidence_ref: str) -> tuple[EvidenceKind, EvidenceStatus, str, list[str], str]:
    stripped = evidence_ref.strip()
    if not stripped:
        return "unknown", "unknown", "Evidence ref is empty.", [], "local"
    if _is_external_url(stripped):
        return "external_lane", "not_run", "External evidence lanes require their own receipt.", [stripped], "external"
    command_tokens = _command_tokens(stripped)
    if command_tokens:
        return "command", "not_run", "Command evidence is classified but not executed by preview verification.", [command_tokens[0]], "local_command"

    node_ref = _split_pytest_node_ref(stripped)
    if node_ref is not None:
        return _pytest_node_status(repo_root, stripped, node_ref)

    candidate = _resolve_repo_path(repo_root, stripped)
    if stripped.endswith(".schema.json"):
        return _schema_status(repo_root, stripped, candidate)
    if _looks_like_receipt(stripped):
        return _receipt_status(repo_root, stripped, candidate)
    if candidate is not None:
        return _file_status(repo_root, stripped, candidate, "file")
    if _is_external(stripped):
        return "external_lane", "not_run", "External evidence lanes require their own receipt.", [stripped], "external"
    return "unknown", "blocked", "Evidence ref is neither a known command nor a repo-local file.", [stripped], "local"


def _is_external_url(evidence_ref: str) -> bool:
    lowered = evidence_ref.lower()
    return lowered.startswith(("http://", "https://"))


def _is_external(evidence_ref: str) -> bool:
    lowered = evidence_ref.lower()
    return any(marker in lowered for marker in EXTERNAL_MARKERS)


def _command_tokens(evidence_ref: str) -> list[str]:
    try:
        tokens = shlex.split(evidence_ref)
    except ValueError:
        return []
    if not tokens:
        return []
    first = tokens[0]
    if first in COMMAND_STARTERS or _known_absolute_command_tokens(tokens):
        return tokens
    return []


def _known_absolute_command_tokens(tokens: list[str]) -> bool:
    if len(tokens) < 2:
        return False
    command = Path(tokens[0])
    if not command.is_absolute():
        return False
    return command.name in {"python", "python3"} and command.parent.name == "bin"


def _resolve_repo_path(repo_root: Path, evidence_ref: str) -> Path | None:
    if any(char.isspace() for char in evidence_ref):
        return None
    path = Path(evidence_ref)
    if path.is_absolute():
        resolved = path.resolve(strict=False)
    else:
        resolved = (repo_root / path).resolve(strict=False)
    if not resolved.is_relative_to(repo_root.resolve()):
        return None
    return resolved


def _split_pytest_node_ref(evidence_ref: str) -> tuple[str, str] | None:
    if "::" not in evidence_ref:
        return None
    path_text, node_id = evidence_ref.split("::", 1)
    if not path_text.endswith(".py") or not node_id:
        return None
    return path_text, node_id


def _repo_relative(repo_root: Path, path: Path) -> str:
    return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()


def _file_status(
    repo_root: Path,
    evidence_ref: str,
    candidate: Path | None,
    kind: EvidenceKind,
) -> tuple[EvidenceKind, EvidenceStatus, str, list[str], str]:
    if candidate is None:
        return kind, "blocked", "Evidence ref does not resolve inside the repository.", [evidence_ref], "local"
    if not candidate.exists():
        return kind, "blocked", "Evidence file does not exist.", [_repo_relative(repo_root, candidate)], "local"
    return kind, "pass", "Evidence file exists inside the repository.", [_repo_relative(repo_root, candidate)], "local"


def _json_artifact_status(
    repo_root: Path,
    evidence_ref: str,
    candidate: Path | None,
    kind: Literal["schema", "receipt"],
) -> tuple[EvidenceKind, EvidenceStatus, str, list[str], str]:
    kind_status, status, reason, evidence, lane = _file_status(repo_root, evidence_ref, candidate, kind)
    if status != "pass" or candidate is None:
        return kind_status, status, reason, evidence, lane
    kind_label = kind.capitalize()
    try:
        json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return kind, "blocked", f"{kind_label} evidence file did not parse as JSON: {exc}", evidence, "local"
    return kind, "pass", f"{kind_label} evidence file exists and parses as JSON.", evidence, "local"


def _schema_status(repo_root: Path, evidence_ref: str, candidate: Path | None) -> tuple[EvidenceKind, EvidenceStatus, str, list[str], str]:
    return _json_artifact_status(repo_root, evidence_ref, candidate, "schema")


def _receipt_status(repo_root: Path, evidence_ref: str, candidate: Path | None) -> tuple[EvidenceKind, EvidenceStatus, str, list[str], str]:
    return _json_artifact_status(repo_root, evidence_ref, candidate, "receipt")


def _pytest_node_status(
    repo_root: Path,
    evidence_ref: str,
    node_ref: tuple[str, str],
) -> tuple[EvidenceKind, EvidenceStatus, str, list[str], str]:
    path_text, node_id = node_ref
    candidate = _resolve_repo_path(repo_root, path_text)
    kind, status, reason, evidence, lane = _file_status(repo_root, path_text, candidate, "file")
    if status != "pass" or candidate is None:
        return kind, status, reason, [evidence_ref], lane
    try:
        text = candidate.read_text(encoding="utf-8")
    except OSError as exc:
        return "file", "blocked", f"Pytest node evidence file could not be read: {exc}", [evidence_ref], "local"
    if not _pytest_node_exists(text, node_id):
        return "file", "blocked", "Pytest node evidence file exists but named test was not found.", [evidence_ref], "local"
    return "file", "pass", "Pytest node evidence file exists and named test is present.", [evidence_ref], "local"


def _pytest_node_exists(text: str, node_id: str) -> bool:
    parts = [part for part in node_id.split("::") if part]
    if not parts:
        return False
    parts[-1] = parts[-1].split("[", 1)[0]
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False
    nodes: list[ast.stmt] = list(tree.body)
    for index, part in enumerate(parts):
        is_leaf = index == len(parts) - 1
        if is_leaf:
            return any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == part for node in nodes)
        class_node = next((node for node in nodes if isinstance(node, ast.ClassDef) and node.name == part), None)
        if class_node is None:
            return False
        nodes = list(class_node.body)
    return False


def _looks_like_receipt(evidence_ref: str) -> bool:
    path = Path(evidence_ref)
    return path.suffix == ".json" and "receipt" in path.name
