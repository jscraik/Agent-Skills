from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tomllib
from typing import Any, Callable

from ask.skills_sdk.ab_profile_contracts import (
    PREFLIGHT_BLOCKER_CLASSES,
    codex_identity_evidence_digest,
    preflight_fact_status_is_admitted,
    resolve_installed_codex_identity,
)
from ask.skills_sdk.cloud_catalog_probe import DEFAULT_CATALOG_URL


PreflightProbe = Callable[[dict[str, Any]], dict[str, Any]]
CloudCatalogRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]
OllamaInventoryResult = tuple[subprocess.CompletedProcess[str] | None, dict[str, Any] | None]
CatalogProbeResult = tuple[dict[str, Any] | None, str | None, dict[str, Any]]
_CLOUD_CATALOG_PROBE = Path(__file__).with_name("cloud_catalog_probe.py")
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


def _profile_filename(lane: str) -> str: return f"{lane}.config.toml"


def _expected_provider(lane: str) -> str | None: return {"oss-local": "ollama", "oss-cloud": "ollama-cloud"}.get(lane)


def _digest(value: object) -> str:
    return f"sha256:{hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}"


def _blocked_fact(blocker_class: str, reason: str, source: str, evidence: object, **fields: object) -> dict[str, Any]:
    return {
        **_fact("blocked", source, evidence),
        **fields,
        "blocker": _blocker(blocker_class, reason),
    }


def _profile_path(lane: str) -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / _profile_filename(lane)


