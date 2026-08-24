"""Human output renderers for successful non-repository ask commands."""

from types import MappingProxyType

from ask.cli_output import print_first_validation_command
from ask.commands.workouts import render_workouts_human
from ask.rendering.plugins import render_plugins_human


def render_plugins_success(args, result):
    return render_plugins_human(args, result)


def render_workouts_success(args, result):
    render_workouts_human(args, result)
    return True


def render_reviewer_success(args, result):
    if args.action != "resolve":
        return False
    resolution = result.data.get("resolution", {})
    handle = resolution.get("canonical_handle") or resolution.get("handle")
    print(f"✅ Reviewer handle: @{handle}")
    print(
        f"  Target source: {resolution.get('handle_source') or resolution.get('kind')}"
    )
    print(f"  Source: {resolution.get('source_path')}")
    print_first_validation_command(resolution)
    return True


def render_runtime_success(args, result):
    if args.action not in {"surface", "budget"}:
        return False
    report = result.data.get("runtime_surface") or result.data.get("runtime_budget", {})
    label = "surface" if args.action == "surface" else "budget"
    print(
        "✅ Runtime "
        f"{label}: "
        f"{report.get('projection_mode')} projection, "
        f"{report.get('default_visible_count')}/{report.get('default_visible_max')} default skills, "
        f"{report.get('hidden_system_count')} system lane"
    )
    print_first_validation_command(result.data)
    return True


def _render_eval_run(args, result):
    print(f"✅ Evaluation complete for {args.path}")
    print(result.data.get("raw_output", ""))
    if result.data.get("dashboard_url"):
        print(
            f"Dashboard: {result.data['dashboard_url']}#{result.data.get('dashboard_tab', 'evals')}"
        )
    print_first_validation_command(result.data)


def _render_eval_benchmark(_args, result):
    print("✅ Benchmark suite complete.")
    print(result.data.get("raw_output", ""))
    print_first_validation_command(result.data)


def _render_eval_dashboard(_args, result):
    print(f"✅ {result.data['message']}")
    print_first_validation_command(result.data)


def _render_eval_closeout(args, result):
    if args.closeout_action != "doctor":
        return
    doctor = result.data.get("eval_closeout_doctor", {})
    print(f"Eval closeout doctor: {doctor.get('status')}")
    print(f"Path: {doctor.get('path')}")
    validation = doctor.get("closeout_validation") or {}
    print(f"Validation: {validation.get('status')}")
    _render_optional_values(
        "Missing result cases", doctor.get("missing_result_cases") or []
    )
    _render_optional_count("Blockers", validation.get("blockers") or [])
    print_first_validation_command(result.data)


def _render_optional_values(label, values):
    if values:
        print(f"{label}: {', '.join(values)}")


def _render_optional_count(label, values):
    if values:
        print(f"{label}: {len(values)}")


_EVAL_ACTIONS = MappingProxyType(
    {
        "run": _render_eval_run,
        "benchmark": _render_eval_benchmark,
        "dashboard": _render_eval_dashboard,
        "closeout": _render_eval_closeout,
    }
)


def render_evals_success(args, result):
    renderer = _EVAL_ACTIONS.get(args.action)
    if renderer is None:
        return False
    renderer(args, result)
    return True


def render_mcp_success(args, result):
    if args.action != "sync":
        return False
    if result.data.get("dry_run"):
        print(f"🔍 Dry run - would sync {result.data['server_count']} MCP server(s):")
        for server in result.data.get("servers", []):
            print(f"   • {server}")
        print(f"\n   Target: {result.data['target_path']}")
    else:
        print(
            f"✅ Synced {result.data['server_count']} MCP servers to {result.data['target_path']}"
        )
        print("   Re-run `codex mcp list` or restart Codex to pick up changes.")
    print_first_validation_command(result.data)
    return True


def render_memory_success(_args, result):
    memory = result.data.get("memory", {})
    print(f"✅ {memory.get('agent_summary', 'Memory provider complete.')}")
    _render_memory_entries(memory.get("entries") or memory.get("results") or [])
    _render_memory_entry(memory.get("entry"))
    print_first_validation_command(result.data)
    return True


def _render_memory_entries(entries):
    for entry in entries:
        print(f"   • {entry.get('id')} ({entry.get('path')})")
        if entry.get("snippet"):
            print(f"     {entry.get('snippet')}")


def _render_memory_entry(entry):
    if not entry:
        return
    print(f"   Entry: {entry.get('id')} ({entry.get('path')})")
    print(f"   Source: {entry.get('source', {}).get('label')}")
    print(entry.get("content", ""))


def _render_wiki_lint(_args, result):
    print(f"✅ {result.data.get('message', 'Wiki lint passed.')}")
    if result.data.get("raw_output"):
        print(result.data["raw_output"])


def _render_wiki_ingest(_args, result):
    message = (
        "🔍 Dry run - would ingest:"
        if result.data.get("dry_run")
        else f"✅ {result.data.get('message', 'Wiki ingest complete.')}"
    )
    print(message)
    print(f"   Raw note: {result.data.get('raw_note')}")
    print(f"   Log file: {result.data.get('log_file')}")


def _render_wiki_add(_args, result):
    message = (
        "🔍 Dry run - would add triaged wiki note:"
        if result.data.get("dry_run")
        else f"✅ {result.data.get('message', 'Wiki note added.')}"
    )
    print(message)
    for label, key in (
        ("Note", "note_path"),
        ("Intent", "intent"),
        ("Status", "status"),
        ("Destination", "destination"),
    ):
        print(f"   {label}: {result.data.get(key)}")


