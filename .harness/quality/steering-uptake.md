# Steering Uptake Ledger

## Active Rule

High-signal steering is not a request to rewrite a guardrail document. Every
Jamie steering or review feedback item is a high-signal candidate until
classified. It is evidence that the agent operating loop may have failed to
preserve an important rule. The uptake path must produce a classified record, a
chosen radius, a durable surface, validation evidence, and a repeat-prevention
claim.

The synthesis is workflow-first: prose explains the rule, but the ledger and
validator prove that the rule was absorbed into the environment.

When steering says the agent is failing to operate effectively, repeating prior
feedback, or making Jamie say the same thing again, the agent must stop the
active lane and do not resume ordinary task work until it acts as a systems thinker:
classify the blocker, make an environment refinement in a durable
surface, validate the mechanism, and report proof that the repeated correction
should be harder to reproduce.

The larger perspective rule is active: before applying principle-shaped
feedback, identify the class of failure and use correction -> pattern -> sweep -> classification -> enforcement.
Search sibling instances or equivalent cases inside the chosen radius before
editing only the named site, unless the sweep proves the issue is genuinely
local.

When context may sit beyond the active turn, the active rule must scale
horizontal OODA across adjacent organizational activity and vertical OODA across
stacked trajectories. The agent must identify the cross-boundary compaction,
harness, environment, repo, tracker, or review boundary and use the smallest
available target context window to reflect before acting.

## Uptake Record: 2026-05-18 larger perspective pattern uptake

Operating failure: The agent can still agree that feedback is high-signal while
operationally treating one named site as the whole task instead of asking what
class of failure the feedback revealed.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: Jamie has to repeat the same correction across a codebase when agents
do not search sibling instances or equivalent cases before applying
principle-shaped feedback line-locally.

Generalized rule: Feedback that names one function, file, command, test, doc
section, review line, error, or example may be evidence of a broader class of
failure; extract the pattern, sweep the relevant surface, classify matches, and
add enforcement before claiming uptake.

Similar-case disposition: Root guide, high-signal steering protocol, steering
ledger, validator active-rule requirements, and validator regression tests are
fixed now; source-code sweeps remain task-specific and must run when a concrete
API, package, skill, or workflow receives principle-shaped feedback.

Pattern sweep: Checked root instructions, the high-signal steering protocol,
the active steering ledger, validator active-rule phrase checks, and validator
tests for places where the larger-perspective behavior could remain only
advice.

Sweep scope: Root guide, high-signal steering protocol, steering ledger,
steering uptake validator, and steering uptake validator tests.

Search terms: larger perspective, class of failure, correction -> pattern ->
sweep -> classification -> enforcement, sibling instances, equivalent cases,
line-local, transferable principle.

Matches considered: Root high-signal steering bullets, Larger Perspective Rule
section, active ledger rule, active-rule validator phrase list, and regression
tests for missing active-rule posture.

Exclusions: Concrete production APIs and skill eval suites because this uptake
changes the reusable operating mechanism; future task-specific feedback must run
its own bounded source sweep in the relevant radius.

Disposition: fixed now by adding the larger-perspective loop to root guidance,
making it explicit in the steering protocol, requiring the active ledger rule to
name the loop and equivalent-case search, and adding a regression test for
active rules that omit it.

Horizontal OODA: The correction applies across code review, SDK design, skill
authoring, validator work, docs, and harness workflows because Jamie often gives
one concrete example to communicate a wider operating or design rule.

Vertical OODA: The rule must carry from steering to pattern extraction, sibling
search, match classification, durable enforcement, validation, closeout, and
future-agent inheritance.

Durable surface: AGENTS.md, Docs/agents/19-high-signal-steering-feedback.md,
.harness/quality/steering-uptake.md,
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py, and
Infrastructure/scripts/testing/test_validate_steering_uptake.py.

Environment refinement: The repo now has an explicit larger-perspective rule
and the steering uptake validator rejects active ledger rules that omit the
class-of-failure, sibling-instance, equivalent-case, and correction-pattern-
sweep-classification-enforcement language.

Mechanism: Future agents cannot make a valid high-signal uptake record unless
the active rule itself encodes broader pattern uptake, and transferable records
already require sweep scope, search terms, matches considered, exclusions,
generalized rule, and similar-case disposition.

Proof: The new regression test constructs an otherwise complete steering ledger
whose active rule lacks larger-perspective pattern uptake and expects validation
failure.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q.

Repeat prevention: When Jamie points at one example but the feedback expresses a
principle, agents must identify the class of failure, search sibling instances
or equivalent cases, classify matches, and add enforcement before reporting the
work as handled.

## Uptake Record: 2026-05-17 cross-boundary OODA reflection

Operating failure: The agent could describe horizontal and vertical OODA but
still orient only on the current turn when the needed context lived across
compaction, harness, environment, tracker, review, or memory boundaries.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: Without a target context-window reflection step, future agents can
claim systems thinking while missing adjacent organizational activity or
stacked trajectories that change the correct action.

Generalized rule: Cross-boundary OODA requires a concrete recall mechanism, not
only a conceptual description of observation and orientation.

Similar-case disposition: Root instructions, steering protocol, steering
ledger, validator, and validator regression tests are fixed now; broader SDK
implementation remains deferred until the Skill SDK lane resumes.

OODA scaling protocol: Use horizontal OODA and vertical OODA to identify compaction, harness, environment, repo, tracker, or review boundaries; query the smallest target context window that can reflect on the missing context; record what changed before action.

Pattern sweep: Checked root instructions, high-signal steering protocol,
active ledger rule, validator, and validator tests for places where
cross-boundary OODA could remain prose-only.

Sweep scope: Root guide, steering protocol, steering ledger, validator, and
validator tests.

Search terms: OODA, horizontal OODA, vertical OODA, cross-boundary, compaction,
harness, environment, target context window, stacked trajectories, reflect.

Matches considered: Root high-signal steering bullet, protocol
Cross-Boundary Recall section, ledger active rule, existing OODA uptake record,
validator active-rule phrase checks, and regression tests.

Exclusions: Skill SDK production schema and runner implementation because this
meta change only governs how agents orient before resuming that lane.

Disposition: fixed now by adding a root operating rule, strengthening the
cross-boundary recall protocol, requiring an OODA scaling protocol marker, and
adding a regression test for missing target-context-window reflection.

Horizontal OODA: Agents must inspect adjacent organizational activity when the
current transcript is insufficient, including memory, active workstreams,
review artifacts, tracker state, prior runs, and external context windows.

Vertical OODA: Agents must orient across stacked trajectories including prior
steering, current plan and spec, validation gates, review loops, generated
projections, compaction recovery, and future-agent inheritance.

Durable surface: AGENTS.md, docs/agents/19-high-signal-steering-feedback.md,
.harness/quality/steering-uptake.md,
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py, and
Infrastructure/scripts/testing/test_validate_steering_uptake.py.

Environment refinement: The validator now rejects cross-boundary OODA uptake
records that omit the explicit OODA scaling protocol and the active rule now
names horizontal OODA, vertical OODA, cross-boundary orientation, and target
context windows.

Mechanism: A future agent that records this class of steering without a
target-context-window reflection protocol fails validation, making the
single-turn OODA horizon visible instead of silently accepted.

Proof: The regression test constructs a cross-boundary OODA record without the
protocol and expects validation failure.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q.

