# Contributing Documentation

This repository treats documentation as structured, navigable data. Clear hierarchy, consistent linking, and predictable patterns help humans and AI tools (including Codex) extend docs safely.

---

## 1. Documentation philosophy

Documentation must be:

- Hierarchical and predictable
- Linked using canonical full paths
- Non-ambiguous and non-redundant
- Referenceable by file path for AI workflows
- Written so code and docs can be traversed together

If Codex can generate working examples from the documentation alone, documentation coverage is strong.

---

## 2. Documentation hierarchy

Use this structure:

```
/docs
  /guides
  /concepts
  /reference
  /deployment
  /examples
  /api
```

### Rules

- Each directory must contain an `index.md`.
- Do not mix conceptual, API, and tutorial content on one page.
- Keep one primary concept per page.
- Avoid cross-domain mixing (for example, deployment details inside guides unless explicitly needed and cross-linked).

---

## 3. Linking standards (critical)

### 3.1 Always use full paths

Use absolute paths from repository root.

Correct:

```
See [Deployment guide](/docs/deployment)
```

Incorrect:

```
See [Deployment guide](deployment)
```

### 3.2 Never use trailing slashes on internal docs links

Correct:

```
/docs/deployment
```

Incorrect:

```
/docs/deployment/
```

---

## 4. File reference conventions for Codex

Use explicit file paths in docs and PR notes so Codex can scope context correctly.

Correct:

```
See implementation in `scripts/docs_lint.py`
```

Codex-friendly references:

```
@scripts/docs_lint.py
@docs/deployment/index.md
```

Avoid vague references like "the server file" or "that config file".

---

## 5. Code example standards

All code examples should:

- Be runnable or compile-valid
- Include required imports
- Avoid pseudo-code unless clearly marked
- Use consistent formatting
- State assumptions if not standalone

---

## 6. PR documentation workflow

If a PR introduces any of the following, docs must be updated in the same PR:

- New environment variables
- New CLI flags
- New configuration fields
- New API endpoints
- New user-visible behavior
- Breaking changes

---

## 7. Codex PR explainer pattern

Step 1:

```bash
gh pr diff <number>
```

Step 2 prompt pattern:

```
Review pull request 12345 using `gh pr diff 12345`.
Summarize:
- What feature was added
- What files changed
- What config changes were introduced
- Whether documentation was updated

If docs are missing, update:
@docs/deployment/index.md
```

---

## 8. Updating docs via Codex

Use structured prompts:

```
You are using Codex in /Users/jamiecraik/dev/agent-skills

1. Review PR 12345:
   gh pr diff 12345
2. Identify new configuration or behavior changes.
3. Update:
   @docs/deployment/index.md
4. Keep style consistent.
5. Use full-path, non-trailing-slash links.
```

---

## 9. Documentation coverage evaluation pattern

Coverage test pattern:

1. Provide only docs as context.
2. Ask Codex to generate minimal working output.
3. Validate generated output with tests/checks.

Example:

```
Using only:
@docs/guides/index.md
@docs/api/index.md

Generate a minimal working example project.
```

---

## 10. Required local and CI checks

Run locally before opening a PR:

```bash
python3 scripts/docs_lint.py --mode warn --config docs-policy.json
```

Use blocking mode to preflight strict enforcement:

```bash
python3 scripts/docs_lint.py --mode block --config docs-policy.json
```

---

## 11. Pull request checklist (required)

- [ ] Documentation updated when behavior, config, API, or CLI changed
- [ ] Internal docs links use full paths
- [ ] Internal docs links do not use trailing slashes
- [ ] Examples are runnable/valid or assumptions are stated
- [ ] New configuration is documented
- [ ] `CONTRIBUTING.md` updated if docs structure contract changed

---

## 12. Common anti-patterns

- Vague references (for example, "the server file")
- Relative internal docs links
- Trailing-slash internal docs links
- Mixed content types on one page
- Hidden configuration details
- Examples missing required imports/context

---

## 13. Summary

Well-structured docs:

- Reduce contributor confusion
- Improve discoverability
- Help Codex reason across code and docs
- Enable reliable documentation automation

Treat documentation as structured data.
