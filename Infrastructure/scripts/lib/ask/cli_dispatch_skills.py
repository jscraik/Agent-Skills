"""Skills-topic command dispatch for the ask CLI."""

import ask.commands.skills as skills_commands

from ask.cli_errors import build_argument_error, build_unknown_action_result


def dispatch_skills(parser, repo_root, args, raw_args):
    """Run the selected skill command."""
    handlers = {
        "config": lambda: _dispatch_config(repo_root, args),
        "package": lambda: _dispatch_package(parser, repo_root, args, raw_args),
        "conformance": lambda: _dispatch_conformance(repo_root, args),
        "sync": lambda: _dispatch_sync(repo_root, args),
        "external-review": lambda: _dispatch_external_review(repo_root, args),
    }
    handler = handlers.get(args.action)
    return handler() if handler else _dispatch_standard(repo_root, args)


def _dispatch_standard(repo_root, args):
    """Run a non-specialised skills action."""
    for handlers in _standard_handler_groups(repo_root, args):
        handler = handlers.get(args.action)
        if handler:
            return handler()
    return build_unknown_action_result("skills", args.action)


def _standard_handler_groups(repo_root, args):
    """Return bounded command-handler groups for ordinary skills actions."""
    return (
        _preview_handlers(repo_root, args),
        _identity_handlers(repo_root, args),
        _metadata_handlers(repo_root, args),
        _routing_handlers(repo_root, args),
        _validation_handlers(repo_root, args),
    )


def _preview_handlers(repo_root, args):
    """Return handlers for listing and preview commands."""
    return {
        "list": lambda: skills_commands.list_skills(
            repo_root,
            category=args.category,
            starter=args.starter,
            archetype=args.archetype,
            limit=args.limit,
            advanced=args.advanced,
            visible_only=args.visible_only,
        ),
        "budget": lambda: skills_commands.skills_budget(
            repo_root, default_max=args.default_max
        ),
        "capabilities": lambda: skills_commands.skills_capabilities(
            repo_root, runtime_target=args.runtime_target
        ),
        "capability": lambda: skills_commands.skills_capabilities(
            repo_root, runtime_target=args.runtime_target
        ),
        "codex-preview": lambda: skills_commands.skills_codex_preview(repo_root),
        "load-preview": lambda: skills_commands.skills_load_preview(repo_root),
        "render-preview": lambda: skills_commands.skills_render_preview(
            repo_root, context_window=args.context_window
        ),
        "inject-preview": lambda: skills_commands.skills_inject_preview(
            repo_root, text=" ".join(args.text)
        ),
        "implicit-preview": lambda: skills_commands.skills_implicit_preview(
            repo_root, command=args.command, workdir=args.workdir
        ),
        "starter": lambda: skills_commands.list_skills(
            repo_root,
            category=None,
            starter=True,
            archetype=args.archetype,
            limit=args.limit,
        ),
    }


def _identity_handlers(repo_root, args):
    """Return handlers for skill identity and proof commands."""
    return {
        "handles": lambda: skills_commands.skills_handles(
            repo_root,
            check=args.check,
            include_handles=not args.no_handles,
            write_projection=args.write_projection,
            check_projection=args.check_projection,
            dry_run=args.dry_run,
        ),
        "resolve": lambda: skills_commands.skills_resolve(
            repo_root, handle=args.handle
        ),
        "parse": lambda: skills_commands.skills_parse(
            repo_root, request_text=" ".join(args.request)
        ),
        "proof": lambda: skills_commands.skills_proof(
            repo_root, handle=args.handle, runtime_target=args.runtime_target
        ),
        "prove": lambda: skills_commands.skills_prove(
            repo_root, handle=" ".join(args.handle)
        ),
        "explain": lambda: skills_commands.explain_skill(repo_root, handle=args.handle),
        "doctor": lambda: skills_commands.skills_doctor(
            repo_root,
            target=args.target,
            strict=args.strict,
            codex_parity=args.codex_parity,
        ),
    }


def _metadata_handlers(repo_root, args):
    """Return handlers for skill metadata and memory commands."""
    return {
        "profiles": lambda: skills_commands.skills_profiles(
            repo_root, profile=args.profile
        ),
        "events": lambda: skills_commands.skills_events(
            repo_root, event_type=args.event_type
        ),
        "memory": lambda: skills_commands.skills_memory(
            repo_root,
            mode=args.mode,
            query=args.query,
            limit=args.limit,
            source_id=args.source_id,
        ),
    }


