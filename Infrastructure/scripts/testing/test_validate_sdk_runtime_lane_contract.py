from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "validate_sdk_runtime_lane_contract.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("validate_sdk_runtime_lane_contract", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_sdk_runtime_lane_contract_current_repo_passes() -> None:
    module = _load_module()

    assert module.validate() == []


def test_contract_blocks_missing_oss_local_command(monkeypatch) -> None:
    module = _load_module()
    original_read = module._read

    def fake_read(path: Path) -> str:
        text = original_read(path)
        if path == module.CONTRACT_PATH:
            return text.replace("oss-local", "missing-local")
        return text

    monkeypatch.setattr(module, "_read", fake_read)

    findings = module.validate()

    assert any(finding.code == "missing_lane_command" for finding in findings)
    assert any("codex exec --profile oss-local" in finding.message for finding in findings)


def test_contract_blocks_missing_pipeline_stage(monkeypatch) -> None:
    module = _load_module()
    original_read = module._read

    def fake_read(path: Path) -> str:
        text = original_read(path)
        if path == module.CONTRACT_PATH:
            return text.replace("1. SDK mechanical validation", "1. Static checks")
        return text

    monkeypatch.setattr(module, "_read", fake_read)

    findings = module.validate()

    assert any(finding.code == "missing_promotion_pipeline" for finding in findings)


def test_contract_blocks_missing_gold_standard_rubric(monkeypatch) -> None:
    module = _load_module()
    original_read = module._read

    def fake_read(path: Path) -> str:
        text = original_read(path)
        if path == module.CONTRACT_PATH:
            return text.replace("Skills SDK Gold Standard Rubric", "Skills SDK release scorecard")
        return text

    monkeypatch.setattr(module, "_read", fake_read)

    findings = module.validate()

    assert any(finding.code == "missing_promotion_pipeline" for finding in findings)


def test_contract_blocks_missing_non_substitution_rule(monkeypatch) -> None:
    module = _load_module()
    original_read = module._read

    def fake_read(path: Path) -> str:
        text = original_read(path)
        if path == module.CONTRACT_PATH:
            return text.replace(
                "Do not treat local Tessl package staging as external Tessl scoring proof",
                "Do not confuse Tessl lanes",
            )
        return text

    monkeypatch.setattr(module, "_read", fake_read)

    findings = module.validate()

    assert any(finding.code == "missing_non_substitution_rule" for finding in findings)


def test_contract_blocks_missing_fast_profile_smoke_boundary(monkeypatch) -> None:
    module = _load_module()
    original_read = module._read

    def fake_read(path: Path) -> str:
        text = original_read(path)
        if path == module.CONTRACT_PATH:
            return text.replace("codex exec --profile fast", "codex exec smoke")
        return text

    monkeypatch.setattr(module, "_read", fake_read)

    findings = module.validate()

    assert any(finding.code == "missing_non_substitution_rule" for finding in findings)
    assert any("codex exec --profile fast" in finding.message for finding in findings)


import re

def test_contract_blocks_missing_tessl_references_not_rules_projection(monkeypatch) -> None:
    module = _load_module()
    original_read = module._read

    def fake_read(path: Path) -> str:
        text = original_read(path)
        if path == module.CONTRACT_PATH:
            return re.sub(
                r"Do not translate skill\s+references into Tessl `rules/`",
                "Use Tessl package folders for support context",
                text,
                count=1,
            )
        return text

    monkeypatch.setattr(module, "_read", fake_read)

    findings = module.validate()

    assert any(finding.code == "missing_promotion_pipeline" for finding in findings)
    assert any("Do not translate skill references" in finding.message for finding in findings)


def test_contract_blocks_missing_tessl_registry_badge_guidance(monkeypatch) -> None:
    module = _load_module()
    original_read = module._read

    def fake_read(path: Path) -> str:
        text = original_read(path)
        if path == module.CONTRACT_PATH:
            return text.replace("GitHub Badge section", "registry presentation section")
        return text

    monkeypatch.setattr(module, "_read", fake_read)

    findings = module.validate()

    assert any(finding.code == "missing_promotion_pipeline" for finding in findings)
    assert any("GitHub Badge section" in finding.message for finding in findings)
