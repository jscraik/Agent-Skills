# Tessl KnowledgeOS Capsule For Skill Factory

Use this reference when Skill Factory work depends on Tessl package layout,
registry behavior, review/eval workflow, MCP packaging, workspace/project setup,
install policy, or security-review boundaries.

## Source Evidence

- Primary capsule:
  `/Users/jamiecraik/dev/knowledge-OS/sources/docs/tessl-registry-knowledge-pack-2026-06-21.md`
- Bounded extraction worksheet:
  `/Users/jamiecraik/dev/knowledge-OS/extractions/tessl-registry-skill-factory/extraction-worksheet.md`
- Bounded source slice:
  `/Users/jamiecraik/dev/knowledge-OS/extractions/tessl-registry-skill-factory/source-slices/slice.tessl-registry-skill-factory.078cec81ef09.yaml`
- Related Skills SDK pack evidence:
  `/Users/jamiecraik/dev/knowledge-OS/exports/packs/pack.skills-sdk/`

The capsule was built from a 2026-06-28 crawl of `docs.tessl.io` and replaces
the older tile-first 2026-06-21 summary. Use it as source evidence, not as proof
that the local Tessl CLI, auth, project link, review run, eval run, registry
publish, or install policy currently passes.

The raw Tessl commands documented below (including `tessl project create`, `tessl project link`, `tessl project repair`) are non-executable vendor reference for understanding Tessl's project model. Do not invoke these raw project mutation commands directly. The Skills SDK wrapper controls all project setup and live evaluation; live scoring requires the wrapper's candidate-bound project-link receipt and must not repair, relink, update, or create a Tessl project outside the wrapper's governance.

## First Principles Gate

```yaml
first_principles_gate:
  desired_outcome: "Skill Factory can answer and act on Tessl plugin, registry, package, review, eval, MCP, workspace, install, and security-policy questions without re-deriving the capsule."
  user_specific_constraints:
    - "Keep KnowledgeOS producer evidence, Skill Factory package shape, Tessl review/eval proof, registry publication, hosted PR state, and runtime visibility as separate lanes."
    - "Do not point Tessl at live repo source for eval staging."
    - "Do not use publish, registry upload, package upload, or npx Tessl lanes unless explicitly requested and policy-approved."
  copied_assumption_rejected: "Do not copy the whole KnowledgeOS capsule into always-loaded SKILL.md files or preserve legacy tile wording as the default."
  fundamental_constraints:
    - "Current Tessl docs are plugin-first."
    - "Review scores are structural quality evidence, not behavior proof."
    - "Eval scores measure scenario lift or regression, not production, security, PR, or merge readiness."
    - "KnowledgeOS exports scenario intent; Skills SDK owns import, staging, execution, and proof claims."
  smallest_effective_mechanism: "One package-local Tessl reference plus load rules from the router and hardening lanes."
  artifact_decision: "IMPROVE_EXISTING"
  rejected_alternatives:
    - alternative: "BUILD_SKILL"
      reason: "Tessl behavior is cross-cutting context for existing Skill Factory lanes, not a separate workflow skill."
    - alternative: "ADD_MCP_TOOL"
      reason: "This change only needs reference knowledge; deterministic Tessl actions already belong to repo wrappers."
    - alternative: "DOCS_ONLY outside the plugin"
      reason: "The plugin must carry the answer surface with its package."
  evidence_required:
    - "Current KnowledgeOS Tessl capsule and bounded extraction worksheet."
    - "Skills SDK pack evidence only for scenario-quality and package-handoff patterns."
  validation_proof:
    - "Package/reference validation for Skill Factory surfaces."
    - "Focused route check for Skill Factory Tessl questions."
  stop_or_pivot_condition: "If current Tessl docs or local CLI behavior disagree with this reference, prefer current docs or wrapper output and update this file."
```

## Mental Model

- Tessl is an external evidence and distribution lane for agent context. It does
  not replace local repo validation, Skills SDK package verification, human code
  review, hosted CI, or runtime projection proof.
- The current package unit is the plugin. A plugin may contain skills, rules,
  bundled MCP servers, or any combination of those surfaces.
