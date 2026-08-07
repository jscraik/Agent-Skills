from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
import shutil
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
from ask.skills_sdk.ab_transport_contracts import (
    OSS_CLOUD_REQUIRED_ENV,
    actual_opaque_env_path,
    configs_auth_wrapper,
    configs_codex_exec_wrapper,
    is_actual_opaque_env_reference,
    opaque_env_identity_digest,
)
from ask.skills_sdk.eval_ab_catalog_validation import (
    CloudCatalogRunner,
    _blocked_catalog_probe,
    _catalog_result_fields,
    _catalog_probe_result,
    _closed_probe_envelope,
    _reject_duplicate_json_keys,
    _reject_json_constant,
    _passing_catalog_probe,
)


PreflightProbe = Callable[[dict[str, Any]], dict[str, Any]]
CloudSmokeRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]
OllamaInventoryResult = tuple[subprocess.CompletedProcess[str] | None, dict[str, Any] | None]
_CLOUD_CATALOG_PROBE = Path(__file__).with_name("cloud_catalog_probe.py")
_CLOUD_SMOKE_RUNNER = Path(__file__).parents[3] / "validation-and-linting" / "run_oss_cloud_smoke.py"
_CLOUD_SMOKE_MARKER = "CODEX_OSS_CLOUD_OK"


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
    default_stream = actual_opaque_env_path()
    path = Path(os.environ.get("SKILLS_SDK_OSS_CLOUD_ENV_FILE", str(default_stream) if default_stream else ""))
    source = "operator-approved-op-env-stream"
    approved = is_actual_opaque_env_reference(str(path))
    source_kind = "1password_desktop_fifo" if approved else "missing_or_invalid"
    auth_wrapper = configs_auth_wrapper()
    evidence = {
        "auth_source": source_kind,
        "configs_auth_wrapper_resolved": auth_wrapper is not None,
        "credential_presence": "delegated_to_configs_auth_wrapper" if approved else "unavailable",
        "env_stream_content_observed": False,
        "auth_stream_identity_digest": opaque_env_identity_digest(path),
    }
    if not approved or auth_wrapper is None:
        return _blocked_fact(
            "cloud_auth_unavailable", "approved opaque 1Password env stream or Configs wrapper is unavailable",
            source, evidence, auth_reference="codex_cli_auth", secret_value_observed=False,
            auth_source=source_kind,
        )
    return {
        **_fact("pass", source, evidence),
        "auth_reference": "codex_cli_auth",
        "secret_value_observed": False,
        "auth_source": source_kind,
        "auth_stream_identity_digest": evidence["auth_stream_identity_digest"],
    }

def _cloud_catalog_command(auth_wrapper: str, env_file: Path, selected_model: str) -> list[str]:
    return [
        "bash", auth_wrapper,
        "--env-file", str(env_file),
        "--require-env", OSS_CLOUD_REQUIRED_ENV,
        "--", sys.executable, str(_CLOUD_CATALOG_PROBE),
        "--url", DEFAULT_CATALOG_URL, "--model", selected_model, "--timeout-seconds", "10",
    ]

def _run_cloud_catalog(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, check=False, text=True, timeout=15, env={name: value for name, value in os.environ.items() if name in {"HOME", "PATH"}})


def _cloud_smoke_command(
    profile_path: Path, env_file: Path, auth_wrapper: str,
) -> list[str]:
    codex_wrapper = configs_codex_exec_wrapper() or "/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh"
    return [
        sys.executable,
        str(_CLOUD_SMOKE_RUNNER),
        "--profile-source", str(profile_path),
        "--env-file", str(env_file),
        "--auth-wrapper", auth_wrapper,
        "--codex-exec-wrapper", codex_wrapper,
        "--marker", _CLOUD_SMOKE_MARKER,
        "--timeout-seconds", "120",
        "--json",
    ]


def _run_cloud_smoke(command: list[str]) -> subprocess.CompletedProcess[str]:
    # Keep the child environment minimal, but preserve the identity-bound
    # executable selected by Configs.  Dropping CODEX_CLI_PATH silently falls
    # back to the caller's PATH (often a mise shim), which can hang in the
    # empty smoke cwd and produce a misleading invalid receipt.
    environment = {
        name: value
        for name, value in os.environ.items()
        if name in {"HOME", "PATH", "CODEX_CLI_PATH"}
    }
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=135,
        env=environment,
    )