Repeat prevention: When future work depends on compaction, harness,
environment, tracker, review, memory, or adjacent organizational context, the
agent must identify the boundary, use the smallest target context window that
can reflect on it, record the changed decision, and only then act.

## Uptake Record: 2026-05-17 semantic pattern sweep enforcement

Operating failure: The environment still allowed an agent to record broad API
design feedback with a vague pattern sweep such as "searched the package,"
without proving equivalent cases were actually found, excluded, or classified.

Feedback type: api_design_rule

Intent radius: repository

Blocker: A line-local implementation could satisfy the steering ledger while
leaving the same class of bool-return, sentinel-error, or interface-shape
misbehavior elsewhere in the repository.

Generalized rule: Design feedback that names one function can still describe a
class of interface failures, so the uptake record must prove equivalent cases
were searched, classified, or explicitly deferred.

Similar-case disposition: Similar API or policy cases are handled through the
structured sweep fields in each broad record; source-specific code sweeps are
deferred until a concrete package or API layer is under review.

Pattern sweep: Checked the high-signal steering protocol, steering uptake
validator, validator regression tests, and active ledger records for places
where pattern sweep detail was requested in prose but not enforced.

Sweep scope: Steering protocol, uptake validator, validator tests, and all
active broad or transferable steering records in the ledger.

Search terms: Pattern sweep, Sweep scope, Search terms, Matches considered,
Exclusions, api_design_rule, bool, sentinel error, line-local.

Matches considered: Validator broad-feedback branch, API-design regression
fixture, protocol pattern-sweep contract, and ledger records with repository,
package, architecture_rule, durable_memory, or transferable feedback types.

Exclusions: Repository source APIs because this is the meta gate that forces a
future source-specific sweep when a concrete package or API layer is under
review.

Disposition: fixed now by requiring Sweep scope, Search terms, Matches
considered, and Exclusions for broad or transferable steering records, adding a
regression test for shallow API-design uptake, and updating all active ledger
records to satisfy the stronger contract.

Horizontal OODA: This applies across code review, API design, validation,
skill SDK work, and harness workflows because design-rule feedback often names
one symptom while implying a class of equivalent failures.

Vertical OODA: The rule must carry from review comment to pattern search,
match disposition, code or policy change, validation, and closeout so future
agents cannot stop at the named line.

Durable surface: docs/agents/19-high-signal-steering-feedback.md,
.harness/quality/steering-uptake.md,
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py, and
Infrastructure/scripts/testing/test_validate_steering_uptake.py.

Environment refinement: The validator now rejects broad or transferable
steering records that omit explicit sweep scope, search terms, matches
considered, or exclusions.

Mechanism: API-design and other transferable feedback cannot validate with a
generic pattern-sweep sentence; the ledger must show how the agent searched and
classified equivalent cases or why no source sweep is applicable yet.

Proof: The new regression test models the exact bool-return feedback failure
mode and fails when the record only says it searched the package.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q.

Repeat prevention: Future feedback that names one function but expresses a
general API principle must produce semantic sweep evidence before closeout; a
single-line fix plus a vague ledger entry will fail validation.

## Uptake Record: 2026-05-17 repeated error research protocol

Operating failure: The agent could keep retrying the same failing command or
edit path without stopping to learn from outside evidence or compare fixes.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: Same-error retry loops waste time, reinforce the wrong hypothesis,
and hide known fixes that could be found through web research, official docs,
repo-local solution notes, or code search.

Generalized rule: Repeated failure is a signal to change the learning loop, not
to keep retrying the same command or edit path.

Similar-case disposition: Root instructions, workflow guidance, validator
logic, tests, and this ledger are fixed now; concrete tool failures must run
the repeated-error research gate when they recur.

Repeated error protocol: The same error twice means stop retrying, research 3-5 possible fixes, choose the most efficient safe solution, implement it, and validate against the original failing path.

Pattern sweep: Checked root instructions, workflow guidance, high-signal
steering guidance, steering uptake validator, validator tests, and this ledger
for places where repeated errors could still be handled by brute-force retries.

Sweep scope: Root guide, workflow guidance, steering protocol, validator,
validator tests, and ledger records.

Search terms: repeated error, same error twice, retry, research, 3-5 fixes,
choose, implement, web.

Matches considered: Root operating guidance, repeated-error workflow guidance,
steering ledger requirements, validator repeated-error branch, and regression
test.

Exclusions: Specific tool or command implementations because the rule governs
the agent's response to repeated failures before any one tool-specific fix is
chosen.

Disposition: fixed now by adding a repeated-error protocol to root and workflow
guidance, requiring a repeated-error protocol marker in the steering validator,
adding regression coverage, and recording this uptake.

Horizontal OODA: Repeated errors may require knowledge outside the current
trajectory, including web research, official docs, cached docs, repo solution
notes, similar issue history, and adjacent tooling behavior.

Vertical OODA: The rule carries from first failure to second failure, research,
option comparison, implementation, validation, and final evidence.

Durable surface: AGENTS.md, Docs/agents/13-workflow-and-safety-guidance.md,
docs/agents/19-high-signal-steering-feedback.md, .harness/quality/steering-uptake.md,
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py, and
Infrastructure/scripts/testing/test_validate_steering_uptake.py.

Environment refinement: Repeated-error steering is now represented in root
guidance, workflow guidance, steering ledger requirements, validator logic, and
regression tests.

Mechanism: Future repeated-error feedback cannot validate without a protocol
that says same error twice, research 3-5 fixes, choose the efficient safe fix,
and implement it.

Proof: The regression test rejects a repeated-error uptake record that omits
the protocol, and the current ledger must satisfy the tightened validator.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q.

Repeat prevention: On the second occurrence of the same error, future agents
must stop the retry loop, research options, choose deliberately, and validate
the chosen fix instead of continuing local trial-and-error.

## Uptake Record: 2026-05-17 steering override halt and prove loop

Operating failure: The agent kept trying to finish the heartbeat implementation
lane even after Jamie's steering made clear that repeated feedback meant the
agent operating environment was failing.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: The active rule required classification and a ledger record, but it
did not explicitly force an active-lane halt, child-agent cleanup, and
environment-refinement proof before resuming ordinary task work.

Generalized rule: When Jamie says the agent is failing operationally, the active
work lane must stop until the environment is changed and proven.

Similar-case disposition: Root guide, steering protocol, systems-thinking
guidance, validator checks, tests, and ledger records are fixed now; runtime
projection files remain excluded as generated surfaces.

Pattern sweep: Checked AGENTS.md, UBIQUITOUS_LANGUAGE.md, the high-signal
steering protocol, the systems-thinking rule, the steering uptake validator,
validator regression tests, and this ledger for places where steering could be
acknowledged while the prior lane continued.

Sweep scope: Root agent guide, glossary, steering protocol,
systems-thinking guidance, validator code, validator tests, and the uptake
ledger.

Search terms: high-signal, steering, ordinary task work, environment
refinement, systems thinker, resume, halt.

Matches considered: Root instruction wording, active ledger rule, protocol
required response shape, validator active-rule phrase checks, and regression
tests.

Exclusions: Runtime projection files and generated artifacts because canonical
sources and the validator own this behavior.

Disposition: fixed now by adding a steering override halt rule to root
instructions and the high-signal protocol, tightening the active-rule validator,
adding regression coverage for halt/refinement/systems-thinking wording, and
recording this uptake before resuming implementation work.

Horizontal OODA: This applies across heartbeats, review swarms, repo closeout,
skill work, generated projections, and validation lanes because any of them can
become the wrong work once Jamie says the agent is failing operationally.