- Skills remain lazy-loaded procedural workflows with `SKILL.md` frontmatter
  and body instructions. Descriptions drive activation and must be specific.
- Rules are eagerly loaded policy or guidance. Treat them differently from
  skills when choosing package shape.
- Tessl projects are the durable repo-linked identity for eval runs and other
  repository-connected data.

## Current Package Layout

Prefer plugin-first layout for new Skill Factory and Skills SDK handoffs:

```text
my-plugin/
  .tessl-plugin/
    plugin.json
  skills/
    my-skill/
      SKILL.md
      references/
      scripts/
      assets/
  rules/
  .mcp.json
  tessl.json
```

Manifest boundaries:

- `.tessl-plugin/plugin.json` is the plugin manifest.
- `tessl.json` is the project manifest that records dependencies, project
  links, managed or vendored mode, and verification configuration.
- Plugin-bundled `.mcp.json` declares MCP servers shipped inside the plugin.
- Project `.mcp.json` wires a consuming repo or agent to Tessl MCP. Do not
  conflate it with bundled plugin MCP metadata.
- `tile.json` is legacy/migration terminology. Current docs say plugin metadata
  takes precedence when both legacy tile metadata and plugin metadata are
  present.

Core plugin manifest fields from the capsule:

```json
{
  "name": "workspace/plugin-name",
  "version": "1.0.0",
  "description": "Short package description",
  "private": true,
  "rules": "./rules/",
  "skills": "./skills/",
  "mcpServers": "./.mcp.json"
}
```

Use relative paths inside plugin packages. Avoid local absolute paths, generated
runtime projection paths, and host-specific cache locations in plugin-owned
metadata.

## Command Map

Setup and health:

```bash
tessl login
tessl whoami
tessl init --agent codex
tessl doctor
tessl status
tessl list
```

Package discovery and install:

```bash
tessl search "api design"
tessl install tessl-labs/api-design-patterns
tessl install myworkspace/my-plugin@1.0.0
tessl install file:./plugins/my-plugin
tessl update
tessl outdated
```

Plugin development:

```bash
tessl plugin new --name myworkspace/my-plugin --path ./my-plugin
tessl plugin lint ./my-plugin
tessl plugin pack --output ./dist ./my-plugin
```

Skill development:

```bash
tessl skill new
tessl skill import ./path/to/my-skill --workspace myworkspace
tessl skill lint ./my-skill
```

Review:

```bash
tessl review run ./my-skill --workspace engteam
tessl review run ./my-skill --workspace engteam --json --threshold 80
tessl review fix ./my-skill --workspace engteam
tessl review view --last
tessl review list
```

Scenario and eval workflow:

```bash
tessl project create <project-name> --workspace <workspace>
tessl project link --workspace <workspace>
tessl project repair --workspace <workspace> --project <project-name>
tessl scenario generate <path/to/plugin> --count=5
tessl scenario list --mine
tessl scenario download --last
tessl eval run <path/to/plugin>
tessl eval run <path/to/plugin> --context "plugins/my-plugin"
tessl eval list
tessl eval view --last
```

Security and inventory:

```bash
tessl inventory import --org your-org --workspace engteam
tessl security-review run ./path-to-skill --workspace engteam
tessl security-review run ./path-to-skill --workspace engteam --json --fail-on high
```

Repository review and verifiers:

```bash
tessl change review --base origin/main --github
tessl change risk --base origin/main --fail-if-review-required --json
tessl change verify --dry-run --all --show-files
```

## Skill Factory Operating Rules

- Use plugin-first language by default. Use tile language only for migration,
  legacy package diagnosis, or current docs that explicitly mention tiles.
- Before Tessl evals, use the explicit Skills SDK project-setup wrapper rather
  than the raw commands in this reference. Its project-link receipt is bound to
  the current source and scenario candidate; live scoring blocks on a missing,
  stale, or mismatched receipt.
- For Skill Factory-owned plugin skills, project identity should resolve to the
  plugin project, for example `jscraik/skill-factory`, not a leaf skill project.
