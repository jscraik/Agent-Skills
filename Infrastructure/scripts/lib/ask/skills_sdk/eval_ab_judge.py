from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ask.skills_sdk.eval_ab_rubric import AB_RUBRIC_DIMENSIONS, canonical_ab_rubric, canonical_ab_rubric_digest
from ask.skills_sdk.eval_profiles import select_judge_profile


AB_JUDGE_PREVIEW_SCHEMA_VERSION = "skills-sdk.ab-judge-preview-receipt.v0"
AB_JUDGE_PREVIEW_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/ab-judge-preview-receipt.v0.schema.json"
)
AB_JUDGE_SCORE_SCHEMA_VERSION = "skills-sdk.ab-judge-score-receipt.v0"
AB_JUDGE_SCORE_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/ab-judge-score-receipt.v0.schema.json"
)
DECISION_SCHEMA_VERSION = "skills-sdk.ab-judge-decision.v0"
ALLOWED_WINNERS = ["skill_a", "skill_b", "inconclusive"]
_EXPERIMENT_ID_RE = re.compile(r"[0-9a-f]{16}")
_DIMENSION_IDS = {dimension["id"] for dimension in AB_RUBRIC_DIMENSIONS}
_DECISION_KEYS = frozenset(
    {
        "schema_version",
        "experiment_id",
        "dimension_scores",
        "normalized_score_a",
        "normalized_score_b",
        "winner",
        "confidence",
        "reason",
        "evidence_refs",
    }
)
_DIMENSION_SCORE_KEYS = frozenset({"dimension_id", "skill_a_score", "skill_b_score", "reason", "evidence_refs"})


@dataclass(frozen=True)
class OllamaJudgeResult:
    exit_code: int
    stdout: str
    stderr: str


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
    if not _run_receipt_shape_valid(payload):
        return None, "run_receipt_contract_invalid"
    return payload, None


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


def _digest_like(value: object) -> bool:
    return isinstance(value, str) and len(value) >= 71 and value.startswith("sha256:")


def _object_field(payload: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = payload.get(key)
    return value if isinstance(value, dict) else None


def _variant_labels(rows: object) -> set[str]:
    if not isinstance(rows, list):
        return set()
    return {row.get("variant_label") for row in rows if isinstance(row, dict)}


def _run_receipt_shape_valid(payload: dict[str, Any]) -> bool:
    return (
        _run_receipt_header_valid(payload)
        and _run_receipt_identity_valid(payload)
        and _run_receipt_variants_valid(payload)
    )


def _run_receipt_header_valid(payload: dict[str, Any]) -> bool:
    return (
        payload.get("schema_version") == "skills-sdk.ab-run-receipt.v0"
        and payload.get("operation") == "ab_run"
        and payload.get("status") in {"completed", "blocked"}
    )


def _run_receipt_identity_valid(payload: dict[str, Any]) -> bool:
    object_keys = ("skill_a", "skill_b", "fixture", "execution_profile", "judge_profile")
    return all(_object_field(payload, key) is not None for key in object_keys) and _experiment_id_valid(
        payload.get("experiment_id")
    )


def _experiment_id_valid(value: object) -> bool:
    return isinstance(value, str) and _EXPERIMENT_ID_RE.fullmatch(value) is not None


def _run_receipt_variants_valid(payload: dict[str, Any]) -> bool:
    if _variant_labels(payload.get("variant_results")) != {"A", "B"}:
        return False
    if _variant_labels(payload.get("command_plan")) != {"A", "B"}:
        return False
    return all(_variant_result_digests_valid(result) for result in payload["variant_results"])


def _variant_result_digests_valid(result: object) -> bool:
    if not isinstance(result, dict):
        return False
    keys = ("output_last_message_digest", "runner_stdout_digest", "runner_stderr_digest")
    return all(_digest_like(result.get(key)) for key in keys)


def _evidence_row(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "variant_label": result["variant_label"],
        "status": result["status"],
        "exit_code": result["exit_code"],
        "sandbox_mode": result["sandbox_mode"],
        "output_last_message_digest": result["output_last_message_digest"],
        "runner_stdout_digest": result["runner_stdout_digest"],
        "runner_stderr_digest": result["runner_stderr_digest"],
        "blockers": result["blockers"],
    }


def _comparison_payload(run_receipt: dict[str, Any]) -> dict[str, Any]:
    rubric = canonical_ab_rubric()
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
        "variant_results": [_evidence_row(result) for result in run_receipt["variant_results"]],
        "allowed_winners": ALLOWED_WINNERS,
    }