Vertical OODA: The rule must carry from the corrective message into agent
cleanup, planning, durable docs, validator tests, validation evidence, future
compaction recovery, and only then the resumed implementation lane.

Durable surface: AGENTS.md, Docs/agents/19-high-signal-steering-feedback.md,
Docs/agents/22-systems-thinking-product-rule.md, UBIQUITOUS_LANGUAGE.md,
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py,
Infrastructure/scripts/testing/test_validate_steering_uptake.py, and this
ledger.

Environment refinement: The active steering rule now requires agents to halt
ordinary work and prove a systems-thinking environment refinement before
resuming, and the validator rejects ledgers whose active rule omits that
halt/refinement posture.

Mechanism: The validator checks the ledger active rule for high-signal
candidate classification, a do-not-resume stop condition, environment
refinement, and systems-thinker language; the regression test proves a ledger
that lacks those phrases fails.

Proof: This record was added before resuming the heartbeat implementation lane,
the architecture review agent was closed, and validation now includes both the
steering uptake validator and its regression tests.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q.

Repeat prevention: Future agents must treat operational steering as a
lane-changing stop signal. They should pause prior work, close or cancel stale
reviewers when needed, make the smallest durable environment refinement, prove
it, and only then resume or explicitly report the blocker.

## Uptake Record: 2026-05-17 default steering candidate posture

Operating failure: The agent still treated some Jamie steering as ordinary
conversation until it contained explicit trigger language, which allowed
repeated feedback to slip through without environment refinement.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: The protocol and validator focused on high-signal trigger phrases
instead of requiring every steering item to be classified before ordinary work.

Generalized rule: Jamie steering starts as a high-signal candidate by default;
agents must classify it down rather than wait for special trigger phrases.

Similar-case disposition: Root guide, glossary, protocol, active ledger rule,
validator, and tests are fixed now; skill-specific docs are out of scope unless
they define their own steering intake.

Pattern sweep: Checked AGENTS.md, UBIQUITOUS_LANGUAGE.md, the high-signal
steering protocol, the steering uptake ledger, the steering uptake validator,
and validator regression tests for wording or checks that made uptake depend on
magic phrases.

Sweep scope: Root agent guide, glossary, steering protocol, active ledger rule,
validator code, and validator tests.

Search terms: high-signal candidate, Jamie steering, classified, trigger,
magic phrase, ordinary work.

Matches considered: Active rule language, protocol trigger language, glossary
prompt translations, validator active-rule requirements, and regression tests.

Exclusions: Skill-specific docs because the default candidate posture belongs
to the repo-level operating contract.

Disposition: fixed now by making all Jamie steering a high-signal candidate by
default, adding glossary language, and adding validator coverage for the active
ledger rule.

Horizontal OODA: This applies across repo docs, skills, evals, review loops,
PR closeout, and future sessions because Jamie steering is the operating signal
that tells agents where the environment is failing.

Vertical OODA: The rule must carry from a single correction into future
orientation, planning, implementation, validation, closeout, and compaction
recovery.

Durable surface: AGENTS.md, Docs/agents/19-high-signal-steering-feedback.md,
UBIQUITOUS_LANGUAGE.md, this ledger, the steering uptake validator, and the
validator regression tests.

Environment refinement: The root guide and steering protocol now require
classification of every Jamie steering item as a high-signal candidate before
ordinary work. The validator now fails the ledger if the active rule does not
encode that default posture.

Mechanism: Future agents cannot prove steering uptake with a ledger whose
active rule omits the candidate-and-classification default; the validator
checks that the environment itself carries this operating posture.

Proof: The new regression test rejects a ledger active rule that lacks the
default high-signal candidate wording, and the current ledger must satisfy the
tightened validator.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q.

Repeat prevention: Future Jamie steering must be classified before ordinary
work resumes. If the agent decides no durable change is needed, it must record
why; silence or acknowledgement alone is not valid uptake.

## Uptake Record: 2026-05-17 explicit environment refinement gate

Operating failure: The agent treated repeated high-signal steering as something
to acknowledge and explain, while the environment still allowed ordinary work
to resume without a new repeat-prevention mechanism.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: A steering record could pass without naming the concrete environment
refinement, and agent_operating_rule was not classified as transferable
feedback by the validator.

Generalized rule: Steering uptake requires a concrete environment refinement;
acknowledgement and explanation are not sufficient evidence.

Similar-case disposition: Root instructions, steering protocol, active ledger
rule, validator, and tests are fixed now; product-specific docs are deferred to
their owning implementation lanes.

Pattern sweep: Checked AGENTS.md, the high-signal steering protocol, the
steering uptake ledger, the steering uptake validator, and the validator
regression tests for places where meta-behavior feedback could remain prose-only
or line-local.

Sweep scope: Root instruction, high-signal steering protocol, active ledger
rule, validator code, and validator tests.

Search terms: environment refinement, mechanism, proof, agent_operating_rule,
transferable, line-local, prose-only.

Matches considered: Required ledger markers, transferable feedback type set,
protocol response shape, root stop condition, and regression fixtures.

Exclusions: Product-specific and skill-specific implementation docs because
this change governs uptake mechanics before domain work resumes.

Disposition: fixed now by adding environment refinement as a required ledger
field, making agent_operating_rule a transferable feedback type, updating the
root instruction, and adding regression coverage.

Horizontal OODA: This applies across repo docs, validation, skill planning,
review loops, and future sessions because the failure is not one artifact; it
is the agent's operating loop.

Vertical OODA: This must carry from the current correction into future
orientation, implementation, review, closeout, and compaction recovery before
ordinary work resumes.

Durable surface: AGENTS.md, Docs/agents/19-high-signal-steering-feedback.md,
.harness/quality/steering-uptake.md,
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py, and
Infrastructure/scripts/testing/test_validate_steering_uptake.py.

Environment refinement: The validator now requires an explicit Environment
refinement field in every uptake record and treats agent_operating_rule as
transferable feedback, forcing pattern sweep and disposition instead of local
acknowledgement.

Mechanism: Future high-signal steering must name what changed in the operating
environment before the ledger validates, and meta-behavior feedback now carries
the same sweep requirement as API, validation, product, and architecture rules.

Proof: The regression test rejects a steering record that lacks Environment
refinement, Mechanism, and Proof, and the current ledger must satisfy the
tightened validator.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q.

Repeat prevention: If Jamie gives high-signal steering again, the agent cannot
prove uptake with explanation alone; it must update or cite the environment
refinement, pass the validator, and report the mechanism before returning to
ordinary task work.

## Uptake Record: 2026-05-17 repeated steering loop environment refinement

Operating failure: The agent repeatedly articulated Jamie's criticism without
proving that the environment would prevent the same correction from recurring.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: The prior steering mechanism could pass with a record that lacked a
systems-thinking explanation of blocker, mechanism, and proof.

Generalized rule: A repeated correction must be converted into blocker,
mechanism, proof, and repeat-prevention evidence before ordinary work resumes.

Similar-case disposition: Root instructions, steering guidance,
systems-thinking guidance, validator, tests, and active ledger records are fixed
now; runtime projections and external memory files are excluded.

Pattern sweep: Checked root instructions, high-signal steering guidance,
systems-thinking guidance, the steering uptake validator, and the active ledger
records for fields that allowed ceremonial uptake.

Sweep scope: Root guide, steering guidance, systems-thinking guidance,
validator, tests, and active ledger records.