- For review quality, prefer `tessl review run` over deprecated
  `tessl skill review`. The capsule says `tessl skill review` remains
  available only as a transitional path through July 2026.
- For behavior quality, use scenario/eval workflows and compare baseline versus
  context-injected runs.
- Downloaded `evals/` from Tessl scenario generation can land relative to the
  current working directory, while `tessl eval run <path/to/plugin>` expects
  evals inside the plugin directory. Move or stage generated scenarios into the
  plugin-shaped package before running evals.
- In this repo, run Tessl evals through `./bin/ask evals ...` wrappers where
  available so staging happens under `/tmp/ask-tessl-*`, not against live
  canonical source.
- Preserve staged Tessl evidence. Archive prior stable temp contents instead of
  deleting them before reruns.
- Keep registry publication and public sharing out of ordinary hardening unless
  Jamie explicitly asks for that lane.
- Do not use `npx tessl`, registry upload, package upload, `tessl plugin publish`,
  or `tessl skill publish` from Skill Factory hardening by default.

## Evidence Lanes

Keep these claims separate:

| Lane | What It Can Prove | What It Does Not Prove |
| --- | --- | --- |
| KnowledgeOS capsule | Current source crawl summary, terminology, command map, source map, and evidence boundaries | Local Tessl auth, CLI support, project link, review/eval pass, registry readiness |
| Skills SDK pack evidence | Candidate scenario intent, package handoff patterns, source-backed eval ideas | Behavior proof, Tessl readiness, scenario quality approval |
| Skill Factory package validation | Local package shape, reference parseability, repo contract compliance | External Tessl score, registry state, Desktop/runtime visibility |
| Tessl Review | Structural and best-practice quality for a skill or plugin | Behavior lift, security safety, CI, human review, publish readiness |
| Tessl Eval | Baseline delta or regression for the specific scenario suite | Production readiness, security review, PR mergeability, registry trust |
| Tessl Security Review / policy | Security signals, install policy, source-age or publisher trust constraints | Behavior quality or task success |
| Registry publish/install | Dependency availability and package-manager state | Local code correctness, review resolution, CI pass, runtime picker visibility |
| Runtime projection | Codex or agent loader can see a skill/plugin | Package quality, Tessl proof, registry safety |

When answering questions, state which lane the answer uses and whether the lane
was verified in the current turn.

## KnowledgeOS And Skills SDK Consumption

Use the Tessl capsule for current plugin, registry, package, review, eval, MCP,
install, workspace, and security-policy behavior.

Use the Skills SDK pack evidence only for scenario-quality and package-handoff
patterns. The pack exports 10 candidate scenarios and explicitly says they are
below the 20 gold-standard scenario floor for behavioral live Tessl readiness.
KnowledgeOS owns candidate scenario intent and provenance; Skills SDK owns
canonical import, scenario-quality review, scorer calibration, Tessl staging,
execution, and proof claims.

Do not claim a KnowledgeOS export proves Skill Factory behavior. Import selected
material into package references or evals, validate the package, then run the
appropriate local or Tessl proof lane.

## Answer Checklist

Before answering a Tessl-related Skill Factory question:

1. Identify whether the question is about package layout, install, review,
   eval, MCP, project/workspace, security policy, registry, rollout, or proof.
2. Load this reference and the smallest source evidence needed.
3. Prefer current plugin terminology unless the user asks about tile migration.
4. Name the evidence lane used.
5. Keep unavailable live state as `not checked` or `blocked`; do not infer it
   from the capsule.
6. Route execution through repo wrappers when the question turns into a local
   validation or eval command.

## Capsule Limits

This reference does not prove:

- local `tessl` binary support for every documented command or flag;
- Tessl authentication or workspace access;
- project link health for this repo;
- Skill Factory package readiness;
- Tessl Review or Tessl Eval success;
- registry publication, installability, or security-policy approval;
- Codex Desktop plugin loadability or runtime picker visibility.

If live behavior disagrees with this file, update the reference from current
docs or wrapper output and report the drift as evidence, not as an agent memory
problem.
