# Outline — Artificial Intelligence (Lieven Scheire)

## Speaker

**Lieven Scheire** — Belgian comedian, physicist and science communicator. Studied physics at Ghent University before moving to TV comedy (Neveneffecten, Basta, Team Scheire, Ons DNA). Founder of Nerdland, a Belgian science-and-tech brand with a 300k-listener podcast, a 25k-visitor festival, and bestselling books. The "Artificial Intelligence" stage show has toured internationally including Northern Ireland Science Festival, CERN Comedy Festival and Edinburgh Fringe, with a UK tour in 2026. Has shared stages with Neil deGrasse Tyson and Walter Isaacson.

## Abstract (as provided)

> What exactly is this Artificial Intelligence that everyone is talking about? In this session, Lieven Scheire introduces this new superhero of technology in an entertaining and accessible way. You'll get a glimpse of how it all works, what it already can do, and what it will be capable of in the future. It's a first encounter with something that might soon become your new friend, butler, advisor, psychologist, personal trainer or guardian angel: Artificial Intelligence.

## Thesis (synthesis, not provided)

AI is not magic and is not (yet) thinking — it is "simply a new kind of software that is good at pattern recognition", a capability unlocked only recently by sufficient compute and data after 70 years of waiting. That single capability, by being chained with pattern *generation*, produced every demo we now associate with AI. Today's large language models are best understood as impressive language *imitation* rather than conceptual reasoning, and the field's main practical hazards are training-data bias and the black-box nature of trained networks.

## Section-by-section TOC

| Section | Summary | Transcript lines |
|---|---|---|
| Host introduction | The MC introduces Scheire and his name-pronunciation joke. | L1–L10 |
| Self-introduction & framing | Scheire introduces himself, his physics background, and that he speaks to a developer audience today. | L10–L24 |
| AI's birthday: Dartmouth 1956 | AI is turning 70 (June 18, 1956 Dartmouth workshop, John McCarthy); why the boom happened only recently — compute + data. | L24–L36 |
| The one-sentence definition | AI = "a new kind of software that is good at pattern recognition". | L36–L46 |
| Why classic software fails at pattern recognition | The mean-age example vs the 1000 cat/dog images example. | L46–L60 |
| Pattern recognition as a new superpower | "Where's Wally" robot demo as illustration of what changed. | L60–L72 |
| From pattern recognition to generative to (?) AGI | Recognise → generate images/video → generate language → agentic → AGI (question mark). | L72–L84 |
| AI in your pocket: the smartphone | Apollo 11 compute comparison; everyday apps (Shazam-style, Merlin bird ID, plant ID, PhotoMath). | L84–L108 |
| PhotoMath & education | Choose-wisely framing: same tool can make students dumber or smarter. | L96–L112 |
| Speech, translation, voice cloning | AI translation beating "Master Yoda sentences"; voice as a sound-wave pattern. | L112–L124 |
| HeyGen Italian-dub demo | Live demo: Scheire's clip translated to Italian with cloned voice and lip-sync. | L124–L140 |
| How brains do pattern recognition | 86 billion neurons, tentacle connections, co-activation strengthens links; the childhood-aroma memory analogy. | L140–L168 |
| Building a neural network | Cat/dog classifier walkthrough; training by labelled examples; mimicking the brain in software. | L168–L196 |
| The black box of AI | Nobody knows why the trained network works; "It somehow functional don't touch it" / Belgian politics joke. | L196–L210 |
| Training-data bias: wolves vs huskies | The "snow in the background" story; heat-map method for finding what the net is looking at. | L210–L232 |
| Training-data bias: skin cancer ruler | Dermatology app that was actually detecting doctors' rulers. | L232–L244 |
| Hobbyist AI: Custom Vision & Teachable Machine | What hobbyists can build at home — face/sound/voice recognition. | L244–L268 |
| Ben Hamm's cat flap | American engineer's cat-flap that locks when the cat carries prey, plus auto-donation to bird protection. | L268–L286 |
| Inverness Caledonian Thistle bald-referee AI camera | AI football-tracking camera kept locking onto a bald assistant referee's head. | L286–L302 |
| Patterns easy for humans, hard for AI | Muffin-or-chihuahua etc. visual confusion sets. | L302–L316 |
| Wrap-up: LLMs as language imitation, not thought | Scheire's skeptical close on conceptual thinking in LLMs; cat-story example. | L316–L334 |
| Resources | lieven.scheire.com/ai-links and the lieven.shire domain joke. | L334–L342 |

