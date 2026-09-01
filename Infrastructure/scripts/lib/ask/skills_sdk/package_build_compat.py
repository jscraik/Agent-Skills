"""Temporary Agent-Skills projection of the portable SDK package receipt."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skills_sdk.models.packaging import PackageReceiptV2

from ask.skills_sdk.portable_adapter import (
    PortableAdapterBlocker,
    run_portable_validation,
)


@dataclass(frozen=True, slots=True)
class PackageBuildProjection:
    """CLI projection plus an optional host-side error message."""

    payload: dict[str, object]
    error_message: str | None = None


def _blocked_payload(
    query: str,
    source_path: str,
    validation_command: str,
    blocker: PortableAdapterBlocker,
) -> dict[str, object]:
    return {
        "schema_version": "skills-sdk-package-build.v1",
        "query": query,
        "status": "blocked",
        "canonical_source_path": source_path,
        "facade_command": "skills-sdk package build",
        "adapter_blocker": {"code": blocker.code, "message": blocker.message},
        "mutation_performed": False,
        "validation_commands": [validation_command],
        "agent_summary": f"skills-sdk package build is blocked for {query}: {blocker.message}",
    }


def _receipt_payload(
    query: str,
    source_path: str,
    validation_command: str,
    receipt: PackageReceiptV2,
) -> PackageBuildProjection:
    candidate = receipt.candidate
    manifest = receipt.manifest
    blocker_message = receipt.blocker.message if receipt.blocker else None
    payload = {
        "schema_version": "skills-sdk-package-build.v1",
        "query": query,
        "status": receipt.status,
        "canonical_source_path": source_path,
        "facade_command": "skills-sdk package build",
        "package_id": candidate.package_id if candidate else None,
        "version": manifest.version if manifest else None,
        "source_revision": candidate.source_revision if candidate else None,
        "source_digest": candidate.content_sha256 if candidate else None,
        "package_digest": receipt.package_digest,
        "included_files": list(receipt.included_files),
        "excluded_files": list(receipt.excluded_files),
        "receipt": receipt.model_dump(mode="json"),
        "mutation_performed": False,
        "validation_commands": [validation_command],
        "agent_summary": (
            f"skills-sdk package build produced digest identity for {query} without writes."
            if blocker_message is None
            else f"skills-sdk package build is blocked for {query}: {blocker_message}"
        ),
    }
    return PackageBuildProjection(payload=payload, error_message=blocker_message)


def build_package_projection(
    source_path: Path,
    *,
    query: str,
    canonical_source_path: str,
    validation_command: str,
) -> PackageBuildProjection:
    """Delegate one build and expose only the temporary CLI compatibility shape."""

    delegated = run_portable_validation(source_path, operation="build")
    if isinstance(delegated, PortableAdapterBlocker):
        return PackageBuildProjection(
            payload=_blocked_payload(
                query,
                canonical_source_path,
                validation_command,
                delegated,
            ),
            error_message=delegated.message,
        )
    if delegated.operation != "build" or not isinstance(
        delegated.payload, PackageReceiptV2
    ):
        raise TypeError("portable build delegation returned an unexpected payload")
    return _receipt_payload(
        query,
        canonical_source_path,
        validation_command,
        delegated.payload,
    )


__all__ = ["PackageBuildProjection", "build_package_projection"]