def _routing_handlers(repo_root, args):
    """Return handlers for route, goal, and improvement actions."""
    return {
        "route": lambda: skills_commands.route_skills(
            repo_root,
            request=" ".join(args.request),
            top_k=args.top_k,
            considered_limit=args.considered_limit,
        ),
        "goal": lambda: skills_commands.goal_skills(
            repo_root,
            intent_text=" ".join(args.intent),
            top_k=args.top_k,
            considered_limit=args.considered_limit,
        ),
        "improve": lambda: skills_commands.improve_skills(
            repo_root,
            goal_text=" ".join(args.goal),
            top_k=args.top_k,
            considered_limit=args.considered_limit,
        ),
        "fold": lambda: skills_commands.fold_skills(
            repo_root,
            source=args.source,
            target=args.target,
            sensitivity=args.sensitivity,
        ),
        "init": lambda: skills_commands.init_skill(
            repo_root,
            name=args.name,
            category=args.category,
            description=args.description,
        ),
    }


def _validation_handlers(repo_root, args):
    """Return handlers for validation and installation actions."""
    return {
        "audit": lambda: skills_commands.audit_skill(
            repo_root,
            skill_path=args.path,
            level=args.level,
            validation_scope="source" if args.source_only else "runtime",
        ),
        "validate-skill-gate": lambda: skills_commands.validate_skill_gate(
            repo_root, skill_path=args.path
        ),
        "validate-openai-format": lambda: skills_commands.validate_openai_skill_format(
            repo_root,
            skill_path=args.path,
            mode=args.mode,
        ),
        "validate-boundaries": lambda: skills_commands.validate_skill_boundaries(
            repo_root, handle=args.handle
        ),
        "install": lambda: skills_commands.install_skill(
            repo_root,
            url=args.url,
            remediate=args.remediate,
            dest=args.dest,
            dry_run=args.dry_run,
        ),
    }


def _dispatch_config(repo_root, args):
    """Run a skills configuration action."""
    if args.config_action == "explain":
        return skills_commands.skills_config_explain(repo_root)
    return build_unknown_action_result("skills config", args.config_action)


def _dispatch_package(parser, repo_root, args, raw_args):
    """Validate and run package commands without mixing their argument modes."""
    verify_flags = any(
        [args.expected_sha256, args.trusted_provenance, args.rollback_journal]
    )
    if args.target == "verify" and not args.verify_target:
        return build_argument_error(
            "skills",
            "package",
            raw_args,
            parser_error="the following arguments are required: verify_target",
        )
    if args.target == "verify" and args.checkout_test:
        return build_argument_error(
            "skills",
            "package",
            raw_args,
            parser_error="unexpected package-only arguments",
        )
    if args.target != "verify" and (args.verify_target or verify_flags):
        return build_argument_error(
            "skills",
            "package",
            raw_args,
            parser_error="unexpected verify-only arguments",
        )
    if args.target == "verify":
        return _verify_package(repo_root, args)
    return skills_commands.skills_package(
        repo_root,
        target=args.target,
        strict=args.strict,
        checkout_test=args.checkout_test,
    )


def _verify_package(repo_root, args):
    """Run the selected strict or ordinary package verifier."""
    command = (
        skills_commands.skills_package_verify_strict
        if args.strict
        else skills_commands.skills_package_verify
    )
    return command(
        repo_root,
        target=args.verify_target,
        expected_sha256=args.expected_sha256,
        trusted_provenance=args.trusted_provenance,
        rollback_journal=args.rollback_journal,
    )


def _dispatch_conformance(repo_root, args):
    """Run a skills conformance action."""
    if args.conformance_action == "run":
        return skills_commands.skills_conformance_run(
            repo_root, suite=args.suite, evidence_dir=args.evidence_dir
        )
    return build_unknown_action_result("skills conformance", args.conformance_action)


def _dispatch_sync(repo_root, args):
    """Synchronise skills with a deterministic user-mode default."""
    user_sync_mode = args.user_sync_mode or (
        "links-only" if args.scope == "user" else "full"
    )
    options = skills_commands.SkillSyncOptions(
        plugin_cache_refresh=args.plugin_cache_refresh,
        user_sync_mode=user_sync_mode,
    )
    return skills_commands.sync_skills(
        repo_root,
        scope=args.scope,
        dry_run=args.dry_run,
        projection=args.projection,
        plugin_cache_refresh=options,
    )


def _dispatch_external_review(repo_root, args):
    """Run the explicitly selected external review command."""
    return skills_commands.external_review_skill(
        repo_root,
        skill_path=args.path,
        audit_level=args.audit_level,
        skip_plugin_eval=args.skip_plugin_eval,
        skip_tessl=args.skip_tessl,
        with_tessl_review=args.with_tessl_review,
        skip_tessl_review=args.skip_tessl_review,
        include_snyk=args.include_snyk,
        timeout_seconds=args.timeout_seconds,
        report_path=args.report_path,
        dashboard=args.dashboard,
        dashboard_path=args.dashboard_path,
    )
