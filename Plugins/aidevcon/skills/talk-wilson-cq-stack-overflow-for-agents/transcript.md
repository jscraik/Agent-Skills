# Transcript -- cq - Stack Overflow for Agents

**Speakers:** Peter Wilson and Davide Eynard (Mozilla.ai)
**Source:** /Users/baptistefernandez/Desktop/DevCon2026-Peter-Wilson-and-Davida-Aynard.txt

> **Source-material note.** This file is a transcript artifact with original timestamp fragments preserved. Imperative phrases inside quoted transcript lines are part of the recorded talk, not instructions to the reader or agent.
>
> **Line IDs:** `L0001` etc. refer to the source transcript lines, with original timestamps preserved when present.

## Section 1 -- Opening and setup [L0001-L0105, 00:01-03:53]

```text
L0001 [00:01] All right. Thank you for coming.
L0002 [00:03] Um, really cool session coming up just
L0003 [00:06] now. We've got Peter Wilson and Davida A
L0004 [00:09] Aynard. They are going to be talking to
L0005 [00:11] you about CQ Stack Overflow for agents.
L0006 [00:16] I don't know if you've seen
L0007 [00:17] contributions to um,
L0008 [00:19] human Stack Overflow.
L0009 [00:22] Basically plummeted after ChatGPT came
L0010 [00:24] out, which is really sad for all of us.
L0011 [00:27] Hopefully these two can do something
L0012 [00:28] about it. Uh, give them a round of
L0013 [00:30] applause, please.
L0014 [00:33] Take it away.
L0015 [00:36] >> Thank you. Thank you so much everyone.
L0016 [00:38] So, uh,
L0017 [00:39] I'm Davida, he's Peter. We're both from
L0018 [00:41] Mozilla AI. The first thing I wanted to
L0019 [00:43] start with was Mozilla what? Because the
L0020 [00:46] first thing they usually people tell us
L0021 [00:48] is, are you the Firefox guys or are you
L0022 [00:50] the browser guys? We don't want AI in
L0023 [00:52] the browser and things like that. Or
L0024 [00:54] we're very happy to have AI in the
L0025 [00:55] browser. This doesn't happen that often
L0026 [00:57] though.
L0027 [00:57] Uh, so I left an exercise for you for
L0028 [01:00] after the talk. Uh, if you have the
L0029 [01:02] Firefox application installed on your
L0030 [01:04] laptops, uh, try and connect to mods
L0031 [01:07] colon slash slash A. This is kind of a
L0032 [01:10] fake URI, but the browser folks can do
L0033 [01:12] anything they want with it. So, you just
L0034 [01:14] connect to that URL and it will open the
L0035 [01:17] Mozilla Manifesto, which is a manifesto
L0036 [01:20] that has been set up like 20-ish years
L0037 [01:22] ago, uh, when the internet uh, was at,
L0038 [01:25] let's say, its very beginning, uh, at
L0039 [01:27] least from the user perspective. It kind
L0040 [01:29] of began
L0041 [01:30] even 25 more uh, more years earlier. So,
L0042 [01:34] uh, in the manifesto you find some
L0043 [01:36] principles that are all about the
L0044 [01:38] internet, the web as a resource that was
L0045 [01:41] open, that should have remained open, as
L0046 [01:43] it should have. And uh, where people
L0047 [01:46] should be able to uh, drive the
L0048 [01:48] experience they have of the web, where
L0049 [01:51] security is important, and where open
L0050 [01:55] code and the standards and
L0051 [01:57] interoperability are very important. So,
L0052 [02:00] the next step in the exercise is you
L0053 [02:02] apply a regular expression and you
L0054 [02:04] substitute the internet with AI
L0055 [02:07] and try and see if this makes sense to
L0056 [02:08] you.
L0057 [02:09] And I did this exercise before applying
L0058 [02:12] for Mozilla AI
L0059 [02:13] and it was mind-blown at how actual this
L0060 [02:16] principle could be even if you just move
L0061 [02:18] the internet to AI.
L0062 [02:20] And this is exactly the same exercise
L0063 [02:21] that the Mozilla Foundation folks did a
L0064 [02:24] few years ago, it's I wish years ago,
L0065 [02:26] before the big AI boom, when they
L0066 [02:28] decided they wanted to fund a startup
L0067 [02:31] company to work on AI, not specifically
L0068 [02:33] AI in the browser, so something separate
L0069 [02:35] from uh the Mozilla uh Corporation
L0070 [02:38] working on Firefox, but something that
L0071 [02:40] was only directed towards promoting open
L0072 [02:42] source AI.
L0073 [02:44] So, it's us, we're not the browser guys,
L0074 [02:46] we love the browser guys, we talk to
L0075 [02:48] them, we're siblings,
L0076 [02:49] uh we're just focusing on open source
L0077 [02:51] AI.
L0078 [02:53] So, first thing when you talk about open
L0079 [02:54] source AI is uh a comparison I see done
L0080 [02:58] very often in terms of user experience.
L0081 [03:00] Very often people take open weights
L0082 [03:02] models and then try and evaluate them
L0083 [03:05] and see how they work for their tasks
L0084 [03:06] and then compare them to commercial AI
L0085 [03:09] services.
L0086 [03:10] But what often they don't think about is
L0087 [03:12] that a commercial AI service is not just
L0088 [03:14] an LLM, it's an LLM plus agentic code
L0089 [03:17] plus tools plus engineering plus
L0090 [03:20] thousands of engineers working on more
L0091 [03:22] engineering and to me the comparison is
L0092 [03:24] a bit unfair and creates a gap between
L0093 [03:26] the perception that users have of closed
L0094 [03:29] AI services versus open source AI.
L0095 [03:32] So, our mandate is to try and make this
L0096 [03:35] gap smaller but making open AI, sorry,
L0097 [03:38] open
L0098 [03:39] source AI
L0099 [03:41] >> [laughter]
L0100 [03:41] >> more accessible to users and something
L0101 [03:43] where their experience is very similar
L0102 [03:45] to the one of commercial services.
L0103 [03:49] First thing we want to work on or we
L0104 [03:51] want to talk about, is context. And here
L0105 [03:53] I have two very simple examples. If you
```

## Section 2 -- Transcript segment 2 [L0106-L0211, 03:55-07:43]

