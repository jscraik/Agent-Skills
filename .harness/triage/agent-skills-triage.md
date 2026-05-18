# Agent Skills Structural Triage

Repository: `agent-skills`

Triage date: 2026-05-07

Input artifacts:

- `.harness/features/agent-skills-intent.md`
- `.harness/features/agent-skills-repo-intent-and-moat.md`
- `.harness/review/agent-skills-architecture-review.md`

Purpose:

This document is the execution compression layer between architecture cognition and implementation planning. It does not restate the intent or review. It decides what matters, what should become work, what should be ignored, and where execution pressure belongs.

Operating posture:

- Keep the hybrid platform ambition.
- Make proof-driven control-plane behavior the trust mechanism.
- Treat broad skill/plugin breadth as exploration until workflows earn promotion.
- Split `Infrastructure/scripts/lib/ask/commands/skills.py` first.
- Keep Linear shape coarse: a few initiatives, a few projects, and only issue-ready work after the owning initiative is clear.
- Delete aggressively by class, but classify and reference-check before removing files.
- Do not let architecture review findings become an undifferentiated backlog.

Confidence labels:

- High: repeated across prior artifacts with concrete repo evidence.
- Medium: strongly inferred from artifacts but needs implementation verification.
- Low: plausible strategic judgment with limited direct proof.

## 1. Executive Triage Summary

The repository has five execution priorities. Everything else is secondary unless it directly supports one of these. The first execution move should remain structural: split `Infrastructure/scripts/lib/ask/commands/skills.py` before adding more proof machinery or platform breadth. Proof taxonomy is still P0, but it should not become a reason to keep pouring feature logic into the current command module.

| Rank | Priority | Category | Why It Matters | Execution Artifact | Decision |
|---|---|---|---|---|---|
| 1 | Split `Infrastructure/scripts/lib/ask/commands/skills.py` by bounded context | Architectural, Technical Debt, Agent-Native | It is the largest change-amplification point and the first place future agents will lose local reasoning. | Refactor program plus Linear project | Do now |
| 2 | Make `repo doctor` the canonical first command and next-action router | Agent-Native, Operational, Governance | It compresses repo truth into one deterministic control surface. | Linear initiative plus command enhancement issues | Do now |
| 3 | Build outcome proof as the skill promotion mechanism | Strategic, Operational, Agent-Native | This is the moat filter. Catalog breadth without proof is noise. | ADR plus eval program plus Linear initiative | Do now |
| 4 | Burn down repo-surface ownership debt | Governance, Technical Debt, Agent-Native | Unclassified artifacts make the repo cognition-hostile. | Cleanup/refactor program plus anti-drift enforcement | Do next |
| 5 | Clarify CI/check ownership and deprecation budgets | Governance, Operational | Prevents gates from becoming ceremony and legacy from becoming permanent architecture. | ADR plus small governance project | Do next |

High-leverage signal:

- deterministic command contracts;
- source/projection/runtime separation;
- command handles;
- runtime budget;
- repo doctor;
- outcome proof;
- path ownership;
- skill promotion discipline;
- fresh-agent cognition compression.

Medium-leverage signal:

- CI ownership map;
- deprecation manifest;
- skill overlap analytics;
- generated onboarding/orientation output;
- docs glossary enforcement.

Low-leverage signal:

- catalog-size improvements without proof;
- more docs that restate live command output;
- more workflow names without smaller command surfaces;
- broad portability work before the golden path is sharp.

False sophistication:

- large command modules presented as power;
- governance breadth presented as trust;
- plugin count presented as moat;
- structural audit presented as outcome proof;
- historical artifact retention presented as knowledge.

Findings that should not become work items:

- "Add more skills" as a standalone task.
- "Add more plugin categories" as a standalone task.
- "Document everything more thoroughly" without replacing or validating an existing surface.
- "Add another governance check" without owner, proof target, and failure action.
- "Make the platform portable" before local proof and adapters are stable.
- "Create broad architecture diagrams" unless they are generated from live command/source data.
- "Create one Linear issue per review finding." The triage should create a few initiatives and route work beneath them, not explode the architecture review into dozens of parallel tickets.

## 2. Immediate Architectural Risks

