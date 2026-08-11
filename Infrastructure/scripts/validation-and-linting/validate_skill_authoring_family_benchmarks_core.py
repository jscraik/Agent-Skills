#!/usr/bin/env python3
"""Deterministic benchmark checks for the skill-authoring family.

This script enforces equivalent contract/eval/security baseline requirements for:
- Plugins/skill-factory/skills/skill-factory-router
- Plugins/skill-factory/skills/scaffolding_templates/skill-creator
- Plugins/skill-factory/skills/infrastructure_ops/skill-installer
- Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator

It is designed for CI and local gates where live LLM eval execution is not required.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set

try:
    import yaml  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover
    yaml = None  # type: ignore[assignment]
    _YAML_IMPORT_ERROR: ModuleNotFoundError | None = exc
else:
    _YAML_IMPORT_ERROR = None

_JSONSCHEMA_AVAILABLE = importlib.util.find_spec("jsonschema") is not None


REPO_ROOT = Path(__file__).resolve().parents[3]

# Severity ranking for baseline regression comparison (higher = worse)
SEVERITY_RANK = {"INFO": 0, "WARN": 1, "FAIL": 2}
_SKILL_BUILDER_ROOT_CANDIDATES = (
    REPO_ROOT / "Plugins" / "skill-factory",
    REPO_ROOT / "plugins" / "skill-factory",
)
_SKILL_BUILDER_ROOT = next(
    (candidate for candidate in _SKILL_BUILDER_ROOT_CANDIDATES if candidate.exists()),
    _SKILL_BUILDER_ROOT_CANDIDATES[0],
)
_SCHEMA_DIR_CANDIDATES = (
    _SKILL_BUILDER_ROOT / "skills" / "code_quality_review" / "skill-builder" / "references",
    _SKILL_BUILDER_ROOT / "references" / "skill-builder",
)
_SCHEMA_DIR = next(
    (
        candidate
        for candidate in _SCHEMA_DIR_CANDIDATES
        if (candidate / "contract.schema.yaml").exists() and (candidate / "evals.schema.yaml").exists()
    ),
    _SCHEMA_DIR_CANDIDATES[0],
)
_CONTRACT_SCHEMA_PATH = _SCHEMA_DIR / "contract.schema.yaml"
_EVALS_SCHEMA_PATH = _SCHEMA_DIR / "evals.schema.yaml"
DEFAULT_FAMILY_SKILLS = (
    "Plugins/skill-factory/skills/skill-factory-router",
    "skills-system/skill-creator",
    "skills-system/skill-installer",
    "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator",
)

REQUIRED_CONTRACT_KEYS = {
    "purpose",
    "triggers",
    "inputs",
    "outputs",
    "non_goals",
    "risks",
}
REQUIRED_CASE_CATEGORIES = {"happy", "edge", "negative", "pressure"}
REQUIRED_TASK_PROFILE_KEYS = {
    "schema_version",
    "profile_id",
    "scope_skill",
    "scope_profile",
    "rubric_version",
    "evaluator_version",
    "persona_set_id",
    "thresholds",
    "criteria",
    "delegation",
    "learning_posture",
}
RISKY_COMMAND_TOKENS = {"curl", "wget", "rm -rf", "netcat", "nc"}

# Indirect PI tokens to scan in non-eval reference files and SKILL.md body.
# evals.yaml is intentionally excluded — PI language there is test coverage, not injection.
_INDIRECT_PI_TOKENS = re.compile(
    r"ignore (all |previous )?instructions|disregard (all )?previous|"
    r"forget (your|all) instructions|bypass (safety|all checks)|"
    r"you are now|your new instructions are|act as if",
    re.IGNORECASE,
)

# Minimum ratio of cases that must carry deterministic_checks (non-trivial dict).
_DET_CHECK_COVERAGE_WARN_THRESHOLD = 0.30

# rubric_version staleness: WARN if older than this many days.
_RUBRIC_VERSION_STALE_DAYS = 180

# rubric_version family divergence: WARN if spread across members exceeds this many days.
_RUBRIC_VERSION_DIVERGENCE_DAYS = 90


def _require_yaml() -> Any:
    if yaml is not None:
        return yaml
    raise RuntimeError(
        "PyYAML is required for validate_skill_authoring_family_benchmarks.py. "
        "Run through bash Infrastructure/scripts/run-infrastructure-python.sh ..."
    ) from _YAML_IMPORT_ERROR


# Optional contract fields expected at gold standard; absence produces WARN (not FAIL).
_RECOMMENDED_CONTRACT_KEYS = {"rollback_procedure", "observability"}

# Family members that must apply context disposition via progressive disclosure.
_RELOCATION_GUARD_SKILLS = {
    "plugins/skill-factory/skills/skill-factory-router",
}

_CONTEXT_POLICY_PATTERNS = (
    re.compile(r"never drop required context", re.IGNORECASE),
    re.compile(r"required operational context is never removed", re.IGNORECASE),
    re.compile(r"preserve .*context.*relocat", re.IGNORECASE),
    re.compile(r"important,? still-valid context", re.IGNORECASE),
    re.compile(r"stale, duplicated, unsafe, inappropriate, superseded, or low-signal", re.IGNORECASE),
    re.compile(r"removed context.*disposition", re.IGNORECASE),
)

_HARNESS_CACHE_SCOPE_PATTERN = re.compile(
    r"^plugins/cache/agent-skills-local/harness-engineering/[^/]+/skills/([^/]+)$",
    re.IGNORECASE,
)


def _normalize_scope_alias(scope: str) -> str:
    """Normalize known path aliases into canonical scope taxonomy strings."""
    normalized = scope.strip().strip("/").replace("\\", "/")
    harness_match = _HARNESS_CACHE_SCOPE_PATTERN.match(normalized)
    if harness_match:
        return f"product/ops/{harness_match.group(1)}"
    return normalized


@lru_cache(maxsize=1)
def _load_scope_skill_resolver() -> Any:
    """
    Load and return a scope-skill resolver function from the skill builder's inventory script.

    Attempts to import `scripts/skill_graph_inventory.py` under the configured skill-builder root and extract a callable named `resolve_scope_skill_for_path`. Does not raise on import or execution errors; failures result in `None`.

    Returns:
        Callable[[str], str] or None: The `resolve_scope_skill_for_path` function if present and callable, `None` otherwise.
    """
    resolver_path = _SKILL_BUILDER_ROOT / "scripts" / "skill_graph_inventory.py"
    if not resolver_path.exists():
        return None
    module_name = "skill_graph_inventory_shared_resolver"
    spec = importlib.util.spec_from_file_location(module_name, resolver_path)
    if spec is None or spec.loader is None:
        return None
    try:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        resolver = getattr(module, "resolve_scope_skill_for_path", None)
        return resolver if callable(resolver) else None
    except Exception:  # noqa: BLE001
        # Syntax/import errors in skill_graph_inventory.py should not abort the benchmark;
        # gracefully degrade and use fallback scope resolution.
        return None


def _resolve_scope_skill_for_path(relative_skill_dir: str) -> str:
    """Resolve semantic scope taxonomy for a repo-relative skill path."""
    resolver = _load_scope_skill_resolver()
    if resolver is not None:
        try:
            resolved = _normalize_scope_alias(str(resolver(relative_skill_dir)))
            if resolved:
                return resolved
            raise RuntimeError(f"scope resolver returned empty scope for {relative_skill_dir}")
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"scope resolver failed for {relative_skill_dir}: {exc}") from exc
    return _normalize_scope_alias(relative_skill_dir)


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    skill: str
    message: str


def _load_yaml(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        obj = yaml.safe_load(text)
    else:
        obj = _load_yaml_with_ruby(path, text)
    if not isinstance(obj, dict):
        raise ValueError("expected a YAML mapping/object")
    return obj


def _load_yaml_with_ruby(path: Path, text: str) -> Dict[str, Any]:
    code = (
        "require 'yaml'; require 'json'; "
        "print JSON.generate(YAML.safe_load(STDIN.read, permitted_classes: [], aliases: true))"
    )
    try:
        process = subprocess.run(
            ["ruby", "-e", code],
            input=text,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except FileNotFoundError:
        _require_yaml()
    except subprocess.TimeoutExpired as exc:
        raise ValueError(f"{path} ruby YAML fallback timed out") from exc
    if process.returncode != 0:
        raise ValueError(process.stderr.strip())
    obj = json.loads(process.stdout)
    if not isinstance(obj, dict):
        raise ValueError("expected a YAML mapping/object")
    return obj


def _load_json(path: Path) -> Dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("expected a JSON object")
    return obj


def _skill_markdown_body(raw: str) -> str:
    """
    Extract the body of a SKILL.md file by removing leading YAML frontmatter if present.

    Parameters:
        raw (str): The full SKILL.md content.

    Returns:
        str: The markdown content after the closing frontmatter marker `---` if a leading YAML frontmatter block exists; otherwise the original `raw` text.
    """
    # Strip optional BOM/leading whitespace
    stripped = raw.lstrip('\ufeff \t')

    # Check if file starts with frontmatter delimiter
    if not stripped.startswith('---\n') and not stripped.startswith('---\r\n'):
        return raw

    # Find the closing delimiter on its own line
    lines = stripped.split('\n')
    for i in range(1, len(lines)):
        line = lines[i].rstrip('\r')
        if line == '---':
            # Found closing delimiter, return content after it
            return '\n'.join(lines[i+1:])

    # No closing delimiter found, return original
    return raw


def _load_schema(schema_path: Path) -> Any:
    """
    Load a YAML schema file from the given path and return its parsed contents or `None` if the file is absent.

    Parameters:
        schema_path (Path): Filesystem path to the schema file.

    Returns:
        The parsed YAML schema as a Python object, or `None` if the file does not exist.
    """
    if not schema_path.exists():
        return None
    try:
        yaml_module = _require_yaml()
        return yaml_module.safe_load(schema_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _validate_with_schema(
    skill_rel: str,
    data: Dict[str, Any],
    schema_path: Path,
    fail_code: str,
    context: str,
) -> List[Finding]:
    """Validate *data* against a JSON Schema YAML file using jsonschema.

    Returns a FAIL finding for each schema violation, or a WARN if jsonschema
    is not installed (soft dependency so CI without the package still runs).
    """
    findings: List[Finding] = []
    if not _JSONSCHEMA_AVAILABLE:
        findings.append(
            Finding(
                "WARN",
                f"{fail_code}_NO_JSONSCHEMA",
                skill_rel,
                f"jsonschema not installed; skipping schema validation for {context}. "
                "Install via: uv pip install jsonschema (or run with `uv run --python 3.12 --with jsonschema ...`).",
            )
        )
        return findings

    schema = _load_schema(schema_path)
    if schema is None:
        findings.append(
            Finding(
                "WARN",
                f"{fail_code}_SCHEMA_MISSING",
                skill_rel,
                f"schema file not found at {schema_path.relative_to(REPO_ROOT)}; "
                "skipping JSON Schema validation",
            )
        )
        return findings

    import jsonschema as _js  # type: ignore  # noqa: PLC0415

    validator_cls = _js.Draft202012Validator
    try:
        validator_cls.check_schema(schema)
    except _js.SchemaError as exc:  # noqa: BLE001
        findings.append(
            Finding("WARN", f"{fail_code}_SCHEMA_INVALID", skill_rel, f"schema file is invalid: {exc.message}")
        )
        return findings

    for error in sorted(validator_cls(schema).iter_errors(data), key=lambda e: list(e.path)):
        path = " > ".join(str(p) for p in error.path) if error.path else "(root)"
        findings.append(
            Finding("FAIL", fail_code, skill_rel, f"{context} schema violation at {path}: {error.message}")
        )

    return findings


def _normalize_skill_name(skill_dir: Path) -> str:
    return skill_dir.name


def _canonical_skill_rel(skill_rel: str) -> str:
    """Return canonical repo-relative skill path for the given relative path."""
    repo_root = REPO_ROOT.resolve()
    requested = (repo_root / skill_rel).resolve()
    try:
        return requested.relative_to(repo_root).as_posix()
    except ValueError:
        return skill_rel.strip("/")


def _dedupe_requested_skills(skills: Sequence[str]) -> tuple[str, ...]:
    """Deduplicate requested skills by canonical resolved path while preserving order."""
    seen: set[str] = set()
    deduped: list[str] = []
    for skill in skills:
        canonical = _canonical_skill_rel(skill)
        if canonical in seen:
            continue
        seen.add(canonical)
        deduped.append(skill)
    return tuple(deduped)


def _case_has_pi_language(case: Dict[str, Any]) -> bool:
    haystacks = [str(case.get("name", "")), str(case.get("prompt", ""))]
    low = "\n".join(haystacks).lower()
    return any(token in low for token in ("prompt injection", "jailbreak", "ignore previous instructions", "bypass safety"))


def _case_forbidden_commands(case: Dict[str, Any]) -> Set[str]:
    deterministic = case.get("deterministic_checks")
    if not isinstance(deterministic, dict):
        return set()
    raw = deterministic.get("forbidden_commands")
    if not isinstance(raw, list):
        return set()
    out: Set[str] = set()
    for item in raw:
        if isinstance(item, str) and item.strip():
            out.add(item.strip().lower())
    return out


def _validate_contract(skill_rel: str, skill_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    contract_path = skill_dir / "references" / "contract.yaml"
    if not contract_path.exists():
        findings.append(Finding("FAIL", "CONTRACT_MISSING", skill_rel, "missing references/contract.yaml"))
        return findings

    try:
        contract = _load_yaml(contract_path)
    except Exception as exc:  # noqa: BLE001
        findings.append(Finding("FAIL", "CONTRACT_PARSE", skill_rel, f"could not parse contract.yaml: {exc}"))
        return findings

    missing = sorted(REQUIRED_CONTRACT_KEYS - set(contract.keys()))
    if missing:
        findings.append(
            Finding("FAIL", "CONTRACT_KEYS", skill_rel, f"contract.yaml missing required keys: {', '.join(missing)}")
        )

    schema_version = str(contract.get("schema_version", "")).strip()
    if not schema_version:
        findings.append(Finding("FAIL", "CONTRACT_SCHEMA_VERSION", skill_rel, "contract.yaml missing schema_version"))

    # P2.5: Gold-standard recommended fields (WARN, not FAIL)
    missing_recommended = sorted(_RECOMMENDED_CONTRACT_KEYS - set(contract.keys()))
    if missing_recommended:
        findings.append(
            Finding(
                "WARN",
                "CONTRACT_RECOMMENDED_KEYS",
                skill_rel,
                f"contract.yaml missing recommended gold-standard keys: {', '.join(missing_recommended)} "
                "(add rollback_procedure and observability for operational readiness)",
            )
        )

    # Item 3: JSON Schema structural validation
    findings.extend(_validate_with_schema(skill_rel, contract, _CONTRACT_SCHEMA_PATH, "CONTRACT_SCHEMA", "contract.yaml"))

    return findings
__all__ = [name for name in globals() if not name.startswith("__")]
