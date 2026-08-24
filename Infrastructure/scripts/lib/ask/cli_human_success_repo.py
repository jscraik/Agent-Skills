"""Human output renderers for successful repository commands."""

from types import MappingProxyType

from ask.cli_output import print_first_validation_command
from ask.golden_path import render_golden_path_summary


def _render_status(_args, result):
    print(f"✅ Success: {result.metadata['command']}")
    print(f"  Root: {result.data['repo_root']}")
    print(f"  Synced: {result.data['skills_synced']}")
    print_first_validation_command(result.data)


def _render_validate(_args, result):
    print(f"✅ Validation passed! ({result.data['warn_only_issues']} warnings)")
    if result.data.get("scope") and result.data.get("scope") != "all":
        print(f"   Scope: {result.data['scope']}")
    if result.data.get("changed_files"):
        print(f"   Scoped to {len(result.data['changed_files'])} changed file(s)")


def _render_check_stability(args, result):
    print(f"✅ Stability check passed ({result.data['stable_count']} stable skills)")
    if args.changed_files:
        print(f"   Checked {result.data['checked_files']} changed file(s)")
    print_first_validation_command(result.data)


def _render_doctor(_args, result):
    doctor = result.data.get("doctor", result.data)
    for line in render_golden_path_summary(
        doctor, title="Repo doctor", status_icon="✅"
    ):
        print(line)
    signals = doctor.get("signals", {})
    capability = signals.get("capability_readiness", {}).get("details", {})
    memory = signals.get("memory_readiness", {}).get("details", {})
    package = signals.get("package_readiness", {}).get("details", {})
    if capability:
        print(
            "  Capability readiness: "
            f"{signals.get('capability_readiness', {}).get('state')} "
            f"({capability.get('profile_contract_gap_count', 0)} profile gaps, "
            f"{capability.get('event_contract_gap_count', 0)} event gaps)"
        )
    if memory:
        print(
            "  Memory readiness: "
            f"{signals.get('memory_readiness', {}).get('state')} "
            f"({memory.get('entry_count', 0)} entries, "
            f"{memory.get('provider_model')})"
        )
    if package:
        print(
            "  Package readiness: "
            f"{signals.get('package_readiness', {}).get('state')} "
            f"({package.get('target')}, "
            f"{package.get('missing_field_count', 0)} missing fields)"
        )


def _render_closeout(_args, result):
    closeout = result.data.get("repo_closeout", {})
    readiness = closeout.get("commit_readiness", {})
    capability = closeout.get("capability_readiness", {})
    memory = closeout.get("memory_readiness", {})
    package = closeout.get("package_readiness", {})
    runtime_evidence = closeout.get("runtime_evidence", {})
    print(f"Repo closeout: {closeout.get('agent_summary')}")
    print(f"  Commit ready: {readiness.get('ready')}")
    print(
        f"  Capability readiness: {capability.get('status')} ({capability.get('contract_gap_count', 0)} gaps)"
    )
    _render_eval_blocker_classes(capability)
    print(
        f"  Memory readiness: {memory.get('status')} ({memory.get('entry_count', 0)} entries)"
    )
    print(
        f"  Package readiness: {package.get('status')} ({package.get('missing_field_count', 0)} missing fields)"
    )
    print(
        f"  Runtime evidence: {runtime_evidence.get('status')} ({runtime_evidence.get('runtime_card_count', 0)} cards)"
    )
    _render_runtime_boundaries(runtime_evidence)
    _render_focused_validation(closeout.get("focused_validation", []))
    print(f"  Next: {closeout.get('next_command')}")


def _render_eval_blocker_classes(capability):
    blocker_classes = capability.get("eval_blocker_classes") or []
    if blocker_classes:
        count = capability.get("eval_blocker_class_count", len(blocker_classes))
        print(f"  Eval blocker classes: {count} ({', '.join(blocker_classes)})")


def _render_runtime_boundaries(runtime_evidence):
    boundaries = runtime_evidence.get("truth_boundaries") or {}
    if boundaries:
        values = [
            f"{name}={boundaries.get(key)}"
            for name, key in (
                ("command", "command_proof"),
                ("schema", "schema_proof"),
                ("PR", "pr_truth"),
                ("tracker", "tracker_truth"),
                ("docs", "docs_truth"),
            )
        ]
        print(f"  Runtime evidence boundaries: {', '.join(values)}")


def _render_focused_validation(focused):
    ids = [item.get("id") for item in focused if item.get("id")]
    if ids:
        print(f"  Focused validation: {', '.join(ids)}")


def _render_doctor_catalog(_args, result):
    report = result.data.get("catalog_parity", {})
    print(f"✅ Catalog parity: {report.get('decision_status', 'resolved')}")
    print(f"  Canonical count: {report.get('canonical_count')}")
    print(f"  Policy identity: {report.get('policy_identity')}")
    for surface in report.get("surfaces", []):
        print(
            "  - "
            f"{surface.get('surface_name')}: "
            f"{surface.get('observed_count')} / {surface.get('canonical_count')} "
            f"(parity_ok={surface.get('parity_ok')})"
        )


def _render_provider_audit(_args, result):
    report = result.data.get("provider_policy", {})
    print(
        "✅ Provider policy: "
        f"{report.get('status')} ({report.get('violation_count', 0)} violation(s))"
    )
    print_first_validation_command(result.data)


def _render_surface(_args, result):
    report = result.data.get("repo_surface", {})
    summary = report.get("summary", {})
    print(
        f"✅ Repo surface: {summary.get('total_paths', 0)} tracked path(s), "
        f"{summary.get('blocking_findings', 0)} blocking finding(s), "
        f"status={report.get('status')}"
    )
    print_first_validation_command(result.data)


def _render_yaml_inspect(args, result):
    payload = result.data.get("yaml", {})
    detail = _yaml_detail(payload)
    print(
        f"✅ YAML inspect: {result.data.get('path', payload.get('path', args.path))}{detail}"
    )
    print_first_validation_command(result.data)


def _yaml_detail(payload):
    if payload.get("query"):
        return f" query={payload.get('query')} value={payload.get('query_value')!r}"
    values = (
        f"{name}={payload.get(name)}"
        for name in ("root_type", "top_level_keys", "item_count")
        if payload.get(name) is not None
    )
    return " " + " ".join(values)


_REPO_ACTIONS = MappingProxyType(
    {
        "status": _render_status,
        "validate": _render_validate,
        "check-stability": _render_check_stability,
        "doctor": _render_doctor,
        "closeout": _render_closeout,
        "doctor-catalog": _render_doctor_catalog,
        "provider-audit": _render_provider_audit,
        "surface": _render_surface,
        "yaml-inspect": _render_yaml_inspect,
    }
)


def render_repo_success(args, result):
    renderer = _REPO_ACTIONS.get(args.action)
    if renderer is None:
        return False
    renderer(args, result)
    return True
