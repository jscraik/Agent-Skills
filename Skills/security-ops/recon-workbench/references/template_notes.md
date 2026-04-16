# Template scaffold notes

The template under `assets/template/` is a minimal, runnable starter layout. It includes:
- Skills.md, AGENTS.md, rules/recon.rules
- docs/ (references, dependencies, worst-case playbooks, Infrastructure/artifacts/evidence, legal notes, data handling, authorization checklist, CI checks)
- Infrastructure/config/schemas/ (probe-plan, findings, manifest)
- probes/catalog.json (minimal probe catalog)
- Infrastructure/scripts/recon.sh (example runner with schema validation)
- Infrastructure/scripts/validate_schema.py (jsonschema validation)
- Infrastructure/scripts/manifest.sh (artifact hashing + manifest)
- Infrastructure/scripts/ci_check.sh (minimal CI checks)
- Infrastructure/scripts/install_playwright.sh (optional Playwright install)
- Infrastructure/scripts/view_trace.sh (Playwright trace viewer helper)
- Infrastructure/scripts/view_har.sh (HAR viewer helper)
- Infrastructure/scripts/probes/* (minimal probes; extend as needed, includes Playwright HAR + trace)
- .codex/skills/* (skill stubs for repo usage)

Use `Infrastructure/scripts/scaffold_repo.sh --repo <path>` to copy the template into a new repo.
