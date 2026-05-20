from pathlib import Path

import importlib.util


ROOT = Path(__file__).resolve().parents[3]


def load_script(name):
    script = ROOT / f"Plugins/harness-engineering/scripts/{name}.py"
    spec = importlib.util.spec_from_file_location(name, script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hot_path_budget_detects_dangling_fragment(tmp_path):
    module = load_script("check_hot_path_budget")
    skill = tmp_path / "SKILL.md"
    skill.write_text("ok\nreferences with a clear route.\n", encoding="utf-8")

    findings, warnings = module.check_skill(skill)

    assert warnings == []
    assert any(finding["code"] == "HOT_PATH_FRAGMENT" for finding in findings)


def test_reference_integrity_ignores_negative_prompt_paths(tmp_path):
    module = load_script("check_reference_integrity")
    root = tmp_path / "Plugins/harness-engineering"
    skill = root / "skills/he-demo"
    refs = skill / "references"
    refs.mkdir(parents=True)
    path = refs / "evals.yaml"
    path.write_text(
        'cases:\n  - id: negative\n    prompt: "Edit .agents/skills/he-demo/SKILL.md directly."\n',
        encoding="utf-8",
    )

    findings = module.check_file(path, root)

    assert findings == []


def test_lifecycle_mutation_contract_requires_shared_reference(tmp_path):
    module = load_script("check_lifecycle_mutation_contract")
    skill = tmp_path / "he-demo"
    refs = skill / "references"
    refs.mkdir(parents=True)
    (skill / "SKILL.md").write_text("closure mutation live readback confirmation\n", encoding="utf-8")
    (refs / "contract.yaml").write_text("operator_contract: {}\n", encoding="utf-8")

    findings = module.check_skill(skill)

    assert any(finding["code"] == "LIFECYCLE_MUTATION_REFERENCE" for finding in findings)


def test_migration_report_covers_active_he_skills():
    module = load_script("report_legacy_migration")
    he_root = ROOT / "Plugins/harness-engineering"
    active_skills = sorted(path.parent.name for path in (he_root / "skills").glob("*/SKILL.md"))
    rows = module.skill_rows(he_root)
    reported_skills = sorted(row["skill"] for row in rows)

    assert reported_skills == active_skills
    assert len(rows) >= 17
    assert all(row["operator_contract"] == "present" for row in rows)


def test_progressive_validator_checks_shared_stage_references():
    script = (
        ROOT
        / "Infrastructure/scripts/validation-and-linting/validate_he_progressive_disclosure_impl.sh"
    ).read_text(encoding="utf-8")

    assert 'shared_ref_dir="Plugins/harness-engineering/references/skills/${skill_name}"' in script
    assert 'find -L "$shared_ref_dir" -type f -print0' in script
