from __future__ import annotations

from .evals_core import *  # noqa: F403


def _tessl_staging_root_template() -> str:
    """Return the human-readable template for stable Tessl eval staging."""
    return str(Path(tempfile.gettempdir()) / "ask-tessl-evals" / "<skill-path>-<sha12>")


def _tessl_live_staging_root_template() -> str:
    """Return the human-readable template for private Tessl live tile staging."""
    return str(Path(tempfile.gettempdir()) / "ask-tessl-evals-live" / "<skill-path>-<sha12>")


def _tessl_policy() -> dict:
    """Return the repo's Tessl safety contract for eval runs."""
    return {
        "native_tessl_only": True,
        "no_npx": True,
        "no_publish": True,
        "no_registry_upload": True,
        "temp_staged_project_input_only": True,
        "stable_staging_root": _tessl_staging_root_template(),
        "evidence_retention": "stable tmp staging is intentionally left for post-run inspection; reruns archive previous staged evidence under evidence-archive/",
        "tessl_project_marker": "tessl.json",
        "staged_inputs": [
            "SKILL.md",
            "references/evals.yaml",
            "references/contract.yaml",
            "references/task-profile.json",
            "assets/**/*",
            "evals/<case-id>/task.md",
            "evals/<case-id>/criteria.json",
        ],
        "network_permission_required_by_repo": False,
        "project_save_may_use_tessl_service": "only_for_project_link_when_workspace_provided",
        "project_save_default": "compatibility_flag_not_required",
        "project_identity_rule": "plugin skills use the plugin project name; standalone skills use the skill name",
        "project_link_check": "when --tessl-workspace is provided, repair/link existing project first and create only when needed",
    }


