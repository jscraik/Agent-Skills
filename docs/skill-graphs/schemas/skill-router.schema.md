# Skill Router Output Schema (v1.0)

## Table of Contents
- [Overview](#overview)
- [Required fields](#required-fields)
- [Forbidden fields](#forbidden-fields)
- [Candidate schema](#candidate-schema)
- [Policy contract](#policy-contract)

## Overview
Versioned schema for deterministic skill-routing output consumed by humans and agents.

## Required fields
- `schema_version` (string)
- `catalog_version` (string)
- `actor_type` (`human | agent`)
- `policy_mode` (`observe_only | co_pilot | autopilot`)
- `policy_decision` (`suggest | suggest_only | clarify | confirmation_required | auto_select_top1`)
- `requires_clarification` (boolean)
- `prompt_hash` (string SHA-256)
- `uncertainty_reasons` (string[])
- `top_candidates` (array)

## Forbidden fields
These must never appear in payloads:
- `prompt`
- `prompt_text`
- `objective`
- `objective_text`
- `raw_input`
- `raw_prompt`

## Candidate schema
Each candidate in `top_candidates` includes:
- `skill_name` (string)
- `skill_path` (string)
- `confidence` (number, 0-1)
- `confidence_band` (`high | medium | low`)
- `risk_tier` (`low | medium | high`)
- `rationale` (string[])

## Policy contract
- Agents default to safe behavior (`observe_only`) unless explicitly elevated.
- Non-low-risk candidates cannot auto-run in agent mode.
- Low-confidence routes must set `requires_clarification=true`.
- Actor thresholds (v1 calibration):
  - human: `clarify_max=0.60`
  - agent: `confirm_min=0.70`, `autopilot_min=0.90`