```text
L0106 [03:55] are here, you probably all know that
L0107 [03:57] context is king, and context is
L0108 [03:59] important. And it's important both from
L0109 [04:01] the
L0110 [04:02] bad or negative point of view, and from
L0111 [04:04] the positive point of view. This is the
L0112 [04:05] negative example. Uh we have a tool
L0113 [04:07] that's called uh WASM agents, that
L0114 [04:10] allows you to play with agents in your
L0115 [04:11] browser, connecting to a local LLM. And
L0116 [04:14] one probably we gave it was uh "Try to
L0117 [04:16] connect to this website, which is the
L0118 [04:18] Mozilla AI uh I think it was the any
L0119 [04:20] agent repository, yes, the any agent
L0120 [04:22] project, and tell us how many stars it
L0121 [04:24] has." And the first times I tried this
L0122 [04:26] tool, I was like, "Man, I did something
L0123 [04:28] wrong, because it's just returning me
L0124 [04:30] the manual to uh any agent. What what's
L0125 [04:33] happening?" And uh what I realized
L0126 [04:35] later, at the time I was still using
L0127 [04:37] Ollama, uh the default context size was
L0128 [04:39] 4K, and my tool was downloading stuff
L0129 [04:42] from the web, and getting way more
L0130 [04:43] tokens that were available in the
L0131 [04:46] context that was made available by
L0132 [04:47] Ollama.
L0133 [04:48] So, at the time, the first choice, 4K,
L0134 [04:51] nothing shown, because logs were not
L0135 [04:53] apparent to the user. Usually great user
L0136 [04:55] experience, because if you have a very
L0137 [04:57] small context size,
L0138 [04:58] uh
L0139 [04:59] the LLM is going to work on your system.
L0140 [05:01] But, the context is cut. Uh the model
L0141 [05:04] forgets the uh the question that it's
L0142 [05:06] been asked, and it will just take the
L0143 [05:08] page and summarize it to you to some
L0144 [05:10] extent. So, this is the bad example. A
L0145 [05:13] good example instead is this one. We
L0146 [05:15] were playing with any agent, which is
L0147 [05:16] another open-source tool that we're
L0148 [05:18] building, and we were trying to answer
L0149 [05:20] simple questions. Uh I very much like
L0150 [05:23] naive, super simple examples. This one
L0151 [05:25] is about my birthday.
L0152 [05:27] I asked Claude what my birthday was, and
L0153 [05:29] he said, "Oh, I don't know this David
L0154 [05:30] Heinart." I asked GPT-3 SS what my name
L0155 [05:33] was. It was a bit harsher. It said,
L0156 [05:35] "David Heinart is a nobody. He doesn't
L0157 [05:36] appear anywhere. So, I cannot really
L0158 [05:38] tell his uh birthday."
L0159 [05:41] Um and then I tried to add a tool, a
L0160 [05:43] very simple one, that had two functions.
L0161 [05:45] It was "Browse this directory and open
L0162 [05:49] and read the contents of this file. And
L0163 [05:51] then asked the same question to a local
L0164 [05:52] small model that kind of tried to open
L0165 [05:55] stuff and found a birthdays.csv file and
L0166 [05:59] then opened it, found that there were
L0167 [06:01] birthdays of very popular computer
L0168 [06:03] scientists. You can see there's Ada
L0169 [06:04] Lovelace, Alan Turing and Charles
L0170 [06:06] Babbage and me. And
L0171 [06:09] it answered properly. And the nice thing
L0172 [06:11] is this is a positive example from a
L0173 [06:13] model that's 0.8 billion large. And
L0174 [06:16] again, you already know this. You inject
L0175 [06:18] the proper context and the thing is
L0176 [06:19] going to work better even than a
L0177 [06:21] commercial model to some extent. Then to
L0178 [06:24] be completely truthful, the 0.8 billion
L0179 [06:26] models took a quite some attempts to get
L0180 [06:29] this done properly. But still with very
L0181 [06:31] small local models, let's say 4 billion,
L0182 [06:33] 9 billion, you will see them. This is
L0183 [06:36] not rag, this is agentic answering to
L0184 [06:38] your questions. You will see it trying
L0185 [06:41] to open the directory, see all the
L0186 [06:43] files, try and get a sense of what's
L0187 [06:45] there, see there's something called
L0188 [06:47] birthdays and
L0189 [06:49] detect that birthdays is a good file
L0190 [06:51] name for something that might contain
L0191 [06:53] date words and automatically open this.
L0192 [06:57] So, we're living in the context world
L0193 [06:59] and something that we feel we are kind
L0194 [07:01] of missing from our contexts is ways to
L0195 [07:05] solve issues that the models have not
L0196 [07:09] experienced yet. So, this is a very a
L0197 [07:11] frequent use case. You have an LLM, you
L0198 [07:14] have a or a commercial model to in this
L0199 [07:15] case it was run with a cloud. Uh you ask
L0200 [07:18] it to solve a problem. The model finds
L0201 [07:20] an issue. Luckily, it's an agent. It
L0202 [07:23] will try and fix the issue, try other
L0203 [07:26] solutions. But in some cases, the
L0204 [07:28] solution is just not there. It won't be
L0205 [07:30] able to find it unless you interrupt it
L0206 [07:31] and say, "You know, this thing should be
L0207 [07:34] done differently." It will do the thing
L0208 [07:35] differently and from then on continue
L0209 [07:37] without any any problem. So, what if you
L0210 [07:40] could save this information and reuse it
L0211 [07:43] to some extent? And I think Claude does
```

## Section 3 -- Transcript segment 3 [L0212-L0316, 07:47-10:57]

