from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from ask.skills_sdk.lenses import select_lenses
from ask.skills_sdk.id_types import new_branded_id


REVIEW_PLAN_SCHEMA_VERSION = "skills-sdk.review-plan-receipt.v1"
REVIEW_PLAN_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json"
)
REVIEW_PLAN_TRACE_SCHEMA_VERSION = "skills-sdk.review-plan-trace.v1"
REVIEW_PLAN_TRACE_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/sdk-review-plan-trace.v1.schema.json"
)
TRACE_DIR = Path(".harness/artifacts/sdk-review-plan/traces")


def build_review_plan(
    repo_root: Path,
    *,
    target: str,
    task_intent: str,
    prompt: str | None = None,
    repo_files: list[str] | None = None,
    max_lenses: int = 4,
    receipt_out: str | None = None,
    id_provider: Callable[[], str] | None = None,
    clock_provider: Callable[[], datetime] | None = None,
) -> dict[str, object]:
    if max_lenses < 1:
        raise ValueError("max_lenses must be at least 1.")

    source_context = _source_context(
        repo_root,
        target,
        id_provider=id_provider or _default_id_provider,
        clock_provider=clock_provider or _default_clock_provider,
    )
    target_kind = str(source_context["target_kind"])
    prompt_text = prompt or _default_prompt(target=target, task_intent=task_intent, target_kind=target_kind)
    target_files = _repo_file_signals(target=target, target_kind=target_kind, repo_files=repo_files or [])
    selection = select_lenses(
        repo_root,
        prompt=prompt_text,
        task_intent=task_intent,
        repo_files=target_files,
        max_lenses=max_lenses,
        skill=target,
    )
    if selection["status"] != "pass":
        return {
            "schema_version": REVIEW_PLAN_SCHEMA_VERSION,
            "schema_uri": REVIEW_PLAN_SCHEMA_URI,
            "status": "fail",
            "target": target,
            "target_kind": target_kind,
            "task_intent": task_intent,
            "prompt": prompt_text,
            "selected_lenses": [],
            "review_focus": [],
            "recommended_checks": [],
            "evidence_to_collect": [],
            "risk_flags": ["lens_catalog_validation_failed"],
            "source_context": source_context,
            "next_commands": ["./bin/ask sdk lenses validate --json --robot"],
            "mutation_performed": False,
            "receipt_written": False,
            "receipt_path": None,
        }

    selected = selection["selected_lenses"]
    receipt: dict[str, object] = {
        "schema_version": REVIEW_PLAN_SCHEMA_VERSION,
        "schema_uri": REVIEW_PLAN_SCHEMA_URI,
        "status": "pass",
        "target": target,
        "target_kind": target_kind,
        "task_intent": selection["task_intent"],
        "prompt": prompt_text,
        "selected_lenses": selected,
        "review_focus": _review_focus(selected),
        "recommended_checks": _recommended_checks(target=target, target_kind=target_kind, task_intent=task_intent),
        "evidence_to_collect": _evidence_to_collect(target_kind=target_kind),
        "risk_flags": _risk_flags(target_kind=target_kind, selected_lenses=selected),
        "source_context": source_context,
        "next_commands": _next_commands(target=target, task_intent=task_intent),
        "mutation_performed": False,
        "receipt_written": False,
        "receipt_path": None,
    }
    if receipt_out:
        receipt_path = _safe_receipt_path(repo_root, receipt_out)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt["receipt_written"] = True
        receipt["receipt_path"] = _repo_relative(repo_root, receipt_path)
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _write_trace_sidecar(
            repo_root,
            receipt=receipt,
            receipt_path=receipt_path,
            target=target,
            task_intent=task_intent,
        )
    return receipt


def _default_id_provider() -> str:
    return new_branded_id("rp")


def _default_clock_provider() -> datetime:
    return datetime.now(timezone.utc)


def _format_receipt_created_at(created_at: datetime) -> str:
    if created_at.tzinfo is None or created_at.utcoffset() is None:
        raise ValueError("clock_provider must return a timezone-aware datetime.")
    return created_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _source_context(
    repo_root: Path,
    target: str,
    *,
    id_provider: Callable[[], str],
    clock_provider: Callable[[], datetime],
) -> dict[str, object]:
    target_info = _target_info(repo_root, target)
    return {
        "repo_root": str(repo_root.resolve()),
        "head_sha": _head_sha(repo_root),
        "branch": _branch_name(repo_root),
        "branch_policy": "same_head_required",
        "receipt_instance_id": id_provider(),
        "receipt_created_at": _format_receipt_created_at(clock_provider()),
        "target_input": target,
        "target_kind": target_info["target_kind"],
        "target_identity": target_info["target_identity"],
        "target_resolved_path": target_info["target_resolved_path"],
        "target_content_digest": target_info["target_content_digest"],
        "target_digest_status": target_info["target_digest_status"],
        "provenance_risk_flags": target_info["provenance_risk_flags"],
    }


