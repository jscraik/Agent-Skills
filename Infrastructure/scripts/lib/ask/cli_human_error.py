from types import MappingProxyType

import ask.commands.skills as skills_commands
from ask.cli_output import print_first_validation_command
from ask.envelope import ErrorCode, ErrorObject
from ask.golden_path import render_golden_path_summary


def _first_error(result):
    if result.errors:
        return result.errors[0]
    return ErrorObject(code=ErrorCode.ERR_RUNTIME, message="Unknown error")


def _render_failure_details(decision):
    if decision.get("failure_class"):
        print(f"Failure class: {decision['failure_class']}")
    if decision.get("operator_action"):
        print(f"Operator action: {decision['operator_action']}")


def _render_validation_context(decision):
    print_first_validation_command(decision)
    print("")


def _render_ambiguity_candidates(candidates):
    if not candidates:
        return
    print("Ambiguity set:")
    for candidate in candidates:
        print(
            f"  - {candidate.get('name')} ({candidate.get('path')}) "
            f"confidence={candidate.get('confidence', 0.0):.4f}"
        )


def _render_route_decision(decision):
    print(f"🧭 Route decision: {decision.get('decision_status', 'unknown')}")
    _render_failure_details(decision)
    _render_ambiguity_candidates(decision.get("ambiguity_set"))
    _render_validation_context(decision)


def _render_disambiguation_prompts(prompts):
    if not prompts:
        return
    print("Disambiguation prompts:")
    for prompt in prompts:
        print(f"  - {prompt}")


def _render_goal_decision(goal):
    print(f"🎯 Goal decision: {goal.get('decision_status', 'unknown')}")
    _render_failure_details(goal)
    _render_disambiguation_prompts(goal.get("disambiguation_prompts") or [])
    _render_validation_context(goal)


def _render_decision_context(args, data):
    if args.topic == "skills" and args.action == "route" and data.get("decision"):
        _render_route_decision(data["decision"])
    if args.topic == "skills" and args.action == "goal" and data.get("goal_decision"):
        _render_goal_decision(data["goal_decision"])


def _error_message(args, error):
    message = error.message
    if (
        args.topic == "skills"
        and args.action == "audit"
        and " First failures:" in message
    ):
        return message.split(" First failures:", 1)[0]
    return message


def _render_error_header(args, error):
    print(f"❌ Error: {_error_message(args, error)}")
    if error.fix_suggestion:
        print(f"\n💡 {error.fix_suggestion}")


def _render_family_benchmark(data):
    family_data = data.get("family_benchmarks")
    if (
        not isinstance(family_data, dict)
        or int(family_data.get("exit_code", 0) or 0) == 0
    ):
        return
    failures = skills_commands.extract_family_fail_lines(
        str(family_data.get("stdout", ""))
    )
    if failures:
        print("\n🔎 Family benchmark failures (first 3):")
        for failure in failures[:3]:
            print(f"   - {failure}")
        remaining = len(failures) - 3
        if remaining > 0:
            print(f"   ... and {remaining} more (use --json for full details)")
        return
    for raw_line in str(family_data.get("stderr", "")).splitlines():
        line = raw_line.strip()
        if line:
            print("\n🔎 Family benchmark error:")
            print(f"   {line}")
            return


def _render_audit_examples():
    print("\n📚 Audit examples:")
    print("   ask skills audit backend-platform/cli-spec --level compat")
    print("   ask skills audit backend-platform/cli-spec --level strict")
    print(
        "   ask skills audit "
        "Plugins/skill-factory/skills/code_quality_review/skill-builder --level strict"
    )


def _render_skills_audit(data):
    _render_family_benchmark(data)
    if "diagnostics" in data:
        print(data["diagnostics"]["stdout"])
    if "security_gate" in data:
        print(data["security_gate"]["stdout"])
    _render_audit_examples()


def _print_raw_output(data):
    if "raw_output" in data:
        print(data["raw_output"])
    if "raw_error" in data:
        print(data["raw_error"])


def _render_lifecycle_examples(action):
    if action == "init":
        print(
            "\n📚 Init examples:\n"
            "   ask skills init my-skill --category frontend-ui --description 'Does X'\n"
            "   ask skills init security-guard --category security-ops --description 'Validates Y'"
        )
    elif action == "install":
        print(
            "\n📚 Install examples:\n   ask skills install https://github.com/user/repo --remediate"
        )


def _render_skills_lifecycle(action, data):
    _print_raw_output(data)
    if action in {"fold", "init"}:
        print_first_validation_command(data)
    _render_lifecycle_examples(action)


