# Contributing docs

Docs are part of the product. Keep them short, clear, and safe to follow.

## Update docs when you change

- Env vars.
- CLI flags.
- Config.
- Public APIs.
- User-facing behavior.
- Breaking changes.

## Docs structure (required)

Docs live under `/docs`:

```
/docs
  /guides
  /concepts
  /reference
  /deployment
  /examples
  /api
```

Rules:

- Each directory must include an `index.md`.
- Keep pages single-purpose. Don’t mix guide + concept + API on one page.

## Linking rules (critical)

Use full paths that start with `/`. This keeps links stable in agent prompts and tooling.

Correct:

```
See [Deployment](/docs/deployment)
```

Incorrect:

```
See [Deployment](deployment)
```

Also:

- Do not use trailing slashes: use `/docs/deployment`, not `/docs/deployment/`.
- Use clear link text (avoid “click here”).

## File references for Codex

Prefer explicit file paths in docs and PR notes.

Examples:

```
See `scripts/docs_lint.py`.
@docs/deployment/index.md
```

Avoid vague references like “that config file”.

## Code examples

Code examples should be:

- Runnable or buildable.
- Complete. Include imports.
- Marked as pseudo-code if they are not runnable.
- Clear about assumptions.

## Local checks

Run:

```bash
python3 scripts/docs_lint.py --mode warn --config docs-policy.json
```

To preflight strict enforcement:

```bash
python3 scripts/docs_lint.py --mode block --config docs-policy.json
```

## Pull request checklist (required)

- [ ] Docs updated when behavior, config, API, or CLI changed.
- [ ] Internal docs links use full paths.
- [ ] Internal docs links do not use trailing slashes.
- [ ] Examples run, or assumptions are stated.
- [ ] New config is documented.
- [ ] This doc updated if the docs structure contract changed.

## Issue and support intake

- Bug reports: `/.github/ISSUE_TEMPLATE/bug_report.md`
- Feature requests: `/.github/ISSUE_TEMPLATE/feature_request.md`
- Docs requests: `/.github/ISSUE_TEMPLATE/docs_request.md`
- General support: `/SUPPORT.md`
- Security reports (private only): `/SECURITY.md`

## Common anti-patterns

- Vague references (for example, "the server file").
- Relative internal docs links.
- Trailing-slash internal docs links.
- Mixed content types on one page.
- Hidden config details.
- Examples missing required imports or context.
