from __future__ import annotations

import ast
import re
import shlex
from pathlib import Path
from typing import Any


PARSER_FAMILY_INVENTORY_SCHEMA_VERSION = "skills-sdk.parser-family-inventory-receipt.v1"
PARSER_FAMILY_INVENTORY_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/parser-family-inventory-receipt.v1.schema.json"
)
PARSER_FAMILY_ACCEPTANCE_TRACE = ["FR-008", "SA-003", "VP-032"]

PARSER_FAMILY_IDS = (
    "start",
    "check",
    "score",
    "ir",
    "docs",
    "evidence",
    "route-map",
    "eval",
    "package",
    "sandbox",
    "intake",
    "trust",
    "observability",
    "emitter",
    "ci",
    "explorer",
    "security",
    "plugin",
    "improve",
    "install",
    "rollback",
    "uninstall",
    "lifecycle",
    "status",
    "knowledge",
    "project",
    "lenses",
    "determinism",
    "review",
)

_GENERATED_PROJECTION_FAMILIES = {"docs", "route-map", "status"}
_COMPATIBILITY_WRAPPER_FAMILIES = {"plugin", "project"}
_AUTHORITY_BOUND_FAMILIES = {
    "eval",
    "trust",
    "plugin",
    "improve",
    "install",
    "rollback",
    "uninstall",
    "knowledge",
}

_DISPATCH_MODULES = {
    "evidence": ("Infrastructure/scripts/lib/ask/commands/sdk_evidence.py", "dispatch_sdk_evidence"),
    "route-map": ("Infrastructure/scripts/lib/ask/commands/sdk_evidence.py", "dispatch_sdk_route_map"),
    "eval": ("Infrastructure/scripts/lib/ask/commands/sdk_eval.py", "dispatch_sdk_eval"),
    "intake": ("Infrastructure/scripts/lib/ask/commands/sdk_intake.py", "dispatch_sdk_intake"),
    "knowledge": ("Infrastructure/scripts/lib/ask/commands/sdk_knowledge.py", "dispatch_sdk_knowledge"),
    "emitter": ("Infrastructure/scripts/lib/ask/commands/sdk_emitter.py", "dispatch_sdk_emitter"),
    "ci": ("Infrastructure/scripts/lib/ask/commands/sdk_ci.py", "dispatch_sdk_ci"),
    "explorer": ("Infrastructure/scripts/lib/ask/commands/sdk_explorer.py", "dispatch_sdk_explorer"),
    "security": ("Infrastructure/scripts/lib/ask/commands/sdk_security.py", "dispatch_sdk_security"),
    "plugin": ("Infrastructure/scripts/lib/ask/commands/sdk_plugin.py", "dispatch_sdk_plugin"),
}


def build_parser_family_inventory_receipt(repo_root: Path) -> dict[str, Any]:
    registered, dispatched, compatibility_examples = _discover_inventory_inputs(repo_root)
    checks = _build_inventory_checks(registered, dispatched, compatibility_examples)
    families = _build_family_rows(registered, dispatched, compatibility_examples)
    blockers = _blocker_checks(checks)
    status = "blocked" if blockers else "pass"
    return _receipt_payload(status, families, checks, len(blockers))


def _discover_inventory_inputs(repo_root: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, list[str]]]:
    return (
        _discover_registered_families(repo_root),
        _discover_dispatch_families(repo_root),
        _discover_compatibility_examples(repo_root),
    )


def _build_inventory_checks(
    registered: dict[str, dict[str, str]],
    dispatched: dict[str, dict[str, str]],
    compatibility_examples: dict[str, list[str]],
) -> list[dict[str, Any]]:
    return [
        _parity_check("registration_parity", set(registered), "Top-level parser registrations", "recorded family set"),
        _parity_check("dispatch_parity", set(dispatched), "SDK dispatch keys", "recorded family set"),
        _compatibility_check(compatibility_examples),
    ]


def _parity_check(check_id: str, discovered: set[str], subject: str, expected_label: str) -> dict[str, Any]:
    expected = set(PARSER_FAMILY_IDS)
    if discovered == expected:
        return _check(check_id, "pass", "info", f"{subject} match the {expected_label}.", sorted(discovered))
    evidence = [f"missing={sorted(expected - discovered)}", f"unexpected={sorted(discovered - expected)}"]
    return _check(check_id, "blocker", "blocker", f"{subject} do not match the {expected_label}.", evidence)


def _compatibility_check(compatibility_examples: dict[str, list[str]]) -> dict[str, Any]:
    missing = [family_id for family_id in PARSER_FAMILY_IDS if not compatibility_examples.get(family_id)]
    if missing:
        return _check(
            "missing_compatibility_examples",
            "blocker",
            "blocker",
            "Registered SDK parser families are missing command-metadata compatibility examples.",
            sorted(missing),
        )
    return _check("missing_compatibility_examples", "pass", "info", "Every parser family has a compatibility example.", [])