| Risk | Severity | Likelihood | Blast Radius | Why It Matters | Recommended Response |
|---|---|---|---|---|---|
| `skills.py` continues accumulating skill/plugin/proof/projection logic | Critical | High | All skill lifecycle commands, future refactors, agent local reasoning | It is already 3001 lines and mixes bounded contexts. New work here compounds the core fragility. | Block new feature logic in `skills.py` except extraction. Start service extraction with plugin cache, catalog, projection, and proof boundaries. |
| Catalog parity remains blocked | High | Medium-High | Runtime discovery, source/projection trust, skill handles | The source/projection thesis requires current generated/runtime state. | Treat catalog parity as release-blocking. Route to `doctor-catalog` and record recurrent root causes. |
| Repo-surface debt keeps competing with source truth | High | High | Fresh-agent cognition, docs trust, cleanup safety | Thousands of surface findings mean stale artifacts and generated material can look authoritative. | Create a repo-surface burn-down project with categories, thresholds, and deletion/quarantine rules. |
| Outcome proof stays weaker than structure/reachability proof | High | High | Moat, skill promotion, product credibility | The artifacts repeatedly warn that structure is not proof of agent improvement. | Create an ADR defining proof levels and an eval program for core skills. |
| `repo doctor` remains one useful command among many instead of the canonical entrypoint | High | Medium | Agent onboarding, validation routing, closeout confidence | Future agents need one current truth surface and one next action. | Add `repo doctor --next` or equivalent, link it from primary docs, and preserve outputs as CI artifacts. |
| CI provider/check ownership remains ambiguous | Medium | Medium | Merge confidence, governance edits, agent routing | GitHub Actions is broad while CircleCI appears thin; provider roles can drift. | Generate or maintain a required-check ownership map and enforce with parity checks. |
| Legacy/compatibility paths lack expiry | Medium | High | Hidden branching, tactical design, future migrations | Compatibility without deletion dates becomes permanent architecture. | Add deprecation budgets with owner, removal condition, max age, and validation coverage. |

## 3. Strategic Findings

### Strategic Finding 1: The core product is trusted agent workflow execution, not skill inventory

Classification:

- Strategic
- Agent-Native
- Governance

Fact:

- Both intent artifacts say the project is strongest when it makes agents remember, choose, validate, and close out better.
- The review says the moat is broad skill/plugin capability constrained by operational proof, not catalog breadth alone.

Interpretation:

The broad workbench can remain, but it must be subordinated to proof. Skill count is only useful as exploration. Trusted skill count is the strategic metric.

Operational impact:

- Changes what enters Linear.
- Makes skill promotion harder.
- Prevents catalog growth from masquerading as product progress.

Strategic impact:

- Protects the actual moat.
- Makes commercial positioning sharper: "agents stop forgetting and prove outcomes."

Recommended artifact:

- ADR: `ADR: Outcome Proof Is The Promotion Mechanism`
- Linear initiative: `Outcome-Proven Agent Workflow Core`

Confidence: High.

### Strategic Finding 2: Hybrid platform is correct, but hierarchy must be explicit

Classification:

- Strategic
- Governance

Fact:

- The architecture review was refined to preserve hybrid ambition: broad workbench plus proof-driven control plane.

Interpretation:

The platform should not choose between breadth and control. It should separate experimental breadth from trusted core. That distinction should become product language and governance policy.

Operational impact:

- Adds clear states: experimental, latent, trusted, default-visible, deprecated.
- Prevents premature deletion of useful exploratory skill/plugin work.

Strategic impact:

- Makes the workbench valuable without letting it erode trust.

Recommended artifact:

- ADR: `ADR: Skill Lifecycle States And Promotion Gates`

Confidence: High.

### Strategic Finding 3: Local-first remains the right default

Classification:

- Strategic
- Operational

Fact:

- The intent file recommends staying local-first until proof is strong.
- Commercial portability is identified as underbuilt but premature portability is flagged as abstraction multiplication.

Interpretation:

Portability should be adapter-driven later. It should not drive the current architecture.

Operational impact:

- Avoids platform abstractions that do not help the golden path.
- Keeps execution grounded in the repo's actual Codex/harness environment.

Strategic impact:

- Protects velocity while proof is immature.

Recommended artifact:

- ADR only if portability work is proposed.

Confidence: Medium-High.

## 4. Architectural Findings

