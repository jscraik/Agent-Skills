"""Single-source contract values for HE eval report validation."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


LOCAL_CONTRACT_PATH = Path(__file__).resolve().parents[1] / "references" / "eval-report-schema.json"
SHARED_CONTRACT_PATH = (
    Path(__file__).resolve().parents[3]
    / "references"
    / "skills"
    / "he-eval-report"
    / "eval-report-schema.json"
)


@lru_cache(maxsize=1)
def load_contract() -> dict[str, Any]:
    contract_path = LOCAL_CONTRACT_PATH if LOCAL_CONTRACT_PATH.exists() else SHARED_CONTRACT_PATH
    return json.loads(contract_path.read_text(encoding="utf-8"))


def contract_list(key: str) -> list[str]:
    value = load_contract()[key]
    if not isinstance(value, list):
        raise TypeError(f"eval report contract field is not a list: {key}")
    return [str(item) for item in value]


REQUIRED_SECTIONS = contract_list("required_sections")
LINEAR_FIELDS = contract_list("linear_fields")
GATE_FIELDS = contract_list("gate_fields")
DRIFT_AREAS = contract_list("drift_areas")
DRIFT_VALUES = set(contract_list("drift_values"))
RECOMMENDATIONS = set(contract_list("recommendations"))
AGENTIC_EVAL_FIELDS = contract_list("agentic_eval_fields")
SIDE_EFFECT_AUTHORIZATION_FIELDS = contract_list("side_effect_authorization_fields")
VALIDATOR_DECISIONS = set(contract_list("side_effect_validator_decisions"))
VALIDATOR_CONFIDENCE_VALUES = set(contract_list("side_effect_validator_confidence_values"))
YES_NO_VALUES = set(contract_list("yes_no_values"))
