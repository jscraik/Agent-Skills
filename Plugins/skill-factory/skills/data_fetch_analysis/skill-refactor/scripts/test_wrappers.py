from pathlib import Path


def test_repo_scripts_exist():
    root = next(p for p in Path(__file__).resolve().parents if (p / "Infrastructure").is_dir())
    base = root / "Infrastructure/scripts/skill-refactor"
    assert (base / "scan_codex_sessions.py").exists()
    assert (base / "correlate_multi_source_skill_failures.py").exists()