def _read_profile(lane: str, expected_model: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    path = _profile_path(lane)
    source = str(path)
    evidence = {"path": source, "exists": path.is_file(), "lane": lane}
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return None, _blocked_fact(
            "profile_config_missing_or_invalid",
            f"installed {lane} profile is unavailable or invalid: {type(exc).__name__}",
            source,
            evidence,
            profile_id=lane,
            configured_model_id=None,
            configured_provider_id=None,
        )
    model = payload.get("model")
    provider = payload.get("model_provider")
    evidence.update({"model": model, "model_provider": provider})
    if model != expected_model or provider != _expected_provider(lane):
        return None, _blocked_fact(
            "profile_config_missing_or_invalid",
            "installed profile model or provider does not match the selected lane",
            source,
            evidence,
            profile_id=lane,
            configured_model_id=model if isinstance(model, str) and model else None,
            configured_provider_id=(
                provider if provider in {"ollama", "ollama-cloud"} else None
            ),
        )
    return payload, {
        **_fact("pass", source, evidence),
        "profile_id": lane,
        "configured_model_id": model,
        "configured_provider_id": provider,
    }


def _local_catalog_fact(profile: dict[str, Any], selected_model: str) -> dict[str, Any]:
    raw_path = profile.get("model_catalog_json")
    source = str(raw_path or _profile_path("oss-local"))
    if not isinstance(raw_path, str) or not raw_path:
        return _blocked_fact(
            "model_catalog_entry_missing", "installed profile has no model_catalog_json", source,
            {"catalog_configured": False}, selected_model_id=selected_model, catalog_identity="unresolved",
        )
    path = Path(raw_path).expanduser()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _blocked_fact(
            "model_catalog_entry_missing", f"configured model catalog is unavailable: {type(exc).__name__}",
            str(path), {"path": str(path), "exists": path.is_file()},
            selected_model_id=selected_model, catalog_identity=str(path),
        )
    models = payload.get("models") if isinstance(payload, dict) else None
    slugs = [row.get("slug") for row in models if isinstance(row, dict)] if isinstance(models, list) else []
    evidence = {"path": str(path), "catalog_digest": _digest(payload), "model_slugs": sorted(str(x) for x in slugs)}
    if selected_model not in slugs:
        return _blocked_fact(
            "model_catalog_entry_missing", "selected model is absent from the configured model catalog",
            str(path), evidence, selected_model_id=selected_model, catalog_identity=str(path),
        )
    return {
        **_fact("pass", str(path), evidence),
        "selected_model_id": selected_model,
        "catalog_identity": str(path),
    }


def _local_runtime_fact(selected_model: str) -> dict[str, Any]:
    codex = shutil.which("codex")
    ollama = shutil.which("ollama")
    source = ollama or "PATH:ollama"
    if codex is None:
        return _blocked_fact(
            "codex_cli_unavailable", "Codex CLI is not installed on PATH", "PATH:codex",
            {"binary_resolved": False}, availability_kind="local_model", selected_model_id=selected_model,
        )
    if ollama is None:
        return _blocked_fact(
            "local_runtime_binary_unavailable", "Ollama CLI is not installed on PATH", source,
            {"binary_resolved": False}, availability_kind="local_model", selected_model_id=selected_model,
        )
    completed, failure = _ollama_inventory(ollama, selected_model)
    if failure is not None:
        return failure
    assert completed is not None
    evidence = {"argv": [ollama, "list"], "exit_code": completed.returncode}
    if completed.returncode != 0:
        return _blocked_fact(
            "local_runtime_service_unavailable", "Ollama model inventory probe returned non-zero",
            source, evidence, availability_kind="local_model", selected_model_id=selected_model,
        )
    model_names = {
        line.split()[0] for line in completed.stdout.splitlines()[1:] if line.strip() and line.split()
    }
    evidence["model_name_digests"] = sorted(_digest(name) for name in model_names)
    if selected_model not in model_names:
        return _blocked_fact(
            "local_model_unavailable", "selected local model is absent from Ollama inventory",
            source, evidence, availability_kind="local_model", selected_model_id=selected_model,
        )
    return {
        **_fact("pass", source, evidence),
        "availability_kind": "local_model",
        "selected_model_id": selected_model,
    }


def _ollama_inventory(ollama: str, selected_model: str) -> OllamaInventoryResult:
    try:
        completed = subprocess.run(
            [ollama, "list"], capture_output=True, check=False, text=True, timeout=10,
            # Never allow a caller-provided remote endpoint to redirect the local probe.
            env={name: value for name, value in os.environ.items() if name in {"HOME", "PATH"}},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        failure = _blocked_fact(
            "local_runtime_service_unavailable", f"Ollama model inventory probe failed: {type(exc).__name__}",
            ollama, {"argv": [ollama, "list"], "probe_error": type(exc).__name__},
            availability_kind="local_model", selected_model_id=selected_model,
        )
        return None, failure
    return completed, None


def _cloud_runtime_fact(selected_model: str, profile_path: Path) -> dict[str, Any]:
    installed_identity = resolve_installed_codex_identity()
    evidence = {"codex_binary_resolved": installed_identity is not None, "profile_path": str(profile_path)}
    if installed_identity is None:
        return _blocked_fact(
            "codex_cli_unavailable", "Codex CLI is absent or its identity probe failed", "PATH:codex", evidence,
            availability_kind="cloud_endpoint", selected_model_id=selected_model,
        )
    codex, identity = installed_identity
    return {
        "status": "not_applicable", "evidence_source": codex,
        "evidence_digest": codex_identity_evidence_digest(codex, identity), "blocker": None,
        "availability_kind": "cloud_endpoint", "selected_model_id": selected_model,
        "codex_executable_identity": identity,
    }


def _approved_cloud_auth_fact(selected_model: str) -> dict[str, Any]:
    path = Path(os.environ.get("SKILLS_SDK_OSS_CLOUD_ENV_FILE", Path.home() / ".codex" / ".env"))
    source = "operator-approved-op-env-stream"
    approved = False
    source_kind = "missing_or_invalid"
    try:
        mode = path.lstat().st_mode
        if stat.S_ISFIFO(mode):
            approved, source_kind = True, "op_fifo"
    except OSError:
        pass
    op_binary = shutil.which("op")
    evidence = {
        "auth_source": source_kind,
        "op_binary_resolved": op_binary is not None,
        "credential_presence": "delegated_to_op_run" if approved else "unavailable",
        "env_stream_content_observed": False,
    }
    if not approved or op_binary is None:
        return _blocked_fact(
            "cloud_auth_unavailable", "approved opaque 1Password env stream or CLI is unavailable",
            source, evidence, auth_reference="codex_cli_auth", secret_value_observed=False,
            auth_source=source_kind,
        )
    return {
        **_fact("pass", source, evidence),
        "auth_reference": "codex_cli_auth",
        "secret_value_observed": False,
        "auth_source": source_kind,
    }


def _cloud_catalog_command(op_binary: str, env_file: Path, selected_model: str) -> list[str]:
    return [
        op_binary, "run", "--env-file", str(env_file), "--", sys.executable,
        str(_CLOUD_CATALOG_PROBE), "--url", DEFAULT_CATALOG_URL, "--model", selected_model,
        "--timeout-seconds", "10",
    ]


def _run_cloud_catalog(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, capture_output=True, check=False, text=True, timeout=15,
        env={name: value for name, value in os.environ.items() if name in {"HOME", "PATH"}},
    )


def _safe_command_shape(command: list[str]) -> list[str]:
    safe = list(command)
    env_index = safe.index("--env-file") + 1
    safe[env_index] = "<operator-approved-opaque-env-stream>"
    return safe


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


def _catalog_fact_from_payload(
    selected_model: str, evidence: dict[str, Any], payload: dict[str, Any],
) -> dict[str, Any]:
    result_class = str(payload["result_class"])
    safe_evidence = {**evidence, **payload}
    fields = _catalog_result_fields(selected_model, payload)
    if _passing_catalog_probe(payload, selected_model):
        return {**_fact("pass", DEFAULT_CATALOG_URL, safe_evidence), **fields}
    if result_class == "pass":
        result_class = "unverifiable_catalog_evidence"
    blocker_class = "cloud_auth_unavailable" if result_class == "auth_missing" else (
        "selected_model_unavailable" if result_class in {"model_missing", "model_ambiguous"}
        else "cloud_catalog_unavailable"
    )
    return _blocked_fact(
        blocker_class, f"cloud catalog probe did not prove the selected model: {result_class}",
        DEFAULT_CATALOG_URL, safe_evidence, **fields,
    )


def _cloud_catalog_fact(
    selected_model: str,
    profile_path: Path,
    auth_fact: dict[str, Any],
    runner: CloudCatalogRunner = _run_cloud_catalog,
) -> dict[str, Any]:
    env_file = Path(os.environ.get("SKILLS_SDK_OSS_CLOUD_ENV_FILE", Path.home() / ".codex" / ".env"))
    op_binary = shutil.which("op")
    evidence = {
        "profile_path": str(profile_path),
        "selected_model_digest": _digest(selected_model),
        "probe_url": DEFAULT_CATALOG_URL,
        "safe_non_generation_catalog_probe": True,
        "auth_source": auth_fact.get("auth_source", "missing_or_invalid"),
        "secret_value_observed": False,
        "generation_performed": False,
        "provider_invoked": False,
        "codex_exec_invoked": False,
    }
    if auth_fact.get("status") != "pass" or op_binary is None:
        return _blocked_catalog_probe(
            selected_model, evidence, "cloud_auth_unavailable",
            "cloud catalog probe requires the approved op-run auth boundary", network_accessed=False,
        )
    command = _cloud_catalog_command(op_binary, env_file, selected_model)
    evidence["probe_command_shape"] = _safe_command_shape(command)
    payload, failure, child_evidence = _catalog_probe_result(command, runner)
    evidence.update(child_evidence)
    if payload is None:
        return _blocked_catalog_probe(
            selected_model, evidence, "cloud_catalog_unavailable",
            f"cloud catalog probe failed: {failure}",
            network_accessed=False,
        )
    return _catalog_fact_from_payload(selected_model, evidence, payload)


def installed_profile_preflight(profile: dict[str, Any]) -> dict[str, Any]:
    """Probe installed profile, catalog, runtime, and auth without generation."""
    lane = str(profile["id"])
    model = str(profile["model"])
    profile_payload, profile_fact = _read_profile(lane, model)
    if profile_payload is None:
        return _unresolved_profile_facts(lane, model, profile_fact)
    if lane == "oss-local":
        return _local_profile_facts(profile_payload, profile_fact, model)
    return _cloud_profile_facts(profile_fact, model)


def _catalog_fact(model_catalog: dict[str, Any], identity: str) -> dict[str, Any]:
    return {
        "status": model_catalog["status"], "evidence_source": model_catalog["evidence_source"],
        "evidence_digest": model_catalog["evidence_digest"], "blocker": model_catalog["blocker"],
        "catalog_identity": identity,
    }


def _unresolved_profile_facts(lane: str, model: str, profile_fact: dict[str, Any]) -> dict[str, Any]:
    source = str(_profile_path(lane))
    missing_catalog = _blocked_fact(
        "model_catalog_entry_missing", "profile must resolve before its model catalog can be checked",
        source, {"profile_resolved": False}, selected_model_id=model, catalog_identity="unresolved",
    )
    missing_runtime = _blocked_fact(
        "local_runtime_unavailable" if lane == "oss-local" else "selected_model_unavailable",
        "profile must resolve before runtime admission can be checked", source, {"profile_resolved": False},
        availability_kind="local_model" if lane == "oss-local" else "cloud_endpoint", selected_model_id=model,
    )
    auth = (
        {**_fact("not_applicable", source, {"lane": lane}), "auth_reference": "none", "secret_value_observed": False}
        if lane == "oss-local" else _approved_cloud_auth_fact(model)
    )
    return {
        "profile_config": profile_fact,
        "model_catalog": missing_catalog, "runtime": missing_runtime, "auth": auth,
        "catalog": _catalog_fact(missing_catalog, "unresolved"),
    }


def _local_profile_facts(
    profile_payload: dict[str, Any], profile_fact: dict[str, Any], model: str,
) -> dict[str, Any]:
    model_catalog = _local_catalog_fact(profile_payload, model)
    source = str(_profile_path("oss-local"))
    return {
        "profile_config": profile_fact, "model_catalog": model_catalog, "runtime": _local_runtime_fact(model),
        "auth": {
            **_fact("not_applicable", source, {"lane": "oss-local"}),
            "auth_reference": "none", "secret_value_observed": False,
        },
        "catalog": _catalog_fact(model_catalog, str(model_catalog["catalog_identity"])),
    }


def _cloud_profile_facts(profile_fact: dict[str, Any], model: str) -> dict[str, Any]:
    path = _profile_path("oss-cloud")
    auth = _approved_cloud_auth_fact(model)
    cloud_catalog = _cloud_catalog_fact(model, path, auth)
    return {
        "profile_config": profile_fact, "model_catalog": cloud_catalog,
        "runtime": _cloud_runtime_fact(model, path), "auth": auth,
        "catalog": _catalog_fact(cloud_catalog, str(cloud_catalog["catalog_identity"])),
    }


def _fact(status: str, source: str, evidence: object) -> dict[str, Any]:
    return {
        "status": status,
        "evidence_source": source,
        "evidence_digest": _digest(evidence),
        "blocker": None,
    }


def build_lane_preflight(profile: dict[str, Any], probe: PreflightProbe | None = None) -> dict[str, Any]:
    facts = (probe or installed_profile_preflight)(profile)
    consistency_blockers = _consistency_blockers(profile, facts)
    _attach_consistency_blockers(facts, consistency_blockers)
    blockers = _fact_blockers(str(profile["id"]), facts)
    return {
        **facts,
        "admission": {
            "status": "pass" if not blockers else "blocked",
            "blockers": blockers,
            "secret_values_observed": False,
        },
    }


def _attach_consistency_blockers(
    facts: dict[str, Any], blockers: list[dict[str, str]],
) -> None:
    """Make every admission blocker owned by a typed fact, never metadata-only."""
    owners = {
        "profile_config_missing_or_invalid": "profile_config",
        "model_catalog_entry_missing": "model_catalog",
        "selected_model_unavailable": "model_catalog",
        "local_runtime_unavailable": "runtime",
        "codex_cli_unavailable": "runtime",
        "local_runtime_binary_unavailable": "runtime",
        "local_runtime_service_unavailable": "runtime",
        "local_model_unavailable": "runtime",
        "cloud_auth_unavailable": "auth",
        "cloud_catalog_unavailable": "model_catalog",
        "preflight_evidence_missing": "runtime",
    }
    for blocker in blockers:
        key = owners.get(blocker.get("blocker_class"))
        fact = facts.get(key) if key else None
        if not isinstance(fact, dict) or fact.get("blocker") is not None:
            continue
        fact["status"] = "blocked"
        fact["blocker"] = blocker


def _fact_blockers(lane: str, facts: dict[str, Any]) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    profile_config = facts.get("profile_config", {})
    model_catalog = facts.get("model_catalog", {})
    for key in ("profile_config", "model_catalog", "runtime", "auth", "catalog"):
        fact = facts.get(key)
        if not isinstance(fact, dict):
            blockers.append(_blocker("preflight_evidence_missing", f"{key} evidence is missing"))
            continue
        blocker = fact.get("blocker")
        admitted = preflight_fact_status_is_admitted(
            lane=lane, key=key, fact=fact,
            profile_config=profile_config, model_catalog=model_catalog,
        )
        if not admitted:
            if not isinstance(blocker, dict) or blocker.get("blocker_class") not in PREFLIGHT_BLOCKER_CLASSES:
                blockers.append(_blocker("preflight_evidence_missing", f"{key} status does not prove the lane"))
            else:
                blockers.append({"blocker_class": blocker["blocker_class"], "reason": str(blocker["reason"])})
        if fact.get("evidence_source") is None or fact.get("evidence_digest") is None:
            blockers.append(_blocker("preflight_evidence_missing", f"{key} evidence provenance is missing"))
    return _unique_blockers(blockers)

def _unique_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for blocker in blockers:
        identity = (blocker["blocker_class"], blocker["reason"])
        if identity not in seen:
            seen.add(identity)
            unique.append(blocker)
    return unique


def _consistency_blockers(profile: dict[str, Any], facts: dict[str, Any]) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    profile_id = facts.get("profile_config", {}).get("profile_id")
    configured_model = facts.get("profile_config", {}).get("configured_model_id")
    configured_provider = facts.get("profile_config", {}).get("configured_provider_id")
    selected_model = facts.get("model_catalog", {}).get("selected_model_id")
    runtime_model = facts.get("runtime", {}).get("selected_model_id")
    runtime_kind = facts.get("runtime", {}).get("availability_kind")
    if profile_id != profile.get("id"):
        blockers.append(_blocker("profile_config_missing_or_invalid", "resolved profile id does not match lane"))
    if configured_model != profile.get("model"):
        blockers.append(
            _blocker(
                "profile_config_missing_or_invalid",
                "configured profile model does not match selected profile",
            )
        )
    if configured_provider != _expected_provider(str(profile.get("id"))):
        blockers.append(
            _blocker(
                "profile_config_missing_or_invalid",
                "configured profile provider does not match selected lane",
            )
        )
    if not selected_model or selected_model != profile.get("model"):
        blockers.append(_blocker("selected_model_unavailable", "selected model does not match profile catalog"))
    if runtime_model != selected_model:
        blockers.append(_blocker("selected_model_unavailable", "runtime model does not match selected catalog model"))
    expected_runtime_kind = "local_model" if profile.get("id") == "oss-local" else "cloud_endpoint"
    if runtime_kind != expected_runtime_kind:
        blockers.append(_blocker("local_runtime_unavailable", "runtime availability kind does not match lane"))
    if profile.get("id") == "oss-cloud" and facts.get("auth", {}).get("auth_reference") != "codex_cli_auth":
        blockers.append(_blocker("cloud_auth_unavailable", "approved cloud auth reference is unavailable"))
    return blockers


def _blocker(blocker_class: str, reason: str) -> dict[str, str]:
    return {"blocker_class": blocker_class, "reason": reason}