| Finding | Leverage | Category | What It Should Become | What It Should Not Become | Confidence |
|---|---|---|---|---|---|
| `skills.py` is the first structural choke point | High | Architectural, Technical Debt | Refactor program with service extraction | A full rewrite or behavior change project | High |
| `Infrastructure/bin/ask` should shrink after `skills.py` | High | Architectural, Agent-Native | Follow-on refactor program | First refactor target | High |
| `selection_policy.py` is a deep module to preserve | High | Architectural, Agent-Native | Anti-drift protected boundary | A dumping ground for every policy exception | High |
| `command_surface.py` is moat-critical but nearing size risk | High | Architectural, Agent-Native | Protected interface plus small extraction only when needed | Merge skill discovery/projection logic into it | High |
| `repo doctor` should become the canonical orchestrating health interface | High | Architectural, Operational | Command enhancement and docs routing | Another parallel health command | High |
| Generated/runtime/source boundaries must stay hard | High | Architectural, Governance | Enforcement and education | Optional convention | High |
| `.skillsets/**` ownership must be resolved | Medium-High | Architectural, Governance | Decision plus CI allowlist/generator contract | Ad hoc cleanup | High |

Architectural work to ignore for now:

- Big architecture re-map diagrams.
- New plugin system abstractions.
- New orchestration frameworks.
- General-purpose portability layer.
- Reorganizing all docs before command truth is compressed.

## 5. Operational Findings

### Operational Finding 1: The validation stack is valuable but needs a clearer daily loop

Fact:

- Prior artifacts identify `repo doctor`, docs lint, `verify-work --fast`, and `validate_all.sh` as different confidence layers.

Interpretation:

Full validation should not be the only trustworthy signal. `repo doctor` should guide daily work; full validation should preserve release confidence.

Execution routing:

- Linear project: `Repo Doctor As Daily Control Loop`
- Issues:
  - Add next-action-only output.
  - Preserve doctor output as CI artifact.
  - Document doctor as first command.

Confidence: High.

### Operational Finding 2: Outcome proof is an eval program, not a docs task

Fact:

- Artifacts distinguish reachability, structural audit, quality, and outcome proof.

Interpretation:

The repo needs evaluable proof semantics. A skill passing structural audit should not be called effective.

Execution routing:

- Eval program: `Core Skill Outcome Proof`
- ADR: proof taxonomy.
- Linear issues for the first 3-5 core skills.

Confidence: High.

### Operational Finding 3: CI ownership is a governance risk, not a CI optimization task

Fact:

- The review flags GitHub Actions as broad and CircleCI as thin relative to claimed ownership.

Interpretation:

Do not optimize CI first. Clarify what each check proves.

Execution routing:

- Governance change: required-check ownership map.
- Linear issue: generate/check required-check parity.

Confidence: Medium.

## 6. Governance Findings

| Finding | Leverage | Governance Response | Blocker Rule |
|---|---|---|---|
| New logic in `skills.py` increases drift | High | Add policy: extraction required before feature expansion | Block new feature logic in `skills.py` while over threshold |
| Catalog parity block undermines trust | High | Treat parity as release-blocking | Block releases and core promotion |
| Repo-surface debt is unclassified cognition risk | High | Add burn-down thresholds | Block new unclassified generated/runtime artifacts |
| Default-visible skills need proof | High | Promotion gates | Block new default-visible skills without proof status |
| Compatibility paths lack expiry | Medium | Deprecation budget | Warn initially, block after policy adoption |
| CI checks lack explicit ownership | Medium | Required-check ownership map | Block required-check changes without map updates |

Governance work to avoid:

- More checklist prose without enforcement.
- New mandatory review rituals before existing gates are compressed.
- Review swarms unless they produce artifacts and have a precise risk surface.
- More quality categories that do not change merge or promotion decisions.

## 7. Agent-Native Findings

### What future agents need most

1. One current truth command.
2. One next action.
3. One canonical source pointer.
4. One validation lane.
5. One stop condition.

The current architecture has the pieces, but the pieces are too distributed.

High-leverage agent-native work:

- `repo doctor --next`;
- `skills explain` showing canonical source, handle, visibility, limitations, and smallest validation;
- `skills improve` returning one primary recommendation instead of a buffet;
- `repo closeout --changed` inferring validation/sync needs;
- generated onboarding from live command output.

Low-leverage agent-native work:

- more verbose skill prose;
- more router skills without overlap analytics;
- more generated handles if skill quality is unproven;
- more memory surfaces without indexing and freshness.

Anti-agent architecture:

