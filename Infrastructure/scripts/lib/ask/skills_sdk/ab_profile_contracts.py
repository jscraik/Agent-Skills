from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


PREFLIGHT_BLOCKER_CLASSES = frozenset(
    {
        "profile_config_missing_or_invalid",
        "model_catalog_entry_missing",
        "local_runtime_unavailable",
        "codex_cli_unavailable",
        "local_runtime_binary_unavailable",
        "local_runtime_service_unavailable",
        "local_model_unavailable",
        "cloud_auth_unavailable",
        "cloud_catalog_unavailable",
        "selected_model_unavailable",
        "preflight_evidence_missing",
    }
)


class _SdkContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class EvalExecutionProfile(_SdkContractModel):
    id: str = Field(min_length=1)
    runner: Literal["codex_exec"]
    sandbox_mode: Literal["read-only", "workspace-write"]
    approval_policy: Literal["on-request"]
    codex_json_events_required: Literal[True]
    output_schema_supported: Literal[True]
    mutation_allowed: bool


class EvalJudgeModelSettings(_SdkContractModel):
    num_ctx: Annotated[int, Field(ge=1)]
    num_predict: Annotated[int, Field(ge=1)] | None = None
    repeat_penalty: Annotated[float, Field(ge=0)] | None = None
    temperature: Annotated[float, Field(ge=0)]
    top_k: Annotated[int, Field(ge=0)] | None = None
    top_p: Annotated[float, Field(ge=0, le=1)]


class EvalJudgeRuntimeMetadata(_SdkContractModel):
    model_id: str = Field(min_length=1)
    size_gb: Annotated[float, Field(gt=0)]
    architecture: str = Field(min_length=1)
    parameters: str = Field(min_length=1)
    quantization: str = Field(min_length=1)
    context_length: Annotated[int, Field(ge=1)]
    metadata_source: Literal["ollama_show"]


class EvalJudgeSmokeGuard(_SdkContractModel):
    max_tokens_used: Annotated[int, Field(ge=1)]
    forbid_visible_thinking: bool
    allow_codex_jsonl_reasoning_events: bool = False
    forbid_fallback_metadata: bool


class EvalJudgeProfile(_SdkContractModel):
    id: str = Field(min_length=1)
    codex_profile: str = Field(min_length=1)
    provider: Literal["ollama", "codex"]
    mode: Literal["local", "cloud", "codex-fast"]
    host: str | None
    model: str = Field(min_length=1)
    model_role: Literal[
        "local_sandbox_eval_default",
        "larger_local_transcript_trial",
        "code_heavy_specialist",
        "fast_fallback",
        "local_security_specialist",
        "cloud_confirmation",
        "codex_fast_smoke",
    ]
    model_settings: EvalJudgeModelSettings | None
    runtime_metadata: EvalJudgeRuntimeMetadata | None
    smoke_guard: EvalJudgeSmokeGuard | None
    network_required: bool
    secret_env_names: list[str]
    auth_boundary: Literal["none", "env_secret", "codex_cli_auth"]
    receives_sanitized_outputs_only: Literal[True]


class EvalSecretBoundary(_SdkContractModel):
    skill_execution_env_secret_names: list[str]
    judge_env_secret_names: list[str]
    skill_execution_receives_judge_secrets: Literal[False]


class AbPreflightBlocker(_SdkContractModel):
    blocker_class: Literal[
        "profile_config_missing_or_invalid",
        "model_catalog_entry_missing",
        "local_runtime_unavailable",
        "codex_cli_unavailable",
        "local_runtime_binary_unavailable",
        "local_runtime_service_unavailable",
        "local_model_unavailable",
        "cloud_auth_unavailable",
        "cloud_catalog_unavailable",
        "selected_model_unavailable",
        "preflight_evidence_missing",
    ]
    reason: str = Field(min_length=1)


class AbPreflightFact(_SdkContractModel):
    status: Literal["pass", "blocked", "not_applicable"]
    evidence_source: str = Field(min_length=1)
    evidence_digest: str = Field(min_length=71, pattern=r"^sha256:[0-9a-f]{64}$")
    blocker: AbPreflightBlocker | None


class AbProfileConfigPreflightFact(AbPreflightFact):
    profile_id: Literal["oss-local", "oss-cloud"]
    configured_model_id: str | None = Field(default=None, min_length=1)
    configured_provider_id: Literal["ollama", "ollama-cloud"] | None = None


class AbModelCatalogPreflightFact(AbPreflightFact):
    selected_model_id: str = Field(min_length=1)
    catalog_identity: str = Field(min_length=1)
    probe_url: str | None = Field(default=None, min_length=1)
    http_status: int | None = Field(default=None, ge=100, le=599)
    catalog_digest: str | None = Field(default=None, min_length=71)
    matched_model: str | None = Field(default=None, min_length=1)
    network_accessed: bool = False
    secret_value_observed: Literal[False] = False
    generation_performed: Literal[False] = False
    provider_invoked: Literal[False] = False
    codex_exec_invoked: Literal[False] = False


