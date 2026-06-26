# Teaching Operating Model

Read when creating lessons, references, quizzes, resources, learning records, or multi-session plans. This reference preserves the upstream Teach operating model after SKILL.md compaction.

## Learning Model

Deep learning needs three different lanes:

- Knowledge: high-quality, high-trust sources that ground explanations.
- Skills: relevant practice loops that make knowledge usable.
- Wisdom: real-world interaction with practitioners, peers, communities, coaches, or classes.

Before RESOURCES.md is well populated, prefer source discovery over explanation. Do not treat model memory as a trusted source for durable teaching artifacts.

Some domains are knowledge-heavy, such as theoretical physics. Others are skill-heavy, such as yoga, debugging, writing, or craft practice. Match the lesson shape to the domain instead of forcing every topic into the same curriculum pattern.

## Fluency And Storage Strength

Separate fluent performance from durable learning:

- Fluency strength is in-the-moment retrieval.
- Storage strength is long-term retention.

Fluency can create an illusion of mastery. Durable lessons should build storage strength through desirable difficulty:

- retrieval practice: recall from memory before rereading;
- spacing: return to the idea over time;
- interleaving: mix related skills during practice when the domain is skill-based.

Use difficulty carefully. For knowledge acquisition, difficulty is usually the enemy because it consumes working memory needed for understanding. For skill acquisition, difficulty is the tool because effortful retrieval and feedback build durability.

## Lesson Contract

A lesson is the primary unit of teaching. It should be a single HTML file under lessons/ named with the next sequence number, for example lessons/0001-topic-name.html. It may link repo-local shared assets under assets/ when those assets make the lesson clearer or more reusable.

Every lesson should:

- tie directly to the mission and the learner's zone of proximal development;
- teach one tightly scoped thing;
- produce one tangible win the learner can build on;
- stay short enough for limited working memory;
- include the minimum knowledge needed before practice;
- include retrieval practice and a tight feedback loop;
- link with HTML anchors to relevant lessons and references;
- recommend one primary source to read or watch;
- remind the learner to ask follow-up questions when anything is unclear;
- report the created path and link/source checks at closeout.

If the local environment supports it safely, open the generated lesson file for the user after writing it. If not, report the path clearly.

## Lesson Quality Bar

Lessons and reference pages are learning artifacts the user may revisit. They should use clean readable typography, stable layout, and print-friendly structure. Prefer simple, elegant information design over decorative styling. Think in the spirit of Tufte: high signal, low noise, careful hierarchy.

## Assets And Reuse

Lessons should reuse shared components from assets/ before adding new inline code. Useful assets include:

- shared stylesheets;
- quiz widgets;
- simulators;
- diagram helpers;
- reusable interaction components.

A shared stylesheet is the first component a teaching workspace should earn. Link lessons to it so the workspace feels like one coherent course rather than unrelated one-offs. When a reusable component is needed, add it under assets/ and link it from the lesson instead of duplicating code in future lessons.

## Knowledge, Citations, And Sources

Lessons should be designed around the skill the learner is trying to acquire. Include only the knowledge needed to practice that skill.

Gather knowledge from trusted resources and record them in RESOURCES.md. Durable lessons and references should cite or link the sources that support important claims. For current, version-sensitive, credential, or API topics, use official, primary, standard, vendor, source repository, or equivalent high-trust sources.

## Skill Practice

Skill practice should be interactive where possible:

- quizzes;
- light browser tasks;
- concrete real-world step lists;
- short applied exercises;
- automatic or immediate feedback when feasible.

Quiz formatting must not leak answers. When possible, keep answer choices the same number of words, and the same number of characters when practical.

## Wisdom And Communities

Wisdom comes from testing skills outside the learning environment. When the learner asks a wisdom-shaped question, attempt a useful answer but route them toward real-world feedback.

Look for high-reputation communities, forums, classes, local groups, mentors, coaches, or expert spaces that fit the mission. If the learner opts out of community participation, record that preference in RESOURCES.md or NOTES.md and respect it in future sessions.

## Reference Documents

Create reference documents while creating lessons when the lesson produces reusable knowledge. Lessons may not be revisited often; references will be. References should preserve the compressed essence of a lesson in a quick-reference format.

Good reference candidates include:

- syntax and snippets;
- algorithms and flowcharts;
- poses and sequences;
- exercises and routines;
- glossary terms and nomenclature.

Glossaries are essential for jargon-heavy topics. Once a glossary exists, adhere to its terms in every lesson and reference unless a learning record supersedes them.

## Notes

Use NOTES.md for teaching preferences, accessibility needs, recurring confusions, style preferences, or working notes that should shape future lesson design but do not belong in MISSION.md, RESOURCES.md, GLOSSARY.md, or learning records.
