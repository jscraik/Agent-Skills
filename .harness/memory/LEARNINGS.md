---
schema_version: 1
purpose: Per-project agent knowledge base — repo-specific gotchas and hard-won fixes.
scope: This repo only.
update_policy: |
  Append after any bug, tool failure, or extra-effort fix specific to this repo.
  Universal gotchas go in ~/.codex/instructions/Learnings.md instead.
  Do NOT delete entries. Append only.
  Format: **YYYY-MM-DD [Agent]:** <problem> → <fix>
---

# Learnings

Repo-specific agent knowledge base. Append-only.

> **Scope:** This repo only. Universal gotchas → `~/.codex/instructions/Learnings.md`.
> **Format:** `**YYYY-MM-DD [Agent]:** <problem> → <fix>`

- **2026-03-09 [Codex]:** `scripts/docs_lint.py` does not accept a `--files` selector; passing it exits with argparse error. Use supported global flags (`--mode`, `--config`, optional report flags) and lint the configured scope.

- **2026-03-12 [Codex]:** `run_skill_evals.py --smoke` uses a contract-derived discovery response rather than domain-specific skill output; avoid false regex failures by defining dedicated `smoke_mode` cases and filtering smoke runs to those cases.

- **2026-03-11 [Codex]:** `run_skill_evals.py --runner codex` can fail with `mise ERROR No version is set for shim: codex` even when the skill reports look like content failures. Fix the shim first with `mise use -g npm:@openai/codex@0.114.0`; for `verify_recursive_skill_graph_artifacts --strict --run-state-check`, preserve historical run directories and record explicit waivers instead of backfilling synthetic mandatory artifacts.

- **2026-03-11 [Codex]:** Validator examples inside `SKILL.md` can drift from the actual script layout. The canonical validator entrypoints live under `utilities/skill-builder/scripts/` rather than repo-root `scripts/`, so verify the executable path before treating a validation example as authoritative.

- **2026-03-11 [Codex]:** Timeout tuning for Codex evals can make isolated case reruns pass while the same cases still time out inside a full-suite run. Treat timeout increases as provisional until the full suite reproduces the improvement, not just the filtered case.

- **2026-03-11 [Codex]:** In eval artifacts, `exit_code=124` plus `selected_skill=null`, zero trace events, empty `final.txt`, and empty `stdout.txt` means the case likely died before first response generation; treat it as startup/suite-budget contention, not as evidence that the skill wording or acceptance regex is wrong.

- **2026-03-11 [Codex]:** `run_skill_evals.py` can falsely mark `should_trigger: false` as selected when the model mentions a skill name while explicitly refusing it (for example, project-improver is overkill). Treat explicit final-response refusals as stronger evidence than reasoning or event mentions before scoring trigger selection.

- **2026-03-11 [Codex]:** When MCP filesystem read/write calls drop with `Transport closed` during small skill-doc edits, fall back to direct shell reads/writes for the exact target files, then run the canonical skill validators to confirm no drift.

- **2026-03-11 [Codex]:** In Agentation evals, `watch-mode-contract`, `critique-mode`, and `self-driving-compat` timed out at the default 60-second budget during a supposed fast-shard rerun, so they belong in the heavy-diagnostic lane with Codex-heavy timeouts rather than the quick regression lane.

- **2026-03-11 [Codex]:** In Agentation evals, `annotation-lifecycle` and `mobile-support-limit` also timed out at the default 60-second budget during the trimmed fast-shard run, so they belong in the heavy-diagnostic lane with Codex-heavy timeouts rather than the quick regression lane.

- **2026-03-11 [Codex]:** In isolated Agentation eval reruns, a Codex usage-limit failure can surface as exit code `1`, empty final output, and downstream regex misses. Check stderr for the explicit usage-limit message before treating the case as a skill regression.

- **2026-03-12 [Codex]:** In isolated Agentation heavy reruns, restored quota does not guarantee usable results: `mobile-support-limit` timed out with empty `final.txt` and `stdout.txt` on both Codex (180s) and Gemini (300s), and `watch-mode-contract` showed the same empty-output Codex timeout. Treat that signature as runner stall, not as evidence that the skill wording missed the regex.

- **2026-03-12 [Codex]:** In the same Agentation lane, runner health can differ by case and channel within minutes: `mobile-support-limit` moved from repeated LF timeouts to Gemini PASS with non-empty output, while `watch-mode-contract` remained LF on both Codex and Gemini. Gate queue progression per-case with the LF classifier instead of assuming whole-suite recovery.

- **2026-03-12 [Codex]:** `utilities/skill-builder/SKILL.md` can point at nonexistent `scripts/quick_validate.py`-style validator paths. Use `utilities/skill-builder/scripts/{quick_validate,skill_gate,analyze_skill,openclaw_skill_guard,run_skill_evals}.py` instead of repo-root `scripts/` paths.

- **2026-03-12 [Codex]:** In Ars Contexta queue updates, jq update expressions that use shell-expanded timestamps can silently fail or compile-break when variable escaping is wrong; use direct field assignments (status/completed) with explicit quoted timestamp strings, then immediately verify with jq selection.

- **2026-03-12 [Codex]:** In Ars Contexta skill-source lookups, `fd` with quoted wildcards like `fd "*pipeline*"` is parsed as regex and fails (`repetition operator missing expression`); use `fd --glob "*pipeline*"` for filename matching.