Search terms: operating failure, blocker, mechanism, proof, repeat prevention,
environment refinement, ceremonial uptake.

Matches considered: Ledger required markers, active rule language, validator
required markers, and regression test expectations.

Exclusions: Runtime projections and external memory files because repo-owned
uptake validation is the durable mechanism for this failure.

Disposition: fixed now by tightening the validator and updating active records;
no source-code sweep beyond the validator because this feedback governs agent
operating behavior.

Horizontal OODA: This correction applies across docs, validators, review loops,
skill authoring, harness workflows, and future Codex sessions that inherit this
repo's operating contract.

Vertical OODA: The rule must carry from this correction into future planning,
implementation, review, validation, closeout, and memory surfaces so Jamie does
not have to restate the same operating failure.

Durable surface: AGENTS.md, Docs/agents/19-high-signal-steering-feedback.md,
Docs/agents/22-systems-thinking-product-rule.md, this ledger, and
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py.

Environment refinement: Added an explicit validator field so future uptake
records must name the repo, doc, test, validator, ledger, or workflow mechanism
that changed. Added agent_operating_rule to transferable feedback types so
meta-behavior corrections require pattern sweep and disposition.

Mechanism: The validator now requires every uptake record to state operating
failure, blocker, mechanism, and proof in addition to feedback type, radius,
context, durable surface, validation, and repeat prevention.

Proof: A regression test covers missing mechanism failure, and the changed-file
validation lane runs the steering uptake validator as a required check.

Validation: Run the steering uptake validator, its regression test, docs lint,
and changed-file repo validation for the touched instruction, ledger,
validator, and test files.

Repeat prevention: Future high-signal steering cannot be accepted as absorbed
unless the environment record names the failure, blocker, mechanism, and proof.
If an agent cannot name those, it must stop instead of proceeding.

## Uptake Record: 2026-05-17 high-signal steering and OODA horizon

Operating failure: The agent treated high-signal steering as answer content
instead of as evidence that the operating environment needed refinement.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: Future agents could still proceed from repeated steering without
classifying the failure, checking context boundaries, or updating a durable
surface.

Generalized rule: High-signal steering must expand orientation across adjacent
workstreams and stacked trajectories before choosing the action radius.

Similar-case disposition: Root guide, workflow guidance, glossary, validation
docs, steering protocol, and ledger are fixed now; implementation code is out of
scope for this operating-rule uptake.

OODA scaling protocol: Use horizontal OODA and vertical OODA to identify compaction, harness, environment, repo, tracker, review-loop, or memory boundaries; resume or query the smallest target context window that can reflect on the missing context; record the changed decision before action.

Pattern sweep: Checked the active agent instruction, workflow guidance,
glossary, validation, and ledger surfaces that govern future agent behavior.

Sweep scope: Root guide, workflow guidance, glossary, validation docs,
steering protocol, and ledger.

Search terms: OODA, horizontal, vertical, steering, context boundary,
environment, durable surface.

Matches considered: Protocol OODA section, glossary terms, validation command
list, active ledger records, and root operating rules.

Exclusions: Concrete implementation code because the feedback was about
orientation and future-agent inheritance.

Disposition: policy surface updates, no code sweep because this record governs
agent operating behavior rather than a source-code pattern.

Horizontal OODA: The agent must orient against adjacent organizational activity
when current context is insufficient. The concrete mechanism is targeted
context-window resume/reflection across compaction, harness, environment,
repository, worktree, review-loop, or tracker boundaries.

Vertical OODA: The agent must orient across stacked trajectories, including
prior user steering, current branch intent, generated projections, validation
gates, review artifacts, memory surfaces, and future-agent inheritance.

Durable surface: AGENTS.md, Docs/agents/19-high-signal-steering-feedback.md,
Docs/agents/13-workflow-and-safety-guidance.md, Docs/agents/README.md,
UBIQUITOUS_LANGUAGE.md, this ledger, and
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py.

Environment refinement: Updated the steering protocol and validator-owned
ledger contract so high-signal corrections must be represented as environment
changes, not only as answer text or rewritten prose.

Mechanism: The steering uptake protocol and validator require classified
feedback, radius, context, durable surface, validation, and repeat prevention
before ordinary work resumes.

Proof: The changed-file validation lane includes the steering uptake validator
and reports required_failures=0 only when the ledger satisfies the contract.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and changed-file repo validation for the touched instruction, glossary,
ledger, and validator files.

Repeat prevention: Future high-signal steering must create or update a steering
uptake record before ordinary implementation continues. A passing validator is
required evidence; another prose-only guardrail rewrite is not sufficient.

## Uptake Record: 2026-05-17 misuse-resistant interface design

Operating failure: The agent could interpret an API-design review comment as a
single-line correction instead of a transferable interface design rule.

Feedback type: api_design_rule

Intent radius: repository

Blocker: There was no executable requirement to search equivalent APIs or
classify similar cases before closing a local fix.

Generalized rule: API-shape feedback is a transferable design rule by default;
agents must look for equivalent interfaces before treating one local fix as
complete.

Similar-case disposition: Policy surfaces were updated now; source-code cases
are classified during the concrete API/package review that names the layer to
search.

Pattern sweep: Checked review guidance, validation guidance, glossary, steering
ledger, and the dedicated interface-design policy surface for API/helper design
rules that could otherwise be applied line-locally.

Sweep scope: Review guidance, validation guidance, glossary, steering ledger,
interface-design policy, and future API-review handling.

Search terms: bool, sentinel error, API design, misuse-resistant, named error,
pattern sweep, line-local.

Matches considered: Feedback classification rules, pattern sweep contract,
interface-design principles, validation guidance, and ledger required fields.

Exclusions: Repository source APIs until a concrete implementation package or
review target is named; policy uptake happens here, code sweep happens in that
bounded package.

Generalized rule: Operational failure APIs should expose meaningful authority,
invariants, and error semantics in their shape instead of hiding diagnosis
behind bare booleans or vague helper convenience.

Similar-case disposition: Policy and validator behavior fixed now; source-code
API sweeps are deferred to the named package or layer for each concrete review
so predicate helpers and public migrations can be classified correctly.

Disposition: policy surface updates now; source-code sweeps occur when a
concrete code review comment identifies the repository package or API layer to
search.

Horizontal OODA: Interface guidance must be applied across adjacent code review,
security, validation, skill SDK, and harness work because each surface can
accidentally expose host paths, broad authority, unowned schemas, or vague
helpers as casual public APIs.

Vertical OODA: The rule must survive from review comment to implementation,
tests, docs, and future-agent closeout. A single local correction is not enough
when the feedback describes how Jamie thinks about API design generally.

Durable surface: Docs/agents/20-misuse-resistant-interface-design.md,
Docs/agents/13-workflow-and-safety-guidance.md, Docs/agents/04-validation.md,
Docs/agents/README.md, UBIQUITOUS_LANGUAGE.md, and this ledger.

Environment refinement: Added a durable interface-design rule and connected it
to the steering ledger so API-shape feedback triggers a bounded sweep instead
of staying local to one named function.

Mechanism: Broad or transferable steering records must include a pattern sweep
and disposition, and the interface-design guidance names equivalent API
inspection as required behavior.

Proof: The steering uptake validator fails broad or transferable records that
omit pattern sweep or disposition evidence.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and changed-file repo validation for the touched docs, glossary, and ledger.

