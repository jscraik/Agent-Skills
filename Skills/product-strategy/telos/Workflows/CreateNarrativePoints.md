# CreateNarrativePoints Workflow

**Purpose:** Generate a story-driven consulting narrative that delivers hard truths, presents evidence, establishes existential stakes, and offers a vision that demands courage to execute.

This is NOT a bullet-point list. This is a STORY with emotional arc, tension, and resolution.

---

## The Narrative Arc

```text
┌─────────────────────────────────────────────────────────────────────┐
│  1. OPENING     2. BAD NEWS     3. EVIDENCE     4. STAKES           │
│  "You asked"    "Yes, it's      "Here are      "You might not      │
│                  that bad"       the problems"  have a company"     │
│                                                                     │
│         ↓              ↓              ↓              ↓              │
│                                                                     │
│  5. THE PIVOT   6. REQUIREMENTS  7. THE VISION   8. THE CLOSE      │
│  "Good news:    "Extraordinary   "Here's what   "You will thrive   │
│   there IS a     courage,         it looks       and crush your    │
│   solution"      all the way"     like..."       competition"      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Input Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `source` | Yes | - | TELOS directory, analysis output, or context to analyze |
| `client_ask` | Yes | - | What the client originally asked for (in their words) |
| `vision` | No | - | The solution architecture/vision (if already defined) |
| `artifact_dir` | For `WriteReport` | - | New caller-owned output directory for the complete five-file report artifact set |

---

## The Eight Sections

### Section 1: Opening Context (Set the Stage)

**Purpose:** Mirror their words back. Show you listened. Establish the frame.

**Template:**
> "Look, you asked us to come in and [CLIENT'S EXACT ASK]. This is something [WHO REQUESTED IT - board, investors, leadership] is pushing for because of [UNDERLYING DRIVER - funding raised, market pressure, growth mandate]. And you wanted to know [THE REAL QUESTION BENEATH THE ASK]."

**Key Elements:**
- Use "you asked us" - they initiated this
- Reference the specific ask in their language
- Connect to the underlying pressure/driver
- Surface the real question they're afraid to ask directly

**Example:**
> "Look, you asked us to come in and assess whether you can scale from 200 to 2,000 customers in the next few years - which is something the Board is basically asking you to do based on the money that was raised. And you wanted to know how bad the problems really were and if they were going to stop you from doing that."

---

### Section 2: The Bad News (Deliver the Truth)

**Purpose:** Deliver the material conclusion directly without overstating the evidence.

**Template:**
> "The unfortunate news is yes, [CONFIRM THEIR FEARS]. And it's actually worse. [ESCALATE TO EXISTENTIAL]. Based on what we found, [STARK CONSEQUENCE]."

**Key Elements:**
- Cite the exact source for every observation used in the conclusion.
- Label each material statement as an **observation**, **inference**, or **unknown** before drafting the prose.
- Preserve source qualifiers such as estimates, reported beliefs, time bounds, and disputes.
- State supported consequences plainly, but use calibrated qualifiers when evidence is incomplete, stale, or disputed.
- Never present an inference as an observed fact or fill an unknown with a plausible claim.

**Example:**
> "The current evidence shows three recurring delivery failures [observation; sources: operations review and two role-based interviews]. If that pattern continues, the five-year growth target is unlikely to be met [inference]. The available sources do not establish the churn impact [unknown]."

---

### Section 3: The Evidence (Boom Boom Boom)

**Purpose:** Back up the bad news with undeniable, sourced evidence.

**Template:**
> "Here are the problems:"
> - [Problem 1 - specific, sourced]
> - [Problem 2 - specific, sourced]
> - [Problem 3 - specific, sourced]
> - ...

**Key Elements:**
- Each problem is specific, not vague
- Each has a source (interview, data, observation)
- Problems are ordered by severity or logical chain
- No more than 8-12 problems (focus on the killers)
- Use active voice, present tense

**Evidence Categories to Pull From:**
1. **Organizational dysfunction** - silos, culture conflicts, leadership gaps
2. **Operational failures** - process breakdown, system fragmentation
3. **Financial indicators** - margins, burn rate, revenue concentration
4. **Customer signals** - churn, satisfaction decline, complaints
5. **Competitive threats** - market shifts, commoditization
6. **Technical debt** - architecture problems, scaling blockers

**Example:**
> "Here are the problems:
> - Three acquisitions created three cultures that still fight each other
> - You're spending £3.5M/year on development that's orthogonal to your services team
> - Customer satisfaction is declining despite 99.98% SLA performance
> - Kivu is converting zero percent of IR cases to managed services
> - Your data is fragmented across eight systems with no unified customer view
> - Teams don't know what the priority is because it changes constantly
> - You're building ticketing systems instead of differentiation
> - Nobody owns the customer journey"

---

### Section 4: The Stakes (Existential Consequences)

**Purpose:** Make clear this isn't about optimization - it's about survival.

**Template:**
> "Because of [COMPETITIVE PRESSURE], because of the severity of these problems, and because they are getting worse - not better - [EXISTENTIAL STATEMENT]. The odds of [SURVIVAL/SUCCESS] are not good if this continues."

**Key Elements:**
- Reference external pressure (competition, market)
- Note the trajectory (getting worse, not better)
- State the survival stakes plainly
- This is the bottom of the emotional arc - darkest moment

**Example:**
> "Because of the Microsoft commoditization threat, because of the severity of these problems, and how they are getting worse - not better - the odds of you being around in five years are not good."

---

### Section 5: The Pivot (Hope Emerges)

**Purpose:** Shift from despair to possibility. But with conditions.

**Template:**
> "The good news is there IS a solution. But it will require [WHAT'S DEMANDED]. It's not possible to do this partially - it has to be done [COMMITMENT LEVEL]."

**Key Elements:**
- "Good news" signals the turn
- Solution exists (hope)
- But it demands something extraordinary
- Partial execution = failure
- This filters out the uncommitted

**Example:**
> "The good news is there is a solution. But it will require extraordinary courage from all leaders and full belief that it's not possible to do this partially - it has to be done all the way."

---

### Section 6: The Requirements (What Courage Looks Like)

**Purpose:** Specify what "extraordinary courage" actually means in practice.

**Template:**
> "Here's what [COMMITMENT LEVEL] means:
> - [Requirement 1 - specific organizational change]
> - [Requirement 2 - specific behavioral change]
> - [Requirement 3 - specific resource commitment]
> ..."

**Key Elements:**
- Translate abstract "courage" into concrete requirements
- Include organizational changes (structure, reporting)
- Include behavioral changes (how leaders must act differently)
- Include resource commitments (budget, time, attention)
- Make clear the cost of the transformation

**Example:**
> "Here's what 'all the way' means:
> - Collapse the silos completely - one team, one priority
> - Kill projects that don't serve the core mission
> - Leaders must stop changing priorities every month
> - Invest in the architecture before adding more features
> - Accept short-term pain for long-term survival"

---

### Section 7: The Vision (The Transformed Future)

**Purpose:** Paint the picture of what success looks like. Make them see it.

**Template:**
> "Here's what the solution looks like:
> [DESCRIBE THE ARCHITECTURE / SYSTEM / APPROACH]
>
> And what's even more powerful is [ESCALATING BENEFIT].
>
> This enables [ULTIMATE CAPABILITY]."

**Key Elements:**
- Concrete description of the solution architecture
- Visual if possible (diagrams, layers, flows)
- Escalating benefits (good → better → extraordinary)
- Connect to their original goals
- Make the future feel tangible and achievable

**Example:**
> "Here's what the solution looks like:
>
> Capture SOPs and context for every business unit and department. Create AI agents that are experts in those areas - agents that can answer any question from another agent or from a human about those business areas.
>
> And what's even more powerful - you can have a top-level internal agent that can ask any of those sub-agents to get current state for anything in the company.
>
> Not only that, but you can do the same thing for all your customers - a high-level customer agent able to ask questions and have them answered for your entire customer base.
>
> This is how you deliver on 'you know my company better than I do' - not through UI duct tape, but through intelligent synthesis."

---

### Section 8: The Close (Call to Courage)

**Purpose:** Land the plane. Agency is in their hands. The choice is theirs.

**Template:**
> "This is [ASSESSMENT OF THE OPPORTUNITY]. It is [TIMING STATEMENT]. If you do this, you will not just [SURVIVE] - you will [THRIVE] and [COMPETITIVE OUTCOME].
>
> But it's going to require [WHAT'S DEMANDED] to pull it off."

**Key Elements:**
- Assess the opportunity (extraordinary, rare, pivotal)
- Note the timing (perfect, critical, now-or-never)
- State the upside plainly (thrive, crush competition)
- Return to the courage requirement
- End with their agency - they must choose

**Example:**
> "This is an extraordinary architecture. It is the perfect time to implement it. If you do it, you will not just survive - you will thrive and crush your competition. You will be able to scale with this architecture.
>
> But it's going to require extraordinary courage to pull it off."

---

## Execution Steps

### Step 1: Gather TELOS Context

Scan the source directory/context for:
- **Client's original ask** - What did they hire us to do?
- **Mission/Goals** - What are they trying to achieve?
- **Current state** - Where are they actually?
- **Problems/Blockers** - What's in the way?
- **Evidence** - Interviews, data, observations
- **Stakes** - What happens if this fails?
- **Vision** - What does success look like?

### Step 2: Identify the Emotional Core

Use deep thinking to answer:
1. What is the client most afraid of? (This is the bad news)
2. What do they already suspect but haven't admitted? (This validates their instincts)
3. What's the worst realistic outcome? (This is the stakes)
4. What would make them feel hope? (This is the pivot)
5. What does courage look like for this specific situation? (This is the requirements)
6. What's the most compelling vision of success? (This is the vision)

### Step 3: Draft Each Section

Write each of the 8 sections in order:
1. Opening Context
2. The Bad News
3. The Evidence (8-12 specific problems)
4. The Stakes
5. The Pivot
6. The Requirements
7. The Vision
8. The Close

### Step 4: Validate the Arc

**Checklist:**
- [ ] Opening references their exact words/ask
- [ ] Bad news is direct while preserving every material source qualifier
- [ ] Evidence is specific and sourced
- [ ] Stakes are existential, not incremental
- [ ] Pivot provides genuine hope
- [ ] Requirements are concrete, not abstract
- [ ] Vision is tangible and compelling
- [ ] Close returns agency to them
- [ ] Overall arc has emotional movement (tension → release → agency)

---

## Tone Calibration

**This is tough love from a trusted advisor.**

**Voice characteristics:**
- Direct but not cruel
- Honest but not hopeless
- Confrontational but supportive
- Confident but not arrogant
- Urgent but not panicked

**DO:**
- Use "you" and "your" - this is personal
- State supported hard truths without erasing uncertainty or source qualifiers
- Back up claims with evidence
- Paint a compelling future
- End with their agency

**DON'T:**
- Add unsupported uncertainty language or remove uncertainty present in the source
- Use corporate buzzwords
- Be negative without offering a path forward
- Overwhelm with too many problems (8-12 max)
- End on a negative note

---

## Example Output

```markdown
## TELOS Narrative: [Client Name]