class AbRuntimePreflightFact(AbPreflightFact):
    availability_kind: Literal["local_model", "cloud_endpoint"]
    selected_model_id: str = Field(min_length=1)
    codex_executable_identity: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$",
    )


class AbAuthPreflightFact(AbPreflightFact):
    auth_reference: Literal["none", "codex_cli_auth"]
    secret_value_observed: Literal[False]
    auth_source: Literal["not_applicable", "missing_or_invalid", "op_fifo", "op_opaque_env_file"] = (
        "not_applicable"
    )


class AbCatalogPreflightFact(AbPreflightFact):
    catalog_identity: str = Field(min_length=1)


class AbPreflightAdmission(_SdkContractModel):
    status: Literal["pass", "blocked"]
    blockers: list[AbPreflightBlocker]
    secret_values_observed: Literal[False]


class AbLanePreflight(_SdkContractModel):
    profile_config: AbProfileConfigPreflightFact
    model_catalog: AbModelCatalogPreflightFact
    runtime: AbRuntimePreflightFact
    auth: AbAuthPreflightFact
    catalog: AbCatalogPreflightFact
    admission: AbPreflightAdmission

    @model_validator(mode="after")
    def _admission_matches_facts(self) -> AbLanePreflight:
        facts = (self.profile_config, self.model_catalog, self.runtime, self.auth, self.catalog)
        passing = self._typed_facts_pass() and all(fact.blocker is None for fact in facts)
        if passing != (self.admission.status == "pass"):
            raise ValueError("preflight admission must match typed facts")
        if self.admission.status == "pass" and self.admission.blockers:
            raise ValueError("passing preflight admission must not include blockers")
        if self.admission.status == "blocked" and not self.admission.blockers:
            raise ValueError("blocked preflight admission requires blockers")
        return self

    def _typed_facts_pass(self) -> bool:
        return (
            self.profile_config.status == "pass"
            and self.model_catalog.status == "pass"
            and self._runtime_is_admitted()
            and self.catalog.status == "pass"
            and self.auth.status in {"pass", "not_applicable"}
        )

    def _runtime_is_admitted(self) -> bool:
        if self.runtime.status == "pass":
            return True
        return cloud_runtime_not_applicable_is_valid(
            lane=self.profile_config.profile_id,
            runtime_status=self.runtime.status,
            availability_kind=self.runtime.availability_kind,
            runtime_model_id=self.runtime.selected_model_id,
            configured_model_id=self.profile_config.configured_model_id,
            catalog_model_id=self.model_catalog.selected_model_id,
            evidence_source=self.runtime.evidence_source,
            evidence_digest=self.runtime.evidence_digest,
            codex_executable_identity=self.runtime.codex_executable_identity,
            blocker=self.runtime.blocker,
        )


def cloud_runtime_not_applicable_is_valid(**facts: object) -> bool:
    """Admit only the identity-bound installed-Codex exception for a cloud lane."""
    lane = facts.get("lane")
    runtime_status = facts.get("runtime_status")
    availability_kind = facts.get("availability_kind")
    runtime_model_id = facts.get("runtime_model_id")
    configured_model_id = facts.get("configured_model_id")
    catalog_model_id = facts.get("catalog_model_id")
    evidence_source = facts.get("evidence_source")
    evidence_digest = facts.get("evidence_digest")
    codex_executable_identity = facts.get("codex_executable_identity")
    blocker = facts.get("blocker")
    basic = all((
        lane == "oss-cloud", runtime_status == "not_applicable",
        availability_kind == "cloud_endpoint",
        isinstance(configured_model_id, str) and bool(configured_model_id),
        runtime_model_id == configured_model_id, catalog_model_id == configured_model_id,
        isinstance(evidence_source, str), isinstance(evidence_digest, str),
        isinstance(codex_executable_identity, str), blocker is None,
    ))
    current = resolve_installed_codex_identity() if basic else None
    return bool(
        current == (evidence_source, codex_executable_identity)
        and evidence_digest == codex_identity_evidence_digest(
            str(evidence_source), str(codex_executable_identity),
        )
    )


def _canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def codex_identity_evidence_digest(path: str, identity: str) -> str:
    return _canonical_digest({"codex_executable_identity": identity, "resolved_path": path})