def _judge_prompt(comparison_payload: dict[str, Any]) -> str:
    return (
        "You are judging a Skills SDK A/B eval from sanitized receipt evidence only.\n"
        "Do not infer from package names, local paths, hidden logs, or unavailable content.\n"
        "Use the embedded rubric exactly; do not change weights or criteria.\n"
        "Return JSON only, matching skills-sdk.ab-judge-decision.v0 with dimension_scores, "
        "normalized_score_a, normalized_score_b, winner, confidence, reason, and evidence_refs.\n"
        "Each dimension_scores item must include dimension_id, skill_a_score, skill_b_score, "
        "reason, and evidence_refs.\n"
        "Choose inconclusive when the sanitized evidence is insufficient.\n\n"
        f"Evidence:\n{json.dumps(comparison_payload, sort_keys=True, indent=2)}\n"
    )


def build_ab_judge_preview_receipt(repo_root: Path, *, run_receipt: str) -> dict[str, Any]:
    inputs = _judge_inputs(repo_root, run_receipt)
    blockers = inputs["blockers"]
    loaded_receipt = inputs["loaded_receipt"]
    if loaded_receipt is not None and loaded_receipt["status"] != "completed":
        blockers.append("run_receipt_not_completed")

    comparison_payload, judge_prompt = _judge_input_payload(blockers, loaded_receipt)
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
    blockers: list[str],
    loaded_receipt: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, str | None]:
    if blockers or loaded_receipt is None:
        return None, None
    comparison_payload = _comparison_payload(loaded_receipt)
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
        runner=runner or _run_ollama_judge,
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
    evidence = _score_evidence_paths(repo_root, evidence_root, preview.get("experiment_id"))
    if evidence["blocker"]:
        blockers.append(evidence["blocker"])
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
    if profile["id"] != "oss-local":
        blockers.append("judge_profile_not_local_oss")
    return profile


def _score_evidence_paths(repo_root: Path, evidence_root: str, experiment_id: object) -> dict[str, Any]:
    candidate = Path(evidence_root)
    root = candidate if candidate.is_absolute() else repo_root / candidate
    resolved = _contained_repo_path(repo_root, root)
    if resolved is None:
        return {"blocker": "evidence_root_outside_repo", "prompt_path": None, "output_path": None}
    if _path_has_file_ancestor(repo_root, resolved):
        return {"blocker": "evidence_root_not_directory", "prompt_path": None, "output_path": None}
    if not _experiment_id_valid(experiment_id):
        return {"blocker": "experiment_id_invalid", "prompt_path": None, "output_path": None}
    base = resolved / experiment_id / "judge"
    contained_base = _contained_repo_path(repo_root, base)
    if contained_base is None:
        return {"blocker": "evidence_root_outside_repo", "prompt_path": None, "output_path": None}
    if _path_has_file_ancestor(repo_root, contained_base):
        return {"blocker": "evidence_root_not_directory", "prompt_path": None, "output_path": None}
    prompt_file = _contained_score_evidence_file(repo_root, contained_base / "prompt.txt")
    output_file = _contained_score_evidence_file(repo_root, contained_base / "ollama-output.json")
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
    if path.is_symlink():
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
        result = runner(judge_prompt, judge_profile, timeout_seconds)
    except FileNotFoundError:
        blockers.append("judge_provider_unavailable")
        return None, None, False, False, mutation_performed
    except subprocess.TimeoutExpired as exc:
        stdout = _timeout_output_text(exc.stdout)
        _write_text_evidence(repo_root, evidence["output_file"], stdout)
        blockers.append("judge_provider_timeout")
        return None, _digest_text(stdout), True, True, mutation_performed
    _write_text_evidence(repo_root, evidence["output_file"], result.stdout)
    output_digest = _digest_text(result.stdout)
    if result.exit_code != 0:
        blockers.append(f"judge_provider_exit_{result.exit_code}")
        return None, output_digest, True, True, mutation_performed
    decision, blocker = _parse_judge_decision(result.stdout, preview["comparison_payload"])
    if blocker:
        blockers.append(blocker)
    return decision, output_digest, True, True, mutation_performed


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