### Opening

You asked us to assess whether the current operating model can support the growth
target recorded in the engagement brief [observation; source: client ask]. The
available material does not establish whether the board has approved that target
[unknown].

### The Bad News

The reviewed sources consistently describe recurring delivery failures
[observation; sources: operations review and role-based interviews]. If that
pattern continues, the growth target is unlikely to be met [inference; qualifier:
no independently verified forecast was supplied]. The sources do not establish
the five-year survival outcome [unknown].

### The Evidence

Here is the classified evidence:

1. Role-based interviews report unresolved coordination problems across acquired teams [observation; qualifier: interview evidence, not an organization-wide survey].
2. The supplied finance extract records material platform expenditure [observation; qualifier: unaudited management data].
3. The supplied customer series trends downward during the measured period [observation; qualifier: the period and sample are limited to the supplied dataset].
4. Fragmented customer records may delay cross-team decisions [inference; qualifier: causal impact has not been measured].
5. The current sources do not identify an accountable owner for the end-to-end customer journey [unknown].

### The Stakes

If the observed delivery pattern continues while the reported market pressure
materializes, the transformation target is at risk [inference]. The probability
and timing of that market pressure remain unverified [unknown].

### The Pivot

The evidence supports testing a coordinated operating-model change
[recommendation]. Whether that change will produce the target outcomes remains
unknown until the team defines and measures a bounded pilot.