## Terminology glossary (Scheire's own definitions)

- **Artificial intelligence** — "simply a new kind of software that is good at pattern recognition."
- **Pattern recognition** — recognising faces, objects, sounds, situations; "the basic task of any biological brain."
- **Neural network** — software that mimics the architecture of the brain: input pixels treated as active/inactive neurons, propagating through weighted connections to layers that ultimately output a label like "cat" or "dog".
- **Training** — showing the network labelled examples; "based on this the computer makes some connections stronger and weaker." Scheire's analogy: like a child's brain co-activating an aroma and a memory until the connection strengthens.
- **The black box of AI** — "We have no idea [why it works]. But it works through even. That's how in Belgium we deal estate politics. It somehow functional don't touch it in the fall apart."
- **Bias / "snow in the background" effect** — when a network learns the wrong feature because of an artifact in the training data (snow behind wolves; rulers next to skin-cancer photos). "It is so obvious that we do not see it."
- **Generative AI** — networks trained not just to recognise but to *generate* patterns: images, video, then language.
- **Agentic AI** — language generation fed back into the system as input.
- **AGI (with a question mark)** — Scheire is skeptical: "I am not sure that AGI will lead to AGI [sic — likely 'AI will lead to AGI']. I think it is very impressive language imitation. I don't think it does it has the architecture of conceptual thinking…"

## Named frameworks / concepts

1. **The one-sentence definition** — "AI is simply a new kind of software that is good at pattern recognition." Scheire's deliberate rhetorical anchor against AI mysticism.
2. **Recognise → generate → agentic → AGI(?) progression** — his narrative arc for how today's AI evolved.
3. **The "snow in the background" check** — a reusable heuristic for spotting bias: ask what artifact in your training data might be doing the actual work.
4. **The "choose wisely" framing for AI-as-tool** — "one of these many examples of technology that give you the choice if it's going to make you dumb or smarter."
5. **LLMs as language imitation** — his stance that next-token statistical continuation is not the same as conceptual thought, while conceding "a lot of room for debate."
6. **Compute + data, not new algorithms** — his explanation for why AI took 70 years: the neural-network idea was old; what changed was that we finally had enough of both.

## Tools / apps mentioned (with what Scheire said about each)

- **HeyGen** — upload a clip, get it translated with cloned voice and adjusted lip-sync. Used for the Italian demo.
- **Merlin** — bird-song identification by listening.
- **PhotoMath** — point camera at a maths problem, get the answer plus step-by-step explanations.
- **Custom Vision** — train your own image classifier as a hobbyist.
- **Google Teachable Machine** — "made for young people"; trains on images, sounds, musical styles, body stances, voices.
- **3Blue1Brown** — recommended YouTube channel for the actual maths of backpropagation.
- **lieven.scheire.com/ai-links** — Scheire's own link dump of the apps he uses.

## Open questions / not covered in this talk

- Specific transformer or attention-mechanism details — Scheire stays at the level of "neurons activate other neurons" and explicitly defers backprop to 3Blue1Brown.
- AI safety/alignment as a research field (X-risk, RLHF specifics, etc.) — not addressed.
- Regulation, copyright, or legal aspects of AI — not addressed.
- Specific named LLMs beyond a passing "ChatGPT" — no comparative discussion of GPT vs Claude vs Gemini etc.
- Economic / labour-market impact of AI — not addressed.
- Reinforcement learning, robotics-as-control — not addressed; pattern recognition and generation only.
- Concrete recommendations on *which* AI to use for *which* business problem — this is a popular-science keynote, not a buyer's guide.
- Multimodal architectures or model internals beyond the cat/dog classifier — not addressed.
