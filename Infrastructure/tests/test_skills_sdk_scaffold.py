import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ADR = REPO_ROOT / ".harness/decisions/2026-06-03-jsc-391-skills-sdk-path-map-adr.md"
EVIDENCE = REPO_ROOT / ".harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor"
OWNERSHIP_MAP = EVIDENCE / "module-ownership-map.json"
MODULE_DOC = REPO_ROOT / "Docs/reference/skills-sdk/modules.md"
SCHEMA_DIR = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk"
FIXTURES = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk"
EXAMPLES = REPO_ROOT / "Docs/examples/skills-sdk"
PLACEHOLDERS = EVIDENCE / "placeholders"

REQUIRED_MODULES = {
    "manifest",
    "receipts",
    "risk",
    "install",
    "sandbox",
    "refs",
    "evals",
    "signing",
    "runtime",
    "packaging",
}

DENIED_SOURCE_PREFIXES = (
    ".agents/",
    ".agents/skills/",
    ".skillsets/",
    "skills-codex/",
    "Plugins/cache/",
    "~/.agents/skills/",
    "~/.codex/skills/",
)

FEATURE_LEAK_KEYS = {
    "signing_execution_performed",
    "key_handling_performed",
    "trust_store_write_performed",
    "registry_publication_performed",
    "package_upload_performed",
    "install_write_performed",
    "mutation_performed",
    "execution_performed",
    "network_fetch_performed",
    "external_service_used",
}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_path_map_adr_selects_and_rejects_scaffold_paths() -> None:
    adr = ADR.read_text(encoding="utf-8")

    for selected_path in (
        "Infrastructure/scripts/lib/ask/skills_sdk/**",
        "Docs/reference/skills-sdk/**",
        "Infrastructure/config/schemas/skills-sdk/**",
        "Infrastructure/tests/fixtures/skills_sdk/**",
        "Docs/examples/skills-sdk/**",
        ".harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/**",
    ):
        assert selected_path in adr

    for denied_path in DENIED_SOURCE_PREFIXES:
        assert denied_path in adr


def test_module_ownership_map_has_required_public_contract_fields() -> None:
    ownership = _json(OWNERSHIP_MAP)
    modules = {row["module"]: row for row in ownership["modules"]}

    assert set(modules) == REQUIRED_MODULES

    for module_name, row in modules.items():
        assert row["owns"], module_name
        assert row["collaborators"], module_name
        assert row["public_contract"], module_name
        assert row["forbidden_ownership"], module_name
        assert row["source_paths"], module_name
        assert row["status"] in {
            "placeholder_contract",
            "preserve_existing",
            "preserve_existing_plus_placeholder",
        }
        assert not any(
            path.startswith(DENIED_SOURCE_PREFIXES)
            for path in row["source_paths"]
        ), module_name


def test_module_docs_define_work_modes_risk_and_receipt_language() -> None:
    docs = MODULE_DOC.read_text(encoding="utf-8")

    for term in REQUIRED_MODULES | {
        "inferential",
        "computational",
        "hybrid",
        "probability",
        "impact",
        "detectability",
        "proof metadata",
        "redaction",
    }:
        assert term in docs


def test_schema_and_placeholder_modules_stay_in_lockstep() -> None:
    schema_modules = {
        _json(path)["properties"]["module"]["const"]
        for path in SCHEMA_DIR.glob("*-placeholder.v1.schema.json")
    }
    placeholder_modules = {
        _json(path)["module"]
        for path in PLACEHOLDERS.glob("*.json")
    }

    assert schema_modules == REQUIRED_MODULES - {"runtime", "packaging"}
    assert placeholder_modules == schema_modules


def test_placeholders_do_not_claim_feature_readiness() -> None:
    for path in PLACEHOLDERS.glob("*.json"):
        data = _json(path)
        assert data["status"] in {"not_run", "skipped_optional", "blocked"}
        assert data["status"] != "pass"

        for key in FEATURE_LEAK_KEYS & data.keys():
            assert data[key] is False, f"{path} leaked {key}"


def test_skill_fixtures_cover_valid_invalid_and_projection_rejection() -> None:
    valid_skill = (FIXTURES / "valid_skill/SKILL.md").read_text(encoding="utf-8")
    invalid_skill = (FIXTURES / "invalid_missing_frontmatter/SKILL.md").read_text(
        encoding="utf-8"
    )
    rejected_projection = _json(FIXTURES / "generated_projection/rejected-path.json")

    assert valid_skill.startswith("---\n")
    assert "name: skills-sdk-valid-fixture" in valid_skill
    assert not invalid_skill.startswith("---\n")
    assert rejected_projection["classification"] == "runtime_projection"
    assert rejected_projection["scaffold_source_allowed"] is False
    assert rejected_projection["path"].startswith(DENIED_SOURCE_PREFIXES)


def test_draft_package_fixtures_do_not_publish_or_install() -> None:
    draft_package = _json(FIXTURES / "draft_package/package.json")
    draft_example = _json(EXAMPLES / "draft-package.json")

    assert draft_package["status"] == "not_run"
    assert draft_package["runtime_projection"] is None
    assert draft_package["registry_publication_performed"] is False
    assert draft_package["package_upload_performed"] is False
    assert draft_package["install_write_performed"] is False

    feature_execution = draft_example["feature_execution"]
    assert feature_execution["install_write_performed"] is False
    assert feature_execution["registry_publication_performed"] is False
    assert feature_execution["package_upload_performed"] is False