Repeat prevention: Future reviews of API shape must classify misuse-resistant
design feedback as a transferable rule by default, run a bounded pattern sweep,
and prefer narrow authority, owned schemas, typed invariants, contextual errors,
and policy-like tests over prose process rules.

## Uptake Record: 2026-05-17 zero-setup agent workspace

Operating failure: The product framing could still leave Jamie as the manual
integrator of docs, scripts, runtime projections, and setup steps.

Feedback type: product_contract_rule

Intent radius: repository

Blocker: Setup responsibility was not clearly owned by agent-facing product
surfaces, so future work could ship instructions without self-setup proof.

Generalized rule: Agent-facing product surfaces must own discoverable setup,
readiness proof, and blocker classification instead of pushing integration work
onto Jamie.

Similar-case disposition: Policy and glossary surfaces were updated now;
specific setup/install/doctor flows are deferred until their owning command or
SDK surface is being implemented or reviewed.

Pattern sweep: Checked root instructions, skill-management guidance, glossary,
instruction index, and steering ledger for setup expectations that could leave
the customer as the integration layer.

Sweep scope: Root guide, skill-management docs, instruction index, glossary,
and steering ledger.

Search terms: zero setup, bootstrap, self-setup, readiness, customer
integration, blocker classification.

Matches considered: Product posture instruction, skill-management guidance,
glossary definitions, and ledger records.

Exclusions: Specific installer or doctor implementations until a setup flow is
under active implementation.

Generalized rule: Agent-facing products should make the agent responsible for
discovering, bootstrapping, validating, and reporting workspace readiness rather
than requiring Jamie to integrate scattered pieces manually.

Similar-case disposition: Policy surfaces fixed now; concrete setup, install,
doctor, or projection flows require source-specific implementation work when
those flows are active.

Disposition: policy surface updates now; not applicable to source code until a
specific setup/install/doctor flow is being implemented or reviewed.

Horizontal OODA: The zero-setup rule cuts across skill SDK, harness, runtime
projection, validation, command discovery, permissions, and environment setup.
Each surface must assume the agent is responsible for discovering and proving
readiness, while the customer should not become the integration layer.

Vertical OODA: The rule must carry from product strategy into SDK contracts,
skill manifests, doctor checks, install flows, validation gates, and closeout
reports. A setup doc alone is insufficient if no command can prove readiness.

Durable surface: AGENTS.md, Docs/agents/21-zero-setup-agent-workspace.md,
Docs/agents/17-skill-management.md, Docs/agents/README.md,
UBIQUITOUS_LANGUAGE.md, and this ledger.

Environment refinement: Added zero-setup guidance to the agent-facing
instruction surfaces so setup responsibility moves into discoverable workspace
self-checks rather than Jamie integrating scattered steps.

Mechanism: The zero-setup contract requires discoverable bootstrap, readiness
validation, blocker classification, and closeout evidence for agent-facing
workspace setup.

Proof: Changed-file validation covers the instruction and glossary surfaces
that carry the zero-setup contract.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and changed-file repo validation for the touched docs, glossary, and ledger.

Repeat prevention: Future product, SDK, and skill work must ask whether an
agent dropped into the workspace can discover, bootstrap, validate, and report
readiness without the customer integrating scattered setup steps. If not, the
gap is a product contract failure.

## Uptake Record: 2026-05-17 systems thinking product rule

Operating failure: The agent could produce polished conceptual synthesis
without identifying the blocker, durable mechanism, proof, and remaining limit.

Feedback type: product_contract_rule

Intent radius: repository

Blocker: Systems-thinking language was not yet tied to a required operating
shape that future agents must use during product or meta-work.

Generalized rule: Systems-thinking work must convert a blocker into a durable
mechanism with proof and a named remaining limit; polished explanation is not a
system.

Similar-case disposition: Policy surfaces were updated now; domain-specific
mechanisms are classified when a concrete blocker or implementation lane is in
scope.

Pattern sweep: Checked root instructions, zero-setup policy, instruction index,
glossary, and steering ledger for the umbrella blocker-to-mechanism operating
rule.

Sweep scope: Root guide, zero-setup policy, systems-thinking policy,
instruction index, glossary, and steering ledger.

Search terms: blocker, mechanism, proof, remaining limit, systems thinking,
environment refinement.

Matches considered: Root systems-thinking posture, policy doc, glossary term,
active ledger rule, and uptake records.

Exclusions: Domain implementation files because this is the operating rule for
how future domain mechanisms are framed.

Generalized rule: Systems-thinking work must translate a blocker into a
durable mechanism with proof and a stated remaining limit.

Similar-case disposition: Product and steering policy surfaces fixed now;
domain-specific mechanisms are handled in the relevant implementation lane.

Disposition: policy surface updates now; no code sweep because this is a product
operating rule until applied to a concrete blocker or implementation lane.

Horizontal OODA: Systems thinking must cut across product strategy, SDK shape,
skill authoring, validation, harness workflows, and user-facing explanations.
The shared question is which blocker prevents progress and what mechanism would
let people or agents overcome it systematically.

Vertical OODA: The rule must carry from diagnosis through implementation,
validation, explanation, and future closeout. A good answer names the blocker,
adds or points to a mechanism, proves that mechanism, and states the remaining
limit.

Durable surface: AGENTS.md, Docs/agents/22-systems-thinking-product-rule.md,
Docs/agents/21-zero-setup-agent-workspace.md, Docs/agents/README.md,
UBIQUITOUS_LANGUAGE.md, and this ledger.

Environment refinement: Added the blocker-to-mechanism rule to the durable
instruction surfaces so systems-thinking work must name what changes in the
environment, not only explain the concept.

Mechanism: The systems-thinking rule requires every explanation to state
blocker, mechanism, proof, and remaining limit instead of treating prose as the
system.

Proof: The steering uptake validator now requires every uptake record to state
operating failure, blocker, mechanism, and proof.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and changed-file repo validation for the touched docs, glossary, and ledger.

Repeat prevention: Future meta/product work must avoid polished abstraction
without mechanism. It should state blocker, mechanism, proof, and remaining
limit so code becomes the systematic unblocking path.

## Uptake Record: 2026-05-17 CTF workflow evals

Operating failure: The agent could claim high-level workflow readiness from
static review even when the truth lives in UI or app state.

Feedback type: validation_gap

Intent radius: repository

Blocker: There was no durable rule requiring planted-flag evidence before
release-readiness claims for UI/app-state workflow skills.

Generalized rule: Workflow readiness claims need executable win-condition
evidence when the truth lives in UI or app state.

Similar-case disposition: Skill-management docs, systems-thinking docs,
instruction index, glossary, and ledger are fixed now; concrete UI automation is
deferred until a target app, flag, and credential boundary are selected.

Pattern sweep: Checked skill-management guidance, systems-thinking guidance,
instruction index, glossary, and steering ledger for release-readiness surfaces
that could incorrectly trust static review for UI/app-state workflow skills.

Sweep scope: Skill-management docs, systems-thinking docs, instruction index,
glossary, and steering ledger.

Search terms: CTF, flag, workflow eval, release readiness, static review,
UI state, app state.

Matches considered: Skill readiness guidance, eval guidance, glossary term,
and uptake records that mention validation gaps.

Exclusions: Concrete UI automation code until a target app, flag, credential
boundary, and workflow skill are selected.

Disposition: policy surface updates now; eval implementation is deferred until a
specific workflow skill supplies target app, fixture, flag, and automation scope.

