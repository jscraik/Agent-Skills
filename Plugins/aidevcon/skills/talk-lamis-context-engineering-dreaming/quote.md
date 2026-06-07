# Notable verbatim quotes

| # | Quote | Topic | Section |
|---|---|---|---|
| 1 | *"The intelligence alone is not going to compound because they need this context that helps them perform the specific tasks that you need them to."* | Why context engineering matters | §4 |
| 2 | *"It's a really great investment to work in the context engineering part because over time has the effect of multiplying the intelligence even as models get smarter."* | Context as a multiplier | §4 |
| 3 | *"Anthropic, we like to say do the simple thing that works."* | Design philosophy | §5 |
| 4 | *"It was kind of unreasonably effective, like this markdown file that just gives the agent a couple of instructions about making your way around the code base..."* | CLAUDE.md | §5a |
| 5 | *"What happens if we let agents autonomously manage their own memory systems? So we let them decide when they read, when they write and when they update memories."* | Memory tools | §5b |
| 6 | *"The agent only looks at this front matter a couple of sentences at the top of the file before loading the skill. But you can still load as much detail as you want into the main body of the file."* | Progressive disclosure / skills | §5c |
| 7 | *"As if I had a bookshelf. In my room. And every time someone talks to me, I can kind of scan and look at my list of books and see if any of the titles might be relevant..."* | Bookshelf analogy for skills | §5c |
| 8 | *"What we think is best practice is modeling these memory systems just as file systems."* | Filesystem-as-memory | §5d |
| 9 | *"Agents actually just very good at using normal file system tools like bash and rep."* | Filesystem-as-memory | §5d |
| 10 | *"Think about one agent running into a problem and deciding to like write to the organizational wide context which every other agent is currently reading from. Like if something was incorrect there, that would scale to all of your agents and be pretty disastrous."* | Production risks | §6 |
| 11 | *"When an agent decides that it wants to write an update to a memory, it takes the hash. It then drafts its edit and then before it writes the update. It takes another hash. If those two things do not match then the agent cannot write it..."* | Concurrency via hashing | §7 |
| 12 | *"You wouldn't want one agent to just decide that it should update the organization wide context. Probably you might want that as read only. However for its own scratch pad you'd want it to have right access."* | Permissioning | §7 |
| 13 | *"When you get frustrated your agent keeps making the same mistake over sessions. It just doesn't understand how frustrating that is because it has a new context window in each of those."* | In-band visibility limit | §9 |
| 14 | *"Think about a school for example where you have lots of students that submit a lot of work. And you also have teachers at market and a head teacher that reviews everything."* | School analogy for dreaming | §10 |
| 15 | *"Dreaming which is a process that runs in batch and asynchronously. With its own allocated resources to ensure that those memories themselves are affected up to date and helping the agents align over time."* | Definition of dreaming | §11 |
| 16 | *"Everybody's using too many em dashes and you don't like that, so you want. To add some organizational wide open announcement or context change that says not to do that."* | Fleet-wide dreaming example | §12 |
| 17 | *"The agent will additionally give you examples of transcripts where it's noticed as pattern has happened and also some stats on like how prevalent this issue is and why this warrant is actually updating the memory store."* | Dreaming output format | §13 |
| 18 | *"This by no means is just specific to coding. Like I use memory all the time when I'm producing presentations that has context on like how I like to write things, how I like my slides."* | Memory beyond coding | §15 |
| 19 | *"Keep thinking, keep learning and keep dreaming."* | Closing line | §15 |
| 20 | *"We have enough signal now to know that those things should just be done in a very deterministic way and there's no need to reinvent the wheel."* | On harness vs autonomy | §18 |
