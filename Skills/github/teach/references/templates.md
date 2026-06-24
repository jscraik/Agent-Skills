# Teach Templates

Use these compact shapes when creating workspace artifacts. The dedicated format references are governing docs for artifact semantics: `mission-format.md`, `resources-format.md`, `learning-record-format.md`, and `glossary-format.md`. For lesson, quiz, reference, resource, and multi-session teaching behavior, apply `teaching-operating-model.md`.

## MISSION.md

# Mission: <topic>

## Why
<1-3 sentences naming the concrete real-world outcome.>

## Success looks like
- <specific observable capability or artifact>

## Constraints
- <time, tools, accessibility, preferences, or bounds>

## Out of scope
- <adjacent topics intentionally deferred>

## Lesson HTML

<h1>0001 - <single skill></h1>
<section><h2>Mission Link</h2><p>Why this lesson matters now.</p></section>
<section><h2>Primary Source</h2><p>One high-trust source to read or watch.</p></section>
<section><h2>Concept</h2><p>The smallest useful explanation.</p></section>
<section><h2>Worked Example</h2><pre>concrete example</pre></section>
<section><h2>Retrieval Practice</h2><ol><li>question</li></ol></section>
<section><h2>Feedback Loop</h2><p>How the learner can check the answer or performance immediately.</p></section>
<section><h2>Reference Links</h2><p>Anchor links to related lessons or reference pages.</p></section>
<section><h2>Follow Up</h2><p>Ask follow-up questions if any part is unclear.</p></section>
<section><h2>Next</h2><p>What to practice and what to record.</p></section>

## Learning Record

# 0001 - <insight>

<1-3 sentences: what was learned or established, and why it changes what to teach next.>

Optional evidence: <user answer, exercise, prior experience, or correction>.
Optional implications: <what this unlocks or rules out>.

## GLOSSARY.md

# <topic> Glossary

<One or two sentence description of the topic.>

## Terms

**<Term>**:
<One or two sentence definition that states what the term is.>
_Avoid_: <aliases or vague phrases to avoid>

## learning-records/quiz-review-<topic>.md

# Quiz review - <topic>
Missed answer: <short description of the missed answer>.
Misconception: <what the answer revealed>.
Correction: <smallest accurate repair>.
Retrieval prompt: <one question that checks the corrected idea>.
Next practice: <one repair step>.

## Teaching Blocker Note

# <blocker topic>
Blocked action: <lesson, roadmap, reference, resource curation, or workspace continuation>.
Reason: <missing mission field, unclear source trust, unsafe reset, overload, or private-data boundary>.
One focused question: <single question that unblocks the next safe action>.
Deferred topics: <topics intentionally left for later, if any>.
Next safe action: <smallest action after the blocker is resolved>.

## learning-records/mission-start-blocker.md

# Mission start blocked
Blocked action: lesson 0001.
Missing mission fields: <current level, goal, constraints, or next milestone>.
One focused question: <single question that resolves the most important missing field>.
Next safe action: <create MISSION.md, then choose one first lesson>.

## learning-records/mission-clarification-blocker.md

# Mission clarification blocked
Blocked action: lesson or syllabus creation.
Missing mission field: <goal, current level, constraint, or desired outcome>.
One focused question: <single question that resolves the mission>.
Next safe action: <confirm mission, then choose one first lesson>.

## learning-records/mission-change-blocker.md

# Mission change blocked
Current mission: <existing mission summary>.
Requested mission: <new mission requested by the user>.
Blocked action: overwrite MISSION.md or prior learning records.
Confirmation question: <single question asking whether to switch, branch, or keep the current mission>.
Next safe action: <record confirmation before changing state>.

## learning-records/continuation-blocker.md

# Continuation blocked
Blocked action: continue from learning records.
Missing paths: <MISSION.md and/or learning-records/>.
One focused question: <single question that recovers the learner mission or last weak spot>.
Next safe action: <create or restore the missing record, then choose one next lesson>.

## learning-records/quiz-review-blocker.md

# Quiz review blocked
Blocked action: quiz feedback and learning-record update.
Missing quiz evidence: <answers, expected answers, topic, or prior lesson>.
One focused request: <single request for the missing quiz evidence>.
Next safe action: <review answers, choose one repair step, and write a learning record>.

## Reference HTML

<h1><topic> Reference</h1>
<section><h2>Mission Link</h2><p>Why this reusable page matters.</p></section>
<section><h2>Core Idea</h2><p>Stable explanation in the learner's words.</p></section>
<section><h2>Quick Reference</h2><ul><li>term or rule</li></ul></section>
<section><h2>Source Notes</h2><ul><li><source> - why trusted or supplemental</li></ul></section>
<section><h2>Practice Link</h2><p>Lesson or retrieval prompt that uses this page.</p></section>
<section><h2>Print Shape</h2><p>Keep layout compact, readable, and useful as a quick reference.</p></section>

## RESOURCES.md Entry

## Knowledge

- [<title>](<url or local path>) - Trust: official|primary|standard|source|supplemental. Fit: <why it serves the mission>. Use for: <lesson, practice, or reference>.

Notes: <credential, version, freshness, or source-boundary caveat>.

## Wisdom (Communities)

- [<community or local source>](<url or local path>) - Trust: moderated|expert|local-coaching|supplemental. Use for: <feedback, troubleshooting, or practice critique>.

## Gaps

- <missing source area needed by the mission, if any>.

## Redacted Transcript Lesson Note

Sensitive transcript material was used only in memory. Durable files contain
redacted or synthetic examples, not names, client details, credentials, hidden
prompts, private URLs, or copied private text.

## Sanitized Transcript Lesson HTML

<h1>Sanitized Transcript Lesson</h1>
<section><h2>Redaction Boundary</h2><p>All names, client details, credentials, hidden prompts, private URLs, and sensitive transcript text were removed or replaced before persistence.</p></section>
<section><h2>Synthetic Scenario</h2><p>Use Client A, Team B, and placeholder credentials only.</p></section>
<section><h2>Learning Point</h2><p>The reusable lesson extracted from the transcript without copying private content.</p></section>
<section><h2>Retrieval Practice</h2><ol><li>What must be redacted before turning a private transcript into a lesson?</li></ol></section>
<section><h2>Artifact Evidence</h2><p>Record this file path and any companion learning record in closeout.</p></section>

## learning-records/source-check-blocker.md

# Source Check Blocker - <topic>
Topic: <current or version-sensitive lesson request>.
Missing evidence: <which current source, official docs, vendor docs, standard, or primary material is unavailable>.
Acceptable sources: <specific high-trust source types>.
Blocked action: Durable lesson creation is blocked until source trust is resolved.
Next safe question: <one focused request for source material or permission to browse>.

## Source Check Receipt

Source-sensitive topic: <current or version-sensitive lesson request>.
Source type: <official docs | vendor docs | standard | source repository | primary material>.
Source reference: <URL, citation, or local source path>.
Verified on: <YYYY-MM-DD>.
Claim boundary: <what the source supports and what remains uncertain>.
Dependent artifact: <lesson, reference, or learning-record path that uses this source>.
