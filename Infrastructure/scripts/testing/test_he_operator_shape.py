from pathlib import Path

import importlib.util


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "Plugins/harness-engineering/scripts/check_operator_shape.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_operator_shape", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_operator_shape_passes_for_active_he_plugin():
    module = load_module()
    root = ROOT / "Plugins/harness-engineering"
    findings = []
    for skill_dir in module.iter_skill_dirs(root):
        findings.extend(module.check_skill(skill_dir, root))
    assert findings == []


def test_operator_shape_detects_missing_contract_markers(tmp_path):
    module = load_module()
    root = tmp_path / "Plugins/harness-engineering"
    skill = root / "skills/he-demo"
    refs = skill / "references"
    refs.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: he-demo\ndescription: demo\n---\n", encoding="utf-8")
    (refs / "contract.yaml").write_text("schema_version: 1\npurpose: demo\n", encoding="utf-8")
    (refs / "evals.yaml").write_text("schema_version: '2.0'\ncases: []\n", encoding="utf-8")

    findings = module.check_skill(skill, root)

    assert any(finding["code"] == "CONTRACT_SHAPE" for finding in findings)
    assert any(finding["code"] == "EVAL_SHAPE" for finding in findings)
