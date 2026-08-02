from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from ask.skills_sdk.eval_ab_judge_decision import ALLOWED_WINNERS, DECISION_SCHEMA_VERSION, _parse_judge_decision
from ask.skills_sdk.eval_ab_judge_codex import (
    CodexJudgeResult,
    CodexProfileConfigError,
    _codex_judge_command,
    _codex_judge_work_dir,
    _codex_op_env_file_available,
    _run_codex_judge,
)
from ask.skills_sdk.eval_ab_rubric import canonical_ab_rubric, canonical_ab_rubric_digest
from ask.skills_sdk.eval_profiles import select_judge_profile
from ask.skills_sdk.ab_contracts import _codex_profile_from_judge_argv
from ask.skills_sdk.ab_transport_contracts import is_actual_opaque_env_reference, redact_opaque_env_reference
from ask.skills_sdk.typed_contracts import validate_ab_run_receipt

AB_JUDGE_PREVIEW_SCHEMA_VERSION = "skills-sdk.ab-judge-preview-receipt.v0"
AB_JUDGE_PREVIEW_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/ab-judge-preview-receipt.v0.schema.json"
AB_JUDGE_SCORE_SCHEMA_VERSION = "skills-sdk.ab-judge-score-receipt.v0"
AB_JUDGE_SCORE_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/ab-judge-score-receipt.v0.schema.json"
AB_RUN_RUNTIME_PROOF_SCHEMA_VERSION = "skills-sdk.ab-run-receipt.v1"
_EXPERIMENT_ID_RE = re.compile(r"^(?:ex_[a-z0-9]{16}|[0-9a-f]{16})$")
_SEMANTIC_OUTPUT_EXCERPT_BYTES = 4096
_CODEX_TOKENS_USED_RE = re.compile(r"(?im)tokens used\s*(?::|\n)\s*([0-9][0-9,]*)")
_CODEX_JSON_TOKENS_USED_RE = re.compile(r'"tokens_used"\s*:\s*([0-9]+)')
_CODEX_FALLBACK_METADATA_RE = re.compile(r"(?i)(model metadata .*not found|fallback metadata)")
_VISIBLE_THINKING_RE = re.compile(r"(?im)(<think\b|</think>|^\s*thinking\s*$|thinking trace)")
__all__ = ["CodexJudgeResult"]


def _digest_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _digest_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _resolve_receipt_path(repo_root: Path, run_receipt: str) -> tuple[Path | None, str | None]:
    candidate = Path(run_receipt)
    path = candidate if candidate.is_absolute() else repo_root / candidate
    resolved = _contained_repo_path(repo_root, path)
    if resolved is None:
        return None, "run_receipt_outside_repo"
    if not resolved.is_file():
        return resolved, "run_receipt_missing"
    return resolved, None


