from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "skills-sdk.evaluation-lane-policy.v1"
LOCAL_DEVELOPMENT_TARGET = 20
CLOUD_CHALLENGE_TARGET = 10
CLOUD_ROTATING_TARGET = 2
RELEASE_TARGET = 8
BASELINE_IDENTITY_FIELDS = {
    "case_ids",
    "criteria_digest",
    "rubric_digest",
    "scorer_version",
    "package_digest",
    "execution_model_family",
}
MODEL_LANES = ("oss-local", "oss-cloud", "tessl-external")


def _check(check_id: str, *, passed: bool, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": "pass" if passed else "blocker",
        "severity": "blocker",
        "message": message,
        "evidence": evidence or [],
    }


def _string_list(value: object) -> list[str]:
    return [str(item).strip() for item in value if str(item).strip()] if isinstance(value, list) else []


def _release_case_ids(payload: dict[str, Any], set_id: str) -> list[str]:
    release_sets = payload.get("release_scenario_sets")
    if not isinstance(release_sets, list):
        return []
    selected = next((item for item in release_sets if isinstance(item, dict) and item.get("id") == set_id), None)
    if not isinstance(selected, dict):
        return []
    groups = selected.get("groups")
    if isinstance(groups, dict):
        return [case_id for value in groups.values() for case_id in _string_list(value)]
    return _string_list(selected.get("cases"))


def _pool_cases(pools: object, pool_id: str) -> tuple[dict[str, Any], list[str]]:
    pool = pools.get(pool_id) if isinstance(pools, dict) else None
    row = pool if isinstance(pool, dict) else {}
    return row, _string_list(row.get("cases"))


def _pool_checks(
    pool_id: str,
    pool: dict[str, Any],
    case_ids: list[str],
    *,
    target: int,
    release_ids: list[str],
    known_ids: set[str],
) -> list[dict[str, Any]]:
    missing = sorted(set(case_ids) - known_ids)
    missing_release = sorted(set(release_ids) - set(case_ids))
    return [
        _check(f"eval_lane_{pool_id}_present", passed=bool(pool), message=f"{pool_id} must be declared."),
        _check(f"eval_lane_{pool_id}_target", passed=pool.get("target_scenarios") == target, message=f"{pool_id} must target {target} scenarios.", evidence=[str(pool.get("target_scenarios"))]),
        _check(f"eval_lane_{pool_id}_count", passed=len(case_ids) == target, message=f"{pool_id} must contain exactly {target} cases.", evidence=[f"count:{len(case_ids)}"]),
        _check(f"eval_lane_{pool_id}_unique", passed=len(case_ids) == len(set(case_ids)), message=f"{pool_id} case ids must be unique."),
        _check(f"eval_lane_{pool_id}_cases_exist", passed=not missing, message=f"{pool_id} may reference only declared cases.", evidence=missing),
        _check(f"eval_lane_{pool_id}_contains_release_set", passed=not missing_release, message=f"{pool_id} must contain the fixed release set.", evidence=missing_release),
    ]


def _model_routing_checks(policy: dict[str, Any]) -> list[dict[str, Any]]:
    routing = policy.get("model_routing")
    rows = routing if isinstance(routing, dict) else {}
    families: list[str] = []
    checks = [_check("eval_lane_model_routing_present", passed=bool(rows), message="Model routing must be declared for every proof lane.")]
    for lane in MODEL_LANES:
        row = rows.get(lane)
        identity = row if isinstance(row, dict) else {}
        family = str(identity.get("model_family") or "").strip()
        families.append(family.casefold())
        checks.extend([
            _check(f"eval_lane_{lane}_model_identity", passed=bool(identity), message=f"{lane} must declare a model identity."),
            _check(f"eval_lane_{lane}_model", passed=bool(str(identity.get("model") or "").strip()), message=f"{lane} must declare a model."),
            _check(f"eval_lane_{lane}_provider", passed=bool(str(identity.get("provider") or "").strip()), message=f"{lane} must declare a provider."),
            _check(f"eval_lane_{lane}_model_family", passed=bool(family), message=f"{lane} must declare a model family."),
            _check(f"eval_lane_{lane}_identity_source", passed=bool(str(identity.get("identity_source") or "").strip()), message=f"{lane} must declare its identity source."),
        ])
    checks.append(
        _check(
            "eval_lane_model_families_distinct",
            passed=len(families) == len(set(families)) and all(families),
            message="OSS local, OSS cloud, and Tessl external must use distinct model families unless an explicit exception is recorded.",
            evidence=families,
        )
    )
    return checks