def _tessl_live_private_policy(workspace: str | None = None) -> dict:
    """Return the repo's opt-in private Tessl plugin eval contract."""
    return {
        "enabled_by": "--tessl-live-private",
        "visibility": "private",
        "plugin_private_required": True,
        "workspace_required": True,
        "workspace": workspace,
        "tile_name_format": "workspace/tile-name",
        "project_identity_rule": "plugin skills use the plugin project name; standalone skills use the skill name",
        "project_link_check": "repair/link existing project first and create only when needed",
        "native_tessl_only": True,
        "no_npx": True,
        "no_install": True,
        "no_publish": True,
        "no_registry_upload": True,
        "temp_staged_plugin_input_only": True,
        "stable_staging_root": _tessl_live_staging_root_template(),
        "evidence_retention": "stable tmp staging is intentionally left for post-run inspection; reruns archive previous staged evidence under evidence-archive/",
        "tessl_project_marker": "tessl.json",
        "plugin_manifest": ".tessl-plugin/plugin.json",
        "eval_layout": "evals/<case-id>/{task.md,criteria.json}",
        "staged_inputs": [
            ".tessl-plugin/plugin.json",
            "tessl.json",
            "skills/<skill-name>/SKILL.md",
            "skills/<skill-name>/references/evals.yaml",
            "skills/<skill-name>/references/evals/*.md",
            "skills/<skill-name>/references/eval-scenarios.json",
            "skills/<skill-name>/references/contract.yaml",
            "skills/<skill-name>/references/task-profile.json",
            "skills/<skill-name>/references/**/*",
            "skills/<skill-name>/assets/**/*",
            "evals/<case-id>/task.md",
            "evals/<case-id>/criteria.json",
        ],
        "command_shape": "tessl eval run --json --workspace <workspace> <staged-plugin-dir>",
        "scenario_gate": "skill-owned references/evals.yaml plus reviewed generated scenarios are required before live scoring; behavioral skills need 5 to 10 gold-standard scenarios with 8 as the target; structure-only checks must opt out explicitly",
        "min_scenarios_required": TESSL_LIVE_PRIVATE_MIN_SCENARIOS,
        "target_scenarios": TESSL_LIVE_PRIVATE_TARGET_SCENARIOS,
        "max_scenarios_default": TESSL_LIVE_PRIVATE_MAX_SCENARIOS,
        "scenario_count_policy": (
            "Declare one 5-to-10-case release set, targeting 8 distinct high-value scenarios. "
            "oss-local authors and proves it first; oss-cloud must prove the same case ids; "
            "Tessl dry-run and external evaluation must preserve that exact set."
        ),
        "oss_cloud_alignment_policy": (
            "oss-cloud is the Tessl rehearsal lane and must prove the same case "
            "set Tessl live will upload, not a looser subset or wider historical "
            "ledger."
        ),
        "generated_scenario_policy": (
            "generated-eval.* scenarios are blocked from Tessl live by default "
            "unless a later budgeted lane explicitly opts them in with OSS local "
            "and cloud proof plus cost profile evidence."
        ),
        "expected_variants": ["baseline", "usage-spec"],
        "duplicate_run_guard": "before live scoring, block when a pending eval run already exists for the same workspace/project",
        "pre_tessl_feedback_loop": {
            "required_order": [
                "mechanical_validation",
                "security_risk_modes",
                "scenario_quality",
                "scorer_quality",
                "scorer_calibration",
                "deterministic_local_gates",
                "oss_local_internal_judge",
                "patch_oss_local_failures",
                "oss_cloud_internal_judge",
                "patch_oss_cloud_failures",
                "tessl_local_proof",
                "tessl_live_dry_run",
                "tessl_live_run",
                "patch_tessl_failures",
            ],
            "deterministic_local_gates": [
                "skills audit",
                "sdk eval regression-plan when prior Tessl or internal judge regressions exist",
            ],
            "mechanical_validation": ["skills audit", "skills package verify"],
            "security_risk_modes": ["sdk security risk-modes --preview"],
            "scenario_quality": ["sdk eval scenario-quality --preview"],
            "scorer_quality": ["sdk eval scorer-quality --preview"],
            "scorer_calibration": ["sdk eval scorer-calibration --preview"],
            "internal_judge_sequence": [
                {
                    "profile": "oss-local",
                    "role": "cheap internal remediation judge",
                    "required_before": "oss-cloud",
                    "failure_rule": "owner-classify failures in their source lane; rerun oss-local only when classification shows a local skill regression",
                },
                {
                    "profile": "oss-cloud",
                    "role": "higher-confidence internal remediation judge",
                    "required_before": "tessl_live_dry_run",
                    "failure_rule": "owner-classify failures in their source lane; rerun oss-local only when classification shows a local skill regression",
                },
            ],
            "tessl_sequence": [
                {
                    "stage": "tessl_local_proof",
                    "role": "local Tessl lint, pack, temp install, and optional review proof before staged external scoring",
                },
                {
                    "stage": "tessl_live_dry_run",
                    "role": "package and scenario staging proof before external scoring",
                },
                {
                    "stage": "tessl_live_run",
                    "role": "external confirmation lane after internal judges pass",
                },
            ],
            "failure_loop": "Any oss-local, oss-cloud, Tessl local-proof, dry-run, or live Tessl failure stays in its source lane until owner classification identifies the repair surface; rerun oss-local only for classified local skill regressions.",
            "live_blocked_until": "deterministic gates, oss-local, oss-cloud, Tessl local-proof, and Tessl dry-run all pass for the current candidate or an explicit skip/blocker receipt is recorded.",
        },
        "model_selection_gate": {
            "quality_floor_before_cost": True,
            "cost_is_secondary_to_score": True,
            "required_summary_fields": [
                "model_selection",
                "comparative_quality",
                "cost_observability",
            ],
            "acceptance": "with-skill score must meet the quality floor and beat baseline before model cost can be treated as a selection advantage",
        },
        "cost_observability": {
            "track_turns_when_available": True,
            "track_tokens_when_available": True,
            "track_cost_when_available": True,
            "missing_metrics_are_explicit": True,
            "pre_live_budget_receipt": "skills-sdk.tessl-live-budget-preflight.v1",
            "expected_model_tasks": "scenario_count * 2 variants * (solve + score)",
        },
        "run_limit_policy": {
            "workspace_run_limit": TESSL_WORKSPACE_RUN_LIMIT,
            "limit_source": TESSL_WORKSPACE_RUN_LIMIT_SOURCE,
            "reserve_runs": TESSL_WORKSPACE_RUN_RESERVE,
            "verification_commands": [
                "tessl eval list --json --workspace <workspace>",
                "tessl eval view --json <run-id>",
            ],
            "preflight": "before live scoring, check remaining Tessl workspace run capacity when the API/list surface is available; otherwise use the operator-provided 300-run cap and preserve reserve for rerun/remediation",
            "block_when": "remaining run capacity cannot be checked and the run is nonessential, or known remaining capacity is at/below reserve; use dry-run staging and local scenario gates instead",
        },
        "readiness_gate": "after run completion, fetch tessl eval view --json and require usage score >= 90% and usage score > baseline; 95% remains the target",
        "min_score_required": TESSL_LIVE_PRIVATE_MIN_SCORE,
        "target_score": TESSL_LIVE_PRIVATE_TARGET_SCORE,
        "usage_data_opt_out": "tessl config set shareUsageData false",
    }