Horizontal OODA: Workflow skills span UI state, app automation, credentials,
fixtures, permissions, skill instructions, harness scheduling, and product
codebase drift. Static review cannot prove these workflows close the loop.

Vertical OODA: The rule must carry from planted flag to attempted run,
reflection, skill refinement commit, repeat attempt, reliability measurement,
and release-readiness claim.

Durable surface: Docs/agents/23-ctf-workflow-evals.md,
Docs/agents/17-skill-management.md, Docs/agents/22-systems-thinking-product-rule.md,
Docs/agents/README.md, UBIQUITOUS_LANGUAGE.md, and this ledger.

Environment refinement: Added CTF workflow eval guidance so workflow-skill
readiness requires an executable flag-capture mechanism or an explicit
not-applicable classification.

Mechanism: CTF workflow eval guidance makes flag capture the win condition and
requires iterative evidence before workflow-skill readiness claims.

Proof: The CTF eval record is carried by the steering ledger and covered by the
steering uptake validator and changed-file validation lane.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and changed-file repo validation for the touched docs, glossary, and ledger.

Repeat prevention: Future high-level workflow skills must not claim readiness
from prose or static review alone when the truth lives in UI or app state. They
need CTF-style eval evidence, or an explicit reason the eval is not applicable,
with optimization focused on flag capture, reliability, wall-clock time, and
resistance to codebase drift.

## Uptake Record: 2026-05-17 diagnostic debt classification

Operating failure: The agent described 16942 repo-surface findings as
nonblocking diagnostic debt without classifying the dominant categories, owner
decision, or next action.

Feedback type: diagnostic_debt

Intent radius: repository

Blocker: Large diagnostic counts can hide tracked generated artifacts,
historical evidence, and unresolved ownership decisions when closeout language
collapses them into a generic warning.

Generalized rule: Diagnostic counts must become category, owner, and next-action
classification before closeout language can call them nonblocking.

Similar-case disposition: Doctor output, closeout output, repo-surface
inventory, steering guidance, systems-thinking guidance, glossary, validator,
and tests are fixed now; individual warning-source cleanup needs separate owner
decisions.

Diagnostic classification: category repo-surface ownership debt; owner repo surface policy or explicit cleanup/allowlist decision; next action run repo surface inventory and classify, allowlist, or cleanup the dominant categories.

Pattern sweep: Checked repo doctor, repo closeout, repo-surface inventory,
high-signal steering guidance, systems-thinking guidance, glossary, and the
steering uptake validator for places that could flatten diagnostic debt.

Sweep scope: Repo doctor output, repo closeout output, repo-surface inventory,
steering guidance, systems-thinking guidance, glossary, validator, and tests.

Search terms: diagnostic, warning, blocker, nonblocking, debt, category,
owner, next action.

Matches considered: Diagnostic summary output, closeout summary output,
ledger diagnostic classification rule, and regression tests.

Exclusions: Individual warning sources because this uptake governs summary
classification first; source-specific fixes need their own owner.

Disposition: fixed now in doctor/closeout diagnostic summaries, validator
requirements, policy surfaces, glossary, and this ledger.

Horizontal OODA: Repo diagnostics connect validation, closeout, generated
artifact ownership, historical evidence retention, and future PR readiness. A
warning count must orient future agents to the owning policy surface instead of
letting them treat the number as background noise.

Vertical OODA: The rule must carry from Jamie's steering through meta-change,
doctor output, closeout reporting, validation, and future agent closeouts so the
same feedback is not required again.

Durable surface: Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py,
Infrastructure/scripts/lib/ask/commands/repo_impl.py,
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py,
Infrastructure/tests/test_ask_repo_doctor.py,
Infrastructure/scripts/testing/test_validate_steering_uptake.py,
Docs/agents/19-high-signal-steering-feedback.md,
Docs/agents/22-systems-thinking-product-rule.md, UBIQUITOUS_LANGUAGE.md, and
this ledger.

Environment refinement: Repo-surface inventory now emits blocking count
breakdowns, doctor/closeout now carry a diagnostic summary, and steering uptake
validation now rejects diagnostic feedback that lacks category, owner, and next
action.

Mechanism: Future agents get structured diagnostic categories in the machine
output and a failing steering validator if they try to record diagnostic
feedback as vague prose.

Proof: The doctor test asserts diagnostic top codes appear in repo-surface
warnings and closeout surface policy, and the steering validator test asserts
vague diagnostic uptake fails.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and pytest for Infrastructure/tests/test_ask_repo_doctor.py plus
Infrastructure/scripts/testing/test_validate_steering_uptake.py.

Repeat prevention: Future closeout language must explain high-count diagnostics
with dominant categories, owner or decision boundary, and next action before
calling them nonblocking or residual risk.

## Uptake Record: 2026-05-17 repeated error research gate

Operating failure: The agent could keep retrying the same failing command,
validator, tool call, or implementation approach instead of stopping to research
the failure class.

Feedback type: repeated_error_protocol

Intent radius: repository

Blocker: Repeating the same error without new information wastes time, hides
known fixes, and trains the environment to accept brute-force retry loops.

Generalized rule: The second occurrence of the same failure changes the work
from retrying to researching options, selecting a fix, implementing, and proving
the result.

Similar-case disposition: Root guide, steering protocol, validator code, tests,
glossary, and ledger are fixed now; concrete tool errors must run their own
research pass when they recur.

Repeated error protocol: same error twice means stop retries, research 3-5 plausible fixes using the web when available or repo-local docs when network is blocked, choose the most efficient safe option, implement it, and record evidence.

Pattern sweep: Checked root operating guidance, high-signal steering protocol,
steering uptake validator, validator regression tests, glossary, and this
ledger for retry-loop handling.

Sweep scope: Root guide, steering protocol, validator code, validator tests,
glossary, and steering ledger.

Search terms: repeated error, same error twice, retry loop, research, 3-5,
choose, implement, evidence.

Matches considered: Root repeated-error rule, protocol repeated-error record
requirement, validator repeated-error branch, and regression fixture.

Exclusions: Concrete tool errors because this is the meta protocol; a future
repeated runtime error must run its own web or repo-doc research pass.

Disposition: fixed now by adding repeated-error operating guidance, a
conditional ledger marker, validator enforcement, regression coverage, glossary
language, and this uptake record.

Horizontal OODA: Repeated errors can occur in shell commands, tests, validators,
tool calls, web/API calls, dependency setup, and implementation attempts. The
rule must change the troubleshooting loop across all of them.

Vertical OODA: The loop must move from first failure to second same failure,
research, option comparison, selected fix, implementation, validation, and
closeout evidence.

Durable surface: AGENTS.md, Docs/agents/19-high-signal-steering-feedback.md,
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py,
Infrastructure/scripts/testing/test_validate_steering_uptake.py,
UBIQUITOUS_LANGUAGE.md, and this ledger.

Environment refinement: The repo now has an explicit repeated-error protocol
and a validator branch that rejects repeated-error steering records without the
research/options/selection/implementation rule.

Mechanism: Future agents must stop after the same error twice and gather 3-5
plausible fixes before choosing and implementing the efficient safe path.

Proof: The validator regression test fails a repeated-error uptake record that
omits the protocol, and the root guide carries the operational rule for live
work.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and pytest for Infrastructure/scripts/testing/test_validate_steering_uptake.py.

Repeat prevention: Future agents should not keep fighting repeated errors; the
second same failure changes the task from retrying to researching, choosing,
implementing, and proving a better fix path.

