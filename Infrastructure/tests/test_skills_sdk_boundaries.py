import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_LIB = REPO_ROOT / "Infrastructure" / "scripts" / "lib" / "ask"
SKILLS_IMPL = ASK_LIB / "commands" / "skills_impl.py"
SKILLS_SDK = ASK_LIB / "skills_sdk"


def _module_ast(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imported_modules(path: Path) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(_module_ast(path)):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                modules.add("." * node.level + (node.module or ""))
            if node.module:
                modules.add(node.module)
    return modules


def _defined_functions(path: Path) -> set[str]:
    return {
        node.name
        for node in ast.walk(_module_ast(path))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_skills_sdk_modules_do_not_import_command_layer() -> None:
    sdk_modules = sorted(SKILLS_SDK.glob("*.py"))
    assert sdk_modules

    for module_path in sdk_modules:
        imported_modules = _imported_modules(module_path)
        assert "ask.commands" not in imported_modules
        assert not any(module.startswith("ask.commands.") for module in imported_modules)
        assert not any(
            module.startswith(".") and module.lstrip(".").startswith("commands")
            for module in imported_modules
        )


def test_imported_modules_tracks_relative_import_boundaries(tmp_path: Path) -> None:
    source = tmp_path / "module.py"
    source.write_text("from ..commands import skills_impl\n", encoding="utf-8")

    assert "..commands" in _imported_modules(source)


def test_skills_impl_facades_extracted_sdk_helpers() -> None:
    source = SKILLS_IMPL.read_text(encoding="utf-8")
    defined_functions = _defined_functions(SKILLS_IMPL)

    assert "from ask.skills_sdk.contracts import" in source
    assert "from ask.skills_sdk.runtime_adapters import" in source
    assert "from ask.skills_sdk.package_contracts import" in source
    assert not {
        "_doctor_blocker",
        "_doctor_warning",
        "_doctor_contract_schema_refs",
        "_skill_doctor_check_summary",
        "_runtime_failure_payload",
        "_skill_package_contract",
        "_skill_package_readiness",
        "_skill_package_checkout_test",
        "_capability_metadata_status",
    } & defined_functions