def _safe_command_shape(command: list[str]) -> list[str]:
    safe = list(command)
    env_index = safe.index("--env-file") + 1
    safe[env_index] = "<operator-approved-opaque-env-stream>"
    return safe


def _valid_observed_at(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _cloud_smoke_result(
    command: list[str], runner: CloudSmokeRunner,
) -> tuple[dict[str, Any] | None, str | None, dict[str, Any]]:
    try:
        completed = runner(command)
    except subprocess.TimeoutExpired:
        return None, "timeout", {"smoke_exit_class": "timeout"}
    except OSError:
        return None, "runtime_failure", {"smoke_exit_class": "runtime_failure"}
    envelope, envelope_evidence = _closed_probe_envelope(completed)
    if envelope is None:
        return None, "invalid_smoke_transport_envelope", envelope_evidence
    returncode, stdout, stderr = envelope
    evidence = {
        **envelope_evidence,
        "smoke_exit_class": "zero" if returncode == 0 else "nonzero",
        "smoke_stderr_empty": stderr == "",
    }
    if stderr:
        return None, "smoke_stderr_nonempty", evidence
    try:
        payload = json.loads(
            stdout,
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_json_constant,
        )
    except (TypeError, ValueError, json.JSONDecodeError):
        return None, "malformed_smoke_output", evidence
    if not isinstance(payload, dict):
        return None, "invalid_smoke_contract", evidence
    if not _valid_cloud_smoke_receipt(payload):
        return None, "invalid_smoke_contract", evidence
    expected_returncode = 0 if payload["status"] == "pass" else 1
    evidence.update({
        "smoke_receipt_status": payload["status"],
        "smoke_expected_exit_code": expected_returncode,
    })
    if returncode != expected_returncode:
        return None, "smoke_exit_contract_mismatch", evidence
    return payload, None, evidence


def _valid_cloud_smoke_receipt(payload: dict[str, Any]) -> bool:
    required = {
        "schema_version", "observed_at", "status", "lane", "codex_profile", "model",
        "model_provider", "auth_source", "provider_invoked", "exit_code", "marker",
        "warnings", "findings",
    }
    if not required.issubset(payload) or payload.get("schema_version") != "skills-sdk.oss-cloud-smoke-run.v0":
        return False
    return _valid_cloud_smoke_identity(payload) and _valid_cloud_smoke_outcome(payload)


def _valid_cloud_smoke_identity(payload: dict[str, Any]) -> bool:
    return all((
        payload.get("lane") == "oss-cloud",
        payload.get("codex_profile") == "oss-cloud",
        payload.get("model") == "deepseek-v4-flash:cloud",
        payload.get("model_provider") == "ollama-cloud",
        payload.get("auth_source") == "1password_desktop_fifo",
        type(payload.get("provider_invoked")) is bool and payload.get("provider_invoked") is True,
    ))


def _valid_cloud_smoke_outcome(payload: dict[str, Any]) -> bool:
    return all((
        payload.get("status") in {"pass", "blocked"},
        payload.get("exit_code") == 0,
        payload.get("marker") == _CLOUD_SMOKE_MARKER,
        payload.get("findings") == [],
        isinstance(payload.get("warnings"), list),
        _valid_observed_at(payload.get("observed_at")),
        payload.get("status") == "pass",
        payload.get("secret_value_observed", False) is False,
    ))



def _catalog_fact_from_payload(
    selected_model: str,
    evidence: dict[str, Any],
    payload: dict[str, Any],
    *,
    profile_path: Path | None = None,
    auth_fact: dict[str, Any] | None = None,
    env_file: Path | None = None,
    auth_wrapper: str | None = None,
    smoke_runner: CloudSmokeRunner | None = None,
    profile_evidence_digest: str | None = None,
    codex_executable_identity: str | None = None,
) -> dict[str, Any]:
    result_class = str(payload["result_class"])
    safe_evidence = {**evidence, **payload}
    fields = _catalog_result_fields(selected_model, payload)
    if _passing_catalog_probe(payload, selected_model):
        return {**_fact("pass", DEFAULT_CATALOG_URL, safe_evidence), **fields}
    if result_class in {"model_missing", "model_ambiguous"}:
        return _direct_smoke_catalog_fact(
            selected_model, result_class, safe_evidence, fields,
            profile_path=profile_path, auth_fact=auth_fact, env_file=env_file,
            auth_wrapper=auth_wrapper, smoke_runner=smoke_runner,
            profile_evidence_digest=profile_evidence_digest,
            codex_executable_identity=codex_executable_identity,
        )
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


def _direct_smoke_catalog_fact(
    selected_model: str,
    result_class: str,
    evidence: dict[str, Any],
    fields: dict[str, Any],
    *,
    profile_path: Path | None,
    auth_fact: dict[str, Any] | None,
    env_file: Path | None,
    auth_wrapper: str | None,
    smoke_runner: CloudSmokeRunner | None,
    profile_evidence_digest: str | None,
    codex_executable_identity: str | None,
) -> dict[str, Any]:
    required = (profile_path, env_file, auth_wrapper, profile_evidence_digest, codex_executable_identity)
    if smoke_runner is None or any(value is None for value in required):
        return _blocked_fact(
            "catalog_alias_unlisted",
            f"cloud catalog returned {result_class}; exact-model direct smoke was not admitted",
            DEFAULT_CATALOG_URL, evidence, **fields,
        )
    smoke_command = _cloud_smoke_command(profile_path, env_file, auth_wrapper)
    evidence["direct_smoke_command_shape"] = _safe_smoke_command_shape(smoke_command)
    smoke_receipt, smoke_failure, smoke_evidence = _cloud_smoke_result(smoke_command, smoke_runner)
    evidence["direct_smoke_evidence"] = smoke_evidence
    if smoke_receipt is None:
        return _blocked_fact(
            "catalog_alias_unlisted",
            f"cloud catalog returned {result_class}; direct provider smoke failed: {smoke_failure}",
            DEFAULT_CATALOG_URL, evidence, **fields,
        )
    return _direct_smoke_pass_fact(
        selected_model, evidence, fields, smoke_receipt,
        profile_path=profile_path, auth_fact=auth_fact,
        profile_evidence_digest=profile_evidence_digest,
        codex_executable_identity=codex_executable_identity,
    )


def _direct_smoke_pass_fact(
    selected_model: str,
    evidence: dict[str, Any],
    fields: dict[str, Any],
    smoke_receipt: dict[str, Any],
    *,
    profile_path: Path,
    auth_fact: dict[str, Any] | None,
    profile_evidence_digest: str,
    codex_executable_identity: str,
) -> dict[str, Any]:
    provider_endpoint = _profile_provider_endpoint(profile_path)
    observed_at = str(smoke_receipt["observed_at"])
    receipt_digest = _digest(smoke_receipt)
    binding_digest = _digest({
        "profile_evidence_digest": profile_evidence_digest,
        "selected_model": selected_model,
        "provider_endpoint": provider_endpoint,
        "codex_executable_identity": codex_executable_identity,
        "auth_stream_identity_digest": auth_fact.get("auth_stream_identity_digest") if auth_fact else None,
        "observed_at": observed_at,
        "receipt_digest": receipt_digest,
    })
    return {
        **_fact("pass", DEFAULT_CATALOG_URL, evidence), **fields,
        "matched_model": selected_model,
        "catalog_match_source": "direct_provider_smoke",
        "direct_smoke_receipt_digest": receipt_digest,
        "direct_smoke_binding_digest": binding_digest,
        "direct_smoke_observed_at": observed_at,
        "direct_smoke_provider_endpoint": provider_endpoint,
        "direct_smoke_profile_evidence_digest": profile_evidence_digest,
        "direct_smoke_codex_executable_identity": codex_executable_identity,
        "direct_smoke_auth_stream_identity_digest": auth_fact.get("auth_stream_identity_digest") if auth_fact else None,
        "direct_smoke_provider_invoked": True,
        "direct_smoke_exit_code": 0,
        "direct_smoke_marker": _CLOUD_SMOKE_MARKER,
    }


def _safe_smoke_command_shape(command: list[str]) -> list[str]:
    safe = list(command)
    for index, value in enumerate(safe[:-1]):
        if value == "--env-file":
            safe[index + 1] = "<operator-approved-opaque-env-stream>"
    return safe


def _profile_provider_endpoint(profile_path: Path) -> str | None:
    try:
        payload = tomllib.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None
    providers = payload.get("model_providers")
    provider = providers.get("ollama-cloud") if isinstance(providers, dict) else None
    endpoint = provider.get("base_url") if isinstance(provider, dict) else None
    return endpoint if isinstance(endpoint, str) else None

def _auth_blocked_catalog(selected_model: str, evidence: dict[str, Any], reason: str) -> dict[str, Any]:
    return _blocked_catalog_probe(selected_model, evidence, "cloud_auth_unavailable", reason, network_accessed=False)


def _catalog_auth_admission(
    selected_model: str, auth_fact: dict[str, Any], env_file: Path, auth_wrapper: str | None,
) -> tuple[str | None, str | None]:
    if auth_fact.get("status") != "pass" or auth_wrapper is None:
        return "cloud catalog probe requires the Configs auth-backed wrapper", None
    if not is_actual_opaque_env_reference(str(env_file)):
        return "cloud catalog probe requires the exact approved opaque auth stream", None
    expected_identity = auth_fact.get("auth_stream_identity_digest")
    if isinstance(expected_identity, str) and opaque_env_identity_digest(env_file) != expected_identity:
        return "approved opaque auth stream identity changed before catalog execution", None
    if "evidence_source" in auth_fact and expected_identity is None and _approved_cloud_auth_fact(selected_model).get("status") != "pass":
        return "approved opaque auth stream changed or became unavailable before catalog execution", None
    return None, expected_identity if isinstance(expected_identity, str) else None

def _cloud_catalog_fact(
    selected_model: str, profile_path: Path, auth_fact: dict[str, Any],
    runner: CloudCatalogRunner = _run_cloud_catalog,
    *,
    smoke_runner: CloudSmokeRunner | None = None, profile_evidence_digest: str | None = None,
    codex_executable_identity: str | None = None,
) -> dict[str, Any]:
    env_file, auth_wrapper, evidence = _cloud_catalog_inputs(selected_model, profile_path, auth_fact)
    auth_error, expected_identity = _catalog_auth_admission(selected_model, auth_fact, env_file, auth_wrapper)
    if auth_error is not None:
        return _auth_blocked_catalog(selected_model, evidence, auth_error)
    assert auth_wrapper is not None
    command = _cloud_catalog_command(auth_wrapper, env_file, selected_model)
    evidence["probe_command_shape"] = _safe_command_shape(command)
    if opaque_env_identity_digest(env_file) != expected_identity:
        return _auth_blocked_catalog(
            selected_model, evidence,
            "approved opaque auth stream identity changed before catalog execution",
        )
    payload, failure, child_evidence = _catalog_probe_result(command, runner)
    evidence.update(child_evidence)
    if payload is None:
        return _blocked_catalog_probe(
            selected_model, evidence, "cloud_catalog_unavailable", f"cloud catalog probe failed: {failure}",
            network_accessed=failure != "network_or_runtime_failure",
        )
    return _catalog_fact_from_payload(
        selected_model,
        evidence,
        payload,
        profile_path=profile_path,
        auth_fact=auth_fact,
        env_file=env_file,
        auth_wrapper=auth_wrapper,
        smoke_runner=smoke_runner,
        profile_evidence_digest=profile_evidence_digest,
        codex_executable_identity=codex_executable_identity,
    )


def _cloud_catalog_inputs(
    selected_model: str, profile_path: Path, auth_fact: dict[str, Any]
) -> tuple[Path, str | None, dict[str, Any]]:
    default_stream = actual_opaque_env_path()
    env_file = Path(os.environ.get("SKILLS_SDK_OSS_CLOUD_ENV_FILE", str(default_stream) if default_stream else ""))
    evidence = {
        "profile_path": str(profile_path), "selected_model_digest": _digest(selected_model),
        "probe_url": DEFAULT_CATALOG_URL, "safe_non_generation_catalog_probe": True,
        "auth_source": auth_fact.get("auth_source", "missing_or_invalid"),
        "secret_value_observed": False, "generation_performed": False,
        "provider_invoked": False, "codex_exec_invoked": False,
    }
    return env_file, configs_auth_wrapper(), evidence


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
    runtime = _cloud_runtime_fact(model, path)
    cloud_catalog = _cloud_catalog_fact(
        model,
        path,
        auth,
        smoke_runner=_run_cloud_smoke,
        profile_evidence_digest=profile_fact.get("evidence_digest"),
        codex_executable_identity=runtime.get("codex_executable_identity"),
    )
    return {
        "profile_config": profile_fact, "model_catalog": cloud_catalog,
        "runtime": runtime, "auth": auth,
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