## Uptake Record: 2026-05-17 transferable feedback generalization

Operating failure: The agent overfit Jamie's bool-return example to API design
instead of recognizing it as an example of a general feedback uptake failure.

Feedback type: agent_operating_rule

Intent radius: repository

Blocker: A model can satisfy a named example while missing the class of
misbehavior Jamie is actually pointing at, whether the example is code, tests,
docs, commands, validation, errors, reviews, or workflow behavior.

Generalized rule: Any local-looking feedback can imply a transferable
principle; agents must extract the principle and classify equivalent cases in
the nearest relevant surface before claiming uptake.

Similar-case disposition: Validator logic, validator tests, root guidance,
steering protocol, glossary, and this ledger are fixed now; concrete source,
doc, command, or workflow sweeps run when a specific layer is active.

Pattern sweep: Checked steering protocol, root instructions, glossary,
validator, validator tests, and active steering records for API-only or
design-only generalization language.

Sweep scope: Root guide, steering protocol, glossary, steering validator,
validator tests, and active ledger records.

Search terms: api_design_rule, design feedback, transferable feedback,
generalized rule, similar-case disposition, line, function, example.

Matches considered: API-specific invalid-radius rule, design-generalization
marker set, protocol wording that said design-shaped feedback, glossary naming,
and ledger records that needed generalized-rule fields.

Exclusions: Repository source APIs and workflow commands because this change is
the meta gate; concrete implementation layers need their own bounded sweep when
the feedback names that layer.

Disposition: fixed now by making generalized-rule and similar-case-disposition
requirements apply to all transferable feedback types, not only API or design
feedback.

Horizontal OODA: This applies across implementation, tests, validation, docs,
review, command behavior, repeated errors, diagnostic reporting, and workflow
operations because Jamie often uses one example to point at a broader operating
principle.

Vertical OODA: The rule must carry from local example to principle extraction,
radius selection, similar-case classification, durable surface update,
validation, and closeout evidence.

Durable surface: AGENTS.md, Docs/agents/19-high-signal-steering-feedback.md,
Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py,
Infrastructure/scripts/testing/test_validate_steering_uptake.py,
UBIQUITOUS_LANGUAGE.md, and this ledger.

Environment refinement: The validator now treats every transferable feedback
type as requiring a generalized rule and similar-case disposition, and rejects
line/function radius for all transferable feedback.

Mechanism: Future agents cannot validate an uptake record for transferable
feedback unless they state the generalized principle and classify equivalent
cases or explicitly defer them with reason.

Proof: The validator test suite now includes a non-API validation-gap fixture
that fails when generalized markers are missing.

Validation: Run python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
and pytest for Infrastructure/scripts/testing/test_validate_steering_uptake.py.

Repeat prevention: Future feedback uptake must ask what class of behavior the
example points to across the whole work surface, rather than patching only the
named instance.

## Uptake Record: 2026-05-18 repo-local prek hook home

Operating failure: A known repeated commit/push blocker stayed as recovery
memory instead of becoming a workspace readiness mechanism.

Feedback type: validation_gap

Intent radius: repository

Blocker: Generated `prek` git hooks defaulted to `$PREK_HOME/prek.log`, which
resolved to `~/.cache/prek/prek.log` in Codex sandboxed pushes and required
extra home-directory write access after validation had already passed.

Generalized rule: Repeated hook-enforced delivery failures must be promoted into
setup/readiness contracts, not handled as per-push permission exceptions.

Similar-case disposition: Prek hook install, worktree readiness, environment
check, root instructions, validation docs, workflow docs, glossary, and this
ledger are fixed now; unrelated hook runtime blockers remain classified by their
own exact failing path.

Repeated error protocol: The same `~/.cache/prek/prek.log` failure occurred
across commit and push lanes, so the fix path compared plausible options before
implementation: request home-cache permission per command, bypass hooks, set
`PREK_HOME` per command, patch generated hooks manually, or add a repo installer
that makes generated hooks use repo-local cache state.

Pattern sweep: Checked generated git hook shims, `prek.toml`, Makefile hook
targets, worktree readiness, environment checks, validation docs, workflow docs,
glossary, and memory references for `prek` cache blockers.

Sweep scope: Git hook setup/readiness surfaces and agent-facing validation docs.

Search terms: prek, PREK_HOME, prek.log, .cache/prek, pre-push, pre-commit,
hook, worktree-ready, check-environment.

Matches considered: Generated `.git/hooks/pre-commit`, `.git/hooks/commit-msg`,
`.git/hooks/pre-push`, `prek.toml`, `Makefile`, `scripts/check-environment_impl.sh`,
`Infrastructure/scripts/lifecycle-and-sync/prepare-worktree.sh`, and validation
documentation.

Exclusions: Other hook failures such as lint, Semgrep, generated projection
drift, stale git metadata, and external network/auth failures because they do not
share the `PREK_HOME` log path root cause.

Disposition: fixed now by adding `scripts/install-prek-hooks.sh`, routing
`make worktree-ready` through `scripts/prepare-worktree.sh`, patching worktree
preparation to install repo-local `PREK_HOME` hooks even without `package.json`,
and making environment validation fail when installed hooks lack the patch.

Horizontal OODA: The blocker affects every branch and worktree that commits or
pushes through `prek`, especially Codex sandbox sessions with restricted
home-directory writes.

Vertical OODA: The rule carries from fresh workspace setup, hook installation,
commit validation, pre-push validation, PR delivery, and future closeout
evidence.

Durable surface: `scripts/install-prek-hooks.sh`, `scripts/prepare-worktree.sh`,
`Infrastructure/scripts/lifecycle-and-sync/prepare-worktree.sh`,
`scripts/check-environment_impl.sh`, `Makefile`, `AGENTS.md`,
`Docs/agents/04-validation.md`, `Docs/agents/13-workflow-and-safety-guidance.md`,
`UBIQUITOUS_LANGUAGE.md`, and this ledger.

Environment refinement: Hook installation now rewrites generated `prek` shims
to set `PREK_HOME="$REPO_ROOT/.cache/prek"`, and environment validation reports
a concrete fix command if an installed hook is missing that repo-local cache
patch.

Mechanism: Future agents run `bash scripts/install-prek-hooks.sh` or
`make worktree-ready`; the generated hook writes `prek.log` inside the
workspace, so a normal hook-enforced commit or push no longer needs
`~/.cache/prek` write permission.

Proof: `prek --help` and `prek hook-impl --help` show `--log-file` defaults to
`$PREK_HOME/prek.log`; the installer sets `PREK_HOME` in generated hook shims
before `prek hook-impl` runs.

Validation: Run `bash scripts/install-prek-hooks.sh`, inspect the generated hook
for `PREK_HOME`, run `bash scripts/check-environment.sh` or focused shell syntax
checks, then rerun the normal hook-enforced push path.

Repeat prevention: Do not widen sandbox permissions for this known `prek.log`
failure first. Repair hook readiness with the repo installer, then use the normal
hook-enforced git path.

## Uptake Record: 2026-05-18 environment readiness blockers must close

Operating failure: A failing readiness command was reported as a residual risk
after the adjacent delivery mechanism had been fixed.

Feedback type: validation_gap

Intent radius: repository

Blocker: `bash scripts/check-environment.sh` failed because the validator read
Codex environment actions from the wrong TOML key and the environment setup
referenced a missing path-normalization helper.

Generalized rule: If a changed delivery or readiness surface exposes a concrete
validator failure, fix it in the same lane before closeout instead of labeling it
nonblocking.