def _run_ollama_judge(prompt: str, judge_profile: dict[str, Any], timeout_seconds: int) -> OllamaJudgeResult:
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("OLLAMA_")
    }
    env["OLLAMA_HOST"] = str(judge_profile["host"])
    completed = subprocess.run(
        ["ollama", "run", str(judge_profile["model"])],
        input=prompt,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout_seconds,
        env=env,
    )
    return OllamaJudgeResult(exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)


def _parse_judge_decision(raw_output: str, comparison_payload: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    try:
        decision = json.loads(raw_output, parse_constant=_reject_json_constant)
    except (ValueError, json.JSONDecodeError):
        return None, "judge_output_invalid_json"
    if not isinstance(decision, dict):
        return None, "judge_output_not_object"
    blocker = _decision_contract_blocker(decision, comparison_payload)
    if blocker:
        return None, blocker
    return decision, None


def _decision_contract_blocker(decision: dict[str, Any], comparison_payload: dict[str, Any]) -> str | None:
    if set(decision) != _DECISION_KEYS:
        return "judge_decision_keys_invalid"
    if decision.get("schema_version") != DECISION_SCHEMA_VERSION:
        return "judge_decision_schema_mismatch"
    if decision.get("experiment_id") != comparison_payload["experiment_id"]:
        return "judge_decision_experiment_mismatch"
    scalar_blocker = _decision_scalar_blocker(decision)
    if scalar_blocker:
        return scalar_blocker
    dimension_blocker = _dimension_scores_blocker(decision.get("dimension_scores"))
    if dimension_blocker:
        return dimension_blocker
    return _decision_score_consistency_blocker(decision, comparison_payload)


def _decision_scalar_blocker(decision: dict[str, Any]) -> str | None:
    if decision.get("winner") not in ALLOWED_WINNERS:
        return "judge_decision_winner_invalid"
    if decision.get("confidence") not in {"low", "medium", "high"}:
        return "judge_decision_confidence_invalid"
    if not isinstance(decision.get("reason"), str) or not decision["reason"].strip():
        return "judge_decision_reason_missing"
    if not _evidence_refs_valid(decision.get("evidence_refs")):
        return "judge_decision_evidence_refs_invalid"
    return None


def _decision_score_consistency_blocker(decision: dict[str, Any], comparison_payload: dict[str, Any]) -> str | None:
    if not _normalized_scores_valid(decision):
        return "judge_decision_normalized_scores_invalid"
    computed_scores = _computed_normalized_scores(decision["dimension_scores"], comparison_payload)
    if not _normalized_scores_match(decision, computed_scores):
        return "judge_decision_normalized_scores_mismatch"
    if decision["winner"] != _expected_winner(computed_scores, decision, comparison_payload):
        return "judge_decision_winner_mismatch"
    return None


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is not allowed: {value}")


def _normalized_scores_valid(decision: dict[str, Any]) -> bool:
    for key in ("normalized_score_a", "normalized_score_b"):
        value = decision.get(key)
        if not _number_in_range(value, minimum=0, maximum=1):
            return False
    return True


def _computed_normalized_scores(
    rows: list[dict[str, Any]],
    comparison_payload: dict[str, Any],
) -> dict[str, float]:
    weights = {dimension["id"]: dimension["weight"] for dimension in comparison_payload["rubric"]["dimensions"]}
    score_a = sum(row["skill_a_score"] * weights[row["dimension_id"]] for row in rows) / 5
    score_b = sum(row["skill_b_score"] * weights[row["dimension_id"]] for row in rows) / 5
    return {"normalized_score_a": score_a, "normalized_score_b": score_b}


def _normalized_scores_match(decision: dict[str, Any], computed_scores: dict[str, float]) -> bool:
    return all(math.isclose(decision[key], computed_scores[key], rel_tol=0, abs_tol=1e-9) for key in computed_scores)


def _expected_winner(computed_scores: dict[str, float], decision: dict[str, Any], comparison_payload: dict[str, Any]) -> str:
    winner_policy = comparison_payload["rubric"]["winner_policy"]
    delta = computed_scores["normalized_score_b"] - computed_scores["normalized_score_a"]
    minimum_delta = winner_policy["minimum_normalized_delta"]
    if abs(delta) < minimum_delta:
        return winner_policy["tie_result"]
    if not _confidence_meets_minimum(decision["confidence"], winner_policy["minimum_confidence"]):
        return winner_policy["tie_result"]
    return "skill_b" if delta > 0 else "skill_a"


def _confidence_meets_minimum(value: str, minimum: str) -> bool:
    confidence_rank = {"low": 0, "medium": 1, "high": 2}
    return confidence_rank[value] >= confidence_rank[minimum]


def _dimension_scores_blocker(rows: object) -> str | None:
    if not isinstance(rows, list) or len(rows) != len(_DIMENSION_IDS):
        return "judge_dimension_scores_invalid"
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            return "judge_dimension_scores_invalid"
        if set(row) != _DIMENSION_SCORE_KEYS:
            return "judge_dimension_scores_invalid"
        dimension_id = row.get("dimension_id")
        if dimension_id not in _DIMENSION_IDS or dimension_id in seen:
            return "judge_dimension_scores_invalid"
        seen.add(dimension_id)
        if not _dimension_score_row_valid(row):
            return "judge_dimension_scores_invalid"
    return None if seen == _DIMENSION_IDS else "judge_dimension_scores_invalid"


def _dimension_score_row_valid(row: dict[str, Any]) -> bool:
    if not isinstance(row.get("reason"), str) or not row["reason"].strip():
        return False
    if not _evidence_refs_valid(row.get("evidence_refs")):
        return False
    for key in ("skill_a_score", "skill_b_score"):
        if not _number_in_range(row.get(key), minimum=0, maximum=5):
            return False
    return True


def _number_in_range(value: object, *, minimum: float, maximum: float) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value) and minimum <= value <= maximum


