# Template scaffold notes

The template under `assets/template/` is a minimal, runnable starter layout. It includes:
- Skills.md, AGENTS.md, rules/recon.rules
- docs/ (references, dependencies, worst-case playbooks, artifacts/evidence, legal notes, data handling, authorization checklist, CI checks)
- config/schemas/ (probe-plan, findings, manifest)
- probes/catalog.json (minimal probe catalog)
- scripts/recon.sh (example runner with schema validation)
- scripts/validate_schema.py (jsonschema validation)
- scripts/manifest.sh (artifact hashing + manifest)
- scripts/ci_check.sh (minimal CI checks)
- scripts/install_playwright.sh (optional Playwright install)
- scripts/view_trace.sh (Playwright trace viewer helper)
- scripts/view_har.sh (HAR viewer helper)
- scripts/probes/* (minimal probes; extend as needed, includes Playwright HAR + trace)
- .codex/skills/* (skill stubs for repo usage)

Use `scripts/scaffold_repo.sh --repo <path>` to copy the template into a new repo.