def _target_info(repo_root: Path, target: str) -> dict[str, object]:
    candidate = (repo_root / target).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        if _looks_like_path(target):
            raise ValueError("target path must resolve inside the repository root.")
        return _unresolved_handle_info(target)
    if candidate.is_dir() and (candidate / "SKILL.md").exists():
        return _path_target_info(repo_root, target, candidate, "skill_source")
    if candidate.name == "SKILL.md" and candidate.exists():
        return _path_target_info(repo_root, target, candidate, "skill_source")
    if candidate.exists():
        return _path_target_info(repo_root, target, candidate, "repo_path")
    if _looks_like_path(target):
        raise ValueError("target path does not exist; use a handle without path separators for unresolved handle routing.")
    return _unresolved_handle_info(target)


def _target_kind(repo_root: Path, target: str) -> str:
    return str(_target_info(repo_root, target)["target_kind"])


def _unresolved_handle_info(target: str) -> dict[str, object]:
    return {
        "target_kind": "unresolved_handle",
        "target_identity": f"handle:{target}",
        "target_resolved_path": None,
        "target_content_digest": None,
        "target_digest_status": "not_applicable_unresolved_handle",
        "provenance_risk_flags": ["target_not_resolved_to_repo_path"],
    }


def _path_target_info(repo_root: Path, target: str, resolved: Path, target_kind: str) -> dict[str, object]:
    digest_status, digest, risk_flags = _target_digest(resolved)
    return {
        "target_kind": target_kind,
        "target_identity": f"path:{_repo_relative(repo_root, resolved)}",
        "target_resolved_path": _repo_relative(repo_root, resolved),
        "target_content_digest": digest,
        "target_digest_status": digest_status,
        "provenance_risk_flags": risk_flags,
    }


def _looks_like_path(target: str) -> bool:
    path = Path(target)
    return path.is_absolute() or "/" in target or "\\" in target or target.startswith(".")


def _default_prompt(*, target: str, task_intent: str, target_kind: str) -> str:
    return f"Plan a read-only {task_intent} review for {target_kind} target {target}."


def _repo_file_signals(*, target: str, target_kind: str, repo_files: list[str]) -> list[str]:
    signals = list(repo_files)
    if target_kind in {"repo_path", "skill_source"}:
        signals.insert(0, target)
    return signals


def _review_focus(selected_lenses: object) -> list[str]:
    if not isinstance(selected_lenses, list):
        return []
    focus: list[str] = []
    for lens in selected_lenses:
        if not isinstance(lens, dict):
            continue
        lens_id = str(lens.get("id", "selected_lens"))
        reasons = lens.get("reasons", [])
        reason_text = ", ".join(str(reason) for reason in reasons) if isinstance(reasons, list) else "selected"
        focus.append(f"Apply {lens_id} to the target because {reason_text}.")
    return focus


def _recommended_checks(*, target: str, target_kind: str, task_intent: str) -> list[str]:
    checks = [
        "./bin/ask sdk lenses validate --json --robot",
        f"./bin/ask sdk review plan --target {target} --intent {task_intent} --json --robot",
    ]
    if target_kind == "skill_source":
        checks.append(f"./bin/ask skills doctor {target} --json --robot")
    if task_intent == "validation_review":
        checks.append("uv run --python 3.12 pytest -q")
    return checks


def _evidence_to_collect(*, target_kind: str) -> list[str]:
    evidence = [
        "review plan receipt",
        "selected lens ids and reasons",
        "focused validation command outcomes",
    ]
    if target_kind == "unresolved_handle":
        evidence.append("target ownership or path resolution evidence")
    return evidence


def _risk_flags(*, target_kind: str, selected_lenses: object) -> list[str]:
    flags: list[str] = []
    if target_kind == "unresolved_handle":
        flags.append("target_not_resolved_to_repo_path")
    if not isinstance(selected_lenses, list) or not selected_lenses:
        flags.append("no_lenses_selected")
    return flags