def _render_wiki_query(_args, result):
    count = result.data.get("count", 0)
    print(f"✅ {result.data.get('message', f'Found {count} page(s).')}")
    for entry in result.data.get("results", []):
        print(f"   • {entry.get('title')} ({entry.get('path')})")
        if entry.get("snippet"):
            print(f"     {entry.get('snippet')}")


def _render_wiki_add_asset(_args, result):
    message = (
        "🔍 Dry run - would add asset-backed wiki note:"
        if result.data.get("dry_run")
        else f"✅ {result.data.get('message', 'Asset wiki note added.')}"
    )
    print(message)
    print(f"   Asset source: {result.data.get('asset_source')}")
    print(f"   Asset stored: {result.data.get('asset_stored_path')}")
    print(f"   Note: {result.data.get('note_path')}")


_WIKI_ACTIONS = MappingProxyType(
    {
        "lint": _render_wiki_lint,
        "ingest": _render_wiki_ingest,
        "add": _render_wiki_add,
        "query": _render_wiki_query,
        "add-asset": _render_wiki_add_asset,
    }
)


def render_wiki_success(args, result):
    renderer = _WIKI_ACTIONS.get(args.action)
    if renderer:
        renderer(args, result)
    print_first_validation_command(result.data)
    return True


def _render_graph_related(_args, result):
    print(
        f"\n📊 {result.data['skill']} [{result.data['direction']}, depth={result.data['depth']}]"
    )
    print(f"   Found {result.data['count']} related skill(s)\n")
    for related in result.data["related"][:15]:
        _print_graph_skill(related, "skill", "topic")
    if result.data["count"] > 15:
        print(f"\n   ... and {result.data['count'] - 15} more")
    print_first_validation_command(result.data)
    print()


def _print_graph_skill(entry, name_key, topic_key):
    tier = entry.get("tier")
    icon = "★" if tier == "stable" else ("◆" if tier == "growing" else "◇")
    weight = f" ×{entry['weight']:.1f}" if entry.get("weight", 1) > 1.2 else ""
    print(f"   {icon} {entry[name_key]} [{entry.get(topic_key, '?')}]{weight}")
    if entry.get("description"):
        print(f"      {entry['description'][:70]}")


def _render_graph_find(_args, result):
    print(f"\n🔍 Search: '{result.data['query']}' ({result.data['count']} match(es))\n")
    for match in result.data["matches"][:20]:
        _print_graph_match(match)
    print_first_validation_command(result.data)
    print()


def _print_graph_match(match, *, pad_id=False):
    tier = match.get("tier")
    icon = "★" if tier == "stable" else ("◆" if tier == "growing" else "◇")
    skill_id = f"{match['id']:<35}" if pad_id else match["id"]
    print(
        f"   {icon} {skill_id} [{match.get('topic', '?')}] ↓{match.get('in_degree', 0)}"
    )


def _render_graph_info(_args, result):
    node = result.data["node"]
    tier = node.get("tier")
    icon = "★" if tier == "stable" else ("◆" if tier == "growing" else "◇")
    print(f"\n📋 {result.data['skill']}")
    print(f"   Topic:     {node.get('topic', 'unknown')}")
    print(f"   Tier:      {icon} {node.get('tier', 'experimental')}")
    print(f"   Stability: {node.get('stability', 'unknown')}")
    print(f"   In-links:  {result.data['metrics']['in_degree']}")
    print(f"   Out-links: {result.data['metrics']['out_degree']}")
    _render_graph_out_edges(result.data["out_edges"])
    print_first_validation_command(result.data)
    print()


def _render_graph_out_edges(edges):
    if not edges:
        return
    print("\n   Links to:")
    for edge in edges[:10]:
        weight = f" ×{edge['weight']:.1f}" if edge.get("weight", 1) > 1.2 else ""
        print(f"      → {edge['to']}{weight}")


def _render_graph_chain(_args, result):
    if result.data["reachable"]:
        print(
            f"\n🔗 Chain ({result.data['hops']} hops):\n   {' → '.join(result.data['path'])}\n"
        )
    else:
        print(f"\n❌ No path found from {result.data['from']} to {result.data['to']}\n")
    print_first_validation_command(result.data)


def _render_graph_list(_args, result):
    filters = result.data["filters"]
    filter_text = f"topic={filters['topic']}" if filters["topic"] else "all"
    if filters["tier"]:
        filter_text += f", tier={filters['tier']}"
    print(f"\n📚 Skills [{filter_text}] ({result.data['count']} result(s))\n")
    for skill in result.data["skills"]:
        _print_graph_match(skill, pad_id=True)
    print_first_validation_command(result.data)
    print()


def _render_graph_topics(_args, result):
    print(f"\n🏷️  Topic Clusters ({result.data['count']} topics)\n")
    for topic, count in result.data["topics"].items():
        print(f"   {topic:<25} {count} skill(s)")
    print_first_validation_command(result.data)
    print()


_GRAPH_ACTIONS = MappingProxyType(
    {
        "related": _render_graph_related,
        "find": _render_graph_find,
        "info": _render_graph_info,
        "chain": _render_graph_chain,
        "list": _render_graph_list,
        "topics": _render_graph_topics,
    }
)


def render_graph_success(args, result):
    renderer = _GRAPH_ACTIONS.get(args.action)
    if renderer is None:
        return False
    renderer(args, result)
    return True