Similar-case disposition: Environment action parsing, environment setup, Tools
action setup, focused environment tests, command-surface projection, and closeout
are fixed now.

Pattern sweep: Checked the Codex environment TOML, environment validator,
environment contract tests, prepare-worktree governance tests, command-surface
projection, and closeout.

Sweep scope: Workspace readiness and delivery validation surfaces.

Search terms: check-environment, Codex environment action, Tools, actions,
environments, normalize-path, normalize_path_candidates.

Matches considered: `.codex/environments/environment.toml`,
`Infrastructure/scripts/check-environment_impl.sh`,
`Infrastructure/scripts/testing/test_codex_environment_toml.py`,
`Infrastructure/scripts/testing/test_prepare_worktree_path_rename.py`,
`.skillsets/command-surface.json`, and repo closeout output.

Exclusions: Existing repo-surface ownership diagnostic debt and the
PyYAML/tomllib mismatch in `Infrastructure/tests/test_pr_changes_validation.py`
because they do not share the Codex environment action schema or readiness root
cause.

Disposition: fixed now by making the validator read top-level `[[actions]]`,
making setup and Tools self-contained for PATH normalization, regenerating the
command-surface projection, and proving closeout passes.

Horizontal OODA: The failure affects every workspace relying on Codex
environment readiness, setup bootstrap, or the Tools action contract.

Vertical OODA: The rule carries from generated environment config to readiness
validation, focused contract tests, command-surface projection, closeout,
commit, push, and future-agent inheritance.

Durable surface: `Infrastructure/scripts/check-environment_impl.sh`,
`.codex/environments/environment.toml`, `.skillsets/command-surface.json`,
and this ledger.

Environment refinement: Environment readiness now checks the schema actually
used by Codex environment files and no longer depends on an untracked
`.codex/scripts/normalize-path.sh` helper.

Mechanism: `bash scripts/check-environment.sh` is the proof command; a failure
there is a fix-now signal for the current delivery lane.

Proof: `bash scripts/check-environment.sh`, environment TOML contract tests,
prepare-worktree path governance tests, command-surface projection check, and
repo closeout all pass.

Validation: Run `bash scripts/check-environment.sh`,
`python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`,
`python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q`,
`python3 -m pytest Infrastructure/scripts/testing/test_codex_environment_toml.py -q`,
`python3 -m pytest Infrastructure/scripts/testing/test_prepare_worktree_path_rename.py -q`,
`./bin/ask skills handles --check --json --robot`, and
`./bin/ask repo closeout --changed --json --robot`.

Repeat prevention: Do not leave a concrete readiness command failure in the
final answer as a residual risk when the files in scope can be fixed safely.

## Uptake Record: 2026-05-18 closeout diagnostics must become fixes

Operating failure: Closeout diagnostic debt was reported as nonblocking without
first repairing the safely fixable parts or refining the diagnostic mechanism
that made the debt repeat.

Feedback type: validation_gap

Intent radius: repository

Blocker: `ask_bootstrap` had no PATH shim even though the PATH already included
`~/.local/bin`, command-surface projection drift made `repo doctor` fail despite
zero handle violations, and repo-surface diagnostics kept counting cleanup
candidates after they were deleted from the working tree.

Generalized rule: A nonblocking closeout diagnostic is still operating evidence.
Before final closeout, repair safe findings, mechanize the validator so the fix
is visible before commit, or name the owner and retained-debt class explicitly.

Similar-case disposition: Ask bootstrap PATH readiness, command-surface
projection drift, duplicated `Infrastructure/Infrastructure/**` cleanup, pending
deletion visibility, and `skills-system/**` ownership classification are fixed
now; the remaining repo-surface debt is classified historical artifact debt with
the exact dominant codes still reported by doctor.

Repeated error protocol: The same residual diagnostic was surfaced back to the
user after prior steering. The fix path stopped ordinary readiness work, repaired
the PATH shim, regenerated the canonical projection, deleted the smallest safe
duplicated artifact slice, and changed inventory classification/visibility rules
instead of retrying closeout with a better explanation.

Pattern sweep: Checked bootstrap diagnostics, doctor signal output,
command-surface projection writer/checker, repo-surface findings, duplicated
Infrastructure references, skills-system ownership docs, system-skill lockfile,
selection policy, projection-integrity bridge aliases, and steering uptake
requirements.

Sweep scope: Repo readiness diagnostics and closeout reporting surfaces.

Search terms: ask_bootstrap, PATH shim, command-surface projection,
COMMAND_SURFACE_PROJECTION_DRIFT, repo_surface, duplicated_infrastructure_path,
skills-system, system bridge, closeout diagnostic debt.

Matches considered: `scripts/bootstrap-ask.sh`,
`Infrastructure/scripts/lib/ask/bootstrap.py`, `.skillsets/command-surface.json`,
`scripts/lifecycle-and-sync/command_surface.py`,
`Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py`,
`Docs/agents/15-repo-surface-ownership.md`,
`Infrastructure/GOVERNANCE/skills-system-upstream.lock.json`,
`scripts/lifecycle-and-sync/selection_policy.py`, and this ledger.

Exclusions: The remaining tracked historical artifacts and generated work areas
because they require a larger archival cleanup decision; they are no longer
mixed with unknown ownership or duplicated-path findings after this repair.

Disposition: fixed now by installing the existing PATH shim target,
regenerating `.skillsets/command-surface.json`, deleting six duplicated
`Infrastructure/Infrastructure/**` artifacts after reference scan, excluding
worktree-deleted paths from live surface inventory, and classifying
`skills-system/**` as governed generated-tracked system-skill surface.

Horizontal OODA: This failure affects any agent that treats doctor/closeout
diagnostics as advisory prose instead of operational state to repair or classify
before continuing.

Vertical OODA: The rule carries from bootstrap setup to projection generation,
surface inventory, doctor, closeout, final reporting, and future heartbeat
continuation.

Durable surface: `/Users/jamiecraik/.local/bin/ask`,
`.skillsets/command-surface.json`,
`Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py`,
`Infrastructure/scripts/testing/test_repo_surface_inventory.py`,
`Docs/agents/15-repo-surface-ownership.md`, and this ledger.

Environment refinement: The local PATH now resolves `ask` to this repo's
`bin/ask`; repo-surface inventory now reflects working-tree deletions before
commit; `skills-system/**` has an encoded ownership class tied to the lockfile.

Mechanism: Future runs prove the repair with `bash scripts/bootstrap-ask.sh
--json`, `./bin/ask skills handles --check --no-handles --json --robot`,
`python3 -m pytest Infrastructure/scripts/testing/test_repo_surface_inventory.py
-q`, and `./bin/ask repo doctor --json --robot`.

Proof: Bootstrap reports `status: success` with `path_discovery_status: pass`;
command handles report zero violations and projection check pass; repo-surface
blocking categories no longer include `duplicated_infrastructure_path` or
`ownership_decision_required`.

Validation: Run `bash scripts/bootstrap-ask.sh --json`,
`./bin/ask skills handles --check --no-handles --json --robot`,
`python3 -m pytest Infrastructure/scripts/testing/test_repo_surface_inventory.py
-q`, `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py
--json`, and `./bin/ask repo doctor --json --robot`.

Repeat prevention: Do not call closeout findings harmless until the exact
safe-to-fix subset has been fixed and the remaining diagnostic class is narrower
than the one Jamie challenged.
