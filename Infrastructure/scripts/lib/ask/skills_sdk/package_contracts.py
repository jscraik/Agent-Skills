"""Stable public facade for Skills SDK package-contract helpers.

The implementation is deliberately divided by contract concern. This module
retains the historic import surface and patch seams used by callers.
"""
from __future__ import annotations

from . import package_contracts_assembly as _assembly
from . import package_contracts_common as _common
from . import package_contracts_parsing as _parsing
from . import package_contracts_readiness as _readiness
from .package_contracts_common import *  # noqa: F403
from .package_contracts_parsing import *  # noqa: F403
from .package_contracts_assets import *  # noqa: F403
from .package_contracts_workflow import *  # noqa: F403
from .package_contracts_optimization import *  # noqa: F403
from .package_contracts_reference_quality import *  # noqa: F403
from .package_contracts_writing_support import *  # noqa: F403
from .package_contracts_writing_quality import *  # noqa: F403
from .package_contracts_platform import *  # noqa: F403
from .package_contracts_assembly import *  # noqa: F403
from .package_contracts_readiness import *  # noqa: F403

# These module attributes are intentionally public: existing callers and
# tests patch them to exercise the optional YAML and Ruby parsing paths.
yaml = _common.yaml
subprocess = _common.subprocess


def _sync_parser_state() -> None:
    _common.yaml = yaml
    _parsing.yaml = yaml


def read_agents_openai_yaml_fields(skill_md):
    _sync_parser_state()
    return _parsing.read_agents_openai_yaml_fields(skill_md)


def read_reference_contract(skill_md):
    _sync_parser_state()
    return _parsing.read_reference_contract(skill_md)


def read_structured_reference(path):
    _sync_parser_state()
    return _parsing.read_structured_reference(path)


def sdk_package_contract(repo_root, source_path, frontmatter):
    _sync_parser_state()
    return _assembly.sdk_package_contract(repo_root, source_path, frontmatter)


def skill_package_contract(repo_root, source_path, frontmatter):
    _sync_parser_state()
    return _assembly.skill_package_contract(repo_root, source_path, frontmatter)


def skill_package_readiness(frontmatter, repo_root=None, source_path=None):
    previous = _readiness.sdk_package_contract
    _readiness.sdk_package_contract = sdk_package_contract
    try:
        return _readiness.skill_package_readiness(frontmatter, repo_root, source_path)
    finally:
        _readiness.sdk_package_contract = previous
