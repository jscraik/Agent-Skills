from __future__ import annotations

import json
from pathlib import Path

from ask.skills_sdk.lenses import select_lenses


REVIEW_PLAN_SCHEMA_VERSION = "skills-sdk.review-plan-receipt.v1"
REVIEW_PLAN_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json"
)


def build_review_plan(
    repo_root: Path,
    *,
    target: str,
    task_intent: str,
    prompt: str | None = None,
    repo_files: list[str] | None = None,
    max_lenses: int = 4,
    receipt_out: str | None = None,
) -> dict[str, object]:
    if max_lenses < 1:
        raise ValueError("max_lenses must be at least 1.")

    target_kind = _target_kind(repo_root, target)
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
    return receipt


def _target_kind(repo_root: Path, target: str) -> str:
    candidate = (repo_root / target).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        if _looks_like_path(target):
            raise ValueError("target path must resolve inside the repository root.")
        return "unresolved_handle"
    if candidate.is_dir() and (candidate / "SKILL.md").exists():
        return "skill_source"
    if candidate.name == "SKILL.md" and candidate.exists():
        return "skill_source"
    if candidate.exists():
        return "repo_path"
    if _looks_like_path(target):
        raise ValueError("target path does not exist; use a handle without path separators for unresolved handle routing.")
    return "unresolved_handle"


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
