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
    """
    Load and parse the eval report JSON contract, using the local contract file when present and falling back to the shared contract file otherwise.
    
    Selects LOCAL_CONTRACT_PATH if it exists; otherwise selects SHARED_CONTRACT_PATH and parses its UTF-8 contents as JSON.
    
    Returns:
        dict[str, Any]: The parsed JSON contract as a dictionary.
    """
    contract_path = LOCAL_CONTRACT_PATH if LOCAL_CONTRACT_PATH.exists() else SHARED_CONTRACT_PATH
    return json.loads(contract_path.read_text(encoding="utf-8"))


def contract_list(key: str) -> list[str]:
    """
    Retrieve a list of string values from the loaded eval report contract for the specified key.
    
    Parameters:
        key (str): Name of the contract field to retrieve.
    
    Returns:
        list[str]: The field's values converted to strings.
    
    Raises:
        TypeError: If the contract field exists but is not a list.
    """
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
