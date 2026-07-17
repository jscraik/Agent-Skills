from __future__ import annotations

from pathlib import Path


WRAPPER = Path(__file__).resolve().parents[1] / "harness-cli.sh"


def test_harness_fallback_pin_is_the_approved_release() -> None:
    source = WRAPPER.read_text(encoding="utf-8")

    assert 'SUPPORTED_VERSION="0.15.0"' in source
    assert 'FALLBACK_PACKAGE="@brainwav/coding-harness@$SUPPORTED_VERSION"' in source


def test_harness_fallback_invokes_the_pinned_package() -> None:
    source = WRAPPER.read_text(encoding="utf-8")

    assert 'exec npm exec --yes --package "$FALLBACK_PACKAGE" -- harness "$@"' in source


def test_harness_local_resolution_is_versioned_and_repo_bound() -> None:
    source = WRAPPER.read_text(encoding="utf-8")

    assert 'SUPPORTED_VERSION="0.15.0"' in source
    assert 'HARNESS_SUPPORTED_VERSION="$SUPPORTED_VERSION"' in source
    assert 'const expectedPackageRoot = resolve(' in source
    assert '"node_modules/@brainwav/coding-harness",' in source
    assert 'realpathSync(expectedPackageRoot)' in source
    assert 'packageMetadata.name !== "@brainwav/coding-harness"' in source
    assert "packageMetadata.version !== supportedVersion" in source


def test_harness_local_resolution_has_typed_identity_and_boundary_failures() -> None:
    source = WRAPPER.read_text(encoding="utf-8")

    assert "process.exit(44)" in source
    assert "process.exit(45)" in source
    assert "does not match $SUPPORTED_VERSION" in source
    assert "outside the approved repo-local boundary" in source


def test_harness_executes_only_the_validated_cli_path() -> None:
    source = WRAPPER.read_text(encoding="utf-8")

    assert 'exec node "$CLI_PATH" "$@"' in source
