from __future__ import annotations

import os
from pathlib import Path
import subprocess


WRAPPER = Path(__file__).resolve().parents[1] / "harness-cli.sh"
GATE = Path(__file__).resolve().parents[1] / "run-harness-gate.sh"


def test_harness_fallback_pin_is_the_approved_release() -> None:
    source = WRAPPER.read_text(encoding="utf-8")

    assert 'SUPPORTED_VERSION="0.15.3"' in source
    assert 'FALLBACK_PACKAGE="@brainwav/coding-harness@$SUPPORTED_VERSION"' in source


def test_harness_fallback_invokes_the_pinned_package() -> None:
    source = WRAPPER.read_text(encoding="utf-8")

    assert "resolution_status -eq 42 || $resolution_status -eq 44" in source
    assert 'exec npm exec --yes --package "$FALLBACK_PACKAGE" -- harness "$@"' in source


def test_harness_never_executes_an_unverified_ambient_binary(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    marker = tmp_path / "ambient-harness-ran"
    ambient_harness = fake_bin / "harness"
    ambient_harness.write_text(
        f'#!/usr/bin/env bash\ntouch "{marker}"\n',
        encoding="utf-8",
    )
    ambient_harness.chmod(0o755)
    fake_node = fake_bin / "node"
    fake_node.write_text("#!/usr/bin/env bash\nexit 42\n", encoding="utf-8")
    fake_node.chmod(0o755)

    result = subprocess.run(
        ["bash", str(WRAPPER), "--version"],
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "HARNESS_CLI_ALLOW_NPM_EXEC": "0",
        },
        text=True,
    )

    assert result.returncode == 1
    assert "Refusing to run an ambient harness executable" in result.stderr
    assert not marker.exists()


def test_harness_allows_explicit_pinned_fallback_after_version_drift(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    marker = tmp_path / "npm-arguments"
    fake_node = fake_bin / "node"
    fake_node.write_text("#!/usr/bin/env bash\nexit 44\n", encoding="utf-8")
    fake_node.chmod(0o755)
    fake_npm = fake_bin / "npm"
    fake_npm.write_text(
        f'#!/usr/bin/env bash\nprintf "%s\\n" "$@" > "{marker}"\n',
        encoding="utf-8",
    )
    fake_npm.chmod(0o755)

    result = subprocess.run(
        ["bash", str(WRAPPER), "--version"],
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "HARNESS_CLI_ALLOW_NPM_EXEC": "1",
        },
        text=True,
    )

    assert result.returncode == 0
    assert marker.read_text(encoding="utf-8").splitlines() == [
        "exec",
        "--yes",
        "--package",
        "@brainwav/coding-harness@0.15.3",
        "--",
        "harness",
        "--version",
    ]


def test_harness_gate_has_no_ambient_runner_fallbacks() -> None:
    source = GATE.read_text(encoding="utf-8")

    assert 'run_with_process_storm_guard harness "$@"' not in source
    assert "MISE_RESOLVED=" not in source
    assert "Refusing ambient mise or harness fallbacks" in source


def test_harness_local_resolution_is_versioned_and_repo_bound() -> None:
    source = WRAPPER.read_text(encoding="utf-8")

    assert 'SUPPORTED_VERSION="0.15.3"' in source
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
    assert 'if [[ $resolution_status -eq 44 ]]; then' in source
    assert 'if [[ $resolution_status -eq 45 ]]; then' in source
    assert source.index('if [[ $resolution_status -eq 44 ]]') < source.index('exec node "$CLI_PATH"')