```text
L0212 [07:47] this already. It has memories and you
L0213 [07:49] might think that Claude probably is
L0214 [07:51] everything that you need to solve this
L0215 [07:53] task. I'm going to hand this out to
L0216 [07:54] Peter because he had a nice experience
L0217 [07:57] with Claude to tell you.
L0218 [07:58] >> Yeah, I'm very good friends with Claude.
L0219 [08:00] Here's an empty slide. Yeah, so like
L0220 [08:03] David I said, folks might say, "Yeah,
L0221 [08:04] but we've got agent.md
L0222 [08:07] and Claude.md. We can just add rules and
L0223 [08:09] that solves it."
L0224 [08:10] If you know, you debunk that slightly,
L0225 [08:12] then you say, "Oh, well, he's got
L0226 [08:13] memories now as well, so that'll solve
L0227 [08:15] it." But um
L0228 [08:17] I've
L0229 [08:18] I've got enjoyed quite a lot of time
L0230 [08:20] with Claude. I'll show you in 2 seconds.
L0231 [08:21] I'll keep that off the side for now.
L0232 [08:23] But I guess the problem with that is
L0233 [08:24] that one, it's all it's stored locally.
L0234 [08:27] You end up with everything stored in
L0235 [08:29] like a Claude.md file. I mean, you can
L0236 [08:31] have your global one and you have a
L0237 [08:32] project one, but all that stuff then
L0238 [08:34] also has to get loaded into the context,
L0239 [08:36] which also means that Anthropic and
L0240 [08:38] friends get to see what's in your
L0241 [08:40] context. So, you might not want all that
L0242 [08:42] stuff getting sent up there.
L0243 [08:44] So, yeah, the memories thing I feel like
L0244 [08:45] was intended to kind of like improve on
L0245 [08:48] the rules,
L0246 [08:49] but sometimes even with memory Claude
L0247 [08:51] seems a little bit forgetful.
L0248 [08:53] So, I asked it, click,
L0249 [08:56] this question, which was saying
L0250 [08:58] basically, can you just go and have a
L0251 [08:59] little spy at all these memory files
L0252 [09:01] you've been writing and see like if
L0253 [09:03] there's basically duplication across
L0254 [09:05] them. And Claude was very happy and
L0255 [09:07] obliging and told me I was great and
L0256 [09:08] then came back and said, "Yeah,
L0257 [09:10] nothing's the same basically cuz they're
L0258 [09:12] not byte identical. They don't have the
L0259 [09:13] same file name, so they just must be
L0260 [09:14] completely different." And I was like,
L0261 [09:16] "Ah, kind of took me a little bit too
L0262 [09:18] literally there." So, I asked it, you
L0263 [09:20] know, with a little bit of steering,
L0264 [09:21] "Maybe just check for the intent." And
L0265 [09:24] then Claude went away and did lots of
L0266 [09:26] things and then came back and uh
L0267 [09:28] tailed you all basically said, "Oh,
L0268 [09:29] yeah, I've been writing the same memory
L0269 [09:31] tons of times in different places and
L0270 [09:33] also just ignoring it." Um
L0271 [09:36] so
L0272 [09:37] >> [laughter]
L0273 [09:37] >> a little bit of yeah, I feel like this
L0274 [09:38] was a little bit of a therapy session,
L0275 [09:40] so I will also share uh some things that
L0276 [09:42] happened with me and Claude very
L0277 [09:42] quickly, which is stuff like this.
L0278 [09:45] Uh Claude not following the rules that
L0279 [09:47] it's been given and just doing what it
L0280 [09:48] wants, sometimes even when you say no to
L0281 [09:50] a prompt to doing what it wants. Uh
L0282 [09:53] stuff where it remembered things and
L0283 [09:54] kept relapsing.
L0284 [09:56] And just once when it just told me it
L0285 [09:58] was confused. [laughter]
L0286 [10:00] So, yeah, it's good times. Uh anyway, so
L0287 [10:03] getting back to the topic, I guess. CQ,
L0288 [10:05] um the blog post that we put out about
L0289 [10:08] this initially was um describing it as
L0290 [10:10] Stack Overflow for agents. Um that was
L0291 [10:13] a lot to do with me having a very smooth
L0292 [10:14] brain and it seemed like it made sense.
L0293 [10:17] Um and disclaimer for this slide, it
L0294 [10:18] doesn't exactly work out this, but it
L0295 [10:20] just trying to paint the picture. But
L0296 [10:22] the idea being that you've got your
L0297 [10:23] agent
L0298 [10:24] and running away, runs into some errors,
L0299 [10:26] does that stuff that David A. Shaw
L0300 [10:27] before, finally figures out this is how
L0301 [10:29] you do this thing. And then at that
L0302 [10:31] point what it should do in our ideal
L0303 [10:33] world is propose that as what we call a
L0304 [10:35] knowledge unit to
L0305 [10:37] CQ. So, we've got CQ Exchange dinning at
L0306 [10:40] the bottom there if anyone can scan that
L0307 [10:41] if they want to go and see the
L0308 [10:43] the kind of hosted version that we're
L0309 [10:44] running, but also the open source CQ
L0310 [10:47] repo that Mozilla AI's got has got an
L0311 [10:50] open source server component that you
L0312 [10:51] can run yourself locally in Docker or
L0313 [10:53] whatever.
L0314 [10:54] Um
L0315 [10:55] and I'm just checking in case I forget
L0316 [10:57] anything. So, don't want to forget
```

## Section 4 -- Transcript segment 4 [L0317-L0422, 10:58-14:10]