def resolve_installed_codex_identity() -> tuple[str, str] | None:
    discovered = shutil.which("codex")
    if not discovered:
        return None
    discovered_path = Path(discovered).absolute()
    try:
        resolved = discovered_path.resolve(strict=True)
        if not resolved.is_file() or not os.access(resolved, os.X_OK):
            return None
        completed = subprocess.run(
            [str(resolved), "--version"], capture_output=True, check=False, text=True, timeout=10,
            env={"NO_COLOR": "1", "PATH": os.environ.get("PATH", "")},
        )
        version = completed.stdout.strip()
        if completed.returncode != 0 or completed.stderr or not re.fullmatch(r"codex-cli \S+", version):
            return None
        with resolved.open("rb") as binary:
            binary_digest = f"sha256:{hashlib.file_digest(binary, 'sha256').hexdigest()}"
    except (OSError, subprocess.TimeoutExpired):
        return None
    identity = _canonical_digest({
        "binary_digest": binary_digest, "discovered_path": str(discovered_path),
        "resolved_path": str(resolved), "version": version,
    })
    return str(resolved), identity


def preflight_fact_status_is_admitted(
    *,
    lane: str,
    key: str,
    fact: dict[str, object],
    profile_config: dict[str, object],
    model_catalog: dict[str, object],
) -> bool:
    if fact.get("status") == "pass":
        return True
    if key == "auth":
        return lane == "oss-local" and fact.get("status") == "not_applicable"
    if key != "runtime":
        return False
    if set(fact) != {
        "status", "evidence_source", "evidence_digest", "blocker",
        "availability_kind", "selected_model_id", "codex_executable_identity",
    }:
        return False
    return cloud_runtime_not_applicable_is_valid(
        lane=lane, runtime_status=fact.get("status"),
        availability_kind=fact.get("availability_kind"),
        runtime_model_id=fact.get("selected_model_id"),
        configured_model_id=profile_config.get("configured_model_id"),
        catalog_model_id=model_catalog.get("selected_model_id"),
        evidence_source=fact.get("evidence_source"), evidence_digest=fact.get("evidence_digest"),
        codex_executable_identity=fact.get("codex_executable_identity"), blocker=fact.get("blocker"),
    )


_OLLAMA_CLOUD_CATALOG_URL = "https://ollama.com/api/tags"


def _expected_profile_provider(lane: str) -> str | None:
    if lane == "oss-local":
        return "ollama"
    if lane == "oss-cloud":
        return "ollama-cloud"
    return None


def runtime_preflight_identity_matches_lane(
    lane: Literal["oss-local", "oss-cloud"],
    preflight: AbLanePreflight,
) -> bool:
    if not _common_preflight_identity_matches_lane(lane, preflight):
        return False
    if lane == "oss-local":
        return _local_preflight_identity_matches(preflight)
    return _cloud_preflight_identity_matches(preflight)


def _common_preflight_identity_matches_lane(
    lane: Literal["oss-local", "oss-cloud"],
    preflight: AbLanePreflight,
) -> bool:
    profile = preflight.profile_config
    configured_model = profile.configured_model_id
    return all(
        (
            profile.profile_id == lane,
            profile.configured_provider_id == _expected_profile_provider(lane),
            configured_model is not None,
            preflight.model_catalog.selected_model_id == configured_model,
            preflight.runtime.selected_model_id == configured_model,
            preflight.catalog.catalog_identity == preflight.model_catalog.catalog_identity,
        )
    )


def _local_preflight_identity_matches(preflight: AbLanePreflight) -> bool:
    model_catalog = preflight.model_catalog
    auth = preflight.auth
    return all(
        (
            preflight.runtime.availability_kind == "local_model",
            auth.status == "not_applicable",
            auth.auth_reference == "none",
            auth.auth_source == "not_applicable",
            not model_catalog.network_accessed,
            model_catalog.probe_url is None,
            model_catalog.http_status is None,
            model_catalog.catalog_digest is None,
            model_catalog.matched_model is None,
        )
    )


def _cloud_preflight_identity_matches(preflight: AbLanePreflight) -> bool:
    profile = preflight.profile_config
    model_catalog = preflight.model_catalog
    auth = preflight.auth
    return all(
        (
            preflight.runtime.availability_kind == "cloud_endpoint",
            auth.status == "pass",
            auth.auth_reference == "codex_cli_auth",
            auth.auth_source in {"op_fifo", "op_opaque_env_file"},
            model_catalog.catalog_identity == _OLLAMA_CLOUD_CATALOG_URL,
            model_catalog.probe_url == _OLLAMA_CLOUD_CATALOG_URL,
            model_catalog.http_status == 200,
            model_catalog.catalog_digest is not None,
            model_catalog.matched_model == profile.configured_model_id,
            model_catalog.network_accessed,
            not model_catalog.secret_value_observed,
            not model_catalog.generation_performed,
            not model_catalog.provider_invoked,
            not model_catalog.codex_exec_invoked,
        )
    )
