# Learning Record Format

Learning records live in ./learning-records/ and use sequential numbering: 0001-slug.md, 0002-slug.md, and so on. Create the directory lazily, only when the first record is written.

They are the teaching equivalent of ADRs: they capture non-obvious lessons, key insights, and stated prior knowledge that will steer future sessions. They are used to calculate the zone of proximal development.

## Template

    # {Short title of what was learned or established}

    {1-3 sentences: what was learned or what prior knowledge was established, and why it matters for future sessions.}

That is the core format. A learning record can be a single paragraph. The value is recording that this is now known and why it changes what to teach next, not in filling out sections.

## Optional Sections

Only include these when they add genuine value. Most records do not need them.

- Status frontmatter: active | superseded by LR-NNNN, useful when an earlier understanding turns out to be wrong and is replaced.
- Evidence: how the user demonstrated the understanding, such as a question answered, exercise completed, or prior experience cited.
- Implications: what this unlocks or rules out for future sessions.

## Numbering

Scan ./learning-records/ for the highest existing number and increment by one.

## When To Write A Learning Record

Write one when any of these is true:

1. The user demonstrated genuine understanding of something non-trivial, not just exposure.
2. The user disclosed prior knowledge. Record it so future sessions do not re-teach it, including the depth claimed.
3. A misconception was corrected. These are high-value because they predict future stumbling blocks.
4. The mission shifted in response to learning. Cross-link to MISSION.md and update it.

## What Does Not Qualify

- Material that was merely covered. Coverage is not learning; wait for evidence.
- Anything already captured tersely in GLOSSARY.md as a term definition.
- Session-by-session activity logs. Learning records are not a journal; they are decision-grade insights.

## Supersession

When a later record contradicts an earlier one because the user's understanding deepened or corrected, mark the old record "Status: superseded by LR-NNNN" rather than deleting it. The history of how understanding evolved is useful signal.