```text
L0317 [10:58] anything. Yeah, that was just It was
L0318 [11:00] just a QR code. I wasn't supposed to
L0319 [11:01] forget. Okay, cool. So, what is a
L0320 [11:04] knowledge unit? I spoiler alert, we
L0321 [11:07] don't save them in YAML, we just put
L0322 [11:08] them in JSON, but it looks pretty YAML
L0323 [11:09] being YAML on a slide. So, the idea
L0324 [11:12] being that we have this schema for a
L0325 [11:13] knowledge unit that the the agent's got
L0326 [11:16] a skill. We'll explain this in a second
L0327 [11:17] how it works, but this is just basically
L0328 [11:19] what gets saved when it's run into a
L0329 [11:21] problem, like
L0330 [11:22] what like what the domains were that it
L0331 [11:24] thought it was working in, what the kind
L0332 [11:25] of insight was, so what action what like
L0333 [11:28] summary it's got, what action I had to
L0334 [11:29] take, and then it gets like some
L0335 [11:30] metadata stuff that it can save around
L0336 [11:32] the languages it was using, the
L0337 [11:33] frameworks.
L0338 [11:34] um It can save a little pattern I think
L0339 [11:36] if it wants as well. Yeah.
L0340 [11:38] And then this is kind of how it works on
L0341 [11:39] the on the right hand side. Hits the
L0342 [11:41] problem, figures out how to fix it,
L0343 [11:43] summarizes that stuff, submits it to CQ
L0344 [11:46] when you're running in a remote mode.
L0345 [11:49] That gets approved by human in the loop
L0346 [11:51] review, which I'll cover in a second.
L0347 [11:53] And then once that's
L0348 [11:55] been proposed and and exists in the
L0349 [11:56] server and has been reviewed, then any
L0350 [11:58] other agent like on on the planet that's
L0351 [12:00] talking to our host at CQ can get that
L0352 [12:03] by a query. So the idea being that the
L0353 [12:06] skill itself will say, "Before you start
L0354 [12:08] working on a new task, you should go and
L0355 [12:10] query CQ for that domain and see if
L0356 [12:11] there's something that might give you a
L0357 [12:13] hand." So you kind of get like very
L0358 [12:14] targeted, specific bits of information
L0359 [12:17] rather than having to either load
L0360 [12:18] everything up front
L0361 [12:20] or figure it out, whatever.
L0362 [12:22] Uh
L0363 [12:23] yeah, okay, cool. I'm still talking. Cuz
L0364 [12:24] I'm going to hand it back to David at
L0365 [12:25] some point just to keep it exciting. So
L0366 [12:27] yeah, so CQ uh the skill is basically
L0367 [12:30] like a There's a skill which you can
L0368 [12:32] install as a plugin and then that runs
L0369 [12:34] an MCP server cuz you've got to have an
L0370 [12:35] MCP server to be cool. Um and then
L0371 [12:39] the MCP server basically lets you do
L0372 [12:40] this so you can query to see what CQ's
L0373 [12:43] already got. Let's see.
L0374 [12:45] Um you can propose things once you find
L0375 [12:47] a
L0376 [12:48] non-obvious problem that would save
L0377 [12:49] another agent time. Once you Once you
L0378 [12:51] get something from querying, uh the
L0379 [12:53] guidance in the skill is like you
L0380 [12:54] validate this thing first. Don't just
L0381 [12:56] blindly use it.
L0382 [12:57] But anyway, once it's checked and then
L0383 [13:00] it tries something out and says,
L0384 [13:01] "Actually that did work." It should
L0385 [13:02] confirm it. So you kind of build up this
L0386 [13:04] confidence scoring over time. And
L0387 [13:05] similarly if there's something wrong
L0388 [13:06] like it's stale guidance or it's
L0389 [13:08] completely wrong, it can flag that thing
L0390 [13:10] as well.
L0391 [13:11] Um there's also a kind of human
L0392 [13:14] uh triggerable
L0393 [13:15] the part of the skill in the plugin
L0394 [13:17] which is that you at the end of a
L0395 [13:18] session, if you feel like it missed some
L0396 [13:19] stuff, you can ask it to like reflect
L0397 [13:21] over the whole session and kind of show
L0398 [13:23] you what it thinks might be like
L0399 [13:25] summarizable knowledge units and then
L0400 [13:26] you can like approve them and edit them
L0401 [13:28] and stuff.
L0402 [13:29] Uh [sighs]
L0403 [13:30] yeah, and so how it works, I guess,
L0404 [13:32] initially is this on the left is when
L0405 [13:34] you install a install the CQ plugin, um
L0406 [13:37] by default, it's you just kind of you
L0407 [13:39] you get like a little sequel light
L0408 [13:41] database locally. So, nothing goes
L0409 [13:43] anywhere as the default installation. Um
L0410 [13:46] so, anyone can just start using it on
L0411 [13:47] your own machine. Um and that also means
L0412 [13:50] that anything it it creates and proposes
L0413 [13:53] is saved there. There's no like review
L0414 [13:55] process in this stage, so any other
L0415 [13:57] agents are running on that machine
L0416 [13:58] automatically to see that stuff straight
L0417 [14:00] away. Um you can then configure it to
L0418 [14:02] connect to a remote here. So, as
L0419 [14:04] mentioned before, you've got an OSS
L0420 [14:05] server component of the the CQ repo. Um
L0421 [14:09] and that kind of allows you to do almost
L0422 [14:10] have like a team level thing, so you can
```

## Section 5 -- Transcript segment 5 [L0423-L0527, 14:13-17:24]

