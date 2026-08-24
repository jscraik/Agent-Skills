"""Human output renderers for successful skills commands."""

from types import MappingProxyType

import ask.commands.skills as skills_commands
from ask.cli_output import print_first_validation_command, print_readiness_overview


def _render_list(_args, result):
    print(f"Discovered {len(result.data['skills'])} skills:")
    for skill in result.data["skills"]:
        print(f"  - {skill['name']} [{skill['category']}]")
    if result.data.get("policy_identity"):
        print(f"Policy identity: {result.data['policy_identity']}")
    if result.data.get("advanced_mode"):
        print("Advanced mode: visible")
    if result.data.get("starter_mode"):
        print(
            f"Starter mode: archetype={result.data.get('starter_archetype')} "
            f"limit={result.data.get('starter_limit')}"
        )
    print_first_validation_command(result.data)


def _render_budget(_args, result):
    report = result.data.get("runtime_budget", {})
    print(
        "✅ Runtime budget: "
        f"{report.get('default_visible_count')}/{report.get('default_visible_max')} default skills, "
        f"{report.get('advanced_visible_count')} advanced"
    )
    print_first_validation_command(report)


def _render_capability_preview(args, result):
    payload = (
        result.data.get("codex_preview", {})
        if args.action == "codex-preview"
        else result.data.get("capability_discovery", {})
    )
    lines = (
        skills_commands.format_codex_preview_human(payload)
        if args.action == "codex-preview"
        else skills_commands.format_capabilities_human(payload)
    )
    print("\n".join(lines))


def _render_load_preview(_args, result):
    preview = result.data.get("codex_load_preview", {})
    print(
        "Codex load preview: "
        f"{preview.get('skill_count', 0)} skill(s), status={preview.get('status')}"
    )
    if preview.get("blocked_checks"):
        print(f"Blocked fidelity checks: {len(preview.get('blocked_checks', []))}")
    print_first_validation_command(preview)


def _render_render_preview(_args, result):
    preview = result.data.get("codex_render_preview", {})
    rendered = preview.get("rendered", {})
    report = rendered.get("report", {})
    print(
        "Codex render preview: "
        f"{report.get('included_count', 0)}/{report.get('total_count', 0)} skill(s), "
        f"status={preview.get('status')}"
    )
    if rendered.get("warning_message"):
        print(f"Warning: {rendered.get('warning_message')}")
    print_first_validation_command(preview)


def _render_config(_args, result):
    preview = result.data.get("codex_config_explain", {})
    print(f"Codex config explain: status={preview.get('status')}")
    contract = preview.get("config_contract", {})
    if contract.get("selector_policy"):
        print(f"Selector policy: {contract.get('selector_policy')}")
    print_first_validation_command(preview)


def _render_inject_preview(_args, result):
    preview = result.data.get("codex_inject_preview", {})
    print(
        "Codex inject preview: "
        f"{preview.get('selected_count', 0)} selected, status={preview.get('status')}"
    )
    print_first_validation_command(preview)


def _render_implicit_preview(_args, result):
    preview = result.data.get("codex_implicit_preview", {})
    print(
        "Codex implicit preview: "
        f"{preview.get('attribution_status')}, status={preview.get('status')}"
    )
    print_first_validation_command(preview)


def _render_handles(_args, result):
    surface = result.data.get("sdk_handles", {})
    print(
        "✅ Skill targets: "
        f"{surface.get('handle_count', 0)} target(s), status={surface.get('status')}"
    )
    if result.data.get("policy_identity"):
        print(f"  Policy identity: {result.data['policy_identity']}")
    print_first_validation_command(surface)
    violations = surface.get("violations", [])
    if violations:
        print(f"  Violations: {len(violations)}")


def _render_resolve(_args, result):
    resolution = result.data.get("resolution", {})
    print(f"✅ Skill target: {resolution.get('handle')}")
    print(f"  Runtime visibility: {resolution.get('runtime_visibility')}")
    print(f"  Target source: {resolution.get('handle_source')}")
    print(f"  Source: {resolution.get('source_path')}")
    print_first_validation_command(resolution)


def _render_proof(_args, result):
    proof = result.data.get("proof", {})
    print(f"✅ Skill target proof: {proof.get('handle')} ({proof.get('status')})")
    if proof.get("runtime_satisfied_by"):
        print(f"  runtime satisfied by: {proof.get('runtime_satisfied_by')}")
    required_gates = (proof.get("gate_policy") or {}).get("required") or []
    if required_gates:
        print(f"  required gates: {', '.join(required_gates)}")
    for gate, passed in proof.get("gates", {}).items():
        print(f"  {gate}: {'pass' if passed else 'fail'}")
    live = proof.get("live_runtime_invocation", {})
    if live.get("status"):
        print(f"  live invocation: {live.get('status')}")
    print_first_validation_command(proof)