def _next_commands(*, target: str, task_intent: str) -> list[str]:
    return [
        f"./bin/ask sdk lenses select --intent {task_intent} --prompt 'Review {target}' --repo-file {target} --json --robot",
        f"./bin/ask sdk review plan --target {target} --intent {task_intent} --json --robot",
    ]


def _safe_receipt_path(repo_root: Path, receipt_out: str) -> Path:
    candidate = Path(receipt_out)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    resolved_repo = repo_root.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_repo)
    except ValueError as exc:
        raise ValueError("receipt_out must resolve inside the repository root.") from exc
    return resolved


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def canonical_receipt_digest(receipt: dict[str, object]) -> str:
    payload = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _write_trace_sidecar(
    repo_root: Path,
    *,
    receipt: dict[str, object],
    receipt_path: Path,
    target: str,
    task_intent: str,
) -> None:
    source_context = receipt["source_context"]
    if not isinstance(source_context, dict):
        raise ValueError("source_context must be an object before writing a trace sidecar.")
    receipt_sha256 = canonical_receipt_digest(receipt)
    trace_path = repo_root / TRACE_DIR / f"{receipt_sha256}.trace.json"
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace = {
        "schema_version": REVIEW_PLAN_TRACE_SCHEMA_VERSION,
        "schema_uri": REVIEW_PLAN_TRACE_SCHEMA_URI,
        "receipt_path": _repo_relative(repo_root, receipt_path),
        "receipt_instance_id": source_context["receipt_instance_id"],
        "receipt_sha256": receipt_sha256,
        "repo_root": source_context["repo_root"],
        "head_sha": source_context["head_sha"],
        "branch": source_context["branch"],
        "branch_policy": source_context["branch_policy"],
        "target_input": target,
        "target_identity": source_context["target_identity"],
        "target_resolved_path": source_context["target_resolved_path"],
        "target_content_digest": source_context["target_content_digest"],
        "target_digest_status": source_context["target_digest_status"],
        "created_by_command": (
            f"./bin/ask sdk review plan --target {target} --intent {task_intent} "
            f"--receipt-out {_repo_relative(repo_root, receipt_path)} --json --robot"
        ),
    }
    trace_path.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _target_digest(path: Path) -> tuple[str, str | None, list[str]]:
    if path.is_file():
        return "available", _file_digest(path), []
    if path.is_dir():
        return "available", _directory_digest(path), []
    return "unsupported_directory", None, ["target_digest_unsupported"]


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _directory_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(path.rglob("*")):
        if child.is_symlink():
            raise ValueError("target directory contains symlink; directory digest requires repository-local regular files.")
        if not child.is_file():
            continue
        relative = child.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(child.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _git_dir(repo_root: Path) -> Path:
    dot_git = repo_root / ".git"
    if dot_git.is_dir():
        return dot_git
    text = dot_git.read_text(encoding="utf-8").strip()
    prefix = "gitdir: "
    if not text.startswith(prefix):
        raise ValueError(".git file does not contain a gitdir pointer.")
    git_dir = Path(text.removeprefix(prefix))
    if not git_dir.is_absolute():
        git_dir = repo_root / git_dir
    return git_dir.resolve()


def _head_ref(repo_root: Path) -> str:
    head_text = (_git_dir(repo_root) / "HEAD").read_text(encoding="utf-8").strip()
    if head_text.startswith("ref: "):
        return head_text.removeprefix("ref: ")
    return head_text


def _head_sha(repo_root: Path) -> str:
    git_dir = _git_dir(repo_root)
    head_ref = _head_ref(repo_root)
    if not head_ref.startswith("refs/"):
        return head_ref
    for refs_dir in (git_dir, _common_git_dir(git_dir)):
        ref_path = refs_dir / head_ref
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
    packed_refs = _common_git_dir(git_dir) / "packed-refs"
    if packed_refs.exists():
        for line in packed_refs.read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or not line:
                continue
            sha, _, ref = line.partition(" ")
            if ref == head_ref:
                return sha
    raise ValueError(f"could not resolve git HEAD ref {head_ref}.")


def _branch_name(repo_root: Path) -> str:
    head_ref = _head_ref(repo_root)
    if head_ref.startswith("refs/heads/"):
        return head_ref.removeprefix("refs/heads/")
    return "detached"


def _common_git_dir(git_dir: Path) -> Path:
    common_dir_file = git_dir / "commondir"
    if not common_dir_file.exists():
        return git_dir
    common_dir = Path(common_dir_file.read_text(encoding="utf-8").strip())
    if not common_dir.is_absolute():
        common_dir = git_dir / common_dir
    return common_dir.resolve()