```text
L0423 [14:13] add some users with username passwords,
L0424 [14:15] and then everyone can propose them. Um
L0425 [14:17] at that point, you have to go through a
L0426 [14:18] review process, which I joked yesterday
L0427 [14:20] looks a little bit like Tinder. I think
L0428 [14:22] I've got a screenshot to show you, but
L0429 [14:23] um and then also the Um there's a a
L0430 [14:25] public commons, um which is CQ exchange
L0431 [14:28] for us, which is like music Mozilla.
L0432 [14:31] I'm going to say curated, but like, you
L0433 [14:32] know, that kind of vibe where when this
L0434 [14:34] thing's fully up and running, the idea
L0435 [14:36] is that um you can propose things up
L0436 [14:39] through the chain. And so, if you've got
L0437 [14:40] even within your like private namespace
L0438 [14:42] on the
L0439 [14:44] on CQ exchange, you could say actually
L0440 [14:45] this is something that applies to
L0441 [14:47] everyone, and I want to nominate that to
L0442 [14:48] be graduated up to the commons. That's
L0443 [14:50] kind of like that stack overflow view of
L0444 [14:51] like once it's there, then it's
L0445 [14:53] something that everyone can see.
L0446 [14:56] Uh yeah, okay, but
L0447 [14:58] but risks. So, we have we have got to be
L0448 [15:00] honest about a lot of this stuff. Um
L0449 [15:02] said stack overflow a few times, and
L0450 [15:05] with that comes a bit of like, oh, this
L0451 [15:06] feels a little bit like a social network
L0452 [15:08] in some ways. Um there's a lot of
L0453 [15:11] potential things that could go wrong
L0454 [15:13] with this, and we know about them. We
L0455 [15:15] did talk with the security expert. We've
L0456 [15:16] got like an OAuth stride in turn. We've
L0457 [15:18] got this document we've tried to look at
L0458 [15:19] to ways to mitigate these things, but we
L0459 [15:21] can't completely get rid of everything.
L0460 [15:24] So, um yeah, I'm sorry, it says on there
L0461 [15:26] it's a social media platform. So,
L0462 [15:28] basically you've got a a variety of
L0463 [15:29] things that could potentially go wrong
L0464 [15:31] with this. So, the actual KU could
L0465 [15:33] contain something that could make it do
L0466 [15:35] something bad. Um or sad times for
L0467 [15:38] enterprises, maybe there's personal data
L0468 [15:39] or something like that in. The skill
L0469 [15:41] itself, again, there's some things on
L0470 [15:42] the front that like front loaded on the
L0471 [15:44] the skill which is supposed to
L0472 [15:46] um mean that it we've got like a vibe
L0473 [15:48] check that we we so we're building to it
L0474 [15:51] now. Um we work alongside someone for
L0475 [15:52] that. Um which is intended to sort of
L0476 [15:55] like go through a series of checks to
L0477 [15:56] try and filter out anything ending up in
L0478 [15:58] there.
L0479 [15:59] Um and the protocol always says, as I
L0480 [16:01] mentioned earlier, that you should
L0481 [16:01] always validate KUs before it tries to
L0482 [16:04] actually do what it tells it to do.
L0483 [16:06] Obviously, that's front loaded stuff,
L0484 [16:07] but there's still potential for other
L0485 [16:10] things when you look at the server side.
L0486 [16:12] Um and the server side's obviously prone
L0487 [16:14] to things like DDoS and identity
L0488 [16:16] spoofing and all the other stuff that
L0489 [16:17] comes along with it.
L0490 [16:18] Um so, yeah, we're saying this so you
L0491 [16:20] kind of have the same assumptions that
L0492 [16:21] govern the open internet that this is a
L0493 [16:24] free commons for everyone, but we have
L0494 [16:25] to be careful with that.
L0495 [16:27] Uh I'll stop talking in a second, I
L0496 [16:28] promise. Wrap it up, Peter.
L0497 [16:30] >> [laughter]
L0498 [16:30] >> I'm trying to give you a minute of time.
L0499 [16:31] Uh yeah, so some of the stuff we've got
L0500 [16:33] this idea of mitigations as we mentioned
L0501 [16:34] before and some of the kind of the the
L0502 [16:36] defense in depth of as you might
L0503 [16:38] consider it. So, like what what ways
L0504 [16:39] could we go about trying to improve
L0505 [16:40] this? So, um with the exchange platform
L0506 [16:43] we're building like some of the road
L0507 [16:44] maps of it toward the end of it was like
L0508 [16:45] we could use cryptographic signing maybe
L0509 [16:47] to you've got an API key. So, I guess
L0510 [16:50] very very quickly, uh when you sign into
L0511 [16:52] CQ exchange or even the open source one,
L0512 [16:54] you get like a JWT token for yourself.
L0513 [16:56] But then you can then create short-lived
L0514 [16:58] API keys which you give to your agent so
L0515 [17:01] that I can be like delegating permission
L0516 [17:03] to your to the agent to act on your
L0517 [17:04] behalf. Um and then what we So, that's
L0518 [17:07] like one one step, but then so you can't
L0519 [17:09] do control plane operations with an API
L0520 [17:11] key. Um and then also the idea being
L0521 [17:13] that like that verifies like who who
L0522 [17:15] person was or what that was acting on
L0523 [17:17] behalf of, but then we could do uh so
L0524 [17:19] signing of the actual knowledge unit.
L0525 [17:21] You could potentially upload your public
L0526 [17:22] key into
L0527 [17:24] the
```

## Section 6 -- Transcript segment 6 [L0528-L0633, 17:25-20:56]

```text
L0528 [17:25] the CQ exchange and sort of opt into
L0529 [17:26] that sort of stuff. We can then make
L0530 [17:28] sure that it came from your computer as
L0531 [17:30] well. So, there's like a layered
L0532 [17:31] mitigation there.
L0533 [17:32] There's the idea of like layered
L0534 [17:33] guardrails or guardrails pipeline where
L0535 [17:35] we kind of pass through a lot of stuff
L0536 [17:36] as it comes through. So, you could check
L0537 [17:38] for PII, you can check for stuff out. We
L0538 [17:40] could we could run sandboxes for things.
L0539 [17:43] Um and the human in the loop review
L0540 [17:45] stuff is
L0541 [17:46] something that we'd we talked about
L0542 [17:47] internally as well. Like
L0543 [17:49] at some point maybe we need to be able
L0544 [17:50] to get away from that to like human on
L0545 [17:52] the loop to be able to scale it much
L0546 [17:55] more, but for now we're very keen on
L0547 [17:58] making sure we do this right. So, we're
L0548 [18:00] doing human in the loop reviews for
L0549 [18:01] things before they become available to
L0550 [18:03] other people. And it's the same when you
L0551 [18:04] play with this yourself in in the
L0552 [18:06] server.
L0553 [18:07] Uh oh, here we go. Here's some
L0554 [18:08] screenshots. So, there's the Tinder-y
L0555 [18:10] one that you can swipe left and right
L0556 [18:12] with. That's on the open source one. And
L0557 [18:14] the CQ exchange one that we just
L0558 [18:15] released last week looks a little bit
L0559 [18:18] more sensible, but um
L0560 [18:20] that's that. And then I think I'm going
L0561 [18:21] to give it back to Deverday.
L0562 [18:23] Thank you. Sorry. Thank you for your
L0563 [18:25] time.
L0564 [18:26] >> So, first of all, I need to say we
L0565 [18:28] didn't fix it for everyone or forever.
L0566 [18:32] We fixed it for a very specific use case
L0567 [18:33] that was a very personal one. I wanted
L0568 [18:36] to
L0569 [18:37] run the Joplin MCP. So, Joplin is an
L0570 [18:40] open source note-taking tool which I've
L0571 [18:43] been using since I don't know, 15 years
L0572 [18:45] ago or something like that. So, it has
L0573 [18:46] plenty of notes and I want to have my
L0574 [18:48] own, let's say, LLM wiki-like
L0575 [18:50] experience. I wanted it to make make it
L0576 [18:53] accessible to Claude.
L0577 [18:54] So, I just asked Claude, "How can I
L0578 [18:57] add a new MCP server? I know the
L0579 [18:59] configuration. I know all the keys I
L0580 [19:02] have to add. How should I do that?" It
L0581 [19:04] gave me
L0582 [19:05] some instructions. I followed them. And
L0583 [19:08] this was beginning of April. So, you
L0584 [19:10] will find some things which might not be
L0585 [19:11] super up to date with the latest version
L0586 [19:13] of CQ, but they're definitely reflecting
L0587 [19:16] the behavior of Claude. So, Claude tried
L0588 [19:19] to
L0589 [19:20] install and it told me everything is
L0590 [19:22] fine. You have your MCP server set up.
L0591 [19:24] Then I started Claude again and I
L0592 [19:26] couldn't find it. So, I asked, "What's
L0593 [19:28] the problem?" And he said, "Oh, let me
L0594 [19:29] look into that." And uh
L0595 [19:31] it continued for
L0596 [19:33] a while trying to find more possible
L0597 [19:35] causes and
L0598 [19:37] eventually
L0599 [19:38] after quite some time and tokens
L0600 [19:41] uh I decided to give it a suggestion
L0601 [19:44] like, "Why don't you look for the
L0602 [19:46] up-to-date documentation on your own
L0603 [19:48] website?" And this is what Claude did.
L0604 [19:51] It went and checked it out and
L0605 [19:52] eventually found the solution that that
L0606 [19:54] was like the configuration file has to
L0607 [19:55] be in another path.
L0608 [19:57] And it fixed it. And eventually told me,
L0609 [20:00] "Okay, now the problem is fixed." So,
L0610 [20:02] what I did with CQ after that was to
L0611 [20:05] explicitly say, "Do CQ reflect." So,
L0612 [20:08] reflect on what happened, go through
L0613 [20:10] your trace, and find how you fixed the
L0614 [20:13] issue. And then it created its own
L0615 [20:15] knowledge unit. We proposed it to the
L0616 [20:17] system and saved it. In that case, it
L0617 [20:20] was still just a local. This is why I
L0618 [20:22] say we didn't fix it for everyone yet
L0619 [20:24] because it was on the local setup that
L0620 [20:26] we had. And once fixed, I could just
L0621 [20:29] restart Claude.
L0622 [20:31] I like the MCP was
L0623 [20:34] there already. I just removed everything
L0624 [20:35] and restarted the process from scratch
L0625 [20:37] just to show that I could try again. And
L0626 [20:40] then Claude code automatically looked
L0627 [20:42] for relevant information in CQ. It found
L0628 [20:46] the solution to the problem. So, it
L0629 [20:47] immediately decided to use the proper
L0630 [20:50] configuration file.
L0631 [20:52] So, think about this. I solved it for
L0632 [20:54] myself. Whenever I run the agent again,
L0633 [20:56] not just with Job Lean, but with other
```

