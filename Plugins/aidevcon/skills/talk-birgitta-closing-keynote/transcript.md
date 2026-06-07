# Transcript -- State of Play: AI Coding Assistants

> **Speaker-label warning.** The source transcript has no per-speaker labels. The opening segment is host Simon Maple introducing the speaker. From `L0025 [01:06] >> Okay. Thanks Simon...` onward it is Birgitta Böckeler speaking. Cross-reference any named addressee before attributing.
>
> **Transcription artifacts preserved verbatim:** "Bagita Bokela", "Bigita", "Bita", "bigita bller" (all = Birgitta Böckeler); "Thor works" (= Thoughtworks); "Martin Fer's" (= Martin Fowler's); "Tesla" / "Tessle" (= Tessl); "cloud code" / "clots" / "claw" appear to mean Claude Code / Claude / Claude 3.5 in context; "codeex" appears to mean Codex; "gas town" appears to be a transcription artifact for a swarm/background-agent experiment. Do not silently correct these inside quotations.
>
> **Line IDs:** `L0001` etc. refer to source transcript lines from `DevCon2026-Birgitta.txt`, with the original timestamps preserved.

## Section 1 -- Host introduction (Simon Maple) [L0001-L0024, 00:00-00:57]

Simon introduces Birgitta as a Thoughtworks distinguished engineer, mentions her Martin Fowler-site writing, and frames the closing session as a look back over the previous 12 months.

```text
L0001 [00:00] Bagita Bokela is a is a distinguished
L0002 [00:02] engineer at Thor works and um I've been
L0003 [00:06] chatting to Bigita for a little while
L0004 [00:08] and actually was really impressed by a
L0005 [00:11] very a post that went viral on Martin
L0006 [00:13] Fowler's uh site that wrote uh talking
L0007 [00:17] about specs and talking about uh the the
L0008 [00:20] comparison at the time between SpecKit
L0009 [00:23] uh Tessle and uh Kira I think it was and
L0010 [00:27] uh okay Tesla's moved on a little bit
L0011 [00:29] since them. But it's still amazing to
L0012 [00:31] see how many people go to go to that uh
L0013 [00:33] site. Uh Bita is an amazing person. I
L0014 [00:35] very much encourage you to to follow
L0015 [00:37] her. She's she's very thoughtful in with
L0016 [00:39] so many posts and blogs that she writes
L0017 [00:41] and a really wonderful way to finish off
L0018 [00:44] uh this conference with a very visionary
L0019 [00:47] uh session whereby we is going to look
L0020 [00:49] at the last 12 months where what's been
L0021 [00:51] changing where we are today and what we
L0022 [00:53] can look forward to. So please give a
L0023 [00:55] very AI native dev warm welcome to
L0024 [00:57] bigita bller.
```

## Section 2 -- Birgitta's self-introduction and framing [L0025-L0062, 01:06-02:25]

Birgitta explains her Thoughtworks role, her three years immersed in AI coding and AI on software teams, and sets up the talk as a forest-for-the-trees recap.

```text
L0025 [01:06] >> Okay. Thanks Simon. Thanks Simon and
L0026 [01:08] Patrick for inviting me. Yeah. So I'm a
L0027 [01:11] distinguished engineer at Thoughtworks.
L0028 [01:12] And what that means for me specifically
L0029 [01:14] is that uh three years ago I got a
L0030 [01:17] full-time role to just be immersed in
L0031 [01:19] this space of AI coding or in general
L0032 [01:21] using AI on software teams to help my
L0033 [01:24] colleagues to help our clients. I kind
L0034 [01:25] of stay on top of it. So I talk a lot to
L0035 [01:28] uh our teams, our clients and so on. And
L0036 [01:31] then I write about it for example on my
L0037 [01:33] colleague Martin Fer's website. Um and
L0038 [01:35] so that's kind of like what what all of
L0039 [01:37] this is um based on. And yeah, it's kind
L0040 [01:39] of like a tough task of wrapping up
L0041 [01:42] after everybody heard about this topic
L0042 [01:43] for two days. Uh, so I'm going to try
L0043 [01:46] and help you see the forest for the
L0044 [01:48] trees or the multiple forests for all of
L0045 [01:50] the the trees. So I'll kind of do like a
L0046 [01:52] recap. I'll start with the recap slide.
L0047 [01:54] Simon was briefly confused and thought
L0048 [01:57] maybe my slide setup is wrong, but I
L0049 [01:59] it's kind of like recap a lot of what
L0050 [02:00] the stuff that you heard also over the
L0051 [02:02] last two days, but also kind of what
L0052 [02:04] happened in the last 12 months like
L0053 [02:06] advancements as well as things that are
L0054 [02:08] maybe not going so well or that are kind
L0055 [02:10] of like the all the second order
L0056 [02:12] consequences and implications that we're
L0057 [02:14] experiencing right now. So that when you
L0058 [02:16] get back to work tomorrow and your
L0059 [02:18] colleague who maybe isn't as immersed in
L0060 [02:20] the space ask you, so what should I
L0061 [02:23] know? Right? I hope I can help you
L0062 [02:25] answer that question and I'll start with
```

## Section 3 -- Models, learning map, and model selection [L0063-L0214, 02:28-07:54]

She argues that models matter but the ecosystem around them is more interesting, then lays out a learning map: not magic, statelessness, context window vs attention, and choosing models by task.

```text
L0063 [02:28] uh yeah the reason why all of this is
L0064 [02:30] happening which is uh the models. So
L0065 [02:32] kind of first and most obvious um there
L0066 [02:35] wasn't even that much talk about models
L0067 [02:36] here at the conference I think um which
L0068 [02:38] is not surprising and totally okay I
L0069 [02:40] think because for me this is not really
L0070 [02:42] the most exciting part to be honest I'm
L0071 [02:44] much more interested in everything
L0072 [02:46] that's now happening around it the
L0073 [02:47] ecosystem all of the integrations and so
L0074 [02:49] on and uh I mean obviously if we talk
L0075 [02:52] about the last 12 months there was the
L0076 [02:54] Opus 4.5 moment kind of last year um
L0077 [02:57] that uh made a lot of people kind of
L0078 [02:59] like come back to this that hadn't maybe
L0079 [03:01] tried AI AI coding for a while. Um,
L0080 [03:05] and uh, yeah, so that was maybe the
L0081 [03:07] biggest event in models that happened
L0082 [03:09] like that. I mean, almost every week
L0083 [03:11] there's a new model, but I usually don't
L0084 [03:12] even follow it that much because like I
L0085 [03:14] said, it's uh, kind of interesting to
L0086 [03:16] see all the stuff around it. So, if uh,
L0087 [03:19] we think about models like what are the
L0088 [03:22] core things kind of as users who use
L0089 [03:24] them for coding that we need to know or
L0090 [03:26] learn almost like a kind of like
L0091 [03:28] learning map, right? So the first thing
L0092 [03:31] I always try to get out of the way is
L0093 [03:32] that they are not magic right they are
L0094 [03:34] very very impressive and very very
L0095 [03:36] useful math but uh unfortunately even
L0096 [03:39] like a lot of technologists a lot of our
L0097 [03:41] peers kind of like it's very easy to
L0098 [03:43] fall into that trap right like of uh
L0099 [03:45] thinking of them as as more than that
L0100 [03:47] right so I kind of like this
L0101 [03:48] visualization to remind ourselves that
L0102 [03:51] you know even though we don't really
L0103 [03:52] know what's like why it works and what's
L0104 [03:54] happening it's still like very
L0105 [03:56] impressive math right so first of all
L0106 [03:58] they're not magic
L0107 [03:59] Um I mention here as the second point
L0108 [04:02] their statelessness because that's also
L0109 [04:04] something that I often notice that
L0110 [04:06] people haven't quite grasped right so
L0111 [04:08] the the model doesn't have a session
L0112 [04:10] right so the longer our conversation
L0113 [04:12] with them gets the longer our session
L0114 [04:13] with them gets every single time the our
L0115 [04:17] our agent our harness basically sends
L0116 [04:19] the whole history of the conversation
L0117 [04:20] right maybe not quite there's caching
L0118 [04:22] and all kinds of clever ways that uh
L0119 [04:25] different tools try to optimize that but
L0120 [04:27] they are stateless Right. So that is a a
L0121 [04:29] factor that happens like the longer our
L0122 [04:32] conversations get with them. So I think
L0123 [04:33] that's a really important core thing
L0124 [04:35] that um uh yeah people need to
L0125 [04:39] understand.
L0126 [04:41] Uh the third thing we need to know about
L0127 [04:44] is of course the size of the context
L0128 [04:46] window and um in relationship but also
L0129 [04:48] in relationship to what that means for
L0130 [04:49] attention. Right? So even though
L0131 [04:51] technically the context windows have
L0132 [04:53] gotten a lot bigger, um it comes with a
L0133 [04:55] trade-off on like how well the models
L0134 [04:57] are able to keep attention on all of the
L0135 [04:59] many instructions and all of the context
L0136 [05:01] that we're trying to feed them now. So
L0137 [05:03] there's something there to be understood
L0138 [05:05] by everybody who uses this about what
L0139 [05:07] that trade-off is. Um and then um
L0140 [05:11] finally there's uh this and that's maybe
L0141 [05:13] the the biggest area. So those first
L0142 [05:15] things are kind of like you could you
L0143 [05:17] can learn them in a formal training and
L0144 [05:18] kind of like understand the basics,
L0145 [05:20] right? But this last one is a lot more
L0146 [05:21] about using the models and figuring this
L0147 [05:24] out, right? Which model do we use for
L0148 [05:26] which task, right? So there's I mean
L0149 [05:29] these are just like a few illustrative
L0150 [05:30] examples like uh we we have autocomplete
L0151 [05:33] like there's still people who use that a
L0152 [05:35] lot. Uh let's say or let's say you want
L0153 [05:38] to just change a few specific files and
L0154 [05:39] you have very clear instructions and a
L0155 [05:41] very clear idea of what you want to do
L0156 [05:43] or you have a larger and more complex
L0157 [05:44] change that needs a bunch of code
L0158 [05:46] research before the model actually does
L0159 [05:48] it or the agent actually does that or
L0160 [05:50] you have like tasks like planning,
L0161 [05:52] debugging, designing that maybe have a
L0162 [05:54] lot more like things like asking you
L0163 [05:56] questions and a lot more reasoning
L0164 [05:58] involved. So um different tasks will
L0165 [06:01] have different levels of reasoning that
L0166 [06:03] are useful. uh will need different uh
L0167 [06:06] sizes of context and will have different
L0168 [06:09] levels of need for tool calling. And I
L0169 [06:12] actually think that in this area here,
L0170 [06:15] we don't even have to know that much
L0171 [06:16] about the details of all of the
L0172 [06:18] different features of the models, but
L0173 [06:20] it's a lot more about us reflecting on
L0174 [06:22] these types of tasks, right? Which is
L0175 [06:24] something that we've done in the
L0176 [06:25] profession for for a long time, right?
L0177 [06:27] Like all of those like philosophical
L0178 [06:28] discussions about what does complexity
L0179 [06:30] mean, right? like that we have in in
L0180 [06:32] estimations or stuff like that, right?
L0181 [06:35] So, um you have to think about like how
L0182 [06:37] many files might this involve, what's
L0183 [06:38] the blast radius, how much uncertainty
L0184 [06:40] do I still have, all of those things.
L0185 [06:43] So, I think yeah, like as I said, I
L0186 [06:44] think it's um much more important for us
L0187 [06:47] to to work on this like reflection on
L0188 [06:49] the types of tasks that we have and then
L0189 [06:51] match them to different uh levels of
L0190 [06:53] power that the the models have.
L0191 [06:57] And you if you've been bathing in
L0192 [06:59] powerful models for the last few months,
L0193 [07:01] then it's actually a nice exercise to
L0194 [07:03] remember what we're already taking for
L0195 [07:05] granted these days when we try to run a
L0196 [07:07] smaller model on our developer laptop,
L0197 [07:10] right? And try to see what it can do and
L0198 [07:13] what it cannot do. And um so here's like
L0199 [07:17] an example. This is just to show you
L0200 [07:18] kind of the speed, right? The speed has
L0201 [07:21] actually come a really long way. So this
L0202 [07:22] is Quen 3.6 six running on my Apple M3
L0203 [07:26] with 48 GB of RAM and it's actually not
L0204 [07:29] even that much slower than like some of
L0205 [07:31] the stuff that happens in cloud code uh
L0206 [07:33] with with sonnet or opus right this is
L0207 [07:35] uh this is open code um by the way so
L0208 [07:38] the speed has actually come quite a bit
L0209 [07:40] of a way tool calling is still kind of
L0210 [07:43] even with this like quite powerful model
L0211 [07:45] that I could hardly even run on a 64 GB
L0212 [07:48] RAM uh MacBook so it it it crashed after
L0213 [07:51] my my first attempts to use So even that
L0214 [07:54] model was still struggling a bit with
```

## Section 4 -- Coding harnesses and their features [L0215-L0349, 07:55-12:46]

She defines the coding harness/agent layer: prompts, tool integrations, code search, orchestration, UI, extensibility, observability, and the growing need to understand tool footprint and features.

```text
L0215 [07:55] tool calling which is really crucial for
L0216 [07:57] our agentic workflows, right? Um but it
L0217 [08:01] it also has gotten a lot better than it
L0218 [08:03] than it was like I don't know 6 months
L0219 [08:04] ago or so. Um and complexity of all the
L0220 [08:07] instructions I mean uh you know many of
L0221 [08:10] you might have seen this when you when
L0222 [08:12] you try smaller models or I remember
L0223 [08:14] when I first used Gemini for for coding
L0224 [08:16] like a year ago. So I kept I kept
L0225 [08:18] getting these these as well. So um that
L0226 [08:21] is still happening but at the same time
L0227 [08:24] like I was for example recently with uh
L0228 [08:26] Gemma 4 which is like a model that
L0229 [08:28] everybody's talking about right now in
L0230 [08:30] terms of like a smaller model that is
L0231 [08:31] quite capable at coding comparatively
L0232 [08:34] you know to uh to other small models and
L0233 [08:36] so I used this recently again this was
L0234 [08:38] the type of task where I knew exactly
L0235 [08:40] what needed to be done but I couldn't be
L0236 [08:42] bothered to type it out myself right so
L0237 [08:44] I gave it like one small paragraph of
L0238 [08:47] instructions and it was actually really
L0239 [08:48] good at doing that I went after that
L0240 [08:50] back and forth a little bit, had it
L0241 [08:51] refactor it a little bit because it was
L0242 [08:53] quite uh psychometically complex and
L0243 [08:56] then I had my little utility script. So
L0244 [08:58] for this I could actually use it on my
L0245 [09:00] uh on my M3. Right? So again it's a lot
L0246 [09:03] about like knowing the tasks and then
L0247 [09:05] kind of uh mapping that to the level of
L0248 [09:07] power you want to use.
L0249 [09:10] So moving on from the model then the
L0250 [09:11] next thing that we have around the model
L0251 [09:13] is what we what uh we've now kind of
L0252 [09:15] come to calling the coding harness right
L0253 [09:17] or uh you know also sometimes more
L0254 [09:20] colloquially still like the coding agent
L0255 [09:22] right so um that's the thing that's kind
L0256 [09:25] of helping us leverage the model for our
L0257 [09:27] coding tasks and it has things under the
L0258 [09:30] hood like a system prompt or all kinds
L0259 [09:32] of like like other prompts that we
L0260 [09:33] usually can't even see when unless it's
L0261 [09:35] open source right I mean we recently got
L0262 [09:38] a glimpse into the cloud code once But
L0263 [09:40] uh a lot of them are a lot of the big
L0264 [09:42] ones that we actually use a lot are
L0265 [09:44] closed source right um it comes
L0266 [09:47] according comes with a tool integrations
L0267 [09:49] all of the standard stuff that we'll
L0268 [09:50] definitely need right uh changing files
L0269 [09:53] reading files code search is a big one
L0270 [09:55] right so we get like a type of code
L0271 [09:57] search out of the box which each with
L0272 [09:59] each harness that we uh pick um it has
L0273 [10:03] like all kinds of orchestration like
L0274 [10:04] most of them has have sub agents now for
L0275 [10:07] example also decide when to spawn of
L0276 [10:09] certain sub agents or they kind of
L0277 [10:12] decide like how many tool calls at once
L0278 [10:14] they pass onto the model and all of
L0279 [10:16] those types of things. Um maybe there's
L0280 [10:19] some caching involved in uh some of them
L0281 [10:21] they have a user interface of course
L0282 [10:23] right like some of them have a terminal
L0283 [10:26] based user interface some of them are
L0284 [10:27] like in VS code or uh or other more
L0285 [10:30] graphical um user interfaces and they
L0286 [10:33] also come with different levels of
L0287 [10:35] extensibility and observability. So
L0288 [10:37] extensibility famously the PI coding
L0289 [10:39] agent is very popular right now as one
L0290 [10:41] that has kind of brought that more to
L0291 [10:43] our attention of having a coding agent
L0292 [10:45] that we can actually like that is
L0293 [10:46] malleable that we can change right and
L0294 [10:48] observability uh is also a space where
L0295 [10:51] there's a lot happening right now in
L0296 [10:53] terms of uh you know having traces of
L0297 [10:56] what the agent is doing uh how can we
L0298 [10:59] use that to for example analyze more
L0299 [11:01] like how we can improve uh how we're
L0300 [11:04] using the agent um getting some
L0301 [11:07] visibility into for example I've done
L0302 [11:09] some stuff about like visualizing for
L0303 [11:11] myself during a session which files is
L0304 [11:14] it reading and which files is it writing
L0305 [11:16] so I could get an idea of like blast
L0306 [11:18] radius of stuff so I think there's still
L0307 [11:19] a lot of potential here for us to also
L0308 [11:22] make these things part of the the review
L0309 [11:24] cycle
L0310 [11:26] um there are kind of like first
L0311 [11:27] rumblings about the bloat right we
L0312 [11:29] always have the cycle in software right
L0313 [11:31] we we get like a new tool like let's say
L0314 [11:34] spring right and it's like super
L0315 [11:36] lightweight and we're excited because
L0316 [11:38] it's much more lightweight than the
L0317 [11:39] bloated thing that we had before and
L0318 [11:41] then it takes like a number of years,
L0319 [11:43] right? And then we kind of feel like
L0320 [11:45] that's also too big, right? With cloud
L0321 [11:47] code, it hasn't even taken a year and we
L0322 [11:49] feel like it's maybe a bit much, right?
L0323 [11:52] Um, so here's like a comparison of like
L0324 [11:54] when you start out with a session in pi
L0325 [11:56] versus open codex versus cloud code, all
L0326 [11:58] of the stuff that's already in there,
L0327 [12:00] right? Um
L0328 [12:03] but yeah so we need to as when we come
L0329 [12:05] back to like what what do we need to
L0330 [12:07] know right what do we need to understand
L0331 [12:08] as as engineers using these tools we
L0332 [12:11] need to kind of like understand these
L0333 [12:12] features and how they distinguish
L0334 [12:14] between the agents right so just to give
L0335 [12:17] like an example um I remember when cloud
L0336 [12:20] code came out and it became super
L0337 [12:21] popular um I saw a lot of conflation of
L0338 [12:25] the interface with the reason why cloud
L0339 [12:28] go code was good right so I saw said for
L0340 [12:30] a while that people said, "Oh yeah,
L0341 [12:32] terminal based, that's the way to go
L0342 [12:34] because it's really powerful." But
L0343 [12:35] actually, when you have, for example,
L0344 [12:36] one of my favorite harnesses next to
L0345 [12:38] Cloud Code is cursor is also really
L0346 [12:41] really good under the hood with all of
L0347 [12:42] those things that you see in the circle
L0348 [12:44] below there. So, it's not necessarily
L0349 [12:46] because of the terminal, right? So, this
```

## Section 5 -- Harness engineering as context engineering [L0350-L0460, 12:47-16:51]

She describes harness engineering as context engineering for coding agents and separates markdown/context guides into normative, informative, and instructional material.

```text
L0350 [12:47] is just like an example of why it's uh
L0351 [12:50] it's important to kind of distinguish um
L0352 [12:54] you know, kind of know as the engineer
L0353 [12:56] what what's actually happening in the
L0354 [12:58] tools.
L0355 [13:01] So yeah, we have to understand their
L0356 [13:02] footprint, understand their features so
L0357 [13:04] that we can use these features
L0358 [13:06] effectively, right? And so most like one
L0359 [13:09] of the big things that we want to do is
L0360 [13:11] we want to understand how to regulate
L0361 [13:13] the context, how to tune the context
L0362 [13:15] that we give to the agent with the use
L0363 [13:17] of the features that the coding harness
L0364 [13:18] provides us. Right? So about 12 months
L0365 [13:21] ago, the main way that we did that was
L0366 [13:23] rules files or instruction files, right?
L0367 [13:26] So we would have agents MD or claude MD
L0368 [13:28] and maybe write down the typical um
L0369 [13:30] pitfalls and we're still doing that but
L0370 [13:33] these days of course there's so many
L0371 [13:35] different like features in the coding
L0372 [13:36] harnesses that help us do that in a more
L0373 [13:39] sophisticated way right so there's
L0374 [13:40] skills of course uh MCP servers also
L0375 [13:43] existed about a year ago as well there's
L0376 [13:46] now sub agents there's extensions
L0377 [13:48] plugins hooks all of those things and
L0378 [13:50] it's becoming a bit uh overwhelming and
L0379 [13:52] uh confusing right but it's kind of like
L0380 [13:54] the storming phase uh of this of this
L0381 [13:58] technology and this is also how to use
L0382 [14:00] these features is I would say was
L0383 [14:02] probably at least like 50% of the talks
L0384 [14:05] at this at this conference as well uh
L0385 [14:07] unsurprisingly.
L0386 [14:09] So it's kind of context engineering for
L0387 [14:11] coding agents and that means we're
L0388 [14:12] expanding the harness. We're uh using
L0389 [14:15] the features of the harness to uh to
L0390 [14:17] help us do this for our specific
L0391 [14:19] codebase for our um use case, right?
L0392 [14:24] Um
L0393 [14:26] yeah, so we're expanding that harness.
L0394 [14:29] Um so I'm I'm calling it coder harness
L0395 [14:31] here. I have to say like I'm a little
L0396 [14:33] bit unsure. So this is term that uh that
L0397 [14:36] has now gotten traction since February
L0398 [14:38] maybe of harness engineering right which
L0399 [14:41] is basically this right expanding this
L0400 [14:44] coding harness. But in in other areas
L0401 [14:47] you know people also use harness
L0402 [14:48] engineering to talk about like how do
L0403 [14:50] you make the coding harness itself
L0404 [14:51] better right? So it's still like a
L0405 [14:53] little bit clunky term I would say. I
L0406 [14:55] wish we had we had a better one. I also
L0407 [14:56] jumped on the bandwagon and wrote an
L0408 [14:58] article about harness engineering. Um
L0409 [15:00] yeah it would be great m maybe somebody
L0410 [15:03] comes up with an even better word like
L0411 [15:05] the folks at Tesla here at the
L0412 [15:06] conference they've basically they've
L0413 [15:08] also had this kind of like trifecta that
L0414 [15:10] I'm presenting here right like of the
L0415 [15:11] model the harness and then the context
L0416 [15:13] right so I think it's like it's
L0417 [15:16] reasonable to think of harness
L0418 [15:18] engineering as context engineering for
L0419 [15:20] coding agents right so that's just like
L0420 [15:22] to get the terminology out of the way a
L0421 [15:25] little bit um
L0422 [15:28] yeah so let's look at like uh how this
L0423 [15:31] like area of harness engineering context
L0424 [15:33] engineering for coding agents like um a
L0425 [15:36] mental model like how I think about this
L0426 [15:37] like beyond the features right yes this
L0427 [15:40] is about skills this is about MCP
L0428 [15:42] servers but conceptually like what are
L0429 [15:44] we actually doing there when we use
L0430 [15:45] these features so one thing and that's
L0431 [15:48] the most common thing right now is this
L0432 [15:51] uh way of putting conventions product
L0433 [15:53] context workflow uh prompts like
L0434 [15:56] basically markdown files into our uh
L0435 [15:59] codebase somehow, right? Or like making
L0436 [16:01] them accessible through skills and so
L0437 [16:02] on. And in those markdown files is
L0438 [16:04] actually lots of different things going
L0439 [16:05] on, right? We have some normative stuff
L0440 [16:07] like coding conventions. We have some
L0441 [16:10] informative stuff like yeah product
L0442 [16:12] context. What are we actually doing
L0443 [16:14] here? Maybe reference documentation. Uh
L0444 [16:17] and then we also have instructions,
L0445 [16:18] right? Like uh always help me build in
L0446 [16:21] the following workflow or always write a
L0447 [16:23] failing test first or stuff like that.
L0448 [16:25] So there's actually lots of different
L0449 [16:26] things going on in something that looks
L0450 [16:28] just like a bunch of uh text at first
L0451 [16:31] and then also some of them we just have
L0452 [16:32] directly in the workspace and others are
L0453 [16:35] maybe more dynamically loaded from other
L0454 [16:37] data sources, right? And um so these are
L0455 [16:40] all for me like kind of feed forward.
L0456 [16:42] So, we're trying to anticipate what the
L0457 [16:45] agent might do wrong, and we're also
L0458 [16:47] trying to anticipate, of course, what we
L0459 [16:48] want it to do. And we're feeding it all
L0460 [16:51] of this information, these instructions,
```

## Section 6 -- Guides, sensors, and self-correction loops [L0461-L0560, 16:52-20:39]

She presents feed-forward guides and feedback sensors, distinguishing inferential review agents from computational tools such as static analysis, code mods, lint rules, and import checks.

```text
L0461 [16:52] these norms, so that hopefully in its
L0462 [16:54] initial generation of code, it's already
L0463 [16:56] doing perfectly, right? But as we know,
L0464 [16:58] that's not um always happening. So,
L0465 [17:01] we're starting with these guides, but
L0466 [17:02] then we also want to give it feedback,
L0467 [17:05] right? So um ideally uh so that we can
L0468 [17:08] trigger immediately a selfcorrection
L0469 [17:10] loop before we even look at the code so
L0470 [17:12] that we don't have to like have all
L0471 [17:14] those lowhanging fruits still in there.
L0472 [17:16] So um the most common way that people do
L0473 [17:18] that right now is with like code review
L0474 [17:20] agents, right? But there's also all of
L0475 [17:23] these other tools that we have in our
L0476 [17:24] toolbox from before AI like static code
L0477 [17:27] analysis and then of course we can also
L0478 [17:29] an agent usually has access to the logs
L0479 [17:32] so it can start the application see what
L0480 [17:33] what logs come out of it. Uh many people
L0481 [17:36] give an agent access to the browser so
L0482 [17:38] it can look at like something when it
L0483 [17:40] has changed a web component or something
L0484 [17:42] like that. Um and there's actually um uh
L0485 [17:46] a difference kind of between these. So
L0486 [17:48] like a review agent is an LLM judging
L0487 [17:51] the work of another LLM, right? So it's
L0488 [17:53] kind of inferential. It's running on the
L0489 [17:54] GPU. But we have a bunch of tools as
L0490 [17:57] well that are uh uh computational as I
L0491 [18:00] decided to call them here. So kind of
L0492 [18:02] things that run on the CPU, right? Like
L0493 [18:03] the static code analysis is the best
L0494 [18:05] example I think to to think about this.
L0495 [18:08] Um yeah, and we have the same
L0496 [18:10] distinction on the feed forward on the
L0497 [18:12] guide side. So we we can uh we um can
L0498 [18:15] also think about computational guides on
L0499 [18:17] that side. And the best example for me
L0500 [18:20] there is code mods. Uh Ian from MEA also
L0501 [18:22] just mentioned those um which is for
L0502 [18:25] example tools like open rewrite that are
L0503 [18:28] really good at doing uh version upgrades
L0504 [18:30] and m migrations of uh of um frameworks.
L0505 [18:34] I don't know if you remember like quite
L0506 [18:36] a while ago, Amazon had a really big
L0507 [18:38] headline about saving 400 or 500
L0508 [18:41] developer years or something for Java
L0509 [18:43] upgrades. That was under the hood
L0510 [18:45] actually mostly code mods being made
L0511 [18:47] available to AI. So that combination is
L0512 [18:49] really powerful, right? So all of these
L0513 [18:51] things uh or maybe providing a different
L0514 [18:53] type of code search that that is more
L0515 [18:55] effective for your really large
L0516 [18:56] codebase. All of those are ways again to
L0517 [18:59] increase the probability that AI does
L0518 [19:01] what you want in the first go.
L0519 [19:04] So that's then the expanded harness and
L0520 [19:06] then as a human as we've heard in a few
L0521 [19:08] talks uh here as well as the human our
L0522 [19:11] job in part becomes kind of steering
L0523 [19:14] this set of guides and sensors. So as
L0524 [19:17] Mitchell Hashimoto says in his blog post
L0525 [19:19] it's the idea that anytime you find an
L0526 [19:21] agent makes a mistake you take the time
L0527 [19:24] to engineer a solution such that the
L0528 [19:26] agent never makes that mistake again.
L0529 [19:31] And of course AI can help us engineer
L0530 [19:33] those little solutions, right? Which is
L0531 [19:35] really useful. So just two quick
L0532 [19:37] examples to to bring that home. So um
L0533 [19:41] here's like something in the agents MD.
L0534 [19:43] Do not use console log. You know, we
L0535 [19:46] have a custom logger that does
L0536 [19:47] structured logging and so on. It's in
L0537 [19:48] the following place, right? Instead, I
L0538 [19:51] could have like a linting rule um that I
L0539 [19:54] customize where I customize the message
L0540 [19:56] and point uh the agent at that log file
L0541 [20:00] through that. Right? So, especially when
L0542 [20:02] you have things that it doesn't even do
L0543 [20:03] wrong that often that happens maybe once
L0544 [20:05] a week, it's much more effective to have
L0545 [20:07] this linting rule than to like stuff it
L0546 [20:09] into your context every single time the
L0547 [20:11] agent runs. Or here's another example.
L0548 [20:13] Let's say you have a backend coding
L0549 [20:15] conventions skill that talks about the
L0550 [20:17] backend layers that the agent should
L0551 [20:20] respect uh in terms of like which uh
L0552 [20:22] modules are allowed to call which other
L0553 [20:24] modules. There are some tools in most
L0554 [20:26] eco language ecosystems that help you
L0555 [20:28] scan the different imports between
L0556 [20:30] files. And so again you can like come up
L0557 [20:32] together with AI with some rules in
L0558 [20:35] those tools that help you uh already
L0559 [20:37] catch the lowhanging fruit of those
L0560 [20:39] modularity um uh violations.
```

## Section 7 -- Where to place sensors in the path to production [L0561-L0643, 20:44-23:40]

She recommends deciding where sensors run: inside coding sessions, before commits, during PR review, in CI, as scheduled drift detection, and from production observability data.

```text
L0561 [20:44] And then you should think about like how
L0562 [20:46] you where you put those sensors when you
L0563 [20:48] run them, right? So, uh kind of like
L0564 [20:51] strategically think about your path to
L0565 [20:52] production and think about when you want
L0566 [20:54] to run them. So, do you want to run them
L0567 [20:56] in the coding session, right? Which is I
L0568 [20:59] think uh whenever that's possible in
L0569 [21:02] terms of like how cheap is it, how fast
L0570 [21:03] it is to run a sensor, I think you
L0571 [21:05] should run them like even before you
L0572 [21:08] commit, right? So, I have this box here
L0573 [21:10] about integration, right? So it kind of
L0574 [21:12] like depends what that means for you. So
L0575 [21:14] probably 80% of my commits in the last
L0576 [21:16] 15 years have been put straight onto the
L0577 [21:19] main branch which is probably not the
L0578 [21:21] case for most of you. Um so integration
L0579 [21:23] could either be like for you to say okay
L0580 [21:25] I want to do all of those things before
L0581 [21:27] I even create a commit or it could be as
L0582 [21:29] part of the pull request uh process
L0583 [21:31] where you run some additional like uh
L0584 [21:34] inferial sensors or something like that.
L0585 [21:36] Right? Then we have lots of stuff in our
L0586 [21:38] continuous integration pipeline already.
L0587 [21:40] Right? You probably don't want any
L0588 [21:41] inferential sensors in there because you
L0589 [21:44] you don't want, you know, the the green
L0590 [21:46] or red state of your pipeline to depend
L0591 [21:48] on semantic interpretation of an LLM,
L0592 [21:51] right? But we have like lots of uh
L0593 [21:54] computational sensors in there. And then
L0594 [21:56] also what uh I've heard a lot of stories
L0595 [21:58] now about teams doing in ThoughtWorks
L0596 [22:00] and also lots of people writing about
L0597 [22:02] that. Also the um the team Ryan's team
L0598 [22:06] who had a um a presentation yesterday at
L0599 [22:09] OpenAI they call it garbage collection
L0600 [22:11] right so kind of like continuous drift
L0601 [22:13] detection for the technical debt that
L0602 [22:15] still accumulates um where you can
L0603 [22:18] probably put like a lot of inferial
L0604 [22:19] sensors right so in the codebase where
L0605 [22:21] I'm uh where I'm setting up all of these
L0606 [22:23] things I have like a modularity review
L0607 [22:25] like a dependency uh freshness review a
L0608 [22:29] security review that doesn't run every
L0609 [22:31] single time the pipeline runs But I
L0610 [22:33] trigger it maybe like once a week just
L0611 [22:34] to see if there's something new that
L0612 [22:36] came up. Um, and these like continuous
L0613 [22:39] drift detection things, they're probably
L0614 [22:41] also like require some kind of process
L0615 [22:42] on your team to deal with them, right?
L0616 [22:44] There's a lot of parallels to, for
L0617 [22:46] example, security vulnerabilities and
L0618 [22:48] how you deal with them, right? Like uh,
L0619 [22:50] you know, they keep popping up again. Do
L0620 [22:52] you want to suppress them because you
L0621 [22:54] cannot fix them right now, but then you
L0622 [22:55] might forget about them. So, I suspect
L0623 [22:58] we'll have all of these challenges there
L0624 [22:59] with this type of stuff as well. like
L0625 [23:01] how is the team going to going to deal
L0626 [23:03] with these? Again, you can maybe like
L0627 [23:05] have AIS of course like create uh you
L0628 [23:08] can have agents create pull requests for
L0629 [23:09] you, but still how do you deal with
L0630 [23:12] those, right?
L0631 [23:14] And then finally, I should also mention
L0632 [23:16] uh there's of course also this way of
L0633 [23:18] having sensors like in production that
L0634 [23:20] you give AI access to, right? Especially
L0635 [23:23] when it comes to your architecture
L0636 [23:24] fitness, things like scalability,
L0637 [23:26] latency, all of those things. There were
L0638 [23:28] a few talks here at the conference as
L0639 [23:29] well about using observability data and
L0640 [23:33] uh you know both to help you fix
L0641 [23:34] incidents but also just to like monitor
L0642 [23:37] how you can make your uh your runtime
L0643 [23:40] better.
```

## Section 8 -- Summary: what coding-agent users need to learn [L0644-L0665, 23:44-24:30]

She recaps the model, task, harness, and context-engineering knowledge practitioners need in order to use coding agents well.

```text
L0644 [23:44] Okay. So as users of coding agents, we
L0645 [23:48] have to know a few key model
L0646 [23:49] capabilities and like I said kind of
L0647 [23:50] like have good reflection on the types
L0648 [23:52] of tasks uh that we're that we're using
L0649 [23:54] and what complexity means for us in
L0650 [23:56] relationship to what models can do. Um
L0651 [23:59] we should understand the key features of
L0652 [24:01] harnesses and and how they differ and
L0653 [24:03] not just like look at them as like you
L0654 [24:06] know these blobs and one is a terminal
L0655 [24:07] and one is an IDE. But the biggest area
L0656 [24:11] is really this like how do we use them
L0657 [24:13] to our advantage, right? Um yeah, how to
L0658 [24:16] apply this tool to our domain which is
L0659 [24:19] software engineering. So with all of
L0660 [24:21] these things like models getting much
L0661 [24:23] more capable, harness is getting much
L0662 [24:25] more capable. We're kind of like getting
L0663 [24:27] more sophisticated and figuring out how
L0664 [24:28] do we use this? How do we provide our
L0665 [24:30] context? So this kind of like race
```

## Section 9 -- Autonomy, background agents, swarms, and the four-year arc [L0666-L0784, 24:32-28:53]

She summarizes the drive toward more autonomy and less supervision, including background/cloud agents, brute-force swarms, the four-year arc from autocomplete to skills/OpenClaw, and renewed attention spikes.

```text
L0666 [24:32] continues, right? We want more agent
L0667 [24:34] autonomy and we want less human
L0668 [24:36] supervision. And as part of that also
L0669 [24:38] something that has happened over the
L0670 [24:39] last 12 months is that it has become a
L0671 [24:42] lot easier to run agents with uh no
L0672 [24:45] supervision. Right? So um this
L0673 [24:48] screenshot is from like I probably took
L0674 [24:49] it last year in June July or something
L0675 [24:51] that was the first version of codeex and
L0676 [24:54] uh over time now also most of the the
L0677 [24:56] harness products the coding agent
L0678 [24:57] products have now come uh come out with
L0679 [25:00] like platforms where you can always
L0680 [25:02] decide like do I want to run this coding
L0681 [25:04] session locally on my machine or do I
L0682 [25:05] want to do it in the cloud and so it's
L0683 [25:08] become a lot easier um to do this and uh
L0684 [25:11] to to try this out right like whatever
L0685 [25:14] size you feel comfortable size and
L0686 [25:15] complexity of tasks you want to do this
L0687 [25:18] for. Like some people run it to actually
L0688 [25:20] like build full features and others
L0689 [25:22] maybe like just dip their toes in like
L0690 [25:24] clean up this feature toggle or like
L0691 [25:26] small cleanup tasks, right? And uh also
L0692 [25:30] in the meantime we've kind of like taken
L0693 [25:32] this like uh to more extremes right
L0694 [25:34] which is more an experimental stage
L0695 [25:36] right now I would say uh which is this
L0696 [25:38] idea of like swarms or really brute
L0697 [25:40] force just sending lots and lots of
L0698 [25:42] agents out there and also having the
L0699 [25:44] agents decide how many agents they need
L0700 [25:46] right um uh gas town got a lot of
L0701 [25:50] attention in I think it came out in in
L0702 [25:52] January there were these two like big or
L0703 [25:55] even more experiments from like cursor
L0704 [25:57] for example or anthropic to C compiler
L0705 [25:59] in the browser. Um, Cloudflow, I think
L0706 [26:02] it has a different name now. That was
L0707 [26:03] probably even earlier than Gast Town
L0708 [26:05] last year. Uh, kind of people were
L0709 [26:06] playing around with that. So, that's
L0710 [26:08] kind of like taking it to the extreme
L0711 [26:10] and seeing how we can push the
L0712 [26:11] boundaries and actually have AI build uh
L0713 [26:14] much bigger things more autonomously.
L0714 [26:17] Um,
L0715 [26:20] yeah. So, this is our fourth year into
L0716 [26:22] this.
L0717 [26:24] Um so we start with autocomplete then we
L0718 [26:26] had a bit more like integration into the
L0719 [26:28] idees more context claw 3.5 sonnet was
L0720 [26:32] like an early model moment I think where
L0721 [26:35] uh I certainly from that point on just
L0722 [26:37] just always you almost always use clots
L0723 [26:39] on it because it just like um felt so
L0724 [26:42] much better at coding than the other
L0725 [26:43] ones. Um so then um we got these like at
L0726 [26:47] the time most people or I also in my
L0727 [26:50] presentations still called it agentic
L0728 [26:52] coding modes right so that's when like
L0729 [26:54] the the um like like uh cursor and so on
L0730 [26:58] they got like these modes where they
L0731 [26:59] could also run terminal commands which
L0732 [27:01] which had been a thing that was already
L0733 [27:02] out there in open source but not as
L0734 [27:04] widely used and MCP. So that was only
L0735 [27:07] about one and a half years ago. Um then
L0736 [27:10] shortly after that the the vibe coding
L0737 [27:12] term got coined by uh Andre Kapati which
L0738 [27:16] then led to like a lot of attention of
L0739 [27:18] people discovering these neurogentic
L0740 [27:20] modes and going oh this is like so there
L0741 [27:22] was like a wave of like people picking
L0742 [27:24] this up again and saying oh this is has
L0743 [27:26] actually improved quite a bit. Uh then
L0744 [27:28] we got these kind of background agents
L0745 [27:30] that I just talked about right like so
L0746 [27:32] codeex for example you know allowing you
L0747 [27:34] to run things unsupervised in the
L0748 [27:36] background cloud code is
L0749 [27:39] I think generally available probably
L0750 [27:41] about a year old it's like it started a
L0751 [27:44] little bit earlier than that the context
L0752 [27:46] engineering term also started gaining
L0753 [27:48] traction about a year ago uh then we had
L0754 [27:50] that claude opus moment we got skills
L0755 [27:54] open claw is maybe also relevant uh a
L0756 [27:57] relevant moment even though it's not
L0757 [27:58] quite directly about coding. Um, and
L0758 [28:01] then yeah, so like kind of beginning of
L0759 [28:02] this year, we got this like next wave of
L0760 [28:04] people paying attention again and going,
L0761 [28:06] "Oh, this has actually changed uh quite
L0762 [28:09] a bit, right? I can actually see those
L0763 [28:11] two yellow spots in our internal AI
L0764 [28:13] coding chat community in in
L0765 [28:15] ThoughtWorks. I can see the spikes in
L0766 [28:18] activity and then kind of like holding
L0767 [28:20] and then there's like another spike of
L0768 [28:22] like I don't know 250 messages a week or
L0769 [28:25] something median.
L0770 [28:28] Yeah. And then so yeah, the gas town and
L0771 [28:29] all of the swarms and all of that
L0772 [28:31] started those big experiments started
L0773 [28:32] happening beginning of this year. Then
L0774 [28:34] the harness engineering term has now
L0775 [28:36] like a buzzword. So and uh you know I
L0776 [28:39] don't have any additional boxes here
L0777 [28:40] because I think right now it's like us
L0778 [28:41] all like processing right and actually
L0779 [28:44] using all of these things that are
L0780 [28:45] happening. So there's been like I think
L0781 [28:47] not like a big coinage of anything or
L0782 [28:49] like a new buzzword other than these
L0783 [28:51] things but we're just like grappling
L0784 [28:53] with it and and using this stuff, right?
```

## Section 10 -- Costs and second-order consequences [L0785-L0925, 28:58-34:17]

She outlines the costs: security, stability, changeability, token cost, cognitive load and burnout, review bottlenecks, backlog/prototype flow problems, and possible congestion collapse.

```text
L0785 [28:58] So it's come a long way but the costs
L0786 [29:01] have as well and I don't just mean the
L0787 [29:02] token costs.
L0788 [29:04] So one is security right. So our it's
L0789 [29:07] it's both about about like secrets
L0790 [29:10] potentially leaking from our
L0791 [29:11] environments from our machines but also
L0792 [29:13] our ecosystem is under attack right so
L0793 [29:16] um uh we have to like think even more
L0794 [29:19] than before about dependency management
L0795 [29:20] about sandboxing and and stuff like
L0796 [29:23] that. Um on the other hand there was
L0797 [29:25] also a good talk by Joseph from GitHub
L0798 [29:27] here yesterday about like how we can use
L0799 [29:28] AI to improve our security right so
L0800 [29:31] there usually both sides to it stability
L0801 [29:34] right so in the uh Dora report um this
L0802 [29:37] was one of the big like let's say
L0803 [29:39] negative trend findings about stability
L0804 [29:42] actually getting worse according to
L0805 [29:44] their um data but also there were a lot
L0806 [29:46] of talks here about like how we can use
L0807 [29:48] AI to help us improve our stability
L0808 [29:51] um then changeability
L0809 [29:53] is a big thing, right? So like code
L0810 [29:55] quality defined as code that remains
L0811 [29:59] easy to change and remains where it
L0812 [30:02] remains easy to change it with low risk,
L0813 [30:04] right? So this was a change uh I
L0814 [30:06] recently introduced into a still
L0815 [30:08] relatively new codebase that was all
L0816 [30:10] created with AI and I made a change that
L0817 [30:13] touched 41 files but it shouldn't have.
L0818 [30:15] it wasn't like that big of a deal and so
L0819 [30:18] it was like a clear smell that there was
L0820 [30:19] already like accumulate detected that
L0821 [30:22] was making changes more risky and more
L0822 [30:24] uh costly. So but then also here the
L0823 [30:27] question is like how far can we push
L0824 [30:29] this more and improve this more with
L0825 [30:31] guides with sensors with static code
L0826 [30:33] analysis and so on. Token cost is the
L0827 [30:36] most obvious cost thing. Of course, in
L0828 [30:38] the beginning of 2024, I was at a
L0829 [30:40] keynote presentation where the speaker
L0830 [30:42] said, "Generating 100 lines of code only
L0831 [30:44] costs about 12 cents." Can you imagine?
L0832 [30:48] And he was comparing that to developer
L0833 [30:50] salaries. I mean, regardless of, you
L0834 [30:52] know, lines of code is not a measure of
L0835 [30:55] value, right? Let's just get that out of
L0836 [30:57] the way as well. But of course now we
L0837 [30:59] have like there was some numbers or some
L0838 [31:02] quotes in the pragmatic engineer
L0839 [31:03] newsletter recently where somebody for
L0840 [31:05] example there were multiple of these
L0841 [31:06] quotes but somebody said some developers
L0842 [31:08] are now spending $500 a day which if we
L0843 [31:12] take that analogy of a developer salary
L0844 [31:13] is over $100,000 a year salary which is
L0845 [31:16] a pretty decent salary in the even in
L0846 [31:18] the richest countries in the world right
L0847 [31:21] um another type of cost is like
L0848 [31:24] cognitive load and burnout right like
L0849 [31:27] who would have thought, right? It
L0850 [31:28] doesn't actually make us make our lives
L0851 [31:30] more relaxed on the contrary, right?
L0852 [31:32] Like some people are working more even
L0853 [31:34] though they they already create more
L0854 [31:36] output. And Steve Yaggi had this analogy
L0855 [31:39] with the energy vampire from what we do
L0856 [31:41] in the shadows. I don't know if any of
L0857 [31:42] you have seen that uh that show, but he
L0858 [31:45] basically yeah, he's a vampire that
L0859 [31:47] doesn't suck blood that but that sucks
L0860 [31:49] uh energy. So there's lots of stories
L0861 [31:50] about people saying, "Oh, I can only do
L0862 [31:52] this like three hours in a row and then
L0863 [31:54] I have to like take a nap."
L0864 [31:58] Um, then we have the review crisis of
L0865 [32:00] course, right? We have like higher
L0866 [32:02] coding throughput. But then can we if we
L0867 [32:05] can code faster, can we review faster,
L0868 [32:07] test faster, ship faster, review faster?
L0869 [32:10] We've definitely so far the state is no,
L0870 [32:12] we cannot review faster, right?
L0871 [32:13] Everybody's complaining about this about
L0872 [32:16] this pain. Uh, but it's not just coding.
L0873 [32:19] Everybody can create more with AI now,
L0874 [32:21] right? So I was talking to a colleague
L0875 [32:23] the other day who was telling me a story
L0876 [32:25] about an organization uh uh on this side
L0877 [32:27] of like if you can code faster, can you
L0878 [32:29] fill the backlog faster? So here, you
L0879 [32:32] know, there was like another another
L0880 [32:35] kind of like thing popping up before the
L0881 [32:37] coding where the the product managers
L0882 [32:40] were actually like churning out lots and
L0883 [32:41] lots of prototypes and lots and lots of
L0884 [32:43] ideas, right? So now there was this
L0885 [32:45] weird like bottleneck between this pile
L0886 [32:48] of prototypes and the pile of code
L0887 [32:50] because they couldn't get it like to
L0888 [32:51] sync up again and nobody really could
L0889 [32:53] figure out how to converge on what they
L0890 [32:55] actually wanted to build because they
L0891 [32:57] were doing this kind of like in these
L0892 [32:59] two uh silos. So that's maybe like
L0893 [33:02] something like an open question that
L0894 [33:05] we're already seeing a little bit, but
L0895 [33:06] are we are we heading in general towards
L0896 [33:08] like a flow crisis, right? And whenever
L0897 [33:11] I want to understand flow better, I turn
L0898 [33:13] to my colleague uh James Lewis who like
L0899 [33:15] has done a lot of very interesting
L0900 [33:17] presentations about flow that you know
L0901 [33:19] it's easy to find on on YouTube. Um but
L0902 [33:23] here's one where he's talking about
L0903 [33:24] congestion uh collapse. Um, and so he
L0904 [33:28] has this uh this prediction apparently
L0905 [33:31] he has a bet open with Jean Kim for a
L0906 [33:33] crate of beer that this will happen and
L0907 [33:35] that this will become like a big topic
L0908 [33:37] of conversation that we're just like
L0909 [33:39] overloading and also overloading in
L0910 [33:41] these different silos and that
L0911 [33:42] everything will just become super slow
L0912 [33:44] at some point and just uh collapse. So
L0913 [33:46] this comes you know from I think theory
L0914 [33:48] of constraints and and stuff like that.
L0915 [33:50] And here he's he's quoting the Don
L0916 [33:53] Reinardson book about the principles of
L0917 [33:54] product development flow. um as well.
L0918 [33:59] So then humans are seen as the
L0919 [34:00] bottleneck, right? That's what what
L0920 [34:02] multiple people also quoted or or said
L0921 [34:05] here um at the conference. Um
L0922 [34:10] so um it it remains this big question of
L0923 [34:13] like trust in the code and how much
L0924 [34:15] supervision do we want to have and how
L0925 [34:17] much review
```

## Section 11 -- Risk assessment for reducing supervision [L0926-L0990, 34:20-36:46]

She frames autonomy as unevenly distributed and proposes a probability-impact-detectability risk assessment for deciding workflow, review depth, and supervision level.

```text
L0926 [34:20] and of course it depends, right? So the
L0927 [34:22] autonomy of AI coding agents is here.
L0928 [34:26] It's just unevenly distributed, right?
L0929 [34:28] Lots of you are probably already using
L0930 [34:30] it for some things, right? But I think
L0931 [34:32] it will never be that we can use AI
L0932 [34:35] coding agents for any type of task in
L0933 [34:37] any situation, right? It's just always
L0934 [34:39] it depends on the situation and um what
L0935 [34:43] does it depend on, right? So for me the
L0936 [34:45] way I think about it right now is as
L0937 [34:47] this risk assessment uh out of
L0938 [34:49] probability impact and detectability
L0939 [34:52] right which is very typical kind of
L0940 [34:54] components of risk assessment in all
L0941 [34:56] kinds of areas. So, first I think about
L0942 [34:57] the probability that AI gets something
L0943 [35:00] wrong or gets something right. And
L0944 [35:01] that's all about me knowing the things
L0945 [35:03] that I talked about before, my AI tool,
L0946 [35:06] like what my context is. Did I even give
L0947 [35:08] the agent a chance to do it right? Um,
L0948 [35:10] and it's also about me reflecting on my
L0949 [35:13] confidence in my requirements, right?
L0950 [35:14] Like how certain am I even that I even
L0951 [35:16] know what to do. Um, then I think about
L0952 [35:19] the impact if AI gets something wrong.
L0953 [35:21] So that's all about the use case
L0954 [35:22] criticality of course. So, is this like
L0955 [35:25] a super critical business flow that, you
L0956 [35:28] know, will wake me up at 2 a.m. on
L0957 [35:30] Saturday because I'm on call, or is this
L0958 [35:32] something a lot less uh uh a lot less
L0959 [35:35] important than maybe like I'm a little
L0960 [35:37] bit more loose with uh how I review? And
L0961 [35:40] the third thing is I reflect on
L0962 [35:41] detectability that AI got something
L0963 [35:43] wrong. Will I notice? Right? And um by
L0964 [35:46] the way, all of this starts with knowing
L0965 [35:48] what right and wrong means, right? I
L0966 [35:50] should and often that's like, is it
L0967 [35:52] appropriate? Right? Uh so you have to
L0968 [35:55] know your uh feedback loops basically
L0969 [35:57] and then based on these things I decide
L0970 [36:00] which workflow do I use, how much review
L0971 [36:02] do I do and how long let do I let it go
L0972 [36:04] without supervision. For example, if I
L0973 [36:07] don't even know myself yet quite what I
L0974 [36:09] need, then I won't let it go off for
L0975 [36:11] like half an hour and then realize that
L0976 [36:13] it was all for nothing, right?
L0977 [36:16] And yeah, so you have to kind of be this
L0978 [36:17] tall to ride the roller coaster. You
L0979 [36:19] have to be this tall to reduce
L0980 [36:20] supervision, right? So you can think
L0981 [36:22] about uh you know feedback loop in your
L0982 [36:24] team in your organization and you can
L0983 [36:26] also increase the probabilities by
L0984 [36:29] improving your context engineering your
L0985 [36:31] harness engineering um and also uh
L0986 [36:35] refactoring and modernizing and you know
L0987 [36:37] all of those things because um AI can
L0988 [36:41] also deal with a well-actored codebase
L0989 [36:43] much better um than with a messy
L0990 [36:46] codebase.
```

## Section 12 -- Cognitive surrender and closing call to action [L0991-L1127, 36:48-41:45]

She warns against moving unthinkingly from in-the-loop to out-of-the-loop, names cognitive load/debt/deferral/surrender, and calls for critical thinking, risk assessment, patience, and sustainable delivery.

```text
L0991 [36:48] So, we're tempted to move from in the
L0992 [36:50] loop to on the loop to out of the loop.
L0993 [36:52] This I I feel this every day being drawn
L0994 [36:55] to like ah I don't want to look at this.
L0995 [36:57] I don't want to look at the code
L0996 [36:58] anymore. It's like uh yeah, there's all
L0997 [37:00] of these forces that pull us there. But
L0998 [37:02] we're also starting to actually feel the
L0999 [37:04] costs. It's not just speculation
L1000 [37:05] anymore. It's not just like dooming kind
L1001 [37:08] of predictions. We're actually feeling
L1002 [37:10] the cost of tokens risks and cognitive
L1003 [37:13] X, right? Cognitive load, cognitive
L1004 [37:16] debt, right? this idea uh of like we
L1005 [37:18] don't even understand anymore how our
L1006 [37:20] codebase is structured. Um I sometimes
L1007 [37:22] think of like cognitive deferral as
L1008 [37:24] well. It feels like we keep like
L1009 [37:26] deferring the review to other people or
L1010 [37:29] like deferring processing what actually
L1011 [37:31] happened. And recently uh there was like
L1012 [37:34] a new cognitive X term coined that um I
L1013 [37:38] I saw because Addiosmani wrote about it
L1014 [37:41] which is cognitive surrender. Right? So
L1015 [37:43] in this paper they put um AI into the
L1016 [37:46] context of the system one system two uh
L1017 [37:50] thinking fast and slow. I think probably
L1018 [37:52] lots of you have heard about that book.
L1019 [37:53] If not then look it up. It's like really
L1020 [37:55] great. And so they're they're talking
L1021 [37:57] about a mode where we're basically
L1022 [37:59] displacing system 2 like our actually
L1023 [38:01] like active thinking with AI and they
L1024 [38:04] call it cognitive surrender. And apart
L1025 [38:06] from like this paper and the cognitive
L1026 [38:09] part of it, this term like surrender has
L1027 [38:11] just been stuck in my head like ever
L1028 [38:13] since I heard this. And I feel like
L1029 [38:15] we're there's like so many things where
L1030 [38:17] we we're in danger of just like
L1031 [38:19] surrendering right now, not just
L1032 [38:21] cognitively. Um and so I think we have
L1033 [38:24] to be careful about what we are
L1034 [38:25] surrendering, right? And like really
L1035 [38:27] think about be mindful of uh where
L1036 [38:30] that's worth doing. So I'll just give
L1037 [38:32] like some examples, right? Um so it's
L1038 [38:36] like ah it's too much to reason about
L1039 [38:37] this big change it'll be fine right I do
L1040 [38:40] it myself I just do it myself quickly
L1041 [38:43] instead of teaching somebody right
L1042 [38:45] everybody's talking about oh how will
L1043 [38:46] juniors learn how will we do this but I
L1044 [38:49] don't see that much like active action
L1045 [38:51] right because everybody's just in a
L1046 [38:53] tunnel of you know I see experienced
L1047 [38:55] people building tools for themselves to
L1048 [38:57] use AI better but like why are we not
L1049 [39:00] taking more initiative to think about
L1050 [39:02] how this is sustainable for people who
L1051 [39:04] don't have all of this experience
L1052 [39:06] already or this like I'll just use a big
L1053 [39:08] model you know I can't be bothered to
L1054 [39:11] then like try retry it again so let's
L1055 [39:13] just use the most expensive biggest
L1056 [39:14] model or this surrendering to like ah I
L1057 [39:17] don't want to solve all these problems
L1058 [39:18] models will get better tokens will be
L1059 [39:20] cheaper again we just have to wait it
L1060 [39:22] out right um we're working more we're
L1061 [39:26] producing more but we're still getting
L1062 [39:28] the same compensation
L1063 [39:30] is that also a type of surrender
L1064 [39:32] um or is like oh I don't have time to
L1065 [39:35] find better approaches which is by the
L1066 [39:37] way not necessarily the individual's
L1067 [39:38] fault it's also like what's happening
L1068 [39:40] around them and incentives and pressures
L1069 [39:42] right uh sandboxing is too tedious
L1070 [39:44] surely nothing will go wrong right
L1071 [39:48] or I I can't work on this codebase
L1072 [39:50] without AI anymore right that's the the
L1073 [39:52] original cognitive surrender cognitive
L1074 [39:54] debt kind of definition um this was like
L1075 [39:57] Hannah yesterday in a talk and she was
L1076 [39:59] kind of talking about what she's keeping
L1077 [40:00] what she's trashing and what she's
L1078 [40:02] trying and I think that's similar in
L1079 [40:05] terms of like we have to think about
L1080 [40:06] what we're surrendering and what we
L1081 [40:08] should be uh what we should be keeping.
L1082 [40:10] So if you are a person of influence in
L1083 [40:12] your engineering organization, are you
L1084 [40:14] creating an environment that leads to
L1085 [40:16] surrender, right? That makes people feel
L1086 [40:18] like they just have to crank out the PRs
L1087 [40:20] and don't have time to like actually
L1088 [40:22] figure out how to improve the
L1089 [40:23] environment, how to improve the context
L1090 [40:25] engineering and so on. Um if you're if
L1091 [40:28] you maybe feel a bit like powerless or
L1092 [40:30] you feel like you can't influence it and
L1093 [40:31] there's all these pressures around you
L1094 [40:33] still like try to think about your
L1095 [40:34] sphere of influence and the small things
L1096 [40:36] you can do like what do you really have
L1097 [40:38] to surrender right um so there's lots of
L1098 [40:41] options between not using AI at all and
L1099 [40:44] like just total surrender and hoping
L1100 [40:46] hoping the models will fix it all in the
L1101 [40:47] future and again like if you feel kind
L1102 [40:50] of like powerless and like this is like
L1103 [40:52] washing over you we can also work
L1104 [40:54] together and collaborate on these things
L1105 [40:56] Right? So if you feel like you're not a
L1106 [40:57] good communicator about this, maybe look
L1107 [41:00] for somebody in your team or
L1108 [41:01] organization who's good at that and
L1109 [41:02] share your data, share your observations
L1110 [41:04] with them. Right? So like we can
L1111 [41:06] collectively do a lot about this as
L1112 [41:08] well. In terms of skills, we need to
L1113 [41:10] know our toolbox past and present. We
L1114 [41:12] also need to rediscover some things. Uh
L1115 [41:15] we need critical thinking, risk
L1116 [41:17] assessment, and some form of like
L1117 [41:18] patience, right? So we need to evaluate
L1118 [41:21] that productivity maybe doesn't just
L1119 [41:23] mean like typing and for leadership you
L1120 [41:26] know this is still horizon 2 right this
L1121 [41:28] is not horizon one yet so maybe we don't
L1122 [41:31] know the ROI yet maybe we just have to
L1123 [41:33] like give people some time to um to
L1124 [41:35] create a good setup so that we can
L1125 [41:38] continue to safely and quickly deliver
L1126 [41:41] software to users in a sustainable way.
L1127 [41:45] Thank you.
```
