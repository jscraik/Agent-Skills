# Ars Contexta Conversion Map

Use this reference when converting [`agenticnotetaking/arscontexta`](https://github.com/agenticnotetaking/arscontexta) from its Claude-oriented package shape into a Codex or OpenAI plugin package without dropping important surfaces.

## Table of Contents
- [Goal](#goal)
- [Source snapshot](#source-snapshot)
- [Conversion posture](#conversion-posture)
- [Target package layout](#target-package-layout)
- [Source-to-target mapping](#source-to-target-mapping)
- [Generated runtime outputs](#generated-runtime-outputs)
- [Hook conversion notes](#hook-conversion-notes)
- [Manifest mapping](#manifest-mapping)
- [Marketplace mapping](#marketplace-mapping)
- [Terminology mapping](#terminology-mapping)
- [Do-not-lose inventory](#do-not-lose-inventory)
- [Suggested conversion sequence](#suggested-conversion-sequence)
- [Validation checklist](#validation-checklist)

## Goal
Convert Ars Contexta into an organized Codex plugin package while keeping three classes of information separate:

1. package-owned plugin surfaces that should ship inside the plugin;
2. generated runtime outputs that should be created by setup flows, not bundled as static plugin assets;
3. Claude-only or provisional behavior that must be carried forward as migration notes rather than claimed as working Codex behavior.

This separation prevents the most common conversion failures:
- losing source material that setup depends on;
- bundling generated vault state as if it were part of the plugin package;
- claiming hook behavior that Codex does not currently execute.

## Source snapshot
At the time of mapping, the Ars Contexta source repo exposes these top-level surfaces:

- `.claude-plugin/`
- `agents/`
- `generators/`
- `hooks/`
- `methodology/`
- `platforms/`
- `presets/`
- `reference/`
- `Infrastructure/scripts/`
- `skill-sources/`
- `skills/`
- `README.md`
- `LICENSE`

Important observed characteristics:
- `.claude-plugin/plugin.json` contains publisher metadata but not full Codex manifest fields.
- `.claude-plugin/marketplace.json` uses Claude marketplace structure, not Codex marketplace structure.
- `skills/` contains plugin-level, always-available command surfaces.
- `skill-sources/` contains generated or derived runtime skill templates, not pure package-owned always-on skills.
- `hooks/hooks.json` uses `SessionStart` and `PostToolUse`; `PostToolUse` is not part of the current Codex hook contract documented by this repo.
- `agents/knowledge-guide.md` is a useful optional agent surface.
- `presets/`, `reference/`, `methodology/`, and parts of `platforms/` contain source-of-truth material that setup flows likely rely on.

## Conversion posture
Treat Ars Contexta as a two-layer conversion.

### Layer 1: package-owned plugin surfaces
These are the files and directories that should ship in the Codex plugin package itself.

### Layer 2: generated runtime outputs
These are the artifacts a setup flow creates in a user workspace or vault. They should be described, templated, or generated, but not bundled as if they were static plugin package surfaces.

Do not collapse these layers into one folder tree.

## Target package layout

```text
Plugins/arscontexta/
  .codex-plugin/plugin.json
  README.md
  LICENSE
  skills/
    setup/
    help/
    tutorial/
    ask/
    health/
    recommend/
    architect/
    add-domain/
    reseed/
    upgrade/
  Infrastructure/references/
    arscontexta-quickstart.md        # optional reference text; not a runtime prompt surface
    arscontexta-setup-checklist.md
  hooks.json
  hooks/
    Infrastructure/scripts/
      session-orient.sh
  agents/                            # optional
    knowledge-guide.md
  .mcp.json                          # optional, but useful if shipping the qmd starter config
  .app.json                          # optional metadata shell under the current local contract
  Infrastructure/references/
    methodology/
    presets/
    reference/
    platforms/
    generators/
    migration-notes.md
  Infrastructure/templates/
    skill-sources/
```

Notes:
- Runtime packaging remains skill-first; if prompt text is retained, keep it under `Infrastructure/references/` as migration/support documentation, not as a runtime `prompts/` surface.
- a valid first pass may ship no `prompts/` directory at all if the conversion does not need prompt assets.
- `agents/` is optional and should only contain agent assets that remain useful in Codex.
- `Infrastructure/references/` is the correct place to preserve rich source material required by setup, migration, or generation flows.
- `Infrastructure/templates/skill-sources/` is the preferred landing zone for Ars Contexta generated-skill source material because those files are closer to generation inputs than to ordinary prose references.

## Source-to-target mapping

| Source surface | Target surface | Keep | Notes |
| --- | --- | --- | --- |
| `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | Yes | Translate fields into Codex manifest shape and add missing required fields. |
| `.claude-plugin/marketplace.json` | `.agents/Plugins/marketplace.json` | Yes | Rewrite entry schema; do not copy Claude marketplace format directly. |
| `README.md` | `README.md` | Yes | Keep install story, but rewrite Claude command language to Codex terminology. |
| `LICENSE` | `LICENSE` | Yes | Preserve license as-is if it remains valid for the converted package. |
| `skills/add-domain` | `skills/add-domain` | Yes | Plugin-owned skill. |
| `skills/architect` | `skills/architect` | Yes | Plugin-owned skill. |
| `skills/ask` | `skills/ask` | Yes | Plugin-owned skill. |
| `skills/health` | `skills/health` | Yes | Plugin-owned skill. |
| `skills/help` | `skills/help` | Yes | Plugin-owned skill. |
| `skills/recommend` | `skills/recommend` | Yes | Plugin-owned skill. |
| `skills/reseed` | `skills/reseed` | Yes | Plugin-owned skill. |
| `skills/setup` | `skills/setup` | Yes | Core migration and generator entrypoint. |
| `skills/tutorial` | `skills/tutorial` | Yes | Plugin-owned onboarding skill. |
| `skills/upgrade` | `skills/upgrade` | Yes | Plugin-owned maintenance skill. |
| `skill-sources/*` | `Infrastructure/templates/skill-sources/` | Partial | Preserve as generated-skill source templates; do not present as always-on plugin skills by default. |
| `hooks/hooks.json` | `hooks.json` | Partial | Keep only verified Codex-compatible behavior in working hooks. |
| `hooks/Infrastructure/scripts/session-orient.sh` | `hooks/Infrastructure/scripts/session-orient.sh` | Partial | Good candidate for Codex `SessionStart`, but requires env and payload adaptation. |
| `hooks/Infrastructure/scripts/write-validate.sh` | `Infrastructure/references/migration-notes.md` | No direct runtime carry-over | Claude `PostToolUse` specific; keep as migration note or future work item. |
| `hooks/Infrastructure/scripts/auto-commit.sh` | `Infrastructure/references/migration-notes.md` | No direct runtime carry-over | Async `PostToolUse` behavior is provisional or unsupported in current Codex hook contract. |
| `hooks/Infrastructure/scripts/vaultguard.sh` | `hooks/Infrastructure/scripts/` or `Infrastructure/references/` | Partial | Reuse only if decoupled from Claude-specific expectations. |
| `agents/knowledge-guide.md` | `agents/knowledge-guide.md` | Optional | Good optional agent asset. |
| `presets/` | `Infrastructure/references/presets/` | Yes | Preserve preset definitions; setup likely depends on them. |
| `reference/` | `Infrastructure/references/reference/` | Yes | Preserve support corpus; do not flatten into `SKILL.md`. |
| `methodology/` | `Infrastructure/references/methodology/` | Yes | Preserve derivation methodology and supporting docs. |
| `generators/` | `Infrastructure/references/generators/` or `Infrastructure/scripts/` | Partial | Keep generator logic if used by setup; otherwise capture as migration support material. |
| `platforms/README.md` | `Infrastructure/references/platforms/README.md` | Yes | Preserve platform-orientation guidance alongside platform-specific adapters. |
| `platforms/claude-code/*` | `Infrastructure/references/platforms/claude-code/` | Yes | Preserve as migration reference, not as Codex runtime config. |
| `platforms/shared/*` | `Infrastructure/references/platforms/shared/` | Yes | Preserve if setup or generation logic reads it. |
| `Infrastructure/scripts/` | `Infrastructure/scripts/` or `Infrastructure/references/` | Partial | Keep only scripts still needed in Codex package workflows. |

## Generated runtime outputs
These source concepts should be treated as generated outputs of `setup`, not as package-owned static plugin surfaces:

- generated processing skills derived from `Infrastructure/templates/skill-sources/`;
- vault or workspace operational state under `.arscontexta`, `Infrastructure/ops/`, `self/`, or similar runtime folders;
- `CLAUDE.md`;
- `.claude/settings.json`;
- generated `.claude/hooks/` files;
- user-specific note structures, inboxes, templates, or local derivation state.

Recommended handling:
- describe these outputs in `skills/setup`;
- keep templates and source material in `Infrastructure/templates/`, `Infrastructure/references/`, or `Infrastructure/scripts/`;
- write generated files into the user target workspace during setup;
- never validate these generated outputs as if they were mandatory plugin package root surfaces.

## Hook conversion notes
Ars Contexta hook conversion must be conservative.

### Verified candidate carry-over
- `SessionStart` orientation behavior can map into Codex `hooks.SessionStart` if:
  - the command script is adapted away from Claude-specific environment variables;
  - stdin payload assumptions are updated to Codex runtime schema;
  - output is aligned to the Codex `SessionStart` output schema.

### Provisional or non-portable behavior
- `PostToolUse` write validation is not part of the current Codex hook contract in this repo.
- async post-write auto-commit should not be represented as working Codex behavior.
- any hook depending on Claude project config files should be documented as migration-only until Codex runtime parity is verified.

Recommended first-pass `hooks.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "./hooks/Infrastructure/scripts/session-orient.sh",
        "timeoutSec": 10
      }
    ],
    "Stop": []
  }
}
```

Document deferred behavior in `Infrastructure/references/migration-notes.md`.

## Manifest mapping
Map Ars Contexta metadata into the required Codex manifest fields.

| Claude source field | Codex target field | Mapping note |
| --- | --- | --- |
| `name` | `name` | Keep kebab-case plugin identifier. |
| `version` | `version` | Preserve semver if the converted package represents the same release line. |
| `description` | `description` | Keep concise package summary. |
| `author.name` | `author.name` | Preserve. |
| missing | `author.email` | Add placeholder or verified contact value; Codex contract requires it. |
| `author.url` | `author.url` | Preserve. |
| `homepage` | `homepage` | Preserve if still canonical. |
| `repository` | `repository` | Preserve. |
| `license` | `license` | Preserve SPDX identifier. |
| `keywords[]` | `keywords[]` | Preserve and extend if needed. |
| missing | `skills` | Set to `./skills/`. |
| missing | `hooks` | Set to `./hooks.json`. |
| optional qmd docs | `mcpServers` | Set to `./.mcp.json` when shipping MCP starter config. |
| missing | `apps` | Set to `./.app.json` when shipping app metadata shell. |
| missing | `interface.*` | Fill from package UX metadata, not from Claude manifest. |

Recommended `interface.capabilities` for first pass:
- `Interactive`
- `Write`

Recommended `interface.defaultPrompt`:
- a setup-oriented starter prompt, not a copied Claude slash command string.

## Marketplace mapping
Do not copy `.claude-plugin/marketplace.json` directly.

Claude entry shape:
- owner metadata
- plugin list entry
- `source: "./"`
- `strict: false`
- lowercase category

Codex entry shape required by this repo:

```json
{
  "name": "arscontexta",
  "source": {
    "source": "local",
    "path": "./Plugins/arscontexta"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

Carry-over rules:
- preserve plugin `name`;
- rewrite `source` into object form with `source: "local"` and plugin path;
- add marketplace `interface.displayName` at the root when the target marketplace is created or refreshed;
- always add `policy.installation`, `policy.authentication`, and `category`;
- accept legacy flat `installPolicy` and `authPolicy` only as temporary migration inputs, not as fresh scaffold output;
- ignore Claude-specific `strict` because it is not part of the Codex marketplace contract here.

## Terminology mapping
Apply the canonical terminology map during docs and asset conversion.

| Claude-oriented term | Codex term | How to handle in Ars Contexta |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | Required rename. |
| `/plugin ...` install commands | plugin install instructions | Rewrite docs to Codex plugin workflow language. |
| slash commands | prompts or skills | Use `prompts/` for true prompt assets and `skills/` for durable workflow skills. |
| `commands/` | `prompts/` | Only when the source content is actually command-style prompt content rather than a reusable skill workflow. |
| generated command set | generated runtime skills or prompts | Do not blindly convert to always-on plugin prompts. |
| `.claude/settings.json` | no direct package equivalent | Treat as generated runtime or migration-only reference. |
| Claude hook env vars | Codex hook env or stdin contract | Adapt per runtime, do not preserve names blindly. |

Important distinction:
- `skills/` in Ars Contexta stays `skills/`.
- only Claude slash-command style command surfaces that are actually prompt-like map to `prompts/`.
- not every Claude command should become a prompt; some belong as skills, some as generated runtime outputs.

## Do-not-lose inventory
During conversion review, explicitly verify that these information classes are either preserved or intentionally deferred:

- plugin-level skills under `skills/`;
- generated-skill templates from `skill-sources/`;
- `agents/knowledge-guide.md`;
- hook intent and script bodies, even if not fully portable;
- preset files under `presets/`;
- methodology and reference docs;
- generator support material;
- platform guidance including `platforms/README.md`;
- optional qmd `.mcp.json` example from the README;
- install, health, tutorial, and upgrade workflow documentation;
- distinction between package-owned capabilities and generated vault outputs.

If any of the above is omitted, record the omission as an intentional defer with rationale.

## Suggested conversion sequence
1. Scaffold `Plugins/arscontexta/` with `plugin_builder.py scaffold`.
2. Fill `.codex-plugin/plugin.json` using the mapping above.
3. Copy `README.md` and `LICENSE`, then rewrite Claude-specific terminology.
4. Convert plugin-owned `skills/` first.
5. Convert command-like or prompt-like source material into `skills/` entries; if a lightweight entrypoint is useful, use `interface.defaultPrompt` in the manifest instead of emitting a runtime `prompts/` surface.
6. Preserve `agents/knowledge-guide.md` as optional agent asset.
7. Add `.mcp.json` starter config only if the qmd example is still valid for the intended deployment.
8. Convert only verified hook behavior into `hooks.json`.
9. Preserve `presets/`, `reference/`, `methodology/`, and migration-critical platform docs under `Infrastructure/references/`.
10. Preserve `skill-sources/` under `Infrastructure/templates/skill-sources/`.
11. Record deferred runtime-generation behavior in `Infrastructure/references/migration-notes.md`.

## Validation checklist
After conversion, run these checks:

```bash
python3 Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py validate Plugins/arscontexta --require-marketplace --marketplace-path .agents/Plugins/marketplace.json --show-terminology-map
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/arscontexta/skills/setup
python3 Skills/skill-builder/Infrastructure/scripts/skill_gate.py Plugins/arscontexta/skills/setup
python3 Skills/skill-builder/Infrastructure/scripts/analyze_skill.py Plugins/arscontexta/skills/setup
python3 Skills/skill-builder/Infrastructure/scripts/openclaw_skill_guard.py Plugins/arscontexta/skills/setup --mode both
```

Recommended package-level review questions:
- Did any generated runtime artifact accidentally get bundled as a required plugin surface?
- Did any Claude-only hook behavior get represented as verified Codex runtime behavior?
- Did any setup-critical reference corpus get dropped instead of preserved under `Infrastructure/references/`?
- Did any command-style source content get mislabeled as a skill or vice versa?