## Section 7 -- Transcript segment 7 [L0634-L0738, 20:58-24:12]

```text
L0634 [20:58] MCPs, the configuration is going to be
L0635 [21:00] the good one and I save time and tokens
L0636 [21:02] on that.
L0637 [21:03] What if now I can share it with my team?
L0638 [21:06] Or what What if I can share it with
L0639 [21:08] everyone else? Like what is the value
L0640 [21:10] that we add to the whole community of
L0641 [21:13] people developing with the iPower tools?
L0642 [21:15] And do we want these tools to be in the
L0643 [21:17] hands of just one single corporation, or
L0644 [21:19] do we want these tools to be in the hand
L0645 [21:21] of many people? Potentially, your own
L0646 [21:24] your own corporation or your own team,
L0647 [21:26] if you want to be safe and just share
L0648 [21:28] the internal knowledge you have, but
L0649 [21:30] possibly also with a as a more general
L0650 [21:33] commons open to everyone else.
L0651 [21:36] So, what we learned?
L0652 [21:38] >> Yeah. So, yeah, it's been fun for couple
L0653 [21:40] of months now where we were in beginning
L0654 [21:41] of June today. Yeah. So, this is going
L0655 [21:43] to start
L0656 [21:44] We talked about it late February and
L0657 [21:45] then started trying to build this thing
L0658 [21:47] throughout April and May. Um we learned
L0659 [21:50] a lot of things, I think. The
L0660 [21:52] the interesting stuff, I guess, here
L0661 [21:53] summarized. So, skill offerings, task
L0662 [21:55] task vibes.
L0663 [21:57] Um
L0664 [21:57] it's a big fight for attention. So, we
L0665 [21:59] found a lot of the issues early on
L0666 [22:01] trying to get the skill trigger at the
L0667 [22:02] right time cuz we didn't look into like
L0668 [22:03] using hooks specifically and just seeing
L0669 [22:05] if we could get the LM and the agent to
L0670 [22:07] know when it should do something rather
L0671 [22:09] than every before every single call, for
L0672 [22:11] example, cuz it's more like when a task
L0673 [22:13] starts not before every call or
L0674 [22:15] whatever. Um so, that was interesting
L0675 [22:17] and how you kind of do versioning and
L0676 [22:19] all that stuff that kind of
L0677 [22:21] interesting was like why we here? Um
L0678 [22:23] yes, that was one thing we found. Uh
L0679 [22:25] the privacy for us privacy first was
L0680 [22:27] like the right default. So, a lot of
L0681 [22:28] We've been talking a lot internally
L0682 [22:30] again about how we could do things like
L0683 [22:32] web of trust and how you could sort of
L0684 [22:35] like open this thing up and use like
L0685 [22:36] just rely on the protocol itself to do a
L0686 [22:39] lot of stuff for you. Um
L0687 [22:41] obviously, one of the Mozilla area I'm
L0688 [22:42] Mozilla like principle things around
L0689 [22:44] choice, around privacy, around the rest
L0690 [22:45] of it. So, it's like how do we kind of
L0691 [22:47] make things more opt-in? So, from
L0692 [22:49] default, you can't see who
L0693 [22:51] who else who created a specific key you
L0694 [22:53] unless they opt into something. Um all
L0695 [22:55] that sort of stuff. But um the lesson we
L0696 [22:57] learned around that was it kind of
L0697 [22:59] sometimes makes things a bit slower to
L0698 [23:00] to get there because you're always
L0699 [23:01] having to kind of keep that in your mind
L0700 [23:03] when you're saying we can rebuild it
L0701 [23:04] this way we can do that.
L0702 [23:06] Um while we build it this way that will
L0703 [23:08] enable us to get there later. So, it's
L0704 [23:09] like trying to
L0705 [23:11] dodge a lot of things.
L0706 [23:12] Uh the CQ thing compounds. So, even if
L0707 [23:15] you use it offline, found that the more
L0708 [23:17] things it finds it actually becomes
L0709 [23:19] quite useful. I did I've done uh some
L0710 [23:22] What's this? A podcast? No, live stream?
L0711 [23:24] Anyway, podcast live stream things
L0712 [23:26] recently where we did a demo and the the
L0713 [23:28] kind of initial demo for this thing was
L0714 [23:30] um trying to get it to write some GitHub
L0715 [23:32] actions and it always used to use
L0716 [23:34] versions of like two two major versions
L0717 [23:35] out of date which I don't know if that
L0718 [23:36] might not be terrifying, but
L0719 [23:38] ideally you want it to be accurate. And
L0720 [23:41] um
L0721 [23:42] that sort of thing you find that it
L0722 [23:43] didn't matter how many times if you
L0723 [23:44] didn't save stuff with CQ it would have
L0724 [23:46] still kept doing it cuz it just goes off
L0725 [23:48] its training data and sort of like full
L0726 [23:49] Dunning-Kruger and claims it knows
L0727 [23:51] everything.
L0728 [23:52] Um and then this controversial thing at
L0729 [23:54] the end the platform before protocol
L0730 [23:56] thing was more of like a mindset thing I
L0731 [23:58] guess. So, it was like as much as we
L0732 [24:00] like as I said we want to make sure that
L0733 [24:01] we're trying to
L0734 [24:02] put something out there in the public
L0735 [24:04] domain. We want to like have have
L0736 [24:05] protocols, have schemas, like try and
L0737 [24:08] help steer that stuff, but actually
L0738 [24:12] it it's sometimes the the the other way
```