def _render_skills(args, data):
    if args.action == "audit":
        _render_skills_audit(data)
    elif args.action in {"install", "fold", "init"}:
        _render_skills_lifecycle(args.action, data)
    else:
        print_first_validation_command(data)


def _render_plugin_run(args, run):
    print(f"\n  Step: {run.get('step')}")
    print(f"  Command: {run.get('command')}")
    print(f"  Return code: {run.get('returncode')}")
    _render_plugin_stream(args, "stdout", run)
    _render_plugin_stream(args, "stderr", run)


def _render_plugin_stream(args, name, run):
    value = run.get(name)
    if not value:
        return
    label = name.capitalize()
    if getattr(args, "verbose", False):
        print(f"  {label}:\n{repr(value)}")
    else:
        print(f"  ({label} elided. Use --verbose to view)")


def _render_plugin_runs(args, data):
    if "command_runs" not in data:
        return
    print("\n🔧 Command execution details:")
    for run in data["command_runs"]:
        _render_plugin_run(args, run)
    print(
        "\n📚 Plugin examples:\n   ask plugins init my-plugin --category third-party --with-marketplace\n   ask plugins install https://github.com/<owner>/<repo> --path Plugins/<name>\n   ask plugins harden Plugins/my-plugin\n   ask plugins sync-local-runtime"
    )


_PLUGIN_ACTIONS_WITH_RUN_DETAILS = frozenset(
    {
        "init",
        "create",
        "install",
        "import",
        "harden",
        "sync-local-runtime",
        "prune-stale-config",
        "uninstall",
    }
)


def _render_plugins(args, data):
    if args.action not in _PLUGIN_ACTIONS_WITH_RUN_DETAILS:
        print_first_validation_command(data)
        return
    _print_raw_output(data)
    print_first_validation_command(data)
    _render_plugin_runs(args, data)


def _render_evals(_args, data):
    _print_raw_output(data)
    print_first_validation_command(data)
    print(
        "\n📚 Eval examples:\n   ask evals run backend/cli-spec --mode smoke\n   ask evals run backend/cli-spec --mode release"
    )


def _render_graph(_args, data):
    print_first_validation_command(data)
    print(
        "\n📚 Graph examples:\n   ask graph find security\n   ask graph related skill-builder --depth 2\n   ask graph chain skill-creator skill-installer\n   ask graph info cli-spec"
    )


def _render_repo_surface(data):
    if "repo_surface" not in data:
        return
    summary = data["repo_surface"].get("summary", {})
    print(
        "   Surface summary: "
        f"{summary.get('total_paths', 0)} tracked path(s), "
        f"{summary.get('blocking_findings', 0)} blocking finding(s)"
    )


def _render_repo(args, data):
    print_first_validation_command(data)
    if args.action == "validate":
        print(data.get("raw_output", ""))
    if args.action == "check-stability" and "errors" in data:
        for error in data["errors"]:
            print(f"   ERROR: {error}")
    if args.action == "doctor" and "doctor" in data:
        for line in render_golden_path_summary(data["doctor"], indent="   "):
            print(line)
    if args.action == "surface":
        _render_repo_surface(data)
    print(
        "\n📚 Repo examples:\n   ask repo status\n   ask repo validate --ephemeral\n   ask repo doctor-catalog --strict\n   ask repo surface --json\n   ask repo check-stability --changed-files backend/cli-spec/SKILL.md"
    )


def _render_mcp(_args, data):
    print_first_validation_command(data)
    print("\n📚 MCP examples:\n   ask mcp sync\n   ask mcp sync --dry-run")


def _render_validation_only(_args, data):
    print_first_validation_command(data)


def _render_wiki(_args, data):
    print_first_validation_command(data)
    print(
        "\n📚 Wiki examples:\n   ask wiki lint\n   ask wiki ingest 'Title' --summary 'Summary' --source '<source>'\n   ask wiki add --interactive\n   ask wiki query 'prompt injection'\n   ask wiki add-asset ./tmp/screenshot.png --title 'UI reference' --summary 'Capture for reuse'\n   ask wiki add-asset --interactive"
    )


_TOPIC_RENDERERS = MappingProxyType(
    {
        "skills": _render_skills,
        "plugins": _render_plugins,
        "reviewers": _render_validation_only,
        "evals": _render_evals,
        "graph": _render_graph,
        "repo": _render_repo,
        "mcp": _render_mcp,
        "memory": _render_validation_only,
        "runtime": _render_validation_only,
        "wiki": _render_wiki,
        "workouts": _render_validation_only,
    }
)


def render_error(args, result):
    _render_decision_context(args, result.data)
    _render_error_header(args, _first_error(result))
    renderer = _TOPIC_RENDERERS.get(args.topic)
    if renderer:
        renderer(args, result.data)