- giant command modules;
- ambiguous generated/source surfaces;
- stale artifacts in primary browsing paths;
- overlapping skills with similar triggers;
- blockers without exact next commands;
- proof payloads that do not say what kind of proof they represent.

## 8. Complexity Without Leverage

| Item | Why It Exists | Why It Survived | Why It Is Harmful Now | Action |
|---|---|---|---|---|
| Giant `skills.py` module | Central place for skill command behavior | Convenience and fast feature growth | It hides domain boundaries and raises change cost | Split |
| Large `Infrastructure/bin/ask` front controller | Single CLI entrypoint | Stable user contract and evolving UX | Implementation is harder than interface needs | Simplify after `skills.py` |
| Historical artifacts in tracked surface | Evidence retention and archaeology | Useful during rapid learning | Competes with current source truth | Quarantine/delete after classification |
| Compatibility paths without expiry | Avoid breaking callers | Safer than immediate removal | Creates permanent hidden branches | Add deprecation budget, then remove |
| Catalog breadth without proof | Exploration and ambition | Skill creation is cheaper than proof | Creates false confidence and routing ambiguity | Keep experimental, gate promotion |
| CI breadth without ownership map | Good faith governance growth | Each check seemed useful locally | Agents cannot tell what failures prove | Map ownership; prune weak checks |
| Hand-maintained docs repeating command output | Helpful explanations | Docs are easy to add | Drift risk and token cost | Generate or validate |
| Broad router language | Reduce need to load all details | Easy to describe many cases | Agents face too many adjacent choices | Compress to one primary recommendation |

Complexity to ignore, not fix:

- The existence of multiple skill families. Families are useful if visibility and proof are controlled.
- The source/projection split. It is complexity with leverage.
- Generated handles being shallow. That shallowness is intentional.
- Local-first assumptions. They are acceptable until proof is stronger.

## 9. Moat-Critical Systems

| System | Moat Contribution | Compounds Over Time | Invest? | Complexity Effect |
|---|---|---|---|---|
| Outcome proof | Converts skill claims into evidence | Yes, if linked to real closeouts | Strategic investment | Complexity strengthens moat only if proof taxonomy stays small |
| `./bin/ask` command contract | Builds developer and agent habit | Yes | Protect aggressively | Complexity weakens moat if implementation remains large |
| `repo doctor` | Compresses repo truth into action | Yes | Invest now | Complexity should be hidden behind output |
| Source/projection/runtime separation | Prevents agents editing wrong surfaces | Yes | Protect aggressively | Complexity strengthens moat when enforced |
| Command handles | Low-friction invocation without source drift | Yes | Preserve | Complexity weakens if handles contain logic |
| Runtime budget and selection policy | Controls context cost | Yes | Preserve and measure | Complexity strengthens moat if policy remains deep |
| Path ownership inventory | Keeps repository cognition trustworthy | Yes after burn-down | Invest next | Current unresolved backlog weakens it |
| Learned-fix memory | Accumulates operational advantage | Yes if indexed/fresh | Invest selectively | Complexity weakens if raw memory competes with current truth |
| Skill/plugin lifecycle | Enables broad platform ambition | Maybe | Invest after proof gates | Complexity weakens if breadth outruns proof |

Fake moat systems:

- raw catalog size;
- plugin folder count;
- large CLI files;
- complex governance without measurable failure reduction;
- historical artifact volume;
- AI-native branding;
- structural audit passed off as effectiveness.

Easy-to-copy systems:

- markdown skill layout;
- basic generated handles;
- basic CLI wrappers;
- docs lint;
- GitHub workflow gates;
- broad skill categories.

## 10. Fake Sophistication Signals

False sophistication should not become work unless it is being removed, collapsed, or converted into measurable leverage.

| Signal | Why It Feels Sophisticated | Why It Is False Unless Proven | Triage Decision |
|---|---|---|---|
| More skills | Looks like capability growth | Increases routing ambiguity without outcome proof | Do not create work items for breadth alone |
| More governance checks | Looks like safety | Can slow work without catching real failures | Require proof target and owner |
| More docs | Looks like cognition support | Can increase token cost and drift | Generate or validate, otherwise ignore |
| More plugin surfaces | Looks like platform scale | Easy to copy and hard to route | Keep experimental until proof |
| More orchestration commands | Looks agent-native | Can fragment deterministic execution | Route through `repo doctor`/`ask` golden path |
| More compatibility layers | Looks stable | Preserves old architecture forever | Add expiry or remove |
| More historical evidence | Looks rigorous | Stale evidence confuses current truth | Index summaries, quarantine raw artifacts |