def _evidence_refs_valid(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def _timeout_output_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        return value
    return ""


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
    agent_summary = _score_agent_summary(status, blockers)
    return {
        "schema_version": AB_JUDGE_SCORE_SCHEMA_VERSION,
        "schema_uri": AB_JUDGE_SCORE_SCHEMA_URI,
        "status": status,
        "operation": "ab_judge_score",
        "run_receipt_path": preview["run_receipt_path"],
        "run_receipt_digest": preview["run_receipt_digest"],
        "experiment_id": preview["experiment_id"],
        "judge_profile": judge_profile,
        "rubric_id": preview["rubric_id"],
        "rubric_digest": preview["rubric_digest"],
        "decision_schema_version": DECISION_SCHEMA_VERSION,
        "allowed_winners": ALLOWED_WINNERS,
        "judge_prompt_digest": preview["judge_prompt_digest"],
        "judge_output_path": evidence["output_path"],
        "judge_output_digest": output_digest,
        "decision": decision,
        "calibration_required": True,
        "advisory_only": True,
        "provider_invoked": provider_invoked,
        "network_accessed": network_accessed,
        "mutation_performed": mutation_performed,
        "blockers": blockers,
        "acceptance_trace": ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"],
        "agent_summary": agent_summary,
    }


def _score_agent_summary(status: str, blockers: list[str]) -> str:
    if status == "scored":
        return "A/B local judge scoring completed with advisory decision evidence."
    return f"A/B local judge scoring blocked: {', '.join(blockers)}."