def _tessl_live_handoff_readiness(repo_root: Path, skill_path: str) -> dict:
    from ask.skills_sdk.handoff_readiness import build_handoff_readiness_receipt  # noqa: PLC0415

    return build_handoff_readiness_receipt(
        repo_root,
        source_path=repo_root / skill_path,
        query=skill_path,
    )


def _tessl_dry_run_admission(repo_root: Path, skill_path: str) -> dict:
    from ask.skills_sdk.handoff_readiness import build_tessl_dry_run_admission  # noqa: PLC0415

    return build_tessl_dry_run_admission(
        repo_root,
        source_path=repo_root / skill_path,
        query=skill_path,
    )


def _tessl_scenario_generation_root_template() -> str:
    """Return the human-readable template for Tessl scenario-generation staging."""
    return str(Path(tempfile.gettempdir()) / "ask-tessl-scenario-generation" / "<skill-path>-<sha12>")


def _tessl_scenario_generation_policy(workspace: str | None = None) -> dict:
    """Return the repo's Tessl scenario-generation safety contract."""
    return {
        "enabled_by": "ask evals prepare-tessl-scenarios",
        "purpose": "stage a target tile and, only when explicitly requested, install Tessl's public scenario-generation skill without installing Tessl state into the repo root",
        "default_mode": "staging_only",
        "execution_requires": "--execute",
        "agent_must_generate_scenarios_after_prepare": True,
        "workspace_required": True,
        "workspace": workspace,
        "project_identity_rule": "plugin skills use the plugin project name; standalone skills use the skill name",
        "project_link_check": "repair/link existing project first and create only when needed",
        "scenario_tool_tile": TESSL_SCENARIO_TOOL_TILE,
        "scenario_tool_version": TESSL_SCENARIO_TOOL_VERSION,
        "allowed_install": f"{TESSL_SCENARIO_TOOL_TILE}@{TESSL_SCENARIO_TOOL_VERSION}",
        "allowed_install_scope": "temp tool project only",
        "native_tessl_only": True,
        "no_npx": True,
        "no_repo_root_install": True,
        "no_publish": True,
        "no_registry_upload": True,
        "temp_staged_tile_input_only": True,
        "stable_staging_root": _tessl_scenario_generation_root_template(),
        "evidence_retention": "stable tmp staging is intentionally left for post-run inspection; reruns archive previous staged evidence under evidence-archive/",
        "target_tile": "target-tile",
        "tool_project": "tool-project",
        "scenario_skill_path": ".tessl/plugins/tessl-labs/tessl-skill-eval-scenarios/creating-eval-scenarios/SKILL.md",
        "legacy_scenario_skill_path": ".tessl/tiles/tessl-labs/tessl-skill-eval-scenarios/creating-eval-scenarios/SKILL.md",
        "scenario_reference_path": ".tessl/plugins/tessl-labs/tessl-skill-eval-scenarios/creating-eval-scenarios/references/scenario-generation.md",
        "legacy_scenario_reference_path": ".tessl/tiles/tessl-labs/tessl-skill-eval-scenarios/creating-eval-scenarios/references/scenario-generation.md",
        "generated_output": "target-tile/evals/",
        "canonical_import_target": "references/evals.yaml plus references/evals/*.md after review",
        "live_eval_gate": "the later --tessl-live-private lane stages only reviewed canonical skill assets; generate and import bespoke scenarios before running it",
    }


TESSL_STAGING_IGNORED_NAMES = {".DS_Store"}
TESSL_STAGING_IGNORED_DIRS = {"__MACOSX", ".AppleDouble"}

__all__ = [name for name in globals() if not name.startswith("__")]
