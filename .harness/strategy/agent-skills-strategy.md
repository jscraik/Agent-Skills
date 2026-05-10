# Agent Skills Strategic Direction

Repository: `agent-skills`

Strategy date: 2026-05-07

Source artifacts:

- `.harness/features/agent-skills-intent.md`
- `.harness/features/agent-skills-repo-intent-and-moat.md`
- `.harness/review/agent-skills-architecture-review.md`
- `.harness/triage/agent-skills-triage.md`

Purpose:

This is the strategic spine for the repository. It compresses the intent, architecture review, moat analysis, and triage into durable decisions. Future agents should use this to understand what matters, what must not drift, what can be rewritten, and what should stop receiving protection.

Strategic stance:

- The proof-backed local control plane is the spine.
- The broad skill/plugin workbench is useful, but subordinate.
- Tactical internals are safe to rewrite boldly when public contracts and strategic boundaries are preserved.
- Catalog size, artifact volume, and governance breadth are not strategic assets.

## 1. Executive Strategic Summary

Agent Skills Kit is not strategically valuable because it contains many skills. It is not strategically valuable because it has a lot of governance. It is valuable if it makes agents reliably remember, select, execute, validate, and improve high-value workflows with less context and fewer false completions.

The irreducible strategic direction is:

```text
Build the smallest trustworthy local control plane for proof-backed agent workflows.
Keep the broader skill/plugin workbench as exploration.
Promote only what proves operational value.
```

The project is coherent at the core and noisy at the edges. The core is source/projection separation, deterministic `./bin/ask` commands, generated handles, runtime budget, path ownership, repo doctor, closeout, and outcome proof. The noise is catalog breadth without proof, historical artifact sprawl, compatibility paths without expiry, broad governance without clear failure semantics, and command modules that are too large for local reasoning.

The first strategic execution move is still structural: decompose `Infrastructure/scripts/lib/ask/commands/skills.py`. The proof system is moat-critical, but adding proof machinery into the current 3001-line command module would strengthen the wrong shape.

Strategic rule:

- Trust the spine.
- Simplify the shell.
- Delete or quarantine the fog.
- Make proof the promotion mechanism.

## 2. Core Thesis

Agents do not need more prompts. They need small, deterministic, repo-aware operating loops that tell them:

1. whether the repo is safe to work in;
2. which capability applies;
3. where canonical source lives;
4. what proof exists;
5. what validation closes the work.