## 11. Recommended Deletions

Deletion candidates are classes, not blind file removals. Each requires caller/reference check before execution. The deletion stance is aggressive, but the execution rule is classification-first: remove what is proven stale, quarantine what has archaeology value, and preserve fixtures/indexes that validators or future agents actually use.

| Candidate | Why It Exists | Why It Survived | Why Remove | Impact |
|---|---|---|---|---|
| Tracked runtime databases | Local state leaked into repo surface | Useful during local experimentation | Runtime state is not source | High cognition improvement, low product loss if unreferenced |
| Unindexed historical artifacts/run logs | Evidence retention | Archaeology value | Raw history competes with current truth | High cognition improvement; keep indexed summaries |
| Duplicate infrastructure paths | Migration or accidental copy | Avoided breaking unknown refs | Duplicates ownership and import ambiguity | Medium-High; requires reference scan |
| Stale generated reports | Useful snapshots | No retention policy | Reproducible artifacts should not be source | Medium; improves repo surface |
| Compatibility scripts with no caller | Migration safety | No expiry budget | Hidden branches and stale assumptions | Medium; requires caller proof |
| Low-use skills without scenarios | Exploration | Skill count feels valuable | Routing ambiguity and token cost | Medium; fold or mark experimental |
| Docs duplicating live command output | Helpful at time written | Easier than generation | Drift-prone and token-expensive | Medium; replace with generated snippets |
| Redundant workflow checks | Local safety additions | No ownership map | Governance noise | Medium; prune after check map |

Do not delete:

- source/projection machinery;
- command handles;
- selection policy;
- repo doctor;
- path ownership docs;
- proof/eval concepts;
- root skill families solely because they are broad.

## 12. Refactor Candidates

| Candidate | Priority | Refactor Type | First Move | Validation |
|---|---|---|---|---|
| `Infrastructure/scripts/lib/ask/commands/skills.py` | P0 | Service extraction | Extract plugin cache and catalog/projection service boundaries | skill list/resolve/audit, catalog parity, runtime budget, handle validation |
| `Infrastructure/bin/ask` | P1 | Front-controller slimming | Extract command registry and parser/error UX modules | current CLI help, command smoke tests, robot output samples |
| `repo doctor` | P1 | Interface strengthening | Add next-action-only output and CI artifact | doctor JSON snapshots, docs references |
| Repo-surface inventory | P1 | Classification/refactor | Define categories and thresholds, then burn down highest-noise classes | repo doctor surface signal |
| Skill proof | P1 | Eval architecture | Define proof levels and implement first core-skill proof payload | eval/workout pass and sample closeout evidence |
| CI ownership | P2 | Governance simplification | Build required-check ownership map | CI check-name parity |
| Compatibility paths | P2 | Debt retirement | Add deprecation manifest | stale-entry validation |
| Skill overlap | P2 | Routing analytics | Detect overlapping trigger nouns/handles | warning report and promotion gate |

## 13. Anti-Drift Priorities

| Priority | Finding | Drift Risk | Improves Determinism | Improves Cognition | Reduces Coupling | Simplifies Execution | Future-Agent Benefit |
|---|---|---|---|---|---|---|---|
| P0 | Block new `skills.py` feature logic until extraction | High | Medium | High | High | High | Agents inspect smaller modules |
| P0 | Treat catalog parity as release-blocking | High | High | High | Medium | Medium | Agents trust generated/runtime surfaces |
| P0 | Define proof taxonomy | High | High | High | Medium | Medium | Agents know what evidence proves |
| P1 | Make `repo doctor --next` canonical | Medium-High | High | High | Medium | High | One current truth and next action |
| P1 | Repo-surface burn-down | High | Medium | High | Medium | Medium | Less stale artifact confusion |
| P1 | Skill promotion gates | Medium-High | High | High | Medium | Medium | Fewer wrong skill choices |
| P2 | CI ownership map | Medium | High | Medium | Medium | Medium | Agents update correct workflow |
| P2 | Deprecation budgets | Medium | Medium | Medium | High | Medium | Less legacy ambiguity |
| P2 | Generated docs from command output | Medium | Medium | High | Low | Medium | Lower token cost and docs drift |

## 14. Execution Priority Matrix