def _render_prove(_args, result):
    scorecard = result.data.get("skill_proof", {})
    print(f"Skill proof scorecard: ${scorecard.get('handle')}")
    for section in ("reachability", "structural_quality", "analytics", "outcome_proof"):
        payload = scorecard.get(section) or {}
        if payload.get("status"):
            print(f"  {section}: {payload.get('status')}")
    print_first_validation_command(scorecard)
    if scorecard.get("next_command"):
        print(f"Next: {scorecard.get('next_command')}")


def _render_explain(_args, result):
    explanation = result.data.get("explanation", {})
    print(f"ℹ️  Skill: ${explanation.get('handle')} ({explanation.get('status')})")
    print(explanation.get("agent_summary", ""))
    print(f"Source: {explanation.get('canonical_source_path')}")
    print_first_validation_command(explanation)
    print(f"Next: {explanation.get('next_command')}")


def _render_doctor(_args, result):
    doctor = result.data.get("skill_doctor", {})
    print(f"Skill doctor: {doctor.get('query')} ({doctor.get('status')})")
    print(doctor.get("agent_summary", ""))
    print(f"Source: {doctor.get('canonical_source_path')}")
    _render_lifecycle_event(doctor)
    warning_classes = [
        warning.get("class")
        for warning in doctor.get("warnings", [])
        if warning.get("class")
    ]
    if warning_classes:
        print(f"Warning classes: {', '.join(warning_classes)}")
    _render_check_counts(doctor.get("check_summary") or {})
    print_first_validation_command(doctor)
    print(f"Next: {doctor.get('next_command')}")


def _render_lifecycle_event(payload):
    event = payload.get("lifecycle_event") or {}
    if event.get("event_type"):
        print(f"Event: {event.get('event_type')}")


def _render_check_counts(summary):
    counts = summary.get("status_counts") or {}
    if counts:
        print(f"Checks: {', '.join(f'{key}={counts[key]}' for key in sorted(counts))}")


def _render_package(_args, result):
    package = result.data.get("skill_package_verification") or result.data.get(
        "skill_package", {}
    )
    print(f"Skill package: {package.get('query')} ({package.get('status')})")
    print(package.get("agent_summary", ""))
    identity = package.get("target_identity") or {}
    source = (
        identity.get("path")
        or package.get("canonical_source_path")
        or package.get("query")
    )
    print(f"Source: {source}")
    _render_lifecycle_event(package)
    _render_package_contract(package)
    _render_package_gate(package.get("gate_summary", {}))
    print_first_validation_command(package)
    print(f"Next: {package.get('next_command')}")


def _render_package_contract(package):
    contract = package.get("package_contract") or {}
    values = contract.get("values") or {}
    if contract.get("readiness_level"):
        print(f"Readiness level: {contract.get('readiness_level')}")
    if values.get("compatible_roles"):
        print(f"Compatible roles: {', '.join(values.get('compatible_roles'))}")
    if values.get("runtime_needs"):
        print(f"Runtime needs: {len(values.get('runtime_needs'))} declared")
    if values.get("provenance"):
        print(f"Provenance: {values.get('provenance')}")


def _render_package_gate(gate):
    if gate:
        print(f"Install ready: {gate.get('install_ready')}")
        print(f"Checkout test: {gate.get('checkout_test_status')}")
        print(f"Promotion: {gate.get('promotion_status')}")


def _render_conformance(_args, result):
    conformance = result.data.get("skills_conformance", {})
    print(
        f"Skills conformance: {conformance.get('suite')} ({conformance.get('status')})"
    )
    print(conformance.get("agent_summary", ""))
    print(f"Evidence dir: {conformance.get('evidence_dir')}")
    if conformance.get("evidence_jsonl"):
        print(f"Evidence JSONL: {conformance.get('evidence_jsonl')}")
    print(f"Checks: {len(conformance.get('checks') or [])}")
    print_first_validation_command(conformance)
    print(f"Next: {conformance.get('next_command')}")


def _render_profiles(_args, result):
    profiles = result.data.get("skill_profiles", {})
    print(f"Skill profiles: {profiles.get('status')}")
    print(profiles.get("agent_summary", ""))
    print_readiness_overview(profiles)
    print_first_validation_command(profiles)
    _render_selected_profile(profiles)


def _render_selected_profile(profiles):
    profile_map = profiles.get("profiles", {})
    selected = profiles.get("selected_profile")
    if selected and selected in profile_map:
        profile = profile_map[selected]
        print(f"Profile: {selected}")
        print(f"Intent: {profile.get('intent')}")
        print(f"Write policy: {profile.get('write_policy')}")
    elif profiles.get("profile_order"):
        print(f"Profiles: {', '.join(profiles['profile_order'])}")


