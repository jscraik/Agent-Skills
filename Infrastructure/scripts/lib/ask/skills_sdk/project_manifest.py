"""Canonical loader and validator for the owner-repo Skills SDK project manifest.

The owner manifest (``skills-sdk.json``) declares which project-local skill
roots are canonical source, generated projection, client runtime config, or
unknown before the SDK creates, installs, updates, audits, or evaluates skills.

This module hardens that load so a malformed or ambiguous manifest can never be
silently treated as absent. Evaluation returns one of three explicit states:

* ``absent``  – no manifest file exists at the expected path.
* ``valid``   – the manifest can be trusted for ownership/lifecycle decisions.
* ``invalid`` – the manifest exists but cannot be trusted; deterministic,
  machine-readable blockers explain exactly why.

Compatibility / tolerated legacy boundary
------------------------------------------
Early owner manifests predate the full v1 field contract. To avoid breaking
those repos, a manifest that carries the correct ``schema_version`` but omits
full-contract fields (``project_id``, ``eval_suite``, ``evidence``,
``trust_policy``, ``precedence_policy``) or declares roots through the legacy
``skill_sources`` array instead of ``skill_roots`` is still treated as
``valid`` and flagged ``legacy_compat``. It is *not* silently accepted as
absent, and it is *not* upgraded to invalid. Structural safety rules (JSON
well-formedness, schema version, duplicate roots, classification vocabulary,
and lifecycle default cardinality) are enforced for legacy and full manifests
alike.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MANIFEST_FILENAME = "skills-sdk.json"
MANIFEST_SCHEMA_PATH = "Infrastructure/config/schemas/skills-sdk.project.v1.schema.json"
MANIFEST_SCHEMA_VERSION = "skills-sdk.project.v1"

SKILL_ROOT_CLASSIFICATIONS: frozenset[str] = frozenset(
    {
        "canonical_project_source",
        "generated_runtime_projection",
        "client_runtime_config",
        "unknown",
    }
)

# Full v1 contract fields. Their absence downgrades a manifest to legacy_compat
# rather than invalid, so historical owner repos keep working.
FULL_CONTRACT_FIELDS: tuple[str, ...] = (
    "project_id",
    "skill_roots",
    "eval_suite",
    "evidence",
    "trust_policy",
    "precedence_policy",
)

LIFECYCLE_DEFAULT_FIELDS: tuple[str, ...] = (
    "default_for_create",
    "default_for_install",
    "default_for_update",
)

# Machine-readable blocker vocabulary. Stable identifiers so automation can key
# on the failure class without parsing prose.
MANIFEST_BLOCKER_CLASSES: dict[str, str] = {
    "manifest_unreadable": "The manifest file exists but could not be read from disk.",
    "manifest_invalid_json": "The manifest file is not valid JSON and cannot be parsed.",
    "manifest_not_object": "The manifest top-level value is not a JSON object.",
    "manifest_schema_version_unsupported": (
        "The manifest schema_version is missing or not the supported "
        f"{MANIFEST_SCHEMA_VERSION} contract."
    ),
    "manifest_skill_roots_not_array": "The manifest skill_roots field must be an array of root objects.",
    "manifest_skill_root_not_object": "A skill_roots entry is not an object.",
    "manifest_skill_root_path_missing": "A skill_roots entry is missing a non-empty path.",
    "manifest_duplicate_skill_root": "Two or more skill_roots resolve to the same normalized path.",
    "manifest_unsupported_classification": "A skill_roots entry declares an unsupported ownership classification.",
    "manifest_lifecycle_default_not_boolean": "A skill_roots lifecycle default flag is not a boolean.",
    "manifest_ambiguous_lifecycle_default": (
        "More than one skill root is declared as the default for a lifecycle action; "
        "exactly one default root is allowed per applicable action."
    ),
}


@dataclass(frozen=True)
class ManifestBlocker:
    """One deterministic, machine-readable reason a manifest cannot be trusted."""

    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "class": self.code,
            "message": self.message,
            "definition": MANIFEST_BLOCKER_CLASSES.get(self.code, "Unclassified manifest blocker."),
        }


@dataclass(frozen=True)
class ManifestEvaluation:
    """Explicit result of loading and validating an owner-repo project manifest."""

    state: str  # "absent" | "valid" | "invalid"
    path: str
    manifest: dict[str, Any] | None = None
    blockers: tuple[ManifestBlocker, ...] = ()
    legacy_compat: bool = False
    missing_contract_fields: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.state == "valid"

    @property
    def is_present(self) -> bool:
        return self.state != "absent"

    def blocker_dicts(self) -> list[dict[str, str]]:
        return [blocker.as_dict() for blocker in self.blockers]

    def blocker_codes(self) -> list[str]:
        return [blocker.code for blocker in self.blockers]

    def compatibility_note(self) -> str:
        """Human/agent guidance that names the tolerated legacy boundary when relevant."""
        if self.state == "absent":
            return (
                "No skills-sdk.json owner manifest was found; project-local skill "
                "roots fall back to built-in ownership heuristics."
            )
        if self.state == "invalid":
            return (
                "skills-sdk.json is present but invalid and must not be treated as absent; "
                "resolve the listed blockers before ownership or lifecycle decisions are trusted."
            )
        if self.legacy_compat:
            missing = ", ".join(self.missing_contract_fields) or "legacy skill_sources declaration"
            return (
                "skills-sdk.json is accepted under the tolerated legacy boundary "
                f"(missing full v1 contract fields: {missing}). It is valid for ownership "
                f"but should be migrated to the full {MANIFEST_SCHEMA_VERSION} contract."
            )
        return f"skills-sdk.json satisfies the full {MANIFEST_SCHEMA_VERSION} contract."


def normalize_root_path(raw: object) -> str:
    """Return the case-folded, slash-normalized comparison key for a root path."""
    if not isinstance(raw, str):
        return ""
    parts = Path(raw.strip().strip("/")).parts
    return "/".join(part.casefold() for part in parts)


def evaluate_manifest_payload(payload: object, *, path: str) -> ManifestEvaluation:
    """Validate an already-parsed manifest payload into an explicit evaluation."""
    if not isinstance(payload, dict):
        return ManifestEvaluation(
            state="invalid",
            path=path,
            blockers=(ManifestBlocker("manifest_not_object", MANIFEST_BLOCKER_CLASSES["manifest_not_object"]),),
        )

    blockers: list[ManifestBlocker] = []

    schema_version = payload.get("schema_version")
    if schema_version != MANIFEST_SCHEMA_VERSION:
        found = f"found {schema_version!r}" if "schema_version" in payload else "no schema_version declared"
        blockers.append(
            ManifestBlocker(
                "manifest_schema_version_unsupported",
                f"Manifest schema_version must be {MANIFEST_SCHEMA_VERSION!r}; {found}.",
            )
        )
        # Without a trusted schema version, no further structural claims are safe.
        return ManifestEvaluation(state="invalid", path=path, blockers=tuple(blockers))

    blockers.extend(_validate_skill_roots(payload.get("skill_roots")))

    missing_contract_fields = tuple(
        field_name for field_name in FULL_CONTRACT_FIELDS if field_name not in payload
    )
    has_legacy_skill_sources = isinstance(payload.get("skill_sources"), list)
    legacy_compat = bool(missing_contract_fields) or (
        has_legacy_skill_sources and "skill_roots" not in payload
    )

    if blockers:
        return ManifestEvaluation(
            state="invalid",
            path=path,
            blockers=tuple(blockers),
            legacy_compat=legacy_compat,
            missing_contract_fields=missing_contract_fields,
        )

    return ManifestEvaluation(
        state="valid",
        path=path,
        manifest=payload,
        legacy_compat=legacy_compat,
        missing_contract_fields=missing_contract_fields,
    )


def _validate_skill_roots(skill_roots: object) -> list[ManifestBlocker]:
    if skill_roots is None:
        # A manifest may legitimately omit skill_roots (legacy skill_sources form).
        return []
    if not isinstance(skill_roots, list):
        return [
            ManifestBlocker(
                "manifest_skill_roots_not_array",
                MANIFEST_BLOCKER_CLASSES["manifest_skill_roots_not_array"],
            )
        ]

    blockers: list[ManifestBlocker] = []
    seen_paths: dict[str, str] = {}
    lifecycle_defaults: dict[str, list[str]] = {field_name: [] for field_name in LIFECYCLE_DEFAULT_FIELDS}

    for index, root in enumerate(skill_roots):
        if not isinstance(root, dict):
            blockers.append(
                ManifestBlocker(
                    "manifest_skill_root_not_object",
                    f"skill_roots[{index}] must be an object.",
                )
            )
            continue

        raw_path = root.get("path")
        path_value = raw_path.strip() if isinstance(raw_path, str) else ""
        if not path_value:
            blockers.append(
                ManifestBlocker(
                    "manifest_skill_root_path_missing",
                    f"skill_roots[{index}] must declare a non-empty path.",
                )
            )
        else:
            normalized = normalize_root_path(path_value)
            if normalized in seen_paths:
                blockers.append(
                    ManifestBlocker(
                        "manifest_duplicate_skill_root",
                        (
                            f"skill_roots[{index}] path {path_value!r} duplicates "
                            f"{seen_paths[normalized]!r} after normalization."
                        ),
                    )
                )
            else:
                seen_paths[normalized] = path_value

        classification = root.get("classification")
        if classification is not None and classification not in SKILL_ROOT_CLASSIFICATIONS:
            blockers.append(
                ManifestBlocker(
                    "manifest_unsupported_classification",
                    (
                        f"skill_roots[{index}] classification {classification!r} is not one of "
                        f"{sorted(SKILL_ROOT_CLASSIFICATIONS)}."
                    ),
                )
            )

        label = path_value or f"skill_roots[{index}]"
        for field_name in LIFECYCLE_DEFAULT_FIELDS:
            if field_name not in root:
                continue
            value = root[field_name]
            if not isinstance(value, bool):
                blockers.append(
                    ManifestBlocker(
                        "manifest_lifecycle_default_not_boolean",
                        f"skill_roots[{index}] {field_name} must be a boolean, got {type(value).__name__}.",
                    )
                )
            elif value:
                lifecycle_defaults[field_name].append(label)

    for field_name, roots in lifecycle_defaults.items():
        if len(roots) > 1:
            blockers.append(
                ManifestBlocker(
                    "manifest_ambiguous_lifecycle_default",
                    (
                        f"{field_name} is declared by {len(roots)} skill roots ({', '.join(roots)}); "
                        "declare exactly one default root for this lifecycle action."
                    ),
                )
            )

    return blockers


def evaluate_manifest_file(manifest_path: Path, *, display_path: str | None = None) -> ManifestEvaluation:
    """Load and validate the manifest at ``manifest_path`` into an explicit evaluation."""
    path_label = display_path if display_path is not None else str(manifest_path)
    if not manifest_path.is_file():
        return ManifestEvaluation(state="absent", path=path_label)
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        return ManifestEvaluation(
            state="invalid",
            path=path_label,
            blockers=(
                ManifestBlocker("manifest_unreadable", f"Could not read {path_label}: {exc}."),
            ),
        )
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return ManifestEvaluation(
            state="invalid",
            path=path_label,
            blockers=(
                ManifestBlocker("manifest_invalid_json", f"{path_label} is not valid JSON: {exc}."),
            ),
        )
    return evaluate_manifest_payload(payload, path=path_label)


def evaluate_repo_manifest(repo_root: Path | None) -> ManifestEvaluation:
    """Evaluate the owner manifest at ``<repo_root>/skills-sdk.json``."""
    if repo_root is None:
        return ManifestEvaluation(state="absent", path=MANIFEST_FILENAME)
    return evaluate_manifest_file(repo_root / MANIFEST_FILENAME, display_path=MANIFEST_FILENAME)
