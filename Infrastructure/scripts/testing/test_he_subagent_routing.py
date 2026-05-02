import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "Infrastructure/scripts/validation-and-linting/validate_he_subagent_routing.py"
ROUTING_MAP = ROOT / "Plugins/harness-engineering/references/routing-map.json"


def _mapped_roles() -> list[str]:
    routing = json.loads(ROUTING_MAP.read_text(encoding="utf-8"))
    roles: set[str] = set()
    for policy in routing["subagent_stage_map"].values():
        roles.update(policy.get("baseline_roles", []))
        roles.update(policy.get("conditional_roles", []))
    return sorted(roles)


def test_he_subagent_routing_validator_accepts_manifest_roles(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps([{"role": role} for role in _mapped_roles()]),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--manifest", str(manifest)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "[he-subagent-routing] ok" in result.stdout


def test_he_subagent_routing_validator_rejects_missing_roles(tmp_path: Path) -> None:
    roles = _mapped_roles()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps([{"role": role} for role in roles if role != "worker"]),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--manifest", str(manifest)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "maps roles missing from manifest" in result.stderr
    assert "worker" in result.stderr
