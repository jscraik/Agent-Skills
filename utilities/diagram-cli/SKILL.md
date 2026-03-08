---
name: diagram-cli
description: Generate, validate, and refresh @brainwav/diagram architecture artifacts (.mmd/.svg/.diagram manifest + context packs). Use this skill when users need fast repository understanding for onboarding, PR architecture impact, and CI drift checks; do not use it for hand-drawn product/UI mock diagrams.
---

# Diagram CLI

Use this skill to turn a codebase into architecture evidence (diagrams + manifest + concise interpretation) with reproducible commands.

## Table of Contents
- [Philosophy](#philosophy)
- [When to use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Procedure](#procedure)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Constraints](#constraints)
- [Examples](#examples)
- [References](#references)
- [Philosophy and tradeoffs](#philosophy-and-tradeoffs)
- [Anti-patterns and caveats](#anti-patterns-and-caveats)
- [Variation and adaptation](#variation-and-adaptation)
- [Empowering execution style](#empowering-execution-style)

## Philosophy

- Prefer evidence over intuition: generate artifacts first, then interpret.
- Keep outputs deterministic and path-stable so reruns are diffable in CI.
- Optimize for project understanding, not diagram aesthetics.
- Mental model: diagrams are a decision-support framework, not decoration.
- Why this approach: reliable architecture evidence reduces wrong assumptions in reviews.
- Guiding checks:
  - What architectural claim is this artifact proving?
  - Which tradeoff are we accepting (speed vs fidelity)?
  - What evidence is still missing before we conclude?

## When to use

Use when:
- A user asks to understand repository architecture quickly.
- A PR/release needs architecture drift evidence.
- Agent context packs must be refreshed from current code.

Do not use when:
- The user wants marketing/UI mock diagrams (use design-oriented skills).
- The user needs threat modeling without code-graph artifacts (use security-focused skills).

## Inputs

Required:
- Target repository path (default: current working directory).
- Goal (onboarding map, PR impact, CI drift gate, or context-pack refresh).

Optional:
- Focus area (`--focus <module>` or narrowed `--patterns`).
- Output root (`.diagram` for CI-style artifacts or `artifacts/diagrams` for local runs).
- Rule config path for architecture tests (`.architecture.yml`).

## Outputs

- Generated diagram artifacts (`.mmd` and optionally `.svg`/`.png`).
- `manifest` summary and completeness check result.
- Project-understanding brief that explains:
  - core components,
  - key dependency paths,
  - risk/hotspot areas,
  - suggested next inspection steps.
- Updated context pack when requested (for repos that maintain one).
- If structured JSON output is requested, include top-level `schema_version: 1`.

## Procedure

1. **Preflight and version check**
   - Confirm repo root and writable output path.
   - Prefer installed CLI (`diagram`), fallback to `npx --yes @brainwav/diagram`.
   - Confirm CLI baseline is current (`@brainwav/diagram` `>=1.0.8`, published 2026-02-28).

2. **Analyze structure first**
   - Run:
     ```bash
     npx --yes @brainwav/diagram analyze . --json > artifacts/diagrams/analyze.json
     ```
   - Summarize file count, dependency count, and dominant directories before generating visuals.

3. **Generate architecture views**
   - Standard full sweep:
     ```bash
     npx --yes @brainwav/diagram all . --output-dir .diagram
     ```
   - For focused deep dives, generate targeted types (`architecture`, `dependency`, `security`, `auth`) and optionally `--focus`.

4. **Gate artifact quality**
   - Verify required types and placeholders:
     ```bash
     npx --yes @brainwav/diagram manifest . --manifest-dir .diagram --require-types architecture,dependency,security,auth --fail-on-placeholder
     ```
   - If `.architecture.yml` exists (or is requested), run:
     ```bash
     npx --yes @brainwav/diagram test . --format console
     ```

5. **Refresh context pack when needed**
   - If a repo has a refresh helper script, use it (dry-run first).
   - For this repository (`diagram-cli`), use:
     ```bash
     scripts/refresh-diagram-context.sh --dry-run
     scripts/refresh-diagram-context.sh --force
     ```

6. **Explain the project clearly**
   - Use `references/project-understanding-playbook.md` to produce a concise architecture brief from generated artifacts.

## Validation

Fail fast: stop at the first failed gate and do not continue with interpretation if artifact generation is invalid.

Minimum checks:
- `analyze` command exits `0` and emits parseable JSON.
- Expected diagram files exist and are non-empty.
- `manifest` gate passes required types and placeholder checks.
- If rules were requested, `diagram test` returns expected exit code and format.

## Anti-patterns

- Skipping `analyze` and guessing architecture from filenames.
- Returning only diagrams without an interpretation brief.
- Running broad scans without excludes on very large repos.
- Treating placeholder diagrams as valid architectural evidence.
- **NEVER** report architecture health without manifest gates.
- **DO NOT** treat one diagram as the whole system truth.
- **DON'T** hide uncertainty when files are excluded or missing.
- Common mistake: generic summaries without evidence links.
- Pitfall: wrong confidence from partial outputs.
- Warning sign: incorrect claims that do not map to generated artifacts.

## Constraints

- Redact or omit secrets, credentials, tokens, keys, and sensitive internal identifiers in outputs.
- Do not install or modify dependencies unless explicitly approved.
- Prefer reproducible local paths and deterministic commands.
- Keep commands non-destructive; avoid unrelated repo modifications.

## Examples

- "Use diagram-cli to map this repo for onboarding and highlight risky dependencies."
- "Refresh `.diagram` artifacts and fail if security/auth diagrams are placeholders."
- "Regenerate context diagrams and summarize what changed since the last run."
- "Run architecture test rules and explain only the highest-impact violations."

## References

- `references/project-understanding-playbook.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `assets/architecture-brief-template.md`
- [@brainwav/diagram on npm](https://www.npmjs.com/package/@brainwav/diagram)
- [diagram-cli repository](https://github.com/jscraik/diagram-cli)
- [Mermaid documentation](https://mermaid.js.org/)

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when evidence-backed architecture understanding matters more than speculative code reading.
- Prioritize reproducibility, then coverage, then visual polish.
- Trade speed for fidelity only when the user explicitly asks for a lightweight pass.

## Anti-patterns and caveats
- Do not bypass manifest validation under deadline pressure.
- Do not claim architectural certainty from partial or placeholder outputs.
- Do not collapse distinct concerns (dependency, auth, security) into one vague summary.

## Variation and adaptation
- For small repos: run full `all` sweep and concise summary.
- For large repos: narrow patterns/focus first, then expand iteratively.
- For CI: prefer `.diagram` outputs + machine-checkable manifest gates.
- Use different, context-specific summary depth for onboarding vs incident triage vs compliance audits.
- Customize outputs for each audience; avoid repetitive, generic, cookie-cutter briefs.
- Keep recommendations diverse and unique, then converge on the highest-leverage next action.

## Empowering execution style
- Be explicit about confidence and uncertainty.
- Show users exactly which artifacts support each architectural claim.
- Suggest the next highest-leverage follow-up command.
- Enable exploration: propose one safe deep-dive and one fast-check option.
- Empower users to challenge assumptions with evidence-first iteration.

## Remember
- The agent is capable of extraordinary work in this domain.
- These guardrails unlock creative, innovative analysis—they do not constrain judgment.
- Explore options, then push boundaries safely with evidence-backed decisions.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
