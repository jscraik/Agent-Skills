from __future__ import annotations

from typing import Any

from ask.skills_sdk.eval_ab_preflight import DEFAULT_CATALOG_URL, _digest, _expected_provider


def declared_profile_preflight(profile: dict[str, Any]) -> dict[str, Any]:
    lane = str(profile["id"])
    model = str(profile["model"])
    source = "Infrastructure/tests/skills_sdk_preflight_fixtures.py"
    return {
        "profile_config": _profile_config_fact(profile, lane, model, source),
        "model_catalog": _model_catalog_fact(lane, model, source),
        "runtime": _runtime_fact(lane, model, source),
        "auth": _auth_fact(lane, source),
        "catalog": _catalog_fact(lane, model, source),
    }


def _profile_config_fact(profile: dict[str, Any], lane: str, model: str, source: str) -> dict[str, Any]:
    return {
        **_fact("pass", source, profile),
        "profile_id": lane,
        "configured_model_id": model,
        "configured_provider_id": _expected_provider(lane),
    }


def _model_catalog_fact(lane: str, model: str, source: str) -> dict[str, Any]:
    catalog_identity = _catalog_identity(lane)
    fact = {
        **_fact("pass", source, {"lane": lane, "model": model}),
        "selected_model_id": model,
        "catalog_identity": catalog_identity,
    }
    if lane == "oss-cloud":
        fact.update(_cloud_catalog_probe_fields(model))
    return fact


def _runtime_fact(lane: str, model: str, source: str) -> dict[str, Any]:
    return {
        **_fact("pass", source, {"lane": lane, "model": model}),
        "availability_kind": "local_model" if lane == "oss-local" else "cloud_endpoint",
        "selected_model_id": model,
    }


def _auth_fact(lane: str, source: str) -> dict[str, Any]:
    is_local = lane == "oss-local"
    return {
        **_fact("not_applicable" if is_local else "pass", source, {"lane": lane}),
        "auth_reference": "none" if is_local else "codex_cli_auth",
        "secret_value_observed": False,
        "auth_source": "not_applicable" if is_local else "op_opaque_env_file",
    }


def _catalog_fact(lane: str, model: str, source: str) -> dict[str, Any]:
    return {
        **_fact("pass", source, {"lane": lane, "model": model}),
        "catalog_identity": _catalog_identity(lane),
    }


def _catalog_identity(lane: str) -> str:
    return "declared-local-model-catalog" if lane == "oss-local" else DEFAULT_CATALOG_URL


def _cloud_catalog_probe_fields(model: str) -> dict[str, Any]:
    return {
        "probe_url": DEFAULT_CATALOG_URL,
        "http_status": 200,
        "catalog_digest": _digest({"models": [model]}),
        "matched_model": model,
        "network_accessed": True,
    }


def _fact(status: str, source: str, evidence: object) -> dict[str, Any]:
    return {
        "status": status,
        "evidence_source": source,
        "evidence_digest": _digest(evidence),
        "blocker": None,
    }