def _render_events(_args, result):
    events = result.data.get("skill_events", {})
    print(f"Skill events: {events.get('status')}")
    print(events.get("agent_summary", ""))
    print_readiness_overview(events)
    print_first_validation_command(events)
    _render_selected_event(events)


def _render_selected_event(events):
    selected = events.get("selected_event_type")
    event_types = events.get("event_types", {})
    if selected and selected in event_types:
        print(f"Event: {selected}")
        print(f"Definition: {event_types.get(selected)}")
    elif events.get("event_order"):
        print(f"Events: {', '.join(events['event_order'])}")


def _render_memory(_args, result):
    memory = result.data.get("skill_memory", {})
    print(f"Skill memory: {memory.get('mode')} ({memory.get('status')})")
    print(memory.get("agent_summary", ""))
    if memory.get("provider_model"):
        print(f"Provider: {memory.get('provider_model')}")
    print_first_validation_command(memory)
    sources = (memory.get("source_summary") or {}).get("available_sources") or []
    if sources:
        print(f"Sources: {', '.join(sources)}")
    _render_memory_entry(memory)


def _render_memory_entry(memory):
    if memory.get("entry"):
        print(f"Entry: {memory['entry'].get('path')}")
    elif memory.get("entries") is not None:
        print(f"Entries: {len(memory.get('entries', []))}")


def _render_parse(_args, result):
    parsed = result.data.get("parse", {})
    print(f"✅ Parse succeeded: {parsed.get('status', 'ok')}")
    counts = parsed.get("mention_counts", {})
    print(
        f"  Skills: {counts.get('skills', 0)}, Reviewers: {counts.get('reviewers', 0)}, Unresolved: {counts.get('unresolved', 0)}"
    )
    if parsed.get("skill_mentions"):
        print(f"  Skill mentions: {len(parsed['skill_mentions'])}")
    if parsed.get("reviewer_mentions"):
        print(f"  Reviewer mentions: {len(parsed['reviewer_mentions'])}")
    print_first_validation_command(parsed)


def _render_route(_args, result):
    decision = result.data["decision"]
    print(f"🧭 Route decision: {decision['decision_status']}")
    print(f"Policy identity: {decision['policy_identity']}")
    print(
        "Considered: "
        f"{len(decision['considered_candidates'])}/{decision['considered_total']} "
        f"(limit={decision['considered_limit']}, truncated={decision['considered_truncated']})"
    )
    _render_route_candidates("Selected:", decision.get("selected_candidates") or [])
    if decision.get("failure_class"):
        print(f"Failure class: {decision['failure_class']}")
    if decision.get("operator_action"):
        print(f"Operator action: {decision['operator_action']}")
    _render_route_candidates("Ambiguity set:", decision.get("ambiguity_set") or [])
    print_first_validation_command(decision)


def _render_route_candidates(label, candidates):
    if not candidates:
        return
    print(label)
    for candidate in candidates:
        print(
            f"  - {candidate.get('name')} ({candidate.get('path')}) "
            f"confidence={candidate.get('confidence', 0.0):.4f}"
        )
        rationale = candidate.get("rationale") or []
        if rationale:
            print(f"    rationale: {', '.join(rationale)}")


def _render_goal(_args, result):
    goal = result.data["goal_decision"]
    print(f"🎯 Goal decision: {goal['decision_status']}")
    print(f"Policy identity: {goal['policy_identity']}")
    recommended = goal.get("recommended_candidate")
    if recommended:
        print(f"Recommended: {recommended.get('name')} ({recommended.get('path')})")
    alternatives = goal.get("alternative_candidates", [])
    if alternatives:
        print("Alternatives:")
        for candidate in alternatives:
            print(f"  - {candidate.get('name')} ({candidate.get('path')})")
    _render_disambiguation_prompts(goal.get("disambiguation_prompts", []))
    print_first_validation_command(goal)


def _render_disambiguation_prompts(prompts):
    if prompts:
        print("Disambiguation prompts:")
        for prompt in prompts:
            print(f"  - {prompt}")


def _render_improve(_args, result):
    improvement = result.data["improvement"]
    print(f"🎯 Skill improvement: {improvement['status']}")
    print(improvement["agent_summary"])
    recommended = improvement.get("recommended_capability")
    if recommended:
        print(f"Recommended: ${recommended.get('handle')} ({recommended.get('path')})")
    print(f"Reachability: {improvement.get('reachability', {}).get('status')}")
    print_first_validation_command(improvement)
    if improvement.get("next_command"):
        print(f"Next: {improvement['next_command']}")


def _render_starter(_args, result):
    print(
        f"Starter skills ({len(result.data['skills'])}) "
        f"[{result.data.get('starter_archetype', 'general')}]"
    )
    for skill in result.data["skills"]:
        print(f"  - {skill['name']} [{skill['category']}]")
    print_first_validation_command(result.data)