def eval_lane_execution_identity(evals_payload: dict[str, Any] | None, lane: str | None) -> dict[str, str] | None:
    if not isinstance(evals_payload, dict) or not lane:
        return None
    policy = evals_payload.get("evaluation_lane_policy")
    routing = policy.get("model_routing") if isinstance(policy, dict) else None
    row = routing.get(lane) if isinstance(routing, dict) else None
    if not isinstance(row, dict):
        return None
    identity = {key: str(row.get(key) or "").strip() for key in ("model", "model_family", "provider", "identity_source")}
    return identity if all(identity.values()) else None


def build_eval_lane_policy_checks(evals_payload: dict[str, Any] | None, case_list: list[Any]) -> list[dict[str, Any]]:
    if not isinstance(evals_payload, dict):
        return []
    policy = evals_payload.get("evaluation_lane_policy")
    if policy is None:
        return []
    if not isinstance(policy, dict):
        return [_check("eval_lane_policy_object", passed=False, message="evaluation_lane_policy must be an object.")]
    release_set_id = str(policy.get("release_scenario_set_id") or "")
    release_ids = _release_case_ids(evals_payload, release_set_id)
    known_ids = {str(case.get("id")) for case in case_list if isinstance(case, dict) and case.get("id")}
    pools = policy.get("pools")
    local, local_ids = _pool_cases(pools, "oss-local-development")
    cloud, cloud_ids = _pool_cases(pools, "oss-cloud-challenge")
    baseline_fields = set(_string_list(policy.get("baseline_identity_fields")))
    checks = [
        _check("eval_lane_policy_schema", passed=policy.get("schema_version") == SCHEMA_VERSION, message=f"evaluation_lane_policy must use {SCHEMA_VERSION}."),
        _check("eval_lane_release_set_exact_eight", passed=len(release_ids) == RELEASE_TARGET, message="The Tessl comparison set must contain exactly eight cases.", evidence=[f"count:{len(release_ids)}"]),
        _check("eval_lane_baseline_identity_fields", passed=BASELINE_IDENTITY_FIELDS <= baseline_fields, message="Tessl baseline identity fields must be complete.", evidence=sorted(BASELINE_IDENTITY_FIELDS - baseline_fields)),
    ]
    checks.extend(_model_routing_checks(policy))
    checks.extend(_pool_checks("local_development", local, local_ids, target=LOCAL_DEVELOPMENT_TARGET, release_ids=release_ids, known_ids=known_ids))
    checks.extend(_pool_checks("cloud_challenge", cloud, cloud_ids, target=CLOUD_CHALLENGE_TARGET, release_ids=release_ids, known_ids=known_ids))
    cloud_extras = set(cloud_ids) - set(release_ids)
    checks.extend([
        _check("eval_lane_cloud_rotating_count", passed=cloud.get("rotating_case_count") == CLOUD_ROTATING_TARGET and len(cloud_extras) == CLOUD_ROTATING_TARGET, message="Cloud challenge proof must add exactly two rotating growth cases.", evidence=sorted(cloud_extras)),
        _check("eval_lane_cloud_subset_of_local", passed=set(cloud_ids) <= set(local_ids), message="Cloud challenge cases must come from the local development pool.", evidence=sorted(set(cloud_ids) - set(local_ids))),
    ])
    return checks
