"""Wiki-topic command dispatch for the ask CLI."""

from ask.envelope import ErrorCode, ErrorObject
from ask.cli_errors import build_unknown_action_result
from ask.cli_output import replay_command
from ask.cli_prompts import prompt_choice, prompt_nonempty, prompt_optional
from ask.commands.wiki import (
    wiki_add,
    wiki_add_asset,
    wiki_ingest,
    wiki_lint,
    wiki_query,
)


def dispatch_wiki(repo_root, args, result):
    """Run the selected wiki command, preserving interactive validation errors."""
    handlers = {
        "lint": lambda: wiki_lint(
            repo_root, wiki_root=args.wiki_root, max_age_days=args.max_age_days
        ),
        "ingest": lambda: wiki_ingest(
            repo_root,
            title=args.title,
            sources=args.source or [],
            summary=args.summary,
            tags=args.tag or [],
            dry_run=args.dry_run,
        ),
        "query": lambda: wiki_query(
            repo_root,
            query=args.query,
            wiki_root=args.wiki_root,
            limit=args.limit,
        ),
    }
    if args.action == "add":
        return _add_note(repo_root, args, result)
    if args.action == "add-asset":
        return _add_asset(repo_root, args, result)
    handler = handlers.get(args.action)
    return handler() if handler else build_unknown_action_result("wiki", args.action)


def _add_note(repo_root, args, result):
    """Validate and add a regular wiki note."""
    values = _note_values(args, result)
    missing = _missing(values, ("title", "summary", "source", "intent", "status"))
    if result.status == "error":
        return result
    if missing:
        _append_missing_note_error(args, result, values, missing)
        return result
    return wiki_add(
        repo_root, tags=values["tags"], dry_run=args.dry_run, **_note_payload(values)
    )


def _note_values(args, result):
    """Collect note values from flags or the interactive questionnaire."""
    values = {
        "title": args.title,
        "summary": args.summary,
        "source": args.source,
        "intent": args.intent,
        "status": args.status,
        "destination": args.destination,
        "tags": args.tag or [],
    }
    if args.interactive:
        _prompt_note_values(args, result, values)
    return values


def _prompt_note_values(args, result, values):
    """Complete note values interactively unless JSON output was requested."""
    if args.json:
        _append_interactive_json_error(result)
        return
    print("🧭 Wiki triage questionnaire")
    values["title"] = values["title"] or prompt_nonempty("Title: ")
    values["summary"] = values["summary"] or prompt_nonempty("Summary: ")
    values["source"] = values["source"] or prompt_nonempty("Source: ")
    values["intent"] = values["intent"] or prompt_choice(
        "Intent:", ["finding", "playbook", "design-asset", "lesson-learned"]
    )
    values["status"] = values["status"] or prompt_choice(
        "Status:", ["needs-verification", "verified", "fix-now"]
    )
    values["destination"] = values["destination"] or prompt_choice(
        "Destination:", ["failures", "playbooks", "assets/ui", "learnings"]
    )


def _note_payload(values):
    """Return the note-add payload expected by the wiki command."""
    return {
        "title": values["title"],
        "summary": values["summary"],
        "source": values["source"],
        "intent": values["intent"],
        "status": values["status"],
        "destination": values["destination"],
    }


def _append_missing_note_error(args, result, values, missing):
    """Attach the replay command and error for incomplete note input."""
    command = _note_replay_command(args, values)
    _append_missing_error(
        result,
        command,
        missing,
        "Missing required fields for wiki add",
        "Use --interactive or pass --summary, --source, --intent, and --status explicitly.",
    )


def _note_replay_command(args, values):
    """Build the machine-readable replay command for note validation."""
    command = ["./bin/ask", "wiki", "add"]
    if values["title"]:
        command.append(values["title"])
    _add_option(command, "--summary", values["summary"])
    _add_option(command, "--source", values["source"])
    _add_option(command, "--intent", values["intent"])
    _add_option(command, "--status", values["status"])
    _add_option(command, "--destination", values["destination"])
    _add_tags(command, values["tags"])
    return _finish_replay_command(command, args.dry_run)


