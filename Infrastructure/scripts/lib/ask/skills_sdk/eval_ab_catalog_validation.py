"""Validated transport and catalog semantics for OSS-cloud preflight.

This module owns closed subprocess envelopes and the catalog contract so the
profile preflight coordinator remains focused on lane assembly.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections.abc import Callable
from typing import Any

from ask.skills_sdk.cloud_catalog_probe import DEFAULT_CATALOG_URL


CloudCatalogRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]
CatalogProbeResult = tuple[dict[str, Any] | None, str | None, dict[str, Any]]
_CATALOG_PROBE_KEYS = frozenset(
    "result_class network_accessed http_status catalog_digest matched_model match_count secret_value_observed "
    "secret_not_observed generation_performed provider_invoked codex_exec_invoked".split()
)
_CATALOG_RESULT_CLASSES = frozenset(
    "pass auth_missing http_failure timeout network_failure payload_too_large malformed_json malformed_catalog "
    "model_missing model_ambiguous invalid_catalog_url redirect_rejected".split()
)
_MAX_PROBE_STDOUT_CHARS = 1024 * 1024
_MISSING = object()


def _digest(value: object) -> str:
    return f"sha256:{hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}"


def _fact(status: str, source: str, evidence: object) -> dict[str, Any]:
    return {"status": status, "evidence_source": source, "evidence_digest": _digest(evidence), "blocker": None}


def _blocker(blocker_class: str, reason: str) -> dict[str, str]:
    return {"blocker_class": blocker_class, "reason": reason}


def _blocked_fact(blocker_class: str, reason: str, source: str, evidence: object, **fields: object) -> dict[str, Any]:
    return {**_fact("blocked", source, evidence), **fields, "blocker": _blocker(blocker_class, reason)}


def _catalog_probe_result(command: list[str], runner: CloudCatalogRunner) -> CatalogProbeResult:
    try:
        completed = runner(command)
    except subprocess.TimeoutExpired:
        return None, "timeout", {"probe_exit_class": "timeout"}
    except OSError:
        return None, "network_or_runtime_failure", {"probe_exit_class": "runtime_failure"}
    envelope, envelope_evidence = _closed_probe_envelope(completed)
    if envelope is None:
        return None, "invalid_probe_transport_envelope", envelope_evidence
    returncode, stdout, stderr = envelope
    child_evidence = {
        **envelope_evidence,
        "probe_exit_class": "zero" if returncode == 0 else "nonzero",
        "probe_stderr_empty": stderr == "",
    }
    if -255 <= returncode <= 255:
        child_evidence["probe_exit_code"] = returncode
    if stderr:
        return None, "probe_stderr_nonempty", child_evidence
    try:
        payload = json.loads(stdout, object_pairs_hook=_reject_duplicate_json_keys,
                             parse_constant=_reject_json_constant)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None, "malformed_probe_output", child_evidence
    if not _valid_catalog_probe_payload(payload):
        return None, "invalid_probe_contract", child_evidence
    result_class = str(payload["result_class"])
    expected_returncode = 0 if result_class == "pass" else 2
    child_evidence.update(
        {
            "probe_result_class": result_class,
            "probe_expected_exit_code": expected_returncode,
        }
    )
    if returncode != expected_returncode:
        return None, "probe_exit_contract_mismatch", child_evidence
    return payload, None, child_evidence


def _closed_probe_envelope(
    completed: object,
) -> tuple[tuple[int, str, str] | None, dict[str, Any]]:
    """Copy only an exact, bounded transport envelope across the subprocess boundary."""
    returncode, returncode_class = _read_probe_attribute(completed, "returncode", int)
    stdout, stdout_class = _read_probe_attribute(completed, "stdout", str)
    stderr, stderr_class = _read_probe_attribute(completed, "stderr", str)
    evidence = {
        "probe_transport_class": "closed",
        "probe_returncode_class": returncode_class,
        "probe_stdout_class": stdout_class,
        "probe_stderr_class": stderr_class,
    }
    if returncode_class != "exact_int" or stdout_class != "exact_str" or stderr_class != "exact_str":
        evidence["probe_transport_class"] = "invalid"
        return None, evidence
    assert type(returncode) is int and type(stdout) is str and type(stderr) is str
    stdout_frame = _probe_stdout_frame_class(stdout)
    evidence["probe_stdout_class"] = stdout_frame
    if stdout_frame != "bounded_json_text":
        evidence["probe_transport_class"] = "invalid"
        return None, evidence
    return (returncode, stdout, stderr), evidence


_UNTRUSTED_ATTRIBUTE_EXCEPTION = BaseException


def _read_probe_attribute(
    completed: object, name: str, expected_type: type[int] | type[str],
) -> tuple[object, str]:
    try:
        value = getattr(completed, name, _MISSING)
    except _UNTRUSTED_ATTRIBUTE_EXCEPTION:
        return _MISSING, "attribute_access_failure"
    if value is _MISSING:
        return _MISSING, "missing"
    if type(value) is not expected_type:
        return _MISSING, "invalid_type"
    return value, "exact_int" if expected_type is int else "exact_str"


def _probe_stdout_frame_class(stdout: str) -> str:
    if len(stdout) > _MAX_PROBE_STDOUT_CHARS:
        return "oversized"
    if "\x00" in stdout:
        return "invalid_framing"
    for index, character in enumerate(stdout):
        if ord(character) >= 32:
            continue
        if character == "\n" and index == len(stdout) - 1:
            continue
        return "invalid_framing"
    return "bounded_json_text"


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError("duplicate JSON key")
        payload[key] = value
    return payload


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant: {value}")


def _is_digest(value: object) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
        return False
    return all(character in "0123456789abcdef" for character in value[7:])


def _valid_catalog_probe_payload(payload: object) -> bool:
    if not isinstance(payload, dict) or set(payload) != _CATALOG_PROBE_KEYS:
        return False
    result_class = payload["result_class"]
    if type(result_class) is not str or result_class not in _CATALOG_RESULT_CLASSES:
        return False
    return _valid_catalog_probe_types(payload) and _safe_catalog_probe_flags(payload) and (
        _valid_catalog_result_semantics(payload)
    )

def _valid_catalog_probe_types(payload: dict[str, Any]) -> bool:
    for field in (
        "network_accessed", "secret_value_observed", "secret_not_observed",
        "generation_performed", "provider_invoked", "codex_exec_invoked",
    ):
        if type(payload[field]) is not bool:
            return False
    return _valid_catalog_probe_nullable_types(payload)


def _valid_catalog_probe_nullable_types(payload: dict[str, Any]) -> bool:
    http_status = payload["http_status"]
    match_count = payload["match_count"]
    if http_status is not None and (type(http_status) is not int or not 100 <= http_status <= 599):
        return False
    if match_count is not None and (type(match_count) is not int or match_count < 0):
        return False
    if payload["catalog_digest"] is not None and not _is_digest(payload["catalog_digest"]):
        return False
    if payload["matched_model"] is not None and type(payload["matched_model"]) is not str:
        return False
    return True


def _safe_catalog_probe_flags(payload: dict[str, Any]) -> bool:
    return not any((
        payload["secret_value_observed"] is not False,
        payload["secret_not_observed"] is not True,
        payload["generation_performed"] is not False,
        payload["provider_invoked"] is not False,
        payload["codex_exec_invoked"] is not False,
    ))


def _valid_catalog_result_semantics(payload: dict[str, Any]) -> bool:
    validators = {
        "pass": _valid_pass_semantics,
        "invalid_catalog_url": _valid_auth_missing_semantics,
        "redirect_rejected": _valid_transport_failure_semantics,
        "model_missing": _valid_missing_semantics,
        "model_ambiguous": _valid_ambiguous_semantics,
        "malformed_json": _valid_catalog_parse_failure_semantics,
        "malformed_catalog": _valid_catalog_parse_failure_semantics,
        "payload_too_large": _valid_catalog_parse_failure_semantics,
        "http_failure": _valid_http_failure_semantics,
        "timeout": _valid_transport_failure_semantics,
        "network_failure": _valid_transport_failure_semantics,
        "auth_missing": _valid_auth_missing_semantics,
    }
    validator = validators.get(payload["result_class"])
    return validator is not None and validator(payload)


def _valid_pass_semantics(payload: dict[str, Any]) -> bool:
    return (
        _has_successful_catalog_response(payload)
        and payload["matched_model"] is not None and payload["match_count"] == 1
    )


def _valid_missing_semantics(payload: dict[str, Any]) -> bool:
    return (
        _has_successful_catalog_response(payload)
        and payload["matched_model"] is None and payload["match_count"] == 0
    )


def _valid_ambiguous_semantics(payload: dict[str, Any]) -> bool:
    count = payload["match_count"]
    return (
        _has_successful_catalog_response(payload)
        and payload["matched_model"] is None and type(count) is int and count > 1
    )


def _has_successful_catalog_response(payload: dict[str, Any]) -> bool:
    status = payload["http_status"]
    return (
        payload["network_accessed"] is True and type(status) is int and 200 <= status < 300
        and payload["catalog_digest"] is not None
    )


def _has_no_catalog_claims(payload: dict[str, Any]) -> bool:
    return (
        payload["catalog_digest"] is None and payload["matched_model"] is None
        and payload["match_count"] is None
    )


def _valid_catalog_parse_failure_semantics(payload: dict[str, Any]) -> bool:
    status = payload["http_status"]
    return (
        payload["network_accessed"] is True and type(status) is int and 200 <= status < 300
        and _has_no_catalog_claims(payload)
    )


def _valid_http_failure_semantics(payload: dict[str, Any]) -> bool:
    status = payload["http_status"]
    return (
        payload["network_accessed"] is True and type(status) is int and not 200 <= status < 300
        and _has_no_catalog_claims(payload)
    )


def _valid_transport_failure_semantics(payload: dict[str, Any]) -> bool:
    return (
        payload["network_accessed"] is True and payload["http_status"] is None
        and _has_no_catalog_claims(payload)
    )


def _valid_auth_missing_semantics(payload: dict[str, Any]) -> bool:
    return (
        payload["network_accessed"] is False and payload["http_status"] is None
        and _has_no_catalog_claims(payload)
    )


def _passing_catalog_probe(payload: dict[str, Any], selected_model: str) -> bool:
    digest = payload.get("catalog_digest")
    return all((
        payload.get("result_class") == "pass",
        payload.get("network_accessed") is True,
        isinstance(payload.get("http_status"), int) and 200 <= payload["http_status"] < 300,
        isinstance(digest, str) and digest.startswith("sha256:") and len(digest) == 71,
        payload.get("matched_model") == selected_model,
        payload.get("match_count") == 1,
        payload.get("secret_value_observed") is False,
        payload.get("secret_not_observed") is True,
        payload.get("generation_performed") is False,
        payload.get("provider_invoked") is False,
        payload.get("codex_exec_invoked") is False,
    ))


def _catalog_result_fields(selected_model: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "selected_model_id": selected_model,
        "catalog_identity": DEFAULT_CATALOG_URL,
        "probe_url": DEFAULT_CATALOG_URL,
        "http_status": payload.get("http_status"),
        "catalog_digest": payload.get("catalog_digest"),
        "matched_model": payload.get("matched_model"),
        "catalog_match_source": "exact_catalog" if payload.get("result_class") == "pass" else None,
        "catalog_probe_result_class": payload.get("result_class"),
        "network_accessed": payload.get("network_accessed") is True,
        "secret_value_observed": False,
        "generation_performed": False,
        "provider_invoked": False,
        "codex_exec_invoked": False,
    }


def _blocked_catalog_probe(
    selected_model: str, evidence: dict[str, Any], blocker_class: str, reason: str,
    *, network_accessed: bool,
) -> dict[str, Any]:
    payload = {"network_accessed": network_accessed}
    return _blocked_fact(
        blocker_class, reason, DEFAULT_CATALOG_URL, {**evidence, **payload},
        **_catalog_result_fields(selected_model, payload),
    )