def _load_run_receipt(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "run_receipt_invalid_json"
    payload = _unwrap_run_receipt(payload)
    if not isinstance(payload, dict):
        return None, "run_receipt_not_object"
    try:
        validated = validate_ab_run_receipt(payload)
    except ValueError:
        return None, "run_receipt_contract_invalid"
    return validated.model_dump(mode="json"), None


def _unwrap_run_receipt(payload: object) -> object:
    if not isinstance(payload, dict):
        return payload
    if isinstance(payload.get("receipt"), dict):
        return payload["receipt"]
    data = payload.get("data")
    if not isinstance(data, dict):
        return payload
    command_payload = data.get("skills_sdk_eval_ab_run")
    if isinstance(command_payload, dict) and isinstance(command_payload.get("receipt"), dict):
        return command_payload["receipt"]
    return payload


def _experiment_id_valid(value: object) -> bool:
    return isinstance(value, str) and _EXPERIMENT_ID_RE.fullmatch(value) is not None


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _evidence_row(repo_root: Path, result: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    semantic_excerpt = _semantic_output_excerpt(repo_root, result)
    if semantic_excerpt is None:
        return {}, f"{result.get('variant_label', 'unknown')}:semantic_output_evidence_missing"
    return {
        "variant_label": result["variant_label"],
        "status": result["status"],
        "exit_code": result["exit_code"],
        "sandbox_mode": result["sandbox_mode"],
        "output_last_message_digest": result["output_last_message_digest"],
        "runner_stdout_digest": result["runner_stdout_digest"],
        "runner_stderr_digest": result["runner_stderr_digest"],
        "semantic_output_excerpt": semantic_excerpt,
        "blockers": result["blockers"],
    }, None


def _comparison_payload(repo_root: Path, run_receipt: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    rubric = canonical_ab_rubric()
    variant_rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    for result in run_receipt["variant_results"]:
        row, blocker = _evidence_row(repo_root, result)
        if blocker:
            blockers.append(blocker)
            continue
        variant_rows.append(row)
    if blockers:
        return None, blockers
    return {
        "schema_version": DECISION_SCHEMA_VERSION,
        "experiment_id": run_receipt["experiment_id"],
        "rubric": rubric,
        "rubric_digest": canonical_ab_rubric_digest(),
        "skill_a": {
            "package_id": run_receipt["skill_a"]["package_id"],
            "package_digest": run_receipt["skill_a"]["package_digest"],
        },
        "skill_b": {
            "package_id": run_receipt["skill_b"]["package_id"],
            "package_digest": run_receipt["skill_b"]["package_digest"],
        },
        "fixture": {
            "path": run_receipt["fixture"]["path"],
            "digest": run_receipt["fixture"]["digest"],
        },
        "execution_profile": run_receipt["execution_profile"]["id"],
        "variant_results": variant_rows,
        "allowed_winners": ALLOWED_WINNERS,
    }, []


def _semantic_output_excerpt(repo_root: Path, result: dict[str, Any]) -> str | None:
    raw_excerpt = result.get("semantic_output_excerpt")
    if _non_empty_string(raw_excerpt):
        return _sanitize_semantic_excerpt(raw_excerpt)
    for key in ("output_last_message_path", "runner_stdout_capture_path"):
        excerpt = _read_semantic_excerpt(repo_root, result.get(key))
        if excerpt:
            return excerpt
    return None


def _read_semantic_excerpt(repo_root: Path, raw_path: object) -> str | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    path = Path(raw_path)
    if path.is_absolute() or path.is_symlink():
        return None
    candidate = repo_root / path
    if candidate.is_symlink():
        return None
    resolved = _contained_repo_path(repo_root, candidate)
    if resolved is None or resolved.is_symlink() or not resolved.is_file():
        return None
    try:
        data = resolved.read_bytes()[: _SEMANTIC_OUTPUT_EXCERPT_BYTES + 1]
    except OSError:
        return None
    text = data[:_SEMANTIC_OUTPUT_EXCERPT_BYTES].decode("utf-8", errors="replace")
    return _sanitize_semantic_excerpt(text)


def _sanitize_semantic_excerpt(text: str) -> str | None:
    compact = text.replace("\x00", "").strip()
    return compact or None


def _judge_prompt(comparison_payload: dict[str, Any]) -> str:
    return (
        "You are judging a Skills SDK A/B eval from sanitized receipt evidence only.\n"
        "Do not inspect the repository, call tools, ask follow-up questions, or use hidden context.\n"
        "Do not infer from package names, local paths, hidden logs, or unavailable content.\n"
        "Use the embedded rubric exactly; do not change weights or criteria.\n"
        "Return raw JSON only: no Markdown fences, no prose, no comments, no tool-call objects.\n"
        "The top-level JSON object must have exactly these keys: schema_version, experiment_id, "
        "dimension_scores, normalized_score_a, normalized_score_b, winner, confidence, reason, evidence_refs.\n"
        "Set schema_version to skills-sdk.ab-judge-decision.v0 and experiment_id to the evidence experiment_id.\n"
        "Each dimension_scores item must include dimension_id, skill_a_score, skill_b_score, "
        "reason, and evidence_refs.\n"
        "Use dimension_scores, never dimensions. Use one evidence_refs array per object.\n"
        "Scores are 0 to 5. Normalized scores are 0 to 1: weighted_sum_of_dimension_scores / 5.\n"
        "Compute the normalized delta as normalized_score_b - normalized_score_a after applying the rubric weights.\n"
        "Apply winner_policy to that normalized delta: do not use the raw 0-to-5 score gap; when the absolute\n"
        "delta is below minimum_normalized_delta, or confidence is below minimum_confidence, set winner to\n"
        "inconclusive. A positive delta selects skill_b, and a negative delta selects skill_a; a directional\n"
        "winner is valid only when the normalized policy threshold is met.\n"
        "Choose inconclusive when the sanitized evidence is insufficient.\n\n"
        f"Evidence:\n{json.dumps(comparison_payload, sort_keys=True, indent=2)}\n"
    )


def build_ab_judge_preview_receipt(repo_root: Path, *, run_receipt: str) -> dict[str, Any]:
    inputs = _judge_inputs(repo_root, run_receipt)
    blockers = inputs["blockers"]
    loaded_receipt = inputs["loaded_receipt"]
    if loaded_receipt is not None and loaded_receipt["schema_version"] != AB_RUN_RUNTIME_PROOF_SCHEMA_VERSION:
        blockers.extend(
            [
                "v1_runtime_profile_proof_required",
                "run_receipt_runtime_proof_version_unsupported",
            ]
        )
    if loaded_receipt is not None and loaded_receipt["status"] != "completed":
        blockers.append("run_receipt_not_completed")

    comparison_payload, judge_prompt = _judge_input_payload(repo_root, blockers, loaded_receipt)
    status = "preview" if not blockers else "blocked"
    return _judge_receipt_payload(status, blockers, inputs, loaded_receipt, comparison_payload, judge_prompt)


def _judge_inputs(repo_root: Path, run_receipt: str) -> dict[str, Any]:
    blockers: list[str] = []
    receipt_path, path_blocker = _resolve_receipt_path(repo_root, run_receipt)
    if path_blocker:
        blockers.append(path_blocker)
    receipt_path_label, receipt_digest, loaded_receipt, load_blocker = _load_receipt_inputs(
        repo_root,
        receipt_path,
        path_blocker,
    )
    if load_blocker:
        blockers.append(load_blocker)
    return {
        "blockers": blockers,
        "receipt_path_label": receipt_path_label,
        "receipt_digest": receipt_digest,
        "loaded_receipt": loaded_receipt,
    }


def _load_receipt_inputs(
    repo_root: Path,
    receipt_path: Path | None,
    path_blocker: str | None,
) -> tuple[str | None, str | None, dict[str, Any] | None, str | None]:
    if receipt_path is None or path_blocker:
        return None, None, None, None
    loaded_receipt, _load_blocker = _load_run_receipt(receipt_path)
    return _repo_relative(repo_root, receipt_path), _digest_file(receipt_path), loaded_receipt, _load_blocker


def _judge_input_payload(
    repo_root: Path,
    blockers: list[str],
    loaded_receipt: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, str | None]:
    if blockers or loaded_receipt is None:
        return None, None
    comparison_payload, evidence_blockers = _comparison_payload(repo_root, loaded_receipt)
    if evidence_blockers:
        blockers.extend(evidence_blockers)
        return None, None
    return comparison_payload, _judge_prompt(comparison_payload)


def _judge_receipt_payload(
    status: str,
    blockers: list[str],
    inputs: dict[str, Any],
    loaded_receipt: dict[str, Any] | None,
    comparison_payload: dict[str, Any] | None,
    judge_prompt: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": AB_JUDGE_PREVIEW_SCHEMA_VERSION,
        "schema_uri": AB_JUDGE_PREVIEW_SCHEMA_URI,
        "status": status,
        "operation": "ab_judge_preview",
        "run_receipt_path": inputs["receipt_path_label"],
        "run_receipt_digest": inputs["receipt_digest"],
        "experiment_id": None if loaded_receipt is None else loaded_receipt["experiment_id"],
        "judge_profile": None if loaded_receipt is None else loaded_receipt["judge_profile"],
        "rubric_id": None if comparison_payload is None else comparison_payload["rubric"]["rubric_id"],
        "rubric_digest": None if comparison_payload is None else comparison_payload["rubric_digest"],
        "comparison_payload": comparison_payload,
        "judge_prompt_digest": None if judge_prompt is None else _digest_text(judge_prompt),
        "decision_schema_version": DECISION_SCHEMA_VERSION,
        "allowed_winners": ALLOWED_WINNERS,
        "calibration_required": True,
        "provider_invoked": False,
        "network_accessed": False,
        "mutation_performed": False,
        "blockers": blockers,
        "acceptance_trace": ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"],
        "agent_summary": (
            "A/B judge preview is ready; no judge provider has been invoked."
            if status == "preview"
            else f"A/B judge preview is blocked: {', '.join(blockers)}."
        ),
    }


def build_ab_judge_score_receipt(
    repo_root: Path,
    *,
    run_receipt: str,
    evidence_root: str = ".harness/artifacts/sdk-ab-judges",
    judge_profile_id: str = "oss-local",
    timeout_seconds: int = 300,
    runner: Any | None = None,
) -> dict[str, Any]:
    preview = build_ab_judge_preview_receipt(repo_root, run_receipt=run_receipt)
    blockers, judge_profile, evidence = _score_preflight(
        repo_root, preview, evidence_root, judge_profile_id, timeout_seconds
    )
    decision, output_digest, provider_invoked, network_accessed, mutation_performed = _score_decision(
        blockers=blockers,
        repo_root=repo_root,
        preview=preview,
        judge_profile=judge_profile,
        evidence=evidence,
        timeout_seconds=timeout_seconds,
        runner=runner or _run_codex_judge,
    )
    status = "scored" if decision is not None and not blockers else "blocked"
    return _score_receipt_payload(
        status=status,
        preview=preview,
        judge_profile=judge_profile,
        evidence=evidence,
        decision=decision,
        output_digest=output_digest,
        provider_invoked=provider_invoked,
        network_accessed=network_accessed,
        mutation_performed=mutation_performed,
        blockers=blockers,
    )


def _score_preflight(
    repo_root: Path,
    preview: dict[str, Any],
    evidence_root: str,
    judge_profile_id: str,
    timeout_seconds: int,
) -> tuple[list[str], dict[str, Any] | None, dict[str, Any]]:
    blockers = list(preview["blockers"])
    judge_profile = _selected_score_profile(judge_profile_id, blockers)
    if judge_profile is not None:
        blockers.extend(_missing_judge_profile_secrets(judge_profile))
    evidence = _score_evidence_paths(repo_root, evidence_root, preview.get("experiment_id"))
    if evidence["blocker"]:
        blockers.append(evidence["blocker"])
    if (
        judge_profile is not None
        and evidence.get("output_file") is not None
        and "judge_cloud_op_boundary_unavailable" not in blockers
    ):
        evidence["command_argv"] = _codex_judge_command(
            judge_profile,
            _codex_judge_work_dir(evidence["output_file"]),
            evidence["output_file"],
        )
        try:
            evidence["codex_profile"] = _codex_profile_from_judge_argv(evidence["command_argv"])
        except ValueError:
            evidence["codex_profile"] = None
            blockers.append("judge_command_profile_missing_or_invalid")
    else:
        evidence["command_argv"] = []
        evidence["codex_profile"] = None
    if preview["status"] != "preview":
        blockers.append("judge_input_preview_blocked")
    if timeout_seconds < 1:
        blockers.append("timeout_seconds_invalid")
    return blockers, judge_profile, evidence


def _selected_score_profile(profile_id: str, blockers: list[str]) -> dict[str, Any] | None:
    try:
        profile = select_judge_profile(profile_id)
    except ValueError:
        blockers.append("judge_profile_unknown")
        return None
    supported_codex_profiles = {"oss-local", "oss-local-code", "oss-local-fallback", "oss-security", "oss-cloud"}
    if profile["provider"] != "codex" or profile.get("codex_profile", profile["id"]) not in supported_codex_profiles:
        blockers.append("judge_profile_not_supported_for_codex_score")
    return profile


def _missing_judge_profile_secrets(judge_profile: dict[str, Any]) -> list[str]:
    if _codex_profile_id_for_score(judge_profile) == "oss-cloud" and not _codex_op_env_file_available(judge_profile):
        return ["judge_cloud_op_boundary_unavailable"]
    missing = [
        name
        for name in judge_profile.get("secret_env_names", [])
        if isinstance(name, str) and name and name not in os.environ
    ]
    if missing and _codex_op_env_file_available(judge_profile):
        return []
    return ["judge_profile_secret_missing"] if missing else []


def _codex_profile_id_for_score(judge_profile: dict[str, Any]) -> str:
    return str(judge_profile.get("codex_profile") or judge_profile.get("id"))


def _score_evidence_paths(repo_root: Path, evidence_root: str, experiment_id: object) -> dict[str, Any]:
    candidate = Path(evidence_root)
    root = candidate if candidate.is_absolute() else repo_root / candidate
    if _path_has_symlink_ancestor(repo_root, root):
        return {"blocker": "score_evidence_path_outside_repo", "prompt_path": None, "output_path": None}
    resolved = _contained_repo_path(repo_root, root)
    if resolved is None:
        return {"blocker": "evidence_root_outside_repo", "prompt_path": None, "output_path": None}
    if _path_has_file_ancestor(repo_root, resolved):
        return {"blocker": "evidence_root_not_directory", "prompt_path": None, "output_path": None}
    if not _experiment_id_valid(experiment_id):
        return {"blocker": "experiment_id_invalid", "prompt_path": None, "output_path": None}
    base = resolved / experiment_id / "judge"
    if _path_has_symlink_ancestor(resolved, base):
        return {"blocker": "score_evidence_path_outside_repo", "prompt_path": None, "output_path": None}
    contained_base = _contained_repo_path(resolved, base)
    if contained_base is None:
        return {"blocker": "score_evidence_path_outside_repo", "prompt_path": None, "output_path": None}
    if _path_has_file_ancestor(repo_root, contained_base):
        return {"blocker": "evidence_root_not_directory", "prompt_path": None, "output_path": None}
    prompt_file = _contained_score_evidence_file(repo_root, contained_base / "prompt.txt")
    output_file = _contained_score_evidence_file(repo_root, contained_base / "codex-last-message.json")
    if prompt_file is None or output_file is None:
        return {"blocker": "score_evidence_path_outside_repo", "prompt_path": None, "output_path": None}
    return {
        "blocker": None,
        "prompt_file": prompt_file,
        "output_file": output_file,
        "prompt_path": _repo_relative(repo_root, prompt_file),
        "output_path": _repo_relative(repo_root, output_file),
    }


def _contained_score_evidence_file(repo_root: Path, path: Path) -> Path | None:
    if path.is_symlink() or path.is_dir():
        return None
    return _contained_repo_path(repo_root, path)


def _score_decision(
    *,
    blockers: list[str],
    repo_root: Path,
    preview: dict[str, Any],
    judge_profile: dict[str, Any] | None,
    evidence: dict[str, Any],
    timeout_seconds: int,
    runner: Any,
) -> tuple[dict[str, Any] | None, str | None, bool, bool, bool]:
    if blockers or judge_profile is None:
        return None, None, False, False, False
    judge_prompt = _judge_prompt(preview["comparison_payload"])
    _write_text_evidence(repo_root, evidence["prompt_file"], judge_prompt)
    _clear_text_evidence(repo_root, evidence["output_file"])
    mutation_performed = True
    try:
        result = runner(judge_prompt, judge_profile, timeout_seconds, repo_root, evidence["output_file"])
    except (CodexProfileConfigError, OSError, subprocess.TimeoutExpired) as exc:
        return _score_runner_exception(repo_root, evidence, blockers, exc, mutation_performed)
    return _score_runner_result(repo_root, preview, judge_profile, evidence, blockers, result, mutation_performed)


def _score_runner_exception(
    repo_root: Path,
    evidence: dict[str, Any],
    blockers: list[str],
    exc: Exception,
    mutation_performed: bool,
) -> tuple[dict[str, Any] | None, str | None, bool, bool, bool]:
    if isinstance(exc, CodexProfileConfigError):
        blockers.append("codex_profile_config_missing")
        return _blocked_score_decision(mutation_performed)
    if isinstance(exc, OSError):
        blockers.append("judge_provider_unavailable")
        return _blocked_score_decision(mutation_performed)
    stdout = _timeout_output_text(exc.stdout)
    _write_text_evidence(repo_root, evidence["output_file"], stdout)
    blockers.append("judge_provider_timeout")
    return None, _digest_text(stdout), True, True, mutation_performed


def _score_runner_result(
    repo_root: Path,
    preview: dict[str, Any],
    judge_profile: dict[str, Any],
    evidence: dict[str, Any],
    blockers: list[str],
    result: CodexJudgeResult,
    mutation_performed: bool,
) -> tuple[dict[str, Any] | None, str | None, bool, bool, bool]:
    output_text = _codex_judge_output_text(repo_root, evidence["output_file"], result.output_text) or result.stdout
    if not _contained_file_exists(repo_root, evidence["output_file"]):
        _write_text_evidence(repo_root, evidence["output_file"], output_text)
    output_digest = _digest_text(output_text)
    executed_profile = _validate_judge_execution_argv(evidence, result, blockers)
    if executed_profile is None:
        return None, output_digest, True, True, mutation_performed
    stored_argv = list(result.executed_argv)
    if executed_profile == "oss-cloud":
        stored_argv[3] = redact_opaque_env_reference(stored_argv[3])
    evidence["command_argv"] = stored_argv
    evidence["codex_profile"] = executed_profile
    if result.exit_code != 0:
        blockers.append(f"judge_provider_exit_{result.exit_code}")
        return None, output_digest, True, True, mutation_performed
    runtime_guard_blockers = _codex_runtime_guard_blockers(judge_profile, result, output_text)
    if runtime_guard_blockers:
        blockers.extend(runtime_guard_blockers)
        return None, output_digest, True, True, mutation_performed
    decision, blocker = _parse_judge_decision(output_text, preview["comparison_payload"])
    if blocker:
        blockers.append(blocker)
    return decision, output_digest, True, True, mutation_performed


def _validate_judge_execution_argv(
    evidence: dict[str, Any], result: CodexJudgeResult, blockers: list[str],
) -> str | None:
    planned = evidence.get("command_argv")
    executed = getattr(result, "executed_argv", None)
    if not isinstance(executed, list) or not all(isinstance(item, str) for item in executed):
        blockers.append("judge_command_profile_missing_or_invalid")
        return None
    if executed != planned:
        blockers.append("judge_command_argv_mismatch")
        return None
    try:
        profile = _codex_profile_from_judge_argv(executed)
    except ValueError:
        blockers.append("judge_command_profile_missing_or_invalid")
        return None
    if profile != evidence.get("codex_profile"):
        blockers.append("judge_command_profile_missing_or_invalid")
        return None
    if profile == "oss-cloud" and not is_actual_opaque_env_reference(executed[3]):
        blockers.append("judge_command_profile_missing_or_invalid")
        return None
    return profile


def _blocked_score_decision(mutation_performed: bool) -> tuple[None, None, bool, bool, bool]:
    return None, None, False, False, mutation_performed


def _write_text_evidence(repo_root: Path, path: Path | None, value: str) -> None:
    if path is None:
        return
    if path.is_symlink():
        return
    resolved = _contained_repo_path(repo_root, path)
    if resolved is None:
        return
    resolved.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    file_descriptor = os.open(resolved, flags, 0o600)
    if hasattr(os, "fchmod"):
        os.fchmod(file_descriptor, 0o600)
    with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
        handle.write(value)


def _clear_text_evidence(repo_root: Path, path: Path | None) -> None:
    if path is None:
        return
    if path.is_symlink():
        parent = _contained_repo_path(repo_root, path.parent)
        if parent is not None:
            path.unlink()
        return
    resolved = _contained_repo_path(repo_root, path)
    if resolved is not None and resolved.is_file():
        resolved.unlink()


def _contained_file_exists(repo_root: Path, path: Path | None) -> bool:
    if path is None:
        return False
    resolved = _contained_repo_path(repo_root, path)
    return resolved is not None and resolved.is_file()


def _codex_judge_output_text(repo_root: Path, path: Path | None, fallback: str) -> str:
    if path is None:
        return fallback
    resolved = _contained_repo_path(repo_root, path)
    if resolved is None or not resolved.is_file():
        return fallback
    return resolved.read_text(encoding="utf-8")


def _contained_repo_path(repo_root: Path, path: Path) -> Path | None:
    try:
        repo_base = repo_root.resolve()
        resolved = path.resolve()
        resolved.relative_to(repo_base)
    except (OSError, ValueError):
        return None
    return resolved


def _path_has_file_ancestor(repo_root: Path, path: Path) -> bool:
    repo_base = repo_root.resolve()
    current = path
    while current != repo_base:
        if current.exists() and not current.is_dir():
            return True
        if current.parent == current:
            return True
        current = current.parent
    return False


def _path_has_symlink_ancestor(root: Path, path: Path) -> bool:
    current = path
    while current != root:
        if current.is_symlink():
            return True
        if current.parent == current:
            return True
        current = current.parent
    return False


def _timeout_output_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        return value
    return ""


def _codex_runtime_guard_blockers(
    judge_profile: dict[str, Any],
    result: CodexJudgeResult,
    output_text: str,
) -> list[str]:
    guard = judge_profile.get("smoke_guard")
    if not isinstance(guard, dict):
        return []
    combined_output = "\n".join([result.stdout, result.stderr, output_text])
    blockers: list[str] = []
    if guard.get("forbid_fallback_metadata") is True and _CODEX_FALLBACK_METADATA_RE.search(combined_output):
        blockers.append("codex_runtime_metadata_fallback")
    jsonl_reasoning_allowed = guard.get("allow_codex_jsonl_reasoning_events") is True
    if guard.get("forbid_visible_thinking") is True and (
        _VISIBLE_THINKING_RE.search(combined_output)
        or (not jsonl_reasoning_allowed and _has_codex_reasoning_event(combined_output))
    ):
        blockers.append("codex_runtime_visible_thinking")
    max_tokens = guard.get("max_tokens_used")
    if isinstance(max_tokens, int):
        observed_tokens = _codex_observed_tokens_used(combined_output)
        if observed_tokens is not None and observed_tokens > max_tokens:
            blockers.append("codex_runtime_token_budget_exceeded")
    return blockers


def _codex_observed_tokens_used(text: str) -> int | None:
    values: list[int] = []
    for pattern in (_CODEX_TOKENS_USED_RE, _CODEX_JSON_TOKENS_USED_RE):
        for match in pattern.finditer(text):
            try:
                values.append(int(match.group(1).replace(",", "")))
            except ValueError:
                continue
    values.extend(_codex_jsonl_token_totals(text))
    return max(values) if values else None


def _codex_jsonl_token_totals(text: str) -> list[int]:
    totals: list[int] = []
    for line in text.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        usage = payload.get("usage")
        if not isinstance(usage, dict):
            continue
        token_values = [
            usage.get("input_tokens"),
            usage.get("output_tokens"),
            usage.get("reasoning_output_tokens"),
        ]
        total = sum(value for value in token_values if isinstance(value, int))
        if total > 0:
            totals.append(total)
    return totals


def _has_codex_reasoning_event(text: str) -> bool:
    for line in text.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        item = payload.get("item")
        if isinstance(item, dict) and item.get("type") == "reasoning":
            return True
    return False


def _score_receipt_payload(
    *,
    status: str,
    preview: dict[str, Any],
    judge_profile: dict[str, Any] | None,
    evidence: dict[str, Any],
    decision: dict[str, Any] | None,
    output_digest: str | None,
    provider_invoked: bool,
    network_accessed: bool,
    mutation_performed: bool,
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": AB_JUDGE_SCORE_SCHEMA_VERSION,
        "schema_uri": AB_JUDGE_SCORE_SCHEMA_URI,
        "status": status,
        "operation": "ab_judge_score",
        **_score_receipt_run_fields(preview, evidence, output_digest),
        "judge_profile": judge_profile,
        "rubric_id": preview["rubric_id"],
        "rubric_digest": preview["rubric_digest"],
        "decision_schema_version": DECISION_SCHEMA_VERSION,
        "allowed_winners": ALLOWED_WINNERS,
        "codex_exec_invoked": provider_invoked,
        "decision": decision,
        "calibration_required": True,
        "advisory_only": True,
        "provider_invoked": provider_invoked,
        "network_accessed": network_accessed,
        "mutation_performed": mutation_performed,
        "blockers": blockers,
        "acceptance_trace": ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"],
        "agent_summary": _score_agent_summary(status, blockers),
    }


def _score_receipt_run_fields(
    preview: dict[str, Any],
    evidence: dict[str, Any],
    output_digest: str | None,
) -> dict[str, Any]:
    return {
        "run_receipt_path": preview["run_receipt_path"],
        "run_receipt_digest": preview["run_receipt_digest"],
        "experiment_id": preview["experiment_id"],
        "judge_prompt_digest": preview["judge_prompt_digest"],
        "judge_output_path": evidence["output_path"],
        "judge_output_digest": output_digest,
        "judge_command_argv": evidence["command_argv"],
        "codex_profile": evidence["codex_profile"],
    }


def _score_agent_summary(status: str, blockers: list[str]) -> str:
    if status == "scored":
        return "A/B local judge scoring completed with advisory decision evidence."
    return f"A/B local judge scoring blocked: {', '.join(blockers)}."