def _render_sync(args, result):
    print(f"✅ Planned sync: {len(result.data['plan']['symlinks'])} symlinks.")
    for log in result.data.get("logs", []):
        print(f"  {log}")
    if args.dry_run:
        print("  (Dry run - no changes made)")
    if result.data.get("policy_identity"):
        print(f"  Policy identity: {result.data['policy_identity']}")
    print_first_validation_command(result.data)


def _render_audit(args, result):
    print(f"✅ Audit passed: {args.path}")
    print(result.data["diagnostics"]["stdout"])
    print_first_validation_command(result.data)


def _render_skill_gate(args, result):
    gate = result.data.get("skill_gate", {})
    print(f"✅ Skill gate passed: {args.path}")
    if gate.get("stdout"):
        print(gate["stdout"])
    print_first_validation_command(result.data)


def _render_openai_format(args, result):
    report = result.data.get("openai_skill_format", {})
    print(f"✅ OpenAI skill format passed: {args.path}")
    if report.get("stdout"):
        print(report["stdout"])
    print_first_validation_command(result.data)


def _render_boundaries(args, result):
    boundary = result.data.get("boundary_check", {})
    handle = boundary.get("handle", args.handle)
    print("✅ Skill boundaries passed: $" + str(handle))
    if boundary.get("canonical_skill_path"):
        print(f"Canonical source: {boundary.get('canonical_skill_path')}")
    if boundary.get("runtime_projection_path"):
        print(f"Runtime projection: {boundary.get('runtime_projection_path')}")
    for note in boundary.get("notes") or []:
        print(f"Note: {note}")
    print_first_validation_command(result.data)


def _render_external_review(args, result):
    print(f"External review: {result.status}")
    print(f"Target: {result.data.get('target', args.path)}")
    ask_audit = result.data.get("ask_audit", {})
    if ask_audit.get("status"):
        print(f"Ask audit: {ask_audit.get('status')}")
    for key in ("plugin_eval", "tessl_lint", "tessl_review", "snyk"):
        payload = result.data.get(key) or {}
        if payload.get("status"):
            print(f"{key}: {payload.get('status')}")
    print_first_validation_command(result.data)


def _render_install(args, result):
    if result.data.get("dry_run"):
        _render_install_dry_run(result)
    else:
        print(f"✅ Installed skill: {result.data.get('skill_name', args.url)}")
        print(result.data.get("raw_output", ""))
        print_first_validation_command(result.data)


def _render_install_dry_run(result):
    print("🔍 Dry run - would install:")
    print(f"   URL: {result.data.get('url')}")
    print(f"   Skill: {result.data.get('skill_name')}")
    print(f"   Target: {result.data.get('target_path')}")
    if result.data.get("remediate"):
        print("   Remediate: Yes (scaffold missing files)")
    print_first_validation_command(result.data)
    print("\n💡 To actually install, run:")
    print(f"   {result.metadata.get('next_steps', ['ask skills install <url>'])[0]}")


def _render_fold(_args, result):
    print(f"✅ Result: {result.data['recommendation']}")
    print(f"  Overlap Score: {result.data['overlap_score']}")
    print(f"  Rationale: {result.data['rationale']}")
    print_first_validation_command(result.data)


def _render_init(_args, result):
    print(f"✅ {result.data['message']}")
    print_first_validation_command(result.data)


_SKILLS_ACTIONS = MappingProxyType(
    {
        "list": _render_list,
        "budget": _render_budget,
        "codex-preview": _render_capability_preview,
        "capabilities": _render_capability_preview,
        "capability": _render_capability_preview,
        "load-preview": _render_load_preview,
        "render-preview": _render_render_preview,
        "config": _render_config,
        "inject-preview": _render_inject_preview,
        "implicit-preview": _render_implicit_preview,
        "handles": _render_handles,
        "resolve": _render_resolve,
        "proof": _render_proof,
        "prove": _render_prove,
        "explain": _render_explain,
        "doctor": _render_doctor,
        "package": _render_package,
        "conformance": _render_conformance,
        "profiles": _render_profiles,
        "events": _render_events,
        "memory": _render_memory,
        "parse": _render_parse,
        "route": _render_route,
        "goal": _render_goal,
        "improve": _render_improve,
        "starter": _render_starter,
        "sync": _render_sync,
        "audit": _render_audit,
        "validate-skill-gate": _render_skill_gate,
        "validate-openai-format": _render_openai_format,
        "validate-boundaries": _render_boundaries,
        "external-review": _render_external_review,
        "install": _render_install,
        "fold": _render_fold,
        "init": _render_init,
    }
)


def render_skills_success(args, result):
    renderer = _SKILLS_ACTIONS.get(args.action)
    if renderer is None:
        return False
    renderer(args, result)
    return True
