from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ask.skills_sdk.release_scenario_sets import RELEASE_SCENARIO_MAXIMUM, RELEASE_SCENARIO_MINIMUM
from ask.skills_sdk.typed_contracts import validate_eval_run_receipt

SCHEMA_VERSION = "skills-sdk.eval-shard-aggregate-receipt.v0"
SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/eval-shard-aggregate-receipt.v0.schema.json"
MAX_SHARD_CASES = 2
GOLD_STANDARD_RUBRIC_PATH = Path("Infrastructure/config/skills-sdk/gold-standard-rubric.v1.json")


class EvalShardAggregateError(ValueError):
    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__(receipt["agent_summary"])
        self.receipt = receipt


def _repo_path(repo_root: Path, raw_path: Path) -> tuple[Path | None, str]:
    path = raw_path if raw_path.is_absolute() else repo_root / raw_path
    try:
        resolved = path.resolve(strict=True)
        label = resolved.relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None, raw_path.as_posix()
    return resolved, label


def _load_receipt(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("receipt payload must be a JSON object")
    receipt = payload
    if payload.get("schema_version") != "skills-sdk.eval-run-receipt.v0":
        data = payload.get("data")
        run = data.get("skills_sdk_eval_run") if isinstance(data, dict) else None
        nested_receipt = run.get("receipt") if isinstance(run, dict) else None
        receipt = nested_receipt if isinstance(nested_receipt, dict) else {}
    validated = validate_eval_run_receipt(receipt)
    return validated.model_dump(mode="python")


def _expected_cases(skill_path: Path, scenario_set: str) -> list[str]:
    skill_dir = skill_path.parent if skill_path.name == "SKILL.md" else skill_path
    from ask.skills_sdk.scenario_quality import _yaml_safe_load  # noqa: PLC0415

    payload = _yaml_safe_load((skill_dir / "references" / "evals.yaml").read_text(encoding="utf-8"))
    release_sets = payload.get("release_scenario_sets") if isinstance(payload, dict) else None
    if not isinstance(release_sets, list):
        raise ValueError("release_scenario_sets must be a list")
    selected = next(
        (item for item in release_sets if isinstance(item, dict) and item.get("id") == scenario_set),
        None,
    )
    if not isinstance(selected, dict):
        raise ValueError(f"release scenario set not found: {scenario_set}")
    groups = selected.get("groups")
    if isinstance(groups, dict):
        return [str(case_id) for group in groups.values() if isinstance(group, list) for case_id in group]
    cases = selected.get("cases")
    if isinstance(cases, list):
        return [str(case_id) for case_id in cases]
    raise ValueError(f"release scenario set has no cases: {scenario_set}")


def _check(check_id: str, passed: bool, evidence: list[str]) -> dict[str, Any]:
    return {"id": check_id, "status": "pass" if passed else "blocker", "evidence": evidence}


def _load_receipts(repo_root: Path, paths: list[Path]) -> tuple[list[tuple[str, dict[str, Any]]], list[str]]:
    loaded: list[tuple[str, dict[str, Any]]] = []
    errors: list[str] = []
    for raw_path in paths:
        resolved, label = _repo_path(repo_root, raw_path)
        if resolved is None:
            errors.append(f"missing_or_external:{label}")
            continue
        try:
            loaded.append((label, _load_receipt(resolved)))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"invalid_json:{label}:{exc}")
    return loaded, errors


def _identity_sets(receipts: list[dict[str, Any]]) -> dict[str, set[str]]:
    fields = (
        "package_id",
        "package_digest",
        "rubric_digest",
        "scenario_set_id",
        "execution_model",
        "execution_model_family",
        "execution_model_provider",
        "execution_identity_source",
    )
    return {field: {str(receipt.get(field) or "") for receipt in receipts} for field in fields}


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _current_rubric_digest(repo_root: Path) -> str | None:
    try:
        return _digest_file(repo_root / GOLD_STANDARD_RUBRIC_PATH)
    except OSError:
        return None

def _all_shards_pass(receipts: list[dict[str, Any]]) -> bool:
    return bool(receipts) and all(row.get("status") == "pass" for row in receipts)