| Work Item | Impact | Complexity | Strategic Importance | Risk Type | Route | Decision |
|---|---|---|---|---|---|---|
| Split `skills.py` into services | Critical | Migration-risk | Moat-critical architectural | Regression, cognition | Linear project under refactor program | Implement |
| Add proof taxonomy ADR | Critical | Moderate | Moat-critical strategic | Governance, false confidence | ADR plus eval program | Implement |
| Add `repo doctor --next` | High | Moderate | Agent-native operational | Drift, cognition | Linear project | Implement |
| Fix catalog parity block | High | Moderate | Operational/architectural | Drift, regression | Linear issue | Implement |
| Repo-surface burn-down | High | Difficult | Agent-native governance | Cognition, governance | Linear initiative | Implement in phases |
| Skill promotion gates | High | Moderate | Moat-critical | Governance, routing | Linear initiative plus ADR | Implement |
| CI ownership map | Medium | Moderate | Operational governance | Governance | Linear issue | Implement |
| Deprecation budget | Medium | Moderate | Technical debt | Drift, migration | Linear project | Implement after P0 |
| Shrink `Infrastructure/bin/ask` | High | Migration-risk | Architectural | Regression | Follow-on refactor program | Implement after `skills.py` |
| Skill overlap analytics | Medium | Moderate | Agent-native | Routing, cognition | Linear issue | Implement after promotion gates |
| Generated onboarding from live commands | Medium | Moderate | Agent-native | Cognition | Linear issue | Implement after doctor `--next` |
| Broad portability adapters | Medium future | Difficult | Strategic later | Abstraction | Strategy decision later | Defer |
| New plugin categories | Low | Moderate | Cosmetic/exploratory | Routing | None | Ignore unless proof-backed |
| More architecture docs | Low | Trivial | Cosmetic | Drift | None | Ignore unless generated/validated |
| New governance checklist | Low | Trivial | Governance theater | Governance | None | Reject without proof target |

## 15. Recommended Linear Initiatives

### Initiative 1: Proof-Driven Skill Core

Goal:

Make outcome proof the promotion mechanism for trusted/default-visible skills.

Projects:

- Proof taxonomy ADR.
- Core skill proof payloads for 3-5 highest-value skills.
- Skill promotion gate.

Success metric:

- No new default-visible skill without explicit proof status.
- First core skills have reachability, structural, and outcome evidence separated.

### Initiative 2: Ask Control-Plane Simplification

Goal:

Reduce change amplification in the command layer.

Projects:

- Split `skills.py`.
- Add service boundaries.
- Preserve CLI behavior and robot JSON contracts.
- Later slim `Infrastructure/bin/ask`.

Success metric:

- `skills.py` no longer owns plugin cache, projection/catalog, proof, and command rendering logic in one file.

### Initiative 3: Agent First Golden Path

Goal:

Make the repo guide agents through safe work with one current truth surface.

Projects:

- `repo doctor --next`.
- `skills improve` one primary recommendation.
- `skills explain` canonical source and smallest validation.
- `repo closeout --changed`.

Success metric:

- A fresh agent can run one command and follow exact next commands without reading multiple docs.

### Initiative 4: Repository Cognition Burn-Down

Goal:

Remove or classify stale/generated/runtime surfaces that confuse source truth.

Projects:

- `.skillsets/**` ownership decision.
- Historical artifact quarantine.
- Runtime DB removal/ignore policy.
- Repo-surface thresholds.

Success metric:

- Repo doctor surface warnings move from broad noise to actionable categories.

### Initiative 5: Governance Compression

Goal:

Keep gates that prove real behavior, remove or demote ceremony.

Projects:

- CI ownership map.
- Deprecation budget.
- Generated docs command-output checks.

Success metric:

- Every required check has owner, source contract, failure action, and merge-blocking reason.

## 16. Recommended ADRs

| ADR | Decision Needed | Why ADR Instead Of Issue | Priority |
|---|---|---|---|
| Outcome Proof Is The Promotion Mechanism | Define proof levels and promotion gates | Strategic and governance consequence | P0 |
| Skill Lifecycle States | Define experimental, latent, trusted, default-visible, deprecated | Prevents breadth/trust confusion | P0 |
| Generated Surface Ownership | Decide `.skillsets/**` and generated tracked outputs policy | Affects source/projection contract | P1 |
| CI Check Ownership | Define provider/check responsibilities | Prevents governance drift | P1 |
| Deprecation Budget Policy | Define expiry requirements for legacy/compat paths | Prevents hidden permanent branches | P2 |
| Local-First Until Proof | Defer broad portability until adapters are justified | Prevents speculative abstraction | P2, only if challenged |