- **2026-03-15 [Gemini]:** Antigravity `/` slash command shows no skills when `~/.gemini/antigravity/skills` symlink and `~/.gemini/antigravity/skills.txt` are missing, or when `skills-antigravity/` in the repo is empty. → Run `bash scripts/sync_skills.sh` (or `just sync`) from this repo to rebuild the `skills-antigravity/` projection, create the symlink at `~/.gemini/antigravity/skills`, and write `skills.txt`. Also run `python3 scripts/sync_mcp.py` if MCP tools are missing. Restart Antigravity or type `/refresh` after syncing.

- **2026-03-16 [Gemini]:** Skill graph had 92 isolated nodes and 0 density. → Created 7 topic-map MOC files under `docs/skill-graphs/topic-maps/` (frontend-ui, backend-platform, agent-ops, product-strategy, security-ops, content-publishing, mobile-native, plus `index.md`) and added `## See Also` tables to 19 SKILL.md files with `[[wiki-link]]` cross-refs. After running `bash feedback-loop.sh`, graph health moved from HIGH drift to LOW/stable_state. Sync with `bash scripts/sync_skills.sh` after any batch SKILL.md edit.

- **2026-03-16 [Gemini]:** `docs_lint.py` interprets phrases like "config file" or "role config file" in markdown as `vague-file-reference` warnings — even inside wiki-link list items. → Replace generic phrasing with explicit path syntax like `agents/` dirs and named file extensions (e.g. `openai.yaml`) to silence the rule.

- **2026-03-17 [Gemini]:** Bulk-patching `## See Also` tables into SKILL.md files is safe for skill functionality and CI validation. The `structure-gate` and `skill-diagnostics` checks validate YAML frontmatter and required instruction sections — not trailing markdown metadata. `docs_lint.py` passes with 0 warnings provided wikilinks don't contain vague file references. See Also sections and `**Topic map:**` lines are invisible to agent invocation.

- **2026-03-17 [Gemini]:** Skill graph sink nodes (in-degree=0) make skills invisible to autonomous agent routing — an agent following See Also chains will never discover them. Fix: identify upstream skills that precede the sink in real workflows and add honest backlinks there, not vanity self-references. After fix: 7 sinks → 0.

- **2026-03-17 [Gemini]:** Static hand-authored See Also adjacency (hardcoded in a Python dict) becomes stale as skills are added. → Extract adjacency to `docs/skill-graphs/adjacency.yaml` so new skills update the data file, not the patcher script. `extract-skill-edges.py` can merge YAML seed with auto-extracted SKILL.md refs.

- **2026-03-17 [Gemini]:** `build-adjacency-yaml.py` deduplicates by `str(md.resolve())` but when symlinked skill copies (`skills-antigravity/` vs `utilities/`) resolve to different real paths, both are processed and the second write wins — causing `adjacency.yaml` to capture content from the wrong copy. → Always prefer the canonical location (e.g. `utilities/`) when deduplicating across symlinked skill projections; use `utilities/` as the sort priority or ignore `skills-antigravity/` in the builder.

- **2026-03-17 [Gemini]:** The `feedback-loop.sh` health report reads the Obsidian wikilink graph (topic-map MOC files in `docs/skill-graphs/topic-maps/`) not the SKILL.md See Also graph. The two are fundamentally different formats. The fix is not to change the `notes_dir` but to add a second SKILL.md-native stats block using `skill-edges.json` directly.

- **2026-03-17 [Gemini]:** When validating SKILL.md See Also vs adjacency.yaml drift, a threshold of 0 is too strict if the YAML is rebuilt from a different canonical SKILL.md than what the validator walks. Use `DRIFT_THRESHOLD=5` in CI and run `build-adjacency-yaml.py` + `validate-adjacency.py` in sequence to detect real drift vs. symlink-induced false positives.

- **2026-03-17 [Gemini]:** `scripts/query-graph.py` provides BFS-based skill routing with colour output, weight display, and `--reverse` in-link traversal. This is the fastest way for agents to answer "what should I chain with skill X" — append the one-liner to the agent-ops topic map and repo README to ensure discoverability.

- **2026-03-17 [Codex]:** `run_skill_evals.py` case failures with empty final output can be environment-caused (usage-limit/auth errors) rather than skill regression → inspect report `codex/stderr.txt` and `stdout.txt` before changing skill logic.

- **2026-03-17 [Codex]:** `run_skill_evals.py` and `docs_lint.py` false negatives are often caused by stale or missing skill sync artifacts; rebuild projections with `bash scripts/sync_skills.sh` and verify `/skills-antigravity/` plus `skills.txt` before blaming skill logic for missing invocations.

- **2026-03-17 [Codex]:** During skill install review, validating import quality before enforcing a full fold/merge-first deconflict pass against existing operational skills can delay the correct consolidation call. → Fix: run a mandatory capability overlap matrix first (existing skills vs incoming skill), record an explicit `merge|fold|improve-existing|install-new` decision before any install edits, and treat prior duplicate incidents as hard guardrails.

- **2026-03-27 [Codex]:** Local plugin marketplaces named `openai-curated` can collide with Codex's official synced marketplace namespace and surface `Plugin detail unavailable` or plugin read failures in the TUI. -> Use a unique local marketplace name (for example `agent-skills-local`) and keep local plugin manifests to the known runtime top-level shape without extra metadata keys.

- **2026-03-28 [Codex]:** Codex app-server resolves marketplace `source.path` from the repo root, not from the directory containing `marketplace.json`. -> Keep local marketplace entries as repo-root-relative paths like `./plugins/<plugin-name>` even when the marketplace file itself lives under `plugins/` or `.agents/plugins/`.