def _build_family_rows(
    registered: dict[str, dict[str, str]],
    dispatched: dict[str, dict[str, str]],
    compatibility_examples: dict[str, list[str]],
) -> list[dict[str, Any]]:
    return [
        _family_row(family_id, registered, dispatched, compatibility_examples)
        for family_id in PARSER_FAMILY_IDS
    ]


def _family_row(
    family_id: str,
    registered: dict[str, dict[str, str]],
    dispatched: dict[str, dict[str, str]],
    compatibility_examples: dict[str, list[str]],
) -> dict[str, Any]:
    examples = compatibility_examples.get(family_id, [])
    policy_disposition = _receipt_policy(family_id, examples)
    requires_fixture = _requires_concrete_fixture(examples)
    return {
        "id": family_id,
        "registration_owner": registered.get(family_id) or _missing_owner("registration", family_id),
        "dispatch_owner": dispatched.get(family_id) or _missing_owner("dispatch", family_id),
        "disposition": _family_disposition(family_id),
        "compatibility_examples": examples,
        "compatibility_example_source": _compatibility_source(examples),
        "receipt_policy": {
            "disposition": policy_disposition,
            "requires_concrete_fixture": requires_fixture,
            "reason": _receipt_policy_reason(policy_disposition, requires_fixture),
        },
        "caller_consequence": _caller_consequence(family_id, examples),
    }


def _compatibility_source(examples: list[str]) -> str | None:
    return "Infrastructure/scripts/lib/ask/command_metadata.py" if examples else None


def _blocker_checks(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [check for check in checks if check["status"] == "blocker"]


def _receipt_payload(
    status: str,
    families: list[dict[str, Any]],
    checks: list[dict[str, Any]],
    blocker_count: int,
) -> dict[str, Any]:
    return {
        "schema_version": PARSER_FAMILY_INVENTORY_SCHEMA_VERSION,
        "schema_uri": PARSER_FAMILY_INVENTORY_SCHEMA_URI,
        "status": status,
        "operation": "parser_family_inventory",
        "source_surface": "Infrastructure/scripts/lib/ask/commands/sdk*.py",
        "family_count": len(families),
        "families": families,
        "checks": checks,
        "mutation_performed": False,
        "command_execution_performed": False,
        "acceptance_trace": PARSER_FAMILY_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"Classified {len(families)} public SDK parser famil{'y' if len(families) == 1 else 'ies'} "
            "against the receipt replay policy without executing or mutating a command; "
            f"{blocker_count} blocker check(s) remain."
        ),
    }


