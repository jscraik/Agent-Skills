# JSC-351 PU-006 Architecture Review

## Scope
- Files reviewed:
  - Infrastructure/scripts/lib/ask/services/codex_preview.py
  - Infrastructure/scripts/lib/ask/commands/skills_impl.py
  - Infrastructure/tests/test_ask_skills_codex_preview.py
  - .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html

## Findings (severity-ranked)

### Medium — Contract parsing logic is duplicated across command/service layers, creating drift risk
- Evidence:
  - Infrastructure/scripts/lib/ask/services/codex_preview.py:39-104 defines `_parse_frontmatter_scalar` and `_read_skill_frontmatter_fields`.
  - Infrastructure/scripts/lib/ask/services/codex_preview.py:107-142 defines `_read_agents_openai_yaml_fields`.
  - Infrastructure/scripts/lib/ask/commands/skills_impl.py:368-460 defines another `_parse_frontmatter_scalar` + `_read_skill_frontmatter_fields`.
  - Infrastructure/scripts/lib/ask/commands/skills_impl.py:2911-2942 defines another `_read_agents_openai_yaml_fields`.
- Why this matters architecturally:
  - These functions model the same SKILL metadata contract but now live in two modules that can evolve independently.
  - A future schema/format change can silently produce inconsistent behavior between `skills package` (command lane) and `skills *-preview` (service lane), which weakens ABI-governed intent.
- Recommendation:
  - Extract shared parsing into one contract module (for example `ask/services/skill_metadata_contract.py`) and have both `skills_impl` and `codex_preview` consume that module.
  - Keep one canonical parser test suite and make command/service tests assert parity on representative fixtures.

### Medium — Codex runtime provenance relies on fixed sibling-repo topology (`../codex`), coupling architecture to local checkout layout
- Evidence:
  - Infrastructure/scripts/lib/ask/services/codex_preview.py:154 sets `codex_root = repo_root.parent / "codex"`.
  - Infrastructure/scripts/lib/ask/services/codex_preview.py:165-167 returns blocked state when that sibling repo is absent.
  - Infrastructure/scripts/lib/ask/services/codex_preview.py:169-193 executes git commands directly in that sibling path.
- Why this matters architecturally:
  - Service behavior depends on an external repository path convention rather than an explicit dependency boundary/config input.
  - This makes the preview lane environment-sensitive and harder to reuse in alternate layouts (worktrees, CI temp checkouts, monorepo tools).
- Recommendation:
  - Introduce an explicit source resolver boundary (env/config input + default fallback) so topology is configurable and test-injectable.
  - Keep the current blocked check behavior, but report the resolved lookup chain to make provenance deterministic across environments.

## Compliance Check
- Good alignment:
  - `skills_impl` keeps command routing thin and delegates preview mechanics to `ask.services.codex_preview` (Infrastructure/scripts/lib/ask/commands/skills_impl.py:2846-2878).
  - Tests include an ownership-boundary assertion that command module does not own service internals (Infrastructure/tests/test_ask_skills_codex_preview.py:298-310).
- No circular dependency introduced in reviewed slice:
  - Service imports no command module and boundary test enforces that direction.

## Risk Analysis
- Primary risk is architectural drift (contract mismatch across duplicated parsers) rather than immediate runtime failure.
- Secondary risk is environment-coupling debt from hardcoded external-source location.
- Functional confidence is currently good for covered paths:
  - `python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q` passed (14 tests).

## Recommendations
1. Centralize SKILL metadata parsing into a single reusable contract module and migrate both call sites.
2. Add a small parity test that runs both command and preview parsing against the same fixture and asserts identical normalized metadata.
3. Replace direct `../codex` assumption with a resolver interface that supports explicit override and deterministic fallback chain.

WROTE: artifacts/reviews/jsc-351-pu006/architecture.md