## 17. Recommended Refactor Programs

### Program 1: Skills Command Decomposition

Scope:

- `Infrastructure/scripts/lib/ask/commands/skills.py`

Boundaries:

- plugin cache service;
- skill catalog service;
- projection service;
- proof service;
- skill tool resolution;
- CLI adapter.

Non-goals:

- no command behavior redesign;
- no skill catalog semantics change;
- no plugin architecture rewrite.

### Program 2: Ask Front Door Slimming

Scope:

- `Infrastructure/bin/ask`

Boundaries:

- command registry;
- parser construction;
- fuzzy correction;
- invocation wrapper.

Timing:

- after Program 1 begins or has stable service boundaries.

### Program 3: Repository Surface Ownership

Scope:

- `.skillsets/**`;
- generated work areas;
- historical artifacts;
- runtime state;
- duplicate infrastructure paths.

Boundaries:

- classify before deletion;
- delete/quarantine only after reference scan;
- preserve fixtures and indexed summaries.

### Program 4: Proof And Promotion

Scope:

- proof taxonomy;
- core skill proof payloads;
- promotion gates;
- eval/workout integration.

Boundaries:

- structural audit is not outcome proof;
- invocation is not success;
- core visibility requires evidence.

## 18. Future Agent Operational Risks

| Risk | Agent Failure Mode | Evidence | Response |
|---|---|---|---|
| Giant command modules | Agent edits wrong area or misses coupled behavior | `skills.py` 3001 lines; `ask` 1900 lines | Split modules, expose service contracts |
| Multiple health commands | Agent runs a partial check and claims done | intent/review list doctor/status/catalog/surface/closeout/proof | Make `repo doctor --next` canonical |
| Ambiguous proof semantics | Agent treats audit pass as outcome success | artifacts warn structure != outcome | Proof taxonomy and payload labels |
| Generated/source ambiguity | Agent edits runtime projection | source/projection docs and `.skillsets` ambiguity | Generated-surface ownership ADR and warnings |
| Stale artifacts | Agent cites old evidence as current truth | repo-surface findings and artifact warnings | Archive/index/delete |
| Overlapping skills | Agent chooses by keyword, not domain | broad skill families and overlap risk | Skill overlap analytics and promotion gates |
| CI ownership ambiguity | Agent patches wrong provider | GitHub broad, CircleCI thin | Required-check ownership map |
| Legacy paths | Agent follows compatibility route | legacy/compat references | Deprecation budget and stale validation |

Token-expensive workflows:

- reading multiple docs to infer first action;
- inspecting giant command modules for small command behavior;
- browsing broad skill trees without `skills improve` narrowing;
- parsing historical artifacts without freshness/index metadata;
- resolving CI check meaning from workflow files manually.

## 19. Recommended Compression Opportunities

1. Replace "read these docs first" with `./bin/ask repo orient --json --robot` or `repo doctor --next`.

2. Replace repeated command-output docs with generated snippets checked in CI.

3. Replace broad skill browsing with `skills improve "<goal>"` returning one primary route.

4. Replace proof prose with typed proof payloads:

   - reachability;
   - structural;
   - quality;
   - outcome.

5. Replace repo-surface warning sprawl with a burn-down dashboard:

   - unclassified generated;
   - runtime state;
   - duplicate infrastructure;
   - historical archive;
   - deletion candidates.

6. Replace compatibility comments with deprecation records:

   - owner;
   - caller;
   - removal condition;
   - expiry date;
   - validation.

7. Replace CI provider lore with a generated ownership matrix.

8. Replace high-level moat talk with a small metric set:

   - skill first-choice accuracy;
   - closeout success rate;
   - validation pass after agent edits;
   - context tokens per successful task;
   - catalog parity drift duration;
   - repo-surface unclassified count.

## 20. Evidence & Traceability Matrix