def _add_asset(repo_root, args, result):
    """Validate and add a wiki asset."""
    values = _asset_values(args, result)
    missing = _missing(values, ("asset_path", "title", "summary"))
    if result.status == "error":
        return result
    if missing:
        _append_missing_asset_error(args, result, values, missing)
        return result
    return wiki_add_asset(
        repo_root, tags=values["tags"], dry_run=args.dry_run, **_asset_payload(values)
    )


def _asset_values(args, result):
    """Collect asset values from flags or the interactive questionnaire."""
    values = {
        "asset_path": args.asset_path,
        "title": args.title,
        "summary": args.summary,
        "source": args.source,
        "status": args.status,
        "destination": args.destination,
        "tags": args.tag or [],
    }
    if args.interactive:
        _prompt_asset_values(args, result, values)
    values["status"] = values["status"] or "verified"
    values["destination"] = values["destination"] or "assets/ui"
    return values


def _prompt_asset_values(args, result, values):
    """Complete asset values interactively unless JSON output was requested."""
    if args.json:
        _append_interactive_json_error(result)
        return
    print("🖼️ Wiki asset questionnaire")
    values["asset_path"] = values["asset_path"] or prompt_nonempty("Asset path: ")
    values["title"] = values["title"] or prompt_nonempty("Title: ")
    values["summary"] = values["summary"] or prompt_nonempty("Summary: ")
    values["source"] = values["source"] or prompt_optional("Source (optional): ")
    values["status"] = values["status"] or prompt_choice(
        "Status:", ["needs-verification", "verified", "fix-now"]
    )
    values["destination"] = values["destination"] or prompt_choice(
        "Destination:", ["assets/ui", "learnings"]
    )


def _asset_payload(values):
    """Return the asset-add payload expected by the wiki command."""
    return {
        "asset_path": values["asset_path"],
        "title": values["title"],
        "summary": values["summary"],
        "source": values["source"],
        "status": values["status"],
        "destination": values["destination"],
    }


def _append_missing_asset_error(args, result, values, missing):
    """Attach the replay command and error for incomplete asset input."""
    command = _asset_replay_command(args, values)
    _append_missing_error(
        result,
        command,
        missing,
        "Missing required fields for wiki add-asset",
        "Use --interactive or pass asset_path, --title, and --summary explicitly.",
    )


def _asset_replay_command(args, values):
    """Build the machine-readable replay command for asset validation."""
    command = ["./bin/ask", "wiki", "add-asset"]
    if values["asset_path"]:
        command.append(values["asset_path"])
    _add_option(command, "--title", values["title"])
    _add_option(command, "--summary", values["summary"])
    _add_option(command, "--source", values["source"])
    _add_option(command, "--status", values["status"])
    _add_option(command, "--destination", values["destination"])
    _add_tags(command, values["tags"])
    return _finish_replay_command(command, args.dry_run)


def _missing(values, required):
    """Return the required field names that do not yet have values."""
    return [name for name in required if not values[name]]


def _append_interactive_json_error(result):
    """Reject the unsupported interactive plus JSON combination."""
    result.status = "error"
    result.errors.append(
        ErrorObject(
            code=ErrorCode.ERR_VALIDATION,
            message="--interactive cannot be combined with --json.",
            fix_suggestion="Use interactive mode without --json or pass all fields explicitly.",
        )
    )


def _append_missing_error(result, command, missing, message, fix_suggestion):
    """Add a validation error with its deterministic replay command."""
    result.status = "error"
    result.data["validation_commands"] = [replay_command(*command)]
    result.errors.append(
        ErrorObject(
            code=ErrorCode.ERR_VALIDATION,
            message=f"{message}: {', '.join(missing)}",
            fix_suggestion=fix_suggestion,
        )
    )


def _add_option(command, flag, value):
    """Append an optional flag/value pair when the value is supplied."""
    if value:
        command.extend([flag, value])


def _add_tags(command, tags):
    """Append each repeatable tag flag to a replay command."""
    for tag in tags:
        command.extend(["--tag", tag])


def _finish_replay_command(command, dry_run):
    """Finish a replay command with its required machine-output flags."""
    if dry_run:
        command.append("--dry-run")
    return [*command, "--json", "--robot"]
