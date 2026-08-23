from __future__ import annotations

from typing import Any

from ask.skills_sdk.operational_references import operational_reference_paths


def merge_knowledge_source_context(
    loaded: dict[str, Any],
    *,
    eval_routes: dict[str, bool],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Merge KnowledgeOS reference routes into an existing source context."""
    references = loaded.setdefault("references", [])
    if not isinstance(references, list):
        raise ValueError("references/source-context.yaml references must be a list.")
    managed_kinds = {
        "knowledge_profile",
        "capsule_manifest",
        "generated_knowledge_capsules",
        "operational_reference",
        "knowledge_eval_scenarios",
        "knowledge_eval_fixtures",
    }
    references[:] = [
        item
        for item in references
        if not isinstance(item, dict) or item.get("kind") not in managed_kinds
    ]
    entries = _base_entries(manifest) + _operational_entries(manifest) + _eval_entries(eval_routes)
    existing_paths = {str(item.get("path")) for item in references if isinstance(item, dict)}
    references.extend(entry for entry in entries if entry["path"] not in existing_paths)
    _merge_allowed_claims(loaded, eval_routes)
    return loaded


def _base_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entries = [
        {
            "path": "references/knowledge-demand.yaml",
            "kind": "knowledge_profile",
            "provenance": "vendored KnowledgeOS extraction",
            "load_when": "deciding which pack-backed capsule is relevant",
            "allowed_claims": ["knowledge demand profile for this skill"],
            "forbidden_claims": ["target repo readiness", "raw source availability"],
            "freshness": "knowledge_os_snapshot",
            "context_budget": "small",
            "claim_scope": "knowledge_profile",
            "bounded_unit": True,
        },
        {
            "path": "references/knowledge-capsule.manifest.yaml",
            "kind": "capsule_manifest",
            "provenance": "vendored KnowledgeOS extraction",
            "load_when": "selecting a bounded KnowledgeOS capsule",
            "allowed_claims": ["selected capsules and upstream pack snapshot digests"],
            "forbidden_claims": ["raw source completeness", "runtime dependency on KnowledgeOS"],
            "freshness": "knowledge_os_snapshot",
            "context_budget": "small",
            "claim_scope": "capsule_manifest",
            "bounded_unit": True,
        },
    ]
    if _uses_legacy_capsule_directory(manifest):
        entries.append(_legacy_capsule_entry())
    return entries


def _legacy_capsule_entry() -> dict[str, Any]:
    return {
        "path": "references/knowledge-capsules/",
        "kind": "generated_knowledge_capsules",
        "provenance": "vendored KnowledgeOS extraction",
        "load_when": "only after the manifest selects the relevant capsule",
        "allowed_claims": ["bounded expert viewpoint or evidence lane captured in the selected capsule"],
        "forbidden_claims": ["load all capsules by default", "claims outside selected capsule text"],
        "freshness": "knowledge_os_snapshot",
        "context_budget": "selective",
        "claim_scope": "bounded_capsules",
        "bounded_unit": True,
    }


def _uses_legacy_capsule_directory(manifest: dict[str, Any]) -> bool:
    storage = manifest.get("capsule_storage")
    allowed = (
        isinstance(storage, dict)
        and storage.get("allow_legacy_subdirectory") is True
        and bool(str(storage.get("justification") or "").strip())
    )
    return allowed and any(
        path.startswith("references/knowledge-capsules/")
        for path in operational_reference_paths(manifest)
    )


def _operational_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "path": path,
            "kind": "operational_reference",
            "provenance": "vendored KnowledgeOS extraction",
            "load_when": "only when the capsule manifest selects this operational reference",
            "allowed_claims": ["bounded guidance and evidence from this selected operational reference"],
            "forbidden_claims": ["load every reference by default", "claims outside this selected reference"],
            "freshness": "knowledge_os_snapshot",
            "context_budget": "selective",
            "claim_scope": "bounded_operational_reference",
            "bounded_unit": True,
        }
        for path in operational_reference_paths(manifest)
    ]


def _eval_entries(eval_routes: dict[str, bool]) -> list[dict[str, Any]]:
    entries = []
    if eval_routes["scenarios"]:
        entries.append(
            {
                "path": "references/eval-scenarios.json",
                "kind": "knowledge_eval_scenarios",
                "provenance": "vendored KnowledgeOS extraction",
                "load_when": "checking selected KnowledgeOS eval scenario metadata",
                "allowed_claims": ["selected eval scenario IDs, prompts, and expected failure modes"],
                "forbidden_claims": ["runtime dependency on KnowledgeOS", "Tessl result quality without execution evidence"],
                "freshness": "knowledge_os_snapshot",
                "context_budget": "small",
                "claim_scope": "eval_scenarios",
                "bounded_unit": True,
            }
        )
    if eval_routes["fixtures"]:
        entries.append(
            {
                "path": "references/evals/",
                "kind": "knowledge_eval_fixtures",
                "provenance": "vendored KnowledgeOS extraction",
                "load_when": "only when a selected scenario fixture needs detail beyond references/evals.yaml",
                "allowed_claims": ["fixture detail for selected KnowledgeOS eval scenarios"],
                "forbidden_claims": ["load all fixtures by default", "claims outside selected fixture text"],
                "freshness": "knowledge_os_snapshot",
                "context_budget": "selective",
                "claim_scope": "eval_fixture_detail",
                "bounded_unit": True,
            }
        )
    return entries


def _merge_allowed_claims(loaded: dict[str, Any], eval_routes: dict[str, bool]) -> None:
    allowed_claims = loaded.setdefault("allowed_claims", [])
    if not isinstance(allowed_claims, list):
        raise ValueError("references/source-context.yaml allowed_claims must be a list.")
    capsule_claim = "KnowledgeOS capsules are vendored references, not runtime dependencies"
    if capsule_claim not in allowed_claims:
        allowed_claims.append(capsule_claim)
    eval_claim = "KnowledgeOS-selected eval scenarios must be wired through references/evals.yaml before Tessl proof"
    if eval_routes["scenarios"] and eval_routes["fixtures"]:
        if eval_claim not in allowed_claims:
            allowed_claims.append(eval_claim)
    else:
        allowed_claims[:] = [claim for claim in allowed_claims if claim != eval_claim]
