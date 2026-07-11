import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "Infrastructure/scripts/validation-and-linting/validate_he_subagent_routing.py"
ROUTING_MAP = ROOT / "Plugins/harness-engineering/references/routing-map.json"


def test_he_subagent_routing_validator_accepts_desktop_capability_contract() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "generic Desktop capability routing" in result.stdout


def test_he_subagent_routing_validator_rejects_missing_capability_packet_field(
    tmp_path: Path,
) -> None:
    routing = json.loads(ROUTING_MAP.read_text(encoding="utf-8"))
    routing["desktop_collaboration_contract"]["required_packet_fields"].remove(
        "stop_condition"
    )
    patched_routing = tmp_path / "routing-map.json"
    patched_routing.write_text(json.dumps(routing), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--routing-map", str(patched_routing)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "required_packet_fields" in result.stderr


def test_he_subagent_routing_validator_rejects_empty_stage_capabilities(
    tmp_path: Path,
) -> None:
    routing = json.loads(ROUTING_MAP.read_text(encoding="utf-8"))
    routing["subagent_stage_map"]["he-work"]["baseline_capabilities"] = []
    routing["subagent_stage_map"]["he-work"]["conditional_capabilities"] = []
    patched_routing = tmp_path / "routing-map.json"
    patched_routing.write_text(json.dumps(routing), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--routing-map", str(patched_routing)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "he-work must declare at least one task capability" in result.stderr