def _discover_registered_families(repo_root: Path) -> dict[str, dict[str, str]]:
    commands_root = repo_root / "Infrastructure/scripts/lib/ask/commands"
    discovered: dict[str, dict[str, str]] = {}
    for path in sorted(commands_root.glob("sdk*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        discovered.update(_discover_registered_path(repo_root, path, tree))
    return discovered


def _discover_registered_path(repo_root: Path, path: Path, tree: ast.Module) -> dict[str, dict[str, str]]:
    discovered: dict[str, dict[str, str]] = {}
    for node in _sdk_parser_functions(tree):
        discovered.update(_registered_calls(repo_root, path, node))
    return discovered


def _sdk_parser_functions(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [node for node in tree.body if _is_sdk_parser_function(node)]


def _is_sdk_parser_function(node: ast.AST) -> bool:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    return any(argument.arg == "sdk_subparsers" for argument in node.args.args)


def _registered_calls(repo_root: Path, path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, dict[str, str]]:
    return {
        family_id: {"path": _repo_relative(repo_root, path), "symbol": node.name}
        for call in ast.walk(node)
        if (family_id := _registered_call_family(call)) is not None
    }


def _registered_call_family(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        return None
    if node.func.attr != "add_parser" or not isinstance(node.func.value, ast.Name):
        return None
    if node.func.value.id != "sdk_subparsers" or not node.args:
        return None
    action = node.args[0]
    return action.value if isinstance(action, ast.Constant) and isinstance(action.value, str) else None


def _discover_dispatch_families(repo_root: Path) -> dict[str, dict[str, str]]:
    path = repo_root / "Infrastructure/scripts/lib/ask/commands/sdk.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    dispatch = _find_dispatch_dict(tree)
    return _dispatch_rows(dispatch) if dispatch else {}


def _find_dispatch_dict(tree: ast.Module) -> ast.Dict | None:
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name != "dispatch_sdk":
            continue
        for child in ast.walk(node):
            if _is_dispatch_dict(child):
                return child
    return None


def _is_dispatch_dict(node: ast.AST) -> bool:
    if not isinstance(node, ast.Dict):
        return False
    keys = {key.value for key in node.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)}
    return {"start", "review"} <= keys


def _dispatch_rows(dispatch: ast.Dict) -> dict[str, dict[str, str]]:
    return {
        key.value: _dispatch_owner(key.value, value)
        for key, value in zip(dispatch.keys, dispatch.values)
        if isinstance(key, ast.Constant) and isinstance(key.value, str) and key.value in PARSER_FAMILY_IDS
    }


def _dispatch_owner(family_id: str, value: ast.AST) -> dict[str, str]:
    if family_id in _DISPATCH_MODULES:
        owner_path, owner_symbol = _DISPATCH_MODULES[family_id]
    elif isinstance(value, ast.Name):
        owner_path, owner_symbol = "Infrastructure/scripts/lib/ask/commands/sdk.py", value.id
    else:
        owner_path, owner_symbol = "Infrastructure/scripts/lib/ask/commands/sdk.py", f"dispatch_sdk[{family_id}]"
    return {"path": owner_path, "symbol": owner_symbol}


def _discover_compatibility_examples(repo_root: Path, *, metadata_path: Path | None = None) -> dict[str, list[str]]:
    path = metadata_path or repo_root / "Infrastructure/scripts/lib/ask/command_metadata.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assignment = _command_examples_assignment(tree)
    if assignment is None:
        return _empty_examples()
    examples = _empty_examples()
    for node in ast.walk(assignment):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            family_id = _compatibility_family(node.value)
            if family_id:
                examples[family_id].append(node.value.strip())
    return _dedupe_examples(examples)


def _empty_examples() -> dict[str, list[str]]:
    return {family_id: [] for family_id in PARSER_FAMILY_IDS}


def _command_examples_assignment(tree: ast.Module) -> ast.AST | None:
    for statement in tree.body:
        if _is_command_examples_assignment(statement):
            return statement.value
    return None


def _is_command_examples_assignment(statement: ast.stmt) -> bool:
    if isinstance(statement, ast.AnnAssign):
        return isinstance(statement.target, ast.Name) and statement.target.id == "COMMAND_EXAMPLES"
    if isinstance(statement, ast.Assign):
        return any(isinstance(target, ast.Name) and target.id == "COMMAND_EXAMPLES" for target in statement.targets)
    return False


def _compatibility_family(command: str) -> str | None:
    try:
        argv = shlex.split(command.strip())
    except ValueError:
        return None
    if argv[:2] == ["ask", "sdk"] and len(argv) >= 3:
        family_id = argv[2]
    elif argv[:1] == ["skills-sdk"] and len(argv) >= 2:
        family_id = argv[1]
    else:
        return None
    return family_id if family_id in PARSER_FAMILY_IDS else None


def _dedupe_examples(examples: dict[str, list[str]]) -> dict[str, list[str]]:
    return {family_id: sorted(set(values)) for family_id, values in examples.items()}


def _family_disposition(family_id: str) -> str:
    if family_id in _GENERATED_PROJECTION_FAMILIES:
        return "generated_projection"
    if family_id in _COMPATIBILITY_WRAPPER_FAMILIES:
        return "compatibility_wrapper"
    return "retained_lifecycle_surface"


def _receipt_policy(family_id: str, examples: list[str]) -> str:
    if family_id in _AUTHORITY_BOUND_FAMILIES:
        return "authority_bound_mutation"
    if _requires_concrete_fixture(examples):
        return "template_requires_concrete_fixture"
    if examples and all("--preview" in example for example in examples):
        return "preview_replay"
    return "explicit_run_receipt"


def _requires_concrete_fixture(examples: list[str]) -> bool:
    for example in examples:
        try:
            argv = shlex.split(example)
        except ValueError:
            continue
        if any(re.search(r"<[^>]+>", argument) for argument in argv):
            return True
    return False


def _receipt_policy_reason(disposition: str, requires_fixture: bool) -> str:
    if disposition == "template_requires_concrete_fixture":
        return "At least one compatibility example contains a template token; replace it with a repository-owned fixture before replay."
    if disposition == "authority_bound_mutation":
        if requires_fixture:
            return "The family reaches an authority-bearing or execution path and includes a template token; replace it with a repository-owned fixture before obtaining a bounded mutation receipt."
        return "The family reaches an authority-bearing or execution path; replay requires a bounded mutation receipt."
    if disposition == "preview_replay":
        return "All recorded compatibility examples are preview-only; replay still requires a family-specific run receipt."
    return "The family has a concrete compatibility surface but no preview-only guarantee; replay requires an explicit run receipt."


def _caller_consequence(family_id: str, examples: list[str]) -> str:
    if not examples:
        return (
            f"No compatibility example is recorded for sdk {family_id}; preserve the registration and dispatch, "
            "but do not claim replay coverage until a concrete command example is added."
        )
    return (
        f"Command metadata records a compatibility example for sdk {family_id}; keep the family behind its "
        "recorded replay policy and do not infer runtime proof from example text alone."
    )


def _missing_owner(kind: str, family_id: str) -> dict[str, str]:
    return {
        "path": f"<unresolved-{kind}-owner>",
        "symbol": f"<unresolved-{kind}-owner:{family_id}>",
    }


def _check(check_id: str, status: str, severity: str, message: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": severity,
        "message": message,
        "evidence": evidence,
    }


def _repo_relative(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()
