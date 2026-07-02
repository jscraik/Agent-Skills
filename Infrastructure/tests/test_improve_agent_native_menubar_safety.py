from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE_ROOT = REPO_ROOT / "Prototypes" / "improve-agent-native-menubar"
LAUNCH_COMMAND = PROTOTYPE_ROOT / "Launch.command"
APP_SWIFT = PROTOTYPE_ROOT / "Sources" / "ImproveAgentNativeMenuBar" / "App.swift"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_launcher_defaults_to_build_only_and_uses_launchservices_for_open() -> None:
    script = _read(LAUNCH_COMMAND)

    assert "OPEN_APP=0" in script
    assert "SAFE_OPEN=0" in script
    assert "Usage: ./Launch.command [--open|--open-safe]" in script
    assert "Build-only mode; not launching." in script
    assert '/usr/bin/open -n "$APP_DIR"' in script
    assert "LaunchServices open requested" in script
    assert "IMPROVE_AGENT_NATIVE_DISABLE_TESSL_CLI" in script


def test_launcher_does_not_fallback_to_raw_appkit_executable() -> None:
    script = _read(LAUNCH_COMMAND)

    forbidden_patterns = [
        'nohup "$EXECUTABLE"',
        '"$EXECUTABLE" >',
        "swift run",
        "Launching bundled executable directly",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in script


def test_tessl_probe_is_one_bounded_noninteractive_json_command() -> None:
    source = _read(APP_SWIFT)

    required_patterns = [
        "TesslProbeCache.shared.beginOrCached()",
        "Shell.run(Self.tesslInfoCommand, cwd: root, timeout: 8)",
        "Self.tesslCliDisabled",
        "IMPROVE_AGENT_NATIVE_DISABLE_TESSL_CLI",
        'export TESSL_NONINTERACTIVE=1',
        'exec "$TESSL_BIN" plugin info jscraik/improve-agent-native --json',
    ]
    for pattern in required_patterns:
        assert pattern in source

    forbidden_patterns = [
        "op run",
        "tessl login",
        "plugin info jscraik/improve-agent-native --json 2>",
        '|| "$TESSL_BIN" plugin info',
    ]
    for pattern in forbidden_patterns:
        assert pattern not in source


def test_dashboard_load_is_one_attempt_without_background_polling_loop() -> None:
    source = _read(APP_SWIFT)

    assert "private var didAttemptLoad = false" in source
    assert "func refresh(force: Bool = false) async" in source
    assert "guard force || !didAttemptLoad else { return }" in source

    forbidden_patterns = [
        "refreshIntervalNanoseconds",
        "startAutoRefresh",
        "Task.sleep",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in source