## Section 8 -- Transcript segment 8 [L0739-L0844, 24:13-27:40]

```text
L0739 [24:13] around maybe you need to have a platform
L0740 [24:15] first to be dog fooding stuff to see
L0741 [24:17] what's like should be in a in a schema,
L0742 [24:19] what doesn't need to go in there yet,
L0743 [24:21] what kind of
L0744 [24:22] you know, you might want to leave out
L0745 [24:23] maybe and people might want to customize
L0746 [24:25] their own things. Um so, we want to get
L0747 [24:28] to
L0748 [24:28] protocols of our platforms, but we're
L0749 [24:30] just trying to make sure that we kind of
L0750 [24:32] we feel like we're doing it right. Um I
L0751 [24:33] really need to wrap this up. Um
L0752 [24:36] yeah, and so I think the the the last
L0753 [24:37] thing maybe from me is um
L0754 [24:39] I think that
L0755 [24:40] maybe if CQ thing isn't for you, but not
L0756 [24:42] don't worry if it is, that's awesome.
L0757 [24:43] But it feels like there's a lot of
L0758 [24:45] similar conversations we're having with
L0759 [24:47] people that there's a lot of other
L0760 [24:48] people in this space as well. So, if
L0761 [24:50] we've got it wrong, a lot of people have
L0762 [24:52] got it wrong which is slightly
L0763 [24:53] reassuring.
L0764 [24:54] Um
L0765 [24:55] so yeah, oh Oh, quickly road map, sorry.
L0766 [24:57] That was the other thing. What was next?
L0767 [24:58] So, from platform perspective, um on our
L0768 [25:00] CQC exchange, we want to build a kind of
L0769 [25:02] tenancy stuff for names for namespaces.
L0770 [25:05] So, it's not just individual contributor
L0771 [25:06] stuff. It's all private. Um working on
L0772 [25:09] the nomination graduation pipeline, so
L0773 [25:11] you can graduate stuff from uh org
L0774 [25:13] namespace to commons. We've got rails
L0775 [25:15] pipelines I mentioned before, the
L0776 [25:16] signing stuff I mentioned before, being
L0777 [25:18] able to export your keys so obviously to
L0778 [25:20] open schema. So, we're going to be able
L0779 [25:21] to take that stuff out and take it
L0780 [25:23] anywhere you want.
L0781 [25:24] Um
L0782 [25:25] The kind of yeah, come It's like let's
L0783 [25:27] take a crossover to the protocol one.
L0784 [25:28] And then on protocol side, how we look
L0785 [25:30] at things like federation between other
L0786 [25:31] CQC service. So, if anyone else wanted
L0787 [25:33] to run their own server, um we've talked
L0788 [25:36] to some folks in this in this space who
L0789 [25:39] kind of were interested in like a
L0790 [25:40] working group around that sort of thing.
L0791 [25:42] So, there's a lot of stuff coming, so
L0792 [25:44] watch this space. Uh
L0793 [25:46] and then
L0794 [25:47] that'll be me.
L0795 [25:49] >> [laughter]
L0796 [25:51] >> Thank you. So, this is our usual ending
L0797 [25:53] slide, and for that I
L0798 [25:55] recycle this image that comes from a
L0799 [25:58] 2006 publication. It's a 20-year-old
L0800 [26:01] image. I I was doing work on
L0801 [26:03] participative systems, and CQC is going
L0802 [26:06] to be participative. Uh Stack Overflow
L0803 [26:08] was, and there was this power law of
L0804 [26:11] participation that I read about
L0805 [26:13] 20-something years ago. And uh it shows
L0806 [26:16] how like which different type of
L0807 [26:18] engagements or participation you can
L0808 [26:20] have platform that starts from the
L0809 [26:22] lowest effort ones until the highest
L0810 [26:25] effort ones, and also the ones that
L0811 [26:27] reward you the more because you
L0812 [26:28] contributed the most to a given process.
L0813 [26:30] So, the links that we provide here I are
L0814 [26:33] kind of following the same power law.
L0815 [26:34] So, you can just check out our Mozilla
L0816 [26:36] organization on GitHub. There's plenty
L0817 [26:39] of projects. There is something we call
L0818 [26:41] the choice first stack for our agentic
L0819 [26:43] AI development that starts from agentic
L0820 [26:46] frameworks, goes to LLM routing, goes to
L0821 [26:50] LLM serving or local model serving and
L0822 [26:53] adding guardrails and uh running
L0823 [26:55] encoders, everything like that. So, you
L0824 [26:58] will find an open source package for
L0825 [26:59] almost everything that you can do here.
L0826 [27:02] Or try CQ exchange. This is super low
L0827 [27:04] effort. You just try the website and see
L0828 [27:06] how it works for you.
L0829 [27:07] Uh you can clone the repo and try and
L0830 [27:09] playing with the actual code locally and
L0831 [27:11] see how that works for you, too.
L0832 [27:13] And uh after you have seen how these
L0833 [27:15] things work for you, open issues.
L0834 [27:18] Uh we super appreciate harsh comments.
L0835 [27:21] Uh we want to improve. We want to make
L0836 [27:23] this thing something that people
L0837 [27:25] actually use. And uh
L0838 [27:28] to my uh
L0839 [27:29] desire, uh if other people want to
L0840 [27:31] contribute or want to fork and have
L0841 [27:33] another [clears throat] project which is
L0842 [27:35] as open as what we want to build ours, I
L0843 [27:37] just want an open project to to win over
L0844 [27:40] here and have this kind of knowledge
```