| Conclusion | Fact / Interpretation / Speculation | Evidence | Affected Files / Modules | Confidence | Operational Impact | Strategic Impact | Why It Matters |
|---|---|---|---|---|---|---|---|
| Split `skills.py` first | Fact plus interpretation | Review names `skills.py` as 3001-line god command module and P0 refactor | `Infrastructure/scripts/lib/ask/commands/skills.py` | High | Reduces change amplification and agent context load | Protects maintainability of skill lifecycle | This is the highest leverage structural move. |
| Keep hybrid platform but make proof the trust layer | Interpretation from refined review | Architecture review closeout recommends hybrid with proof-driven hierarchy | `.harness/review/agent-skills-architecture-review.md` | High | Prevents workbench breadth from overwhelming trusted core | Preserves platform ambition while protecting moat | Breadth alone is copyable; proof-backed breadth compounds. |
| Treat outcome proof as moat-critical | Fact plus interpretation | Both intent files and review warn structure/reachability are not outcome proof | `.harness/features/*.md`, `.harness/review/*.md`, `.harness/quality/criteria.md` | High | Changes skill promotion, eval design, and Linear priorities | Defines defensibility | Prevents false confidence from audits. |
| Make `repo doctor` canonical | Fact plus interpretation | Intent recommends doctor as first command; review calls it tracer-bullet architecture | `Infrastructure/scripts/lib/ask/commands/repo.py`, `.harness/features/agent-skills-intent.md` | High | Gives agents one next action | Reduces onboarding and execution ambiguity | Current truth must be executable. |
| Burn down repo-surface debt | Fact plus interpretation | Intent/review cite 4543 repo-surface findings and unclassified generated/historical material | `Docs/agents/15-repo-surface-ownership.md`, repo doctor output cited in artifacts | High | Reduces stale evidence and source confusion | Makes repo cognition trustworthy | File ownership is product architecture here. |
| Resolve `.skillsets/**` ownership | Fact plus interpretation | Intent decision specifically calls out `.skillsets/**` as unresolved generated distribution output | `.harness/features/agent-skills-intent.md`, `.skillsets/**` | High | Prevents generated/runtime source confusion | Protects source/projection model | Ambiguity here weakens the central architecture. |
| Do not create backlog items for catalog growth alone | Interpretation | Artifacts repeatedly say catalog size is not the moat | `Skills/**`, `Plugins/**`, selection policy | High | Prevents issue explosion | Protects focus | More skills can reduce agent reasoning quality. |
| CI ownership needs mapping, not optimization-first | Interpretation | Review flags broad GitHub Actions and thin CircleCI ownership ambiguity | `.github/workflows/**`, `.circleci/config.yml`, `harness.contract.json` | Medium | Prevents wrong workflow edits | Keeps governance credible | Required checks need clear proof semantics. |
| Compatibility paths need expiry | Interpretation from evidence | Review and intent identify legacy/compat permanence risk | `Infrastructure/**`, `Docs/**`, restore manifests | Medium-High | Reduces hidden branching | Improves evolvability | Compatibility without expiry becomes architecture. |
| `selection_policy.py` and `command_surface.py` are protectable deep modules | Fact plus interpretation | Review identifies both as deep modules and moat-critical | `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`, `command_surface.py` | High | Preserves context and handle discipline | Protects agent-native differentiation | These modules compress complexity instead of spreading it. |
| Broad portability should be deferred | Interpretation | Intent recommends local-first until proof is strong | `harness.contract.json`, docs/spec references cited in intent | Medium | Avoids speculative adapters | Keeps product proof-first | Premature portability would multiply abstractions. |
| More docs should not be default response | Interpretation | Artifacts warn docs can drift and repeat command output | `Docs/**`, generated command output, docs lint | Medium-High | Reduces token cost and drift | Keeps cognition compressed | Command truth should replace prose where possible. |

## Final Triage Decision

Execute in this order:

1. Refactor program for `skills.py` decomposition.
2. ADR for proof taxonomy and skill lifecycle states.
3. `repo doctor --next` and golden-path routing.
4. Catalog parity and `.skillsets/**` ownership resolution.
5. Repo-surface burn-down.
6. CI ownership map and deprecation budgets.
7. Skill overlap analytics and generated onboarding.

Linear planning rule:

- Start with the five recommended initiatives.
- Create projects only when a body of work needs sequencing, ownership, or acceptance criteria.
- Create issues only for the next executable slice inside an approved initiative/project.
- Do not convert every finding into an issue.

Explicitly defer:

- broad portability;
- new plugin categories;
- catalog expansion;
- new governance checks without proof targets;
- more docs that are not generated or validated;
- architecture diagrams that do not change execution.