def _all_shards_are_profile_release(receipts: list[dict[str, Any]], profile: str) -> bool:
    return bool(receipts) and all(
        row.get("lane") == profile and row.get("lane_type") == "release-shard" and row.get("profile") == profile
        for row in receipts
    )


def _all_shards_have_exec_proof(receipts: list[dict[str, Any]], profile: str) -> bool:
    return bool(receipts) and all(row.get("codex_exec_invoked") is True and row.get("codex_profile") == profile for row in receipts)


def _all_shards_are_bounded(receipts: list[dict[str, Any]]) -> bool:
    sizes = [len(row.get("selected_case_ids") or []) for row in receipts]
    return bool(receipts) and all(0 < size <= MAX_SHARD_CASES for size in sizes)


def _identities_match(receipts: list[dict[str, Any]], identities: dict[str, set[str]]) -> bool:
    return bool(receipts) and all(len(values) == 1 and "" not in values for values in identities.values())


def _dataset_digest_check(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    digests = [str(receipt.get("dataset_digest") or "").strip() for receipt in receipts]
    return _check("dataset_digests_present", bool(receipts) and all(digests), digests)


def _current_rubric_check(identities: dict[str, set[str]], expected_digest: str | None) -> dict[str, Any]:
    return _check(
        "shards_match_current_rubric",
        expected_digest is not None and identities["rubric_digest"] == {expected_digest},
        [
            f"expected:{expected_digest or 'missing'}",
            f"actual:{','.join(sorted(identities['rubric_digest']))}",
        ],
    )

def _shard_checks(
    receipts: list[dict[str, Any]], identities: dict[str, set[str]], path_errors: list[str], labels: list[str], profile: str
) -> list[dict[str, Any]]:
    return [
        _check("receipt_paths_are_repo_owned", not path_errors and bool(receipts), path_errors or labels),
        _check("shards_pass", _all_shards_pass(receipts), [str(row.get("status")) for row in receipts]),
        _check("shards_match_requested_profile", _all_shards_are_profile_release(receipts, profile), [f"{row.get('lane')}:{row.get('lane_type')}:{row.get('profile')}" for row in receipts]),
        _check("codex_exec_proof_present", _all_shards_have_exec_proof(receipts, profile), [f"{row.get('codex_exec_invoked')}:{row.get('codex_profile')}" for row in receipts]),
        _check("shard_size_bounded", _all_shards_are_bounded(receipts), [str(len(row.get("selected_case_ids") or [])) for row in receipts]),
        _check("identity_fields_match", _identities_match(receipts, identities), [f"{key}:{sorted(values)}" for key, values in identities.items()]),
    ]


def _selected_case_ids(receipts: list[dict[str, Any]]) -> list[str]:
    return [str(case_id) for row in receipts for case_id in row.get("selected_case_ids") or []]


def _result_cases(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [case for row in receipts for case in row.get("cases") or [] if isinstance(case, dict)]


def _coverage_checks(
    receipts: list[dict[str, Any]], identities: dict[str, set[str]], scenario_set: str, expected: list[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected = _selected_case_ids(receipts)
    cases = _result_cases(receipts)
    result_ids = [str(case.get("case_id") or "") for case in cases]
    checks = [
        _check("scenario_set_matches_request", bool(receipts) and identities["scenario_set_id"] == {scenario_set}, sorted(identities["scenario_set_id"])),
        _check("selected_cases_exactly_cover_release_set", sorted(selected) == sorted(expected) and len(selected) == len(set(selected)), [f"expected:{','.join(expected)}", f"actual:{','.join(selected)}"]),
        _check("case_results_match_selection", sorted(result_ids) == sorted(selected), [f"selected:{','.join(selected)}", f"results:{','.join(result_ids)}"]),
        _check(
            "aggregate_scenario_budget",
            RELEASE_SCENARIO_MINIMUM <= len(cases) <= RELEASE_SCENARIO_MAXIMUM,
            [f"count:{len(cases)}", f"minimum:{RELEASE_SCENARIO_MINIMUM}", f"maximum:{RELEASE_SCENARIO_MAXIMUM}"],
        ),
        _check("all_case_results_pass", bool(cases) and all(case.get("status") == "pass" for case in cases), [f"{case.get('case_id')}:{case.get('status')}" for case in cases]),
    ]
    return checks, cases


def _single_identity(identities: dict[str, set[str]], field: str) -> str | None:
    return next(iter(identities[field]), None)


def _receipt_payload(
    loaded: list[tuple[str, dict[str, Any]]], identities: dict[str, set[str]], dataset_digests: list[str],
    scenario_set: str, expected_ids: list[str], result_cases: list[dict[str, Any]], checks: list[dict[str, Any]], profile: str,
) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    codex_exec_check = next(
        (check for check in checks if check["id"] == "codex_exec_proof_present"),
        None,
    )
    codex_exec_invoked = bool(codex_exec_check and codex_exec_check["status"] == "pass")
    return {
        "schema_version": SCHEMA_VERSION, "schema_uri": SCHEMA_URI,
        "status": "pass" if not blockers else "blocked", "lane": profile, "profile": profile,
        "package_id": _single_identity(identities, "package_id"), "package_digest": _single_identity(identities, "package_digest"),
        "execution_model": _single_identity(identities, "execution_model"),
        "execution_model_family": _single_identity(identities, "execution_model_family"),
        "execution_model_provider": _single_identity(identities, "execution_model_provider"),
        "execution_identity_source": _single_identity(identities, "execution_identity_source"),
        "codex_exec_invoked": codex_exec_invoked,
        "codex_profile": profile if codex_exec_invoked else None,
        "shard_dataset_digests": dataset_digests, "rubric_digest": _single_identity(identities, "rubric_digest"),
        "scenario_set_id": scenario_set, "scenario_set_case_ids": expected_ids,
        "shard_receipts": [label for label, _ in loaded], "shard_count": len(loaded), "case_count": len(result_cases),
        "passed_count": sum(case.get("status") == "pass" for case in result_cases),
        "failed_count": sum(case.get("status") != "pass" for case in result_cases), "cases": result_cases,
        "checks": checks, "blockers": blockers, "mutation_performed": False,
        "claims_boundary": f"This receipt proves only aggregate {profile} release evidence. It does not prove Tessl, distribution, runtime, or release readiness.",
        "agent_summary": f"{profile} shard aggregation passed." if not blockers else f"{profile} shard aggregation is blocked by {len(blockers)} check(s).",
    }


def build_eval_shard_aggregate_receipt(
    repo_root: Path,
    *,
    skill_path: Path,
    scenario_set: str,
    receipt_paths: list[Path],
    profile: str = "oss-local",
    expected_package_digest: str | None = None,
) -> dict[str, Any]:
    expected_ids = _expected_cases(skill_path, scenario_set)
    loaded, path_errors = _load_receipts(repo_root, receipt_paths)
    receipts = [receipt for _, receipt in loaded]
    identities = _identity_sets(receipts)
    dataset_digests = sorted({str(receipt.get("dataset_digest") or "") for receipt in receipts})
    checks = _shard_checks(receipts, identities, path_errors, [label for label, _ in loaded], profile)
    checks.append(_dataset_digest_check(receipts))
    checks.append(_current_rubric_check(identities, _current_rubric_digest(repo_root)))
    dataset_digests = [digest for digest in dataset_digests if digest]
    if expected_package_digest is not None:
        checks.append(
            _check(
                "shards_match_current_package",
                identities["package_digest"] == {expected_package_digest},
                [
                    f"expected:{expected_package_digest}",
                    f"actual:{','.join(sorted(identities['package_digest']))}",
                ],
            )
        )
    coverage_checks, result_cases = _coverage_checks(receipts, identities, scenario_set, expected_ids)
    checks.extend(coverage_checks)
    receipt = _receipt_payload(loaded, identities, dataset_digests, scenario_set, expected_ids, result_cases, checks, profile)
    if receipt["blockers"]:
        raise EvalShardAggregateError(receipt)
    return receipt