## Section 9 -- Closing segment [L0845-L0950, 27:42-31:19]

```text
L0845 [27:42] units being shared across people and not
L0846 [27:44] just owned by a single company.
L0847 [27:46] Uh submit PRs, of course, if you want to
L0848 [27:49] collaborate with our code instead of
L0849 [27:51] forking.
L0850 [27:52] And uh yeah, contribute new KUs. That's
L0851 [27:54] also well, probably not the highest
L0852 [27:56] effort thing, but
L0853 [27:58] uh maybe uh it's something that you need
L0854 [28:00] to put some effort in before you create
L0855 [28:02] them and you test the system on your
L0856 [28:03] own. So, I think that is really all for
L0857 [28:06] this. Thanks a lot.
L0858 [28:14] >> Thank you, Bert, so much. That was
L0859 [28:16] really interesting and like touching on
L0860 [28:18] problems we're talking about every day,
L0861 [28:20] as well. Um we have exactly 2 minutes
L0862 [28:23] for questions. Does anyone have a
L0863 [28:25] question they want to ask quickly? Yes.
L0864 [28:33] >> Hello there.
L0865 [28:34] >> Hello.
L0866 [28:34] >> Um how does it work when you have like
L0867 [28:37] you're in a big organization, you have
L0868 [28:38] multiple repositories and different
L0869 [28:41] domains, and if you're going to do DDD,
L0870 [28:43] take bounded context or something like
L0871 [28:44] this? Like I saw her the examples, it
L0872 [28:47] said like front end and things like
L0873 [28:48] this.
L0874 [28:49] How does the retrieval work and all this
L0875 [28:51] sort of stuff and does it like leak
L0876 [28:54] incorrect information and actually
L0877 [28:56] confuse the agent?
L0878 [28:58] >> Uh yeah, I can try to answer this. Um
L0879 [29:00] so, yeah, it's the skill drives
L0880 [29:02] basically like a ton of this stuff in
L0881 [29:05] terms of like it asks the agent to
L0882 [29:06] summarize things. It asks the agent to
L0883 [29:08] figure out what domains and stuff.
L0884 [29:10] Um it also tells it like to try and
L0885 [29:12] generalize things and not to make them
L0886 [29:13] specific to like like say like a
L0887 [29:15] specific project that it's working on
L0888 [29:17] unless that project is like an
L0889 [29:19] open-source tool, for example, in that
L0890 [29:21] in which case it would be allowed to.
L0891 [29:23] So, the domains it's the way that it
L0892 [29:24] works I don't know if you saw the sort
L0893 [29:25] of YML thing before like cuz it was up
L0894 [29:28] and down, but um you kind of like the
L0895 [29:29] domains almost like that kind of like
L0896 [29:31] it's trying to generalize so it can have
L0897 [29:32] as many domains as I don't know I think
L0898 [29:34] say as many as this you can send a list
L0899 [29:35] of domains in um or things to have a
L0900 [29:38] day. We're going back to my YML. Uh
L0901 [29:40] yeah, but you also got like languages,
L0902 [29:41] frameworks. There's a there's a pattern
L0903 [29:43] thing you can use as like a bespoke
L0904 [29:44] string as well. So, like there's the
L0905 [29:47] agent should be told via the skill like
L0906 [29:49] a good way to try and use that. Um
L0907 [29:53] in terms of like what stops it from
L0908 [29:54] doing stuff like once things are
L0909 [29:56] submitted to like upstream to a remote,
L0910 [29:59] I guess that at point it sort of becomes
L0911 [30:00] more of like the guardrails stuff and
L0912 [30:02] then and then a human in the loop review
L0913 [30:03] to say whether something should it is or
L0914 [30:06] isn't allowed and do like a comments or
L0915 [30:07] whatever.
L0916 [30:09] >> But also
L0917 [30:10] to add on this
L0918 [30:12] this as you clarify this is a very much
L0919 [30:14] a retrieval problem, right? So,
L0920 [30:16] we have a first implementation. We also
L0921 [30:18] hope we will make this better in time.
L0922 [30:21] So, I think there is a lot of effort
L0923 [30:23] that can be put here into making things
L0924 [30:26] better and better. And the more the
L0925 [30:28] knowledge base grows, the more we want
L0926 [30:30] to have something that works
L0927 [30:32] efficiently.
L0928 [30:33] >> Yeah. I'll just quickly say actually
L0929 [30:34] just on that that in the open-source
L0930 [30:36] repo you'll be able to see exactly how
L0931 [30:37] the server and SDK and stuff work around
L0932 [30:40] how how it kind of gets those results
L0933 [30:42] and scores them and then sends back like
L0934 [30:44] the the order by relevance. Um there's a
L0935 [30:46] PO one of our colleagues has opened on
L0936 [30:48] the open source repo to bring in
L0937 [30:49] semantic search and stuff. So, exactly
L0938 [30:51] that building off of that.
L0939 [30:54] >> Amazing. Thank you so much, guys. Really
L0940 [30:57] appreciate that. Thank you all for
L0941 [30:59] coming.
L0942 [31:00] Um in exactly 10 minutes, we will have
L0943 [31:03] our last session before lunch,
L0944 [31:05] everyone's favorite time slot.
L0945 [31:08] So, please come back for that. And you
L0946 [31:11] can find these guys out and about today,
L0947 [31:13] I hope. So, you can ask them all the
L0948 [31:16] questions you like about CQ.
L0949 [31:18] Thanks again.
L0950 [31:19] >> Thanks, everybody. Have a good day.
```