### The Requirements

The proposed pilot requires these owner decisions:

- Name one accountable owner and one measured outcome.
- Select a bounded team and time period using supplied constraints.
- Record which initiatives pause during the pilot.
- Define rollback criteria before implementation begins.

### The Vision

The proposed target state captures approved procedures and evidence in one
governed retrieval path [recommendation]. This may reduce time spent locating
current information [inference; qualifier: no runtime benchmark has been run].
Coverage, answer quality, and customer-level use remain unknown until the pilot
defines its corpus, access policy, evaluation set, and acceptance threshold.

### The Close

The evidence justifies a decision on the bounded pilot [inference]. It does not
establish that the proposed architecture guarantees scale, survival, or a
competitive outcome [unknown]. Leadership must decide whether the measured
upside, cost, and rollback boundary warrant proceeding.
```

---

## Integration Notes

### Report artifact producer contract

When `WriteReport` is selected, this workflow is the producer for the five JSON
artifacts consumed by that report. Write them together to the caller-provided
`{artifact_dir}` only after the complete source review:

- `findings.json`: sourced findings. Preserve an `epistemicStatus` of
  `observation`, `inference`, or `unknown` and any material `qualifiers` on each
  finding; do not promote unknowns into findings.
- `recommendations.json`: source-grounded recommendations whose rationale is
  traceable to the findings.
- `roadmap.json`: phases supported by supplied decisions and dependencies; do
  not invent owners, dates, or durations.
- `methodology.json`: only observed interview counts and role categories.
- `narrative.json`: the eight-section narrative fields, including the exact
  report date and risk matrix.

If any required field cannot be sourced truthfully, return a missing-evidence
blocker and write none of the five files. The workflow must first write its
source-grounded JSON payloads to a new sibling
staging directory `{draft_dir}`. Materialize that
draft with the repository producer below; it copies the exact bytes, validates
all five files, and exclusively reserves `{artifact_dir}` before population.
It writes a deterministic completion marker last, after validation. Readers
must require and validate that marker before treating the directory as
published; source and draft validation remains separate and does not require
the marker. The producer never invents content, merges evidence, or overwrites
an existing directory.

```bash
python3 "{REPO_ROOT}/Skills/product-strategy/telos/Tools/validate_report_artifacts.py" \
  --produce "{draft_dir}" "{artifact_dir}"
```

A validation, collision, reservation, or completion-marker failure blocks
`WriteReport`. A failed producer empties only its still-owned reservation but
retains that empty incomplete directory because this platform has no safe
unlink-directory-by-handle primitive. The directory has no completion marker,
so published readers reject it as non-consumable.

**Works with:**
- `InterviewExtraction` workflow output (provides evidence)
- Direct TELOS directory analysis
- Any structured consulting context

**Output is designed for:**
- Board presentations
- Executive briefings
- Consulting deliverables
- Strategic planning sessions
- Transformation kickoffs

**This replaces generic bullet-point summaries with story-driven narratives that move people to action.**