The repository should therefore optimize around a five-command golden path. This path is the strategic product spine, not just a convenience workflow:

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills prove <handle> --json --robot
./bin/ask repo closeout --changed --json --robot
```

Everything else is either:

- infrastructure that makes this loop more reliable;
- experimental workbench capability that may later earn promotion;
- historical/context material that must not compete with live truth;
- accidental complexity to remove.

## 3. Irreducible Core

The irreducible architecture is small:

- `./bin/ask` as the public agent and human command surface.
- `--json --robot` as the machine-readable contract.
- Canonical skill sources separate from generated/runtime projections.
- Generated command handles as small invocation pointers, not logic containers.
- Runtime visible-surface budget and selection policy.
- Path ownership and repo-surface classification.
- `repo doctor` as current truth and next-action compression.
- `skills improve`, `skills explain`, and `skills prove` as capability routing/proof surfaces.
- `repo closeout --changed` as completion-readiness pressure.
- Outcome proof as the promotion mechanism for trusted skills.

Everything outside that core is optional until it proves it improves the core loop.

Operational identity:

- local-first;
- deterministic;
- proof-seeking;
- source-owned;
- context-budgeted;
- anti-drift;
- agent-operable;
- suspicious of breadth without proof.

## 4. Actual Moat

The moat is operational and cognitive first, architectural second.

The defensible thing is not a folder layout, plugin count, or prompt catalog. Those are copyable. The defensible thing is the discipline and accumulated evidence that agents behave better because this repo exists.

Actual moat:

- source/projection/runtime separation that prevents agents editing the wrong surface;
- generated handles that reduce invocation cost while preserving canonical ownership;
- context-budget and selection policy that keep agent loading small;
- repo doctor and closeout commands that compress safety and completion;
- outcome proof that separates real improvement from structural correctness;
- learned-fix memory and validation loops that compound from repeated failures;
- developer habit around `./bin/ask` as the trusted local front door.

Why it is difficult to replicate:

- The visible shell is easy to copy.
- The operating memory, proof corpus, failure taxonomy, and trust in command contracts are harder to copy if they are curated and measured.
- The moat strengthens only when each repeated failure becomes a smaller command, validator, proof artifact, or memory learning.

Does complexity strengthen or weaken it?

- Complexity strengthens the moat only when it hides real operational difficulty behind a smaller deterministic interface.
- Complexity weakens the moat when it increases the amount future agents must read, guess, or route manually.

Moat assumptions likely false:

- More skills means more value.
- More governance means more trust.
- Structural audit proves usefulness.
- Local-first control planes are adopted because they are powerful.
- Agents can navigate expert-level repo complexity safely.

Moat-critical systems:

- `./bin/ask` command contract.
- `repo doctor`.
- source/projection separation.
- command handles.
- runtime budget and selection policy.
- path ownership.
- proof taxonomy and outcome evidence.
- learned-fix memory connected to validation.

Systems that weaken the moat:

- giant command modules;
- catalog breadth without proof;
- historical artifacts in primary paths;
- compatibility paths without expiry;
- governance gates without owner/failure action;
- docs that restate live command output without generation or validation.

What a smart competitor would remove immediately:

- raw artifact sprawl;
- verbose governance language;
- unproven skill breadth;
- huge command modules;
- weak proof claims;
- ambiguous generated/source surfaces;
- broad portability abstractions before local proof.

What future agents must avoid weakening:

- deterministic command contracts;
- source/projection boundary;
- visible-surface budget;
- proof semantics;
- path ownership;
- generated handle shallowness;
- repo doctor as the first truth surface.

## 5. False Moat Signals

These should not be defended as strategic assets.

| Signal | Why It Looks Valuable | Why It Is Not A Moat | Strategic Direction |
|---|---|---|---|
| Skill count | Suggests broad capability | Easy to copy and increases routing ambiguity | Keep breadth experimental until proof-backed |
| Plugin count | Suggests ecosystem | Folders do not create adoption or trust | Promote plugin workflows only with proof |
| Large command modules | Suggest implementation depth | Increase cognitive load and regression risk | Split and simplify |
| Complex CI | Suggests governance maturity | Without ownership, it is ceremony | Map checks to proof targets |
| Historical artifacts | Suggest evidence depth | Raw history can obscure live truth | Index, summarize, quarantine, delete |
| More docs | Suggest cognition support | Can become token-expensive drift | Generate or validate from command truth |
| Structural audits | Suggest skill quality | Do not prove agent outcome improvement | Separate reachability, structural, quality, outcome |

## 6. Strategic Contradictions

| Contradiction | Evidence | Risk | Direction |
|---|---|---|---|
| The repo prevents drift, but repo-surface findings show tracked drift | Prior artifacts cite 4543 repo-surface findings | Agent cognition degrades | Burn down repo-surface debt and block new unclassified artifacts |
| The repo is agent-native, but first contact requires many docs | Intent/review/triage all call for golden path compression | Agents route manually and inconsistently | Make `repo doctor --next` canonical |
| The repo says source/projection separation matters, but `.skillsets/**` ownership is unresolved | Intent decision 2 | Generated output can become de facto source | ADR and generator/validation policy |
| The repo wants proof, but much machinery proves structure more than outcomes | Intent and review warn structural audit is not outcome proof | False confidence | Proof taxonomy and outcome eval program |
| The repo values modularity, but `skills.py` and `ask` are large control points | Review cites 3001 and 1900 lines | Local reasoning fails | Service extraction before feature expansion |
| Governance aims to help, but can become ceremony | Review flags CI ownership and governance breadth | Slower delivery with unclear value | Every gate needs owner, proof target, failure action |

## 7. Complexity Without Leverage

Complexity to remove or collapse:

- `skills.py` as a multi-context command module.
- `Infrastructure/bin/ask` implementation mass after `skills.py` decomposition begins.
- raw historical artifacts that are neither indexed nor fixtures.
- tracked runtime databases.
- generated reports reproducible from source.
- compatibility scripts with no caller/expiry.
- docs duplicating command output.
- redundant workflow checks with unclear proof targets.
- low-use skills without realistic scenarios.

Complexity to preserve:

- source/projection separation;
- generated handles as pointers;
- selection policy and runtime budget;
- path ownership;
- repo doctor;
- proof levels;
- local-first execution until proof is strong.

Strategic test:

If complexity makes future agents know less and act more safely, keep it. If it makes them read more, guess more, or route manually, remove or compress it.

## 8. What Should Be Deleted

Deletion is aggressive by class, conservative by file. Classify and reference-check before removal.

| Candidate | Why It Exists | Why It Survived | Why Remove Now |
|---|---|---|---|
| Tracked runtime databases | Local state leaked into repo surface | Useful during experimentation | Runtime state is not source and confuses agent truth |
| Unindexed historical artifacts/run logs | Evidence retention | Archaeology value | Raw history competes with current operating contracts |
| Duplicate infrastructure paths | Migration/copy safety | Unknown callers | Duplicate ownership creates import and cognition ambiguity |
| Stale generated reports | Review snapshots | No retention policy | Reproducible artifacts should be regenerated, not trusted as source |
| Compatibility scripts without callers | Migration safety | No expiry budget | Permanent hidden branches increase unknown unknowns |
| Low-use skills without scenarios | Exploration | Catalog size feels valuable | Increases routing ambiguity and token cost |
| Docs repeating command output | Helpful at creation | Easy to maintain manually until drift appears | Command output should be generated or validated |
| Redundant workflow checks | Local safety additions | Governance accumulation | Checks without ownership create ceremony |

Do not delete:

- source/projection machinery;
- command handles;
- selection policy;
- repo doctor;
- proof/eval concepts;
- path ownership docs;
- root skill families solely because they are broad.

## 9. What Should Become Core

Core investment areas:

1. Ask control-plane simplification.

   `skills.py` decomposition first; `Infrastructure/bin/ask` slimming second.

2. Proof-driven skill core.

   Define proof levels and require outcome evidence for trusted/default-visible promotion.

3. Agent-first golden path.

   Make `repo doctor`, `skills improve`, `skills explain`, `skills prove`, and `repo closeout` the public loop.

4. Repository cognition burn-down.

   Classify, quarantine, delete, or index artifact surfaces so source truth is obvious.

5. Governance compression.

   Keep gates that prove real behavior; remove or demote ceremony.

6. Context and routing compression.

   Skill selection should return one primary route unless ambiguity is real.

## 10. Architectural Non-Negotiables

Future agents and contributors must preserve these invariants:

- `./bin/ask` remains the public command contract.
- Machine consumers get `--json --robot` outputs where commands are agent-facing.
- Canonical sources are edited; generated/runtime projections are not treated as source.
- Generated handles stay shallow pointers to canonical workflows.
- Runtime visible surface remains budgeted.
- `repo doctor` is the first truth surface for repo health.
- Completion claims require closeout/validation evidence.
- Skill promotion requires proof status.
- Structural audit must not be called outcome proof.
- New governance gates require owner, proof target, failure action, and blocking semantics.
- New orchestration layers require measurable leverage.
- New feature logic must not accumulate in already over-threshold command modules.
- Historical artifacts must not compete with current operating contracts.
- Local-first remains default until proof justifies portability adapters.

## 11. Safe To Rewrite

Future agents may be more aggressive here:

- Internal implementation of `skills.py`, as long as command behavior and contracts are preserved.
- Internal implementation of `Infrastructure/bin/ask`, after command registry/parser/error boundaries are extracted.
- Docs that repeat command output, if replaced by generated or validated snippets.
- Low-use or overlapping skill text, if folded into clearer routers or marked experimental.
- Compatibility wrappers with no caller and no expiry need.
- Historical artifact organization, as long as indexed summaries/fixtures remain.
- CI workflow internals, if required-check ownership and proof semantics are preserved.
- Plugin cache internals, if source/cache/runtime boundaries stay explicit.
- Onboarding docs, if they become shorter and more command-derived.

Safe rewrite rule:

Preserve public contracts and strategic boundaries. Rewrite tactical interiors boldly when doing so reduces cognitive load, drift, coupling, or command-module mass. Do not protect an internal shape just because a previous version happened to work.

## 12. Strategic Risks

| Risk | Confidence | Operational Impact | Strategic Impact | Response |
|---|---|---|---|---|
| Broad workbench ambition outruns proof | High | More routing ambiguity | Moat becomes catalog theater | Promotion gates and proof taxonomy |
| Governance becomes more important than execution | Medium-High | Slower delivery | Trust decays into ceremony | Governance compression |
| The core loop remains hidden behind too many docs | High | Fresh agents struggle | Adoption weakens | Golden path commands and generated orientation |
| Local-first assumptions become portability debt | Medium | Future adapters harder | Commercial expansion delayed | Defer but isolate assumptions |
| Historical artifacts become the repo's memory model | High | Stale evidence misleads agents | Cognition quality collapses | Quarantine raw artifacts; keep indexes |

## 13. Operational Risks

- Catalog parity blocks source/projection trust.
- Repo-surface findings make source truth ambiguous.
- CI provider/check responsibilities can drift.
- Validation layers may be too heavy without a daily loop.
- Compatibility paths can become permanent.
- `skills.py` changes can regress multiple workflows at once.
- `repo doctor` can lose strategic power if parallel health commands proliferate.

Operational direction:

- make `repo doctor --next` the daily loop;
- treat catalog parity as release-blocking;
- classify generated/runtime surfaces;
- extract services before adding command behavior;
- keep full validation as release confidence, not the only usable signal.

## 14. Long-Term Scaling Risks

2-year pressure:

- skill count rises faster than routing quality;
- proof claims remain too structural;
- `ask` command internals become harder to change;
- repo artifacts keep growing;
- CI gates multiply.

5-year pressure:

- local-first assumptions become commercial portability constraints;
- memory/evidence systems need privacy-safe indexing;
- plugin ecosystem boundaries become harder to enforce;
- governance rituals become expensive without outcome metrics;
- future agents need too much context to operate safely.

What breaks first:

1. local reasoning in command modules;
2. trust in generated/runtime surfaces if parity drifts;
3. agent routing if skill breadth outruns proof;
4. repo cognition if artifact sprawl remains;
5. governance credibility if gates lack proof targets.

What compounds positively:

- proof-backed workflows;
- learned fixes tied to validation;
- deterministic command contracts;
- runtime budget discipline;
- source/projection clarity;
- one-command repo orientation.

## 15. Governance Risks

Governance helps only when it reduces uncertainty.

Current governance risks:

- checks without explicit proof target;
- provider split without visible ownership map;
- compatibility without expiry;
- review/process expansion without execution improvement;
- docs added instead of validators/command output;
- default-visible skill changes without proof gates.

Governance direction:

- fewer gates;
- sharper gates;
- explicit owner;
- explicit failure action;
- explicit merge-blocking semantics;
- generated maps where possible;
- no new ritual without measurable failure reduction.

## 16. Agent-Native Risks

Agent-native does not mean "many agent instructions." It means agents can act safely with less context.

Risks:

- giant command modules force source archaeology;
- broad skill trees create routing ambiguity;
- stale artifacts look authoritative;
- generated/source boundaries remain subtle;
- blockers do not always compress to exact next commands;
- proof outputs can be misread;
- docs may be accurate individually but expensive collectively.

Direction:

- one current truth command;
- one primary recommendation;
- one canonical source pointer;
- one smallest validation command;
- one closeout gate.

## 17. Recommended Strategic Direction

Adopt this hierarchy:

1. Proof-backed local control plane.
2. Agent-first golden path.
3. Broad skill/plugin workbench as experimental surface.
4. Platform portability only after proof and adapters justify it.

Execution order:

1. Decompose `skills.py`.
2. Define proof taxonomy and skill lifecycle states.
3. Add/strengthen `repo doctor --next`.
4. Resolve catalog parity and `.skillsets/**` ownership.
5. Burn down repo-surface cognition debt.
6. Map CI ownership and add deprecation budgets.
7. Add skill overlap analytics and generated onboarding.

Do not convert this into dozens of issues. Use a few initiatives, then project slices, then issues only for the next executable work.

## 18. Recommended Simplifications

- Collapse first-contact experience around five golden-path commands.
- Move repeated prose warnings into validators or command output.
- Make `skills improve` return one primary route.
- Make `skills prove` label proof level explicitly.
- Make generated surfaces declare canonical source and edit prohibition.
- Hide catalog breadth from primary positioning.
- Quarantine raw history behind indexes.
- Replace CI lore with a required-check ownership map.
- Add expiry records for legacy/compat paths.
- Keep root skill families broad only if visibility and proof are controlled.

## 19. Core Investment Priorities

| Priority | Investment | Why |
|---|---|---|
| P0 | `skills.py` decomposition | Reduces the largest architectural choke point |
| P0 | Proof taxonomy and skill lifecycle states | Prevents false moat and bad promotion |
| P1 | `repo doctor --next` | Creates one executable truth surface |
| P1 | Catalog parity and `.skillsets/**` ownership | Protects source/projection trust |
| P1 | Repo-surface burn-down | Restores repository cognition |
| P2 | CI ownership map | Prevents governance ambiguity |
| P2 | Deprecation budgets | Stops compatibility becoming architecture |
| P2 | Skill overlap analytics | Protects routing quality as breadth grows |

## 20. Future Agent Guidance

Preserve:

- the five-command golden path;
- source/projection separation;
- generated handle shallowness;
- `--json --robot` contracts;
- proof semantics;
- runtime budget;
- path ownership;
- repo doctor as first truth;
- local-first execution until proof justifies adapters.

Challenge:

- any new skill without outcome scenario;
- any new command that bypasses the golden path;
- any new governance check without proof target;
- any generated file treated as source;
- any compatibility path without expiry;
- any doc that repeats command output manually;
- any artifact retained without index or fixture value;
- any feature added to `skills.py` before extraction.

Rewrite:

- tactical internals;
- overgrown command modules;
- stale docs;
- weak skills;
- unowned compatibility layers;
- artifact layout;
- CI implementation details.

Do not rewrite casually:

- public `ask` command contracts;
- source/projection model;
- command-handle semantics;
- selection policy/runtimes budget;
- proof taxonomy once adopted;
- path ownership rules.

## 21. Evidence & Traceability Matrix

| Strategic Conclusion | Fact / Interpretation / Speculation | Evidence | Affected Systems / Modules | Confidence | Operational Impact | Why It Matters |
|---|---|---|---|---|---|---|
| The repository's irreducible value is proof-backed agent workflow execution | Interpretation from repeated artifact conclusions | Intent says moat is agents remembering/proving workflows; review and triage reject catalog breadth | `./bin/ask`, skill proof, repo doctor, closeout, skills | High | Focuses investment on the golden path | Prevents skill inventory from becoming strategy |
| Keep hybrid platform ambition, but make proof the trust layer | Interpretation | Review final recommendation and triage operating posture | Skills, Plugins, selection policy, proof/eval surfaces | High | Lets breadth exist without becoming trusted by default | Preserves exploration while protecting trust |
| Decompose `skills.py` first | Fact plus interpretation | Review cites 3001-line multi-context command module; triage ranks it first | `Infrastructure/scripts/lib/ask/commands/skills.py` | High | Reduces change amplification and local reasoning cost | First structural move prevents more feature logic entering the choke point |
| `repo doctor` should become first truth surface | Fact plus interpretation | Intent and review call it canonical/tracer-bullet; triage ranks `--next` high | `Infrastructure/scripts/lib/ask/commands/repo.py`, `./bin/ask` | High | Gives agents one current next action | Reduces onboarding and validation ambiguity |
| Source/projection separation is non-negotiable | Fact | Ubiquitous language and intent/review evidence cite canonical source/runtime projection model | `Skills/**`, `.agents/**`, `.skillsets/**`, `command_surface.py` | High | Prevents edits to generated/runtime surfaces | Core to agent safety and trust |
| `.skillsets/**` ownership must be decided | Fact plus interpretation | Intent decision calls it unresolved; triage repeats as priority | `.skillsets/**`, generated distribution policy | High | Prevents generated output becoming ambiguous source | Protects central architecture |
| Outcome proof must not be conflated with structural audit | Fact plus interpretation | All artifacts call out structure/reachability vs outcome proof | skill audit/proof/eval surfaces | High | Changes promotion and eval design | Prevents false confidence |
| Catalog size is a false moat | Interpretation | All artifacts reject "many skills" as defensible alone | `Skills/**`, `Plugins/**`, selection policy | High | Prevents low-leverage expansion | Competitors can copy catalog structure |
| Repo-surface debt is strategic cognition debt | Fact plus interpretation | Prior artifacts cite 4543 repo-surface findings and artifact sprawl | `.harness/**`, historical artifacts, generated areas | High | Reduces stale evidence and source confusion | Repository cognition is part of the product |
| Governance must be compressed | Interpretation | Review and triage flag CI ownership, deprecation, ceremony risk | `.github/workflows/**`, `.circleci/config.yml`, `harness.contract.json` | Medium-High | Keeps gates actionable | Governance without proof target becomes drag |
| Broad portability should be deferred | Interpretation | Intent recommends local-first until proof is strong | local harness/Codex assumptions, future adapters | Medium | Avoids speculative abstractions | Premature portability weakens focus |
| Safe rewrite zones should be explicit | Interpretation | Strategy need inferred from triage and review warnings about over-conservatism | command internals, docs, weak skills, CI internals | Medium-High | Enables future agents to refactor without fear | Prevents strategic artifacts from freezing accidental complexity |

## Final Strategic Decision

Agent Skills Kit should become a proof-backed local control plane for agent workflows, with a broad skill/plugin workbench around it.

The control plane is the product spine. The workbench is the exploration surface. Proof is the promotion mechanism. Simplicity is the adoption strategy. Deleting noise is not cleanup; it is strategic preservation.

Do not protect:

- catalog size;
- raw artifact volume;
- governance breadth;
- giant command modules;
- unproven plugin surfaces;
- compatibility paths without expiry;
- docs that merely repeat live command output.
