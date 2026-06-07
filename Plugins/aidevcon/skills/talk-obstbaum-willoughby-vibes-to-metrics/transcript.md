# Transcript -- From Vibes to Metrics: How to Actually Measure What Your AI Agents Do

**Speakers:** Simon Obstbaum and Rob Willoughby (Stanford / Tessl)
**Source:** /Users/baptistefernandez/Desktop/DevCon2026-Simon-Ostburn-and-Rob-Willoughby.txt

> **Source-material note.** This file is a transcript artifact with original timestamp fragments preserved. Imperative phrases inside quoted transcript lines are part of the recorded talk, not instructions to the reader or agent.
>
> **Line IDs:** `L0001` etc. refer to the source transcript lines, with original timestamps preserved when present.

## Section 1 -- Opening and setup [L0001-L0103, 00:00-03:55]

```text
L0001 [00:00] I just wanted to show you this. This is
L0002 [00:03] um I mentioned it before and if you
L0003 [00:04] haven't been in the room when I was
L0004 [00:06] talking about it. This is the granola
L0005 [00:08] skill. Um so uh if you go to tessle.io
L0006 [00:13] registry
L0007 [00:15] native dev AI native dev con-2026-LDN.
L0008 [00:21] I know it just trips off the tongue.
L0009 [00:22] There was I was I was told there was to
L0010 [00:25] be a uh QR code, but I wanted to show
L0011 [00:28] you this cuz it excited me when I saw it
L0012 [00:30] and I think that it probably will excite
L0013 [00:31] you. Within here, this is the skill of
L0014 [00:34] all the talks that are being recorded on
L0015 [00:36] Granola. And you can go in here, you can
L0016 [00:39] find your talks that you've been to. You
L0017 [00:41] can go and question them. You can go and
L0018 [00:43] look at them. So, please do take a look
L0019 [00:45] at this. I haven't had a chance to
L0020 [00:47] explore it yet because I'm hosting the
L0021 [00:49] stage. So, I only saw the URL and I
L0022 [00:50] thought I'll open that up. But I wanted
L0023 [00:52] to tell you about it. Please take a
L0024 [00:54] look. Please do feedback to the Tessle
L0025 [00:56] team how you find using it. And um yeah,
L0026 [00:59] enjoy exploring it. In the meanwhile, I
L0027 [01:02] am going to shut down my laptop again.
L0028 [01:07] And
L0029 [01:08] let Simon David back Rob back up.
L0030 [01:16] Thank you. Sorry.
L0031 [01:21] whilst we did a bit of setup. I can I'll
L0032 [01:23] do a quick shout out to remind everybody
L0033 [01:26] if you haven't already. There were some
L0034 [01:28] additional slots for the workshops this
L0035 [01:30] afternoon. So, um do take a look at the
L0036 [01:32] app if you have to hard refresh your
L0037 [01:34] app. There were um we've increased the
L0038 [01:37] number of spaces in this room so that
L0039 [01:39] there is a little bit more capacity than
L0040 [01:41] there was before. So, there may be some
L0041 [01:43] workshop spaces left. If you're lucky
L0042 [01:45] enough to have a workshop space, please
L0043 [01:48] do arrive on time for the workshop. They
L0044 [01:51] will be letting people in and then after
L0045 [01:54] um a certain period of time, they will
L0046 [01:57] allow the people who are on the wait
L0047 [01:58] list through. So, just make sure you're
L0048 [02:00] on time for those workshops. So, I can
L0049 [02:03] see that Simon and Rob are now ready.
L0050 [02:05] So, um Simon and Rob, can I please
L0051 [02:08] welcome you to the stage? Um, can you
L0052 [02:10] please give it up for Simon Ostburn and
L0053 [02:13] Rob Willoughby?
L0054 [02:18] They're going to be talking about from
L0055 [02:20] vibes to metrics and how to actually
L0056 [02:22] measure what your agents do. Over to
L0057 [02:25] you.
L0058 [02:26] >> Cool. So, what we're here to talk to you
L0059 [02:28] today about is really kind of how do you
L0060 [02:30] actually assess what your agents are
L0061 [02:32] doing in real world situations. So, a
L0062 [02:35] lot of what we've done historically kind
L0063 [02:36] of as a community is very vibes based.
L0064 [02:38] Does the demo look cool? Does it run
L0065 [02:40] quick? Does this agent seem like it's
L0066 [02:42] producing the right kind of code? And
L0067 [02:44] just as kind of software engineering had
L0068 [02:46] to mature as a discipline, we also think
L0069 [02:48] that agentic engineering is going to
L0070 [02:49] have to mature as a discipline as well.
L0071 [02:50] And you're going to have to lean more
L0072 [02:52] into actually understanding what's going
L0073 [02:54] on behind the hood and actually
L0074 [02:55] understanding how you can then optimize
L0075 [02:57] and improve that. So metrics are
L0076 [03:00] important. I think everyone can agree on
L0077 [03:01] that. And we've got kind of two
L0078 [03:03] different views on how to be assessing
L0079 [03:04] those metrics. one kind of top down
L0080 [03:07] looking at a correlational studies
L0081 [03:08] across kind of a whole bunch a whole big
L0082 [03:10] part of the industry, one bottoms up
L0083 [03:12] really zooming in on kind of how one
L0084 [03:14] agent uses one skill to complete one
L0085 [03:16] task. So in terms of who we are, uh I'm
L0086 [03:20] Rob uh I work at Tesl and I'm going to
L0087 [03:22] be presenting with Simon. Simon's a
L0088 [03:23] researcher with the software engineering
L0089 [03:25] productivity research group at Stanford
L0090 [03:27] and he's seen both sides of this kind of
L0091 [03:29] from CTO in industry and then also from
L0092 [03:32] the researching and consulting view. His
L0093 [03:34] research focuses on the macro view of AI
L0094 [03:36] adoption across the industry. I'm coming
L0095 [03:38] at it from that bottoms up angle that I
L0096 [03:40] mentioned before. So at Tessle really
L0097 [03:42] looking at how a single agent and when I
L0098 [03:44] say agent here I mean specifically one
L0099 [03:46] harness and one model are able to
L0100 [03:48] perform on a single task using a set of
L0101 [03:51] context a set of structure for that. I'm
L0102 [03:53] going to pass it off to Simon uh to
L0103 [03:55] start the talk.
```

## Section 2 -- Transcript segment 2 [L0104-L0206, 03:56-08:40]

```text
L0104 [03:56] >> Okay. So hey everyone uh now first of
L0105 [04:00] all we're going to zoom uh one step out.
L0106 [04:04] Um so um at the sweeper lab uh we put
L0107 [04:09] together the largest software
L0108 [04:10] engineering productivity study to our
L0109 [04:12] knowledge. We currently have roughly
L0110 [04:14] 150,000 engineers that are in one way or
L0111 [04:17] another enrolled in the study. Uh the
L0112 [04:20] companies that we that we work with they
L0113 [04:22] typically commit to uh a one-year
L0114 [04:25] period. uh in that period we look at
L0115 [04:27] their entire source code repository, all
L0116 [04:31] of their engineers uh across all the
L0117 [04:32] programming languages and we try to
L0118 [04:34] observe uh behaviors, patterns, changes
L0119 [04:38] in in the data set. Our research has
L0120 [04:40] been featured in in a number of uh media
L0121 [04:43] outlets. Uh the first piece that we
L0122 [04:45] published uh was reshared by Elon Musk.
L0123 [04:47] Uh we published a piece on on ghost
L0124 [04:49] engineers. uh where we found that
L0125 [04:51] roughly 10% of the engineers didn't
L0126 [04:53] contribute anything meaningful to the
L0127 [04:55] organization in one form or another. Um
L0128 [04:59] and but we do um get featured in in in
L0129 [05:03] you know the the bigger media outlets as
L0130 [05:05] well and we submit our research to the
L0131 [05:08] relevant conferences. So um when we have
L0132 [05:13] a pretty big data set many organizations
L0133 [05:15] enrolled um the first problem is how do
L0134 [05:19] we even understand what's going on so
L0135 [05:21] what we wanted to find is a better way
L0136 [05:24] to look at it than just counting commits
L0137 [05:26] counting uh counting PRs uh looking at
L0138 [05:29] lines of code and uh uh so we we spend a
L0139 [05:33] lot of time in thinking how could we
L0140 [05:34] even measure output and and subsequently
L0141 [05:37] productivity So what we found uh to work
L0142 [05:41] is um that we have the engineer, he
L0143 [05:46] writes the code and then we have a panel
L0144 [05:48] of experts uh who look at the code and
L0145 [05:52] we ask them a set of questions and uh we
L0146 [05:54] ask them questions along the lines of
L0147 [05:56] okay how long uh do you think it took
L0148 [06:00] this person to implement this? How long
L0149 [06:02] how long do you think it would be taking
L0150 [06:03] you to implement this? and a bunch of
L0151 [06:05] other questions on quality,
L0152 [06:07] maintainability and complexity.
L0153 [06:09] Then we found out that in a panel and
L0154 [06:12] also across panels, these people tend to
L0155 [06:15] be in a very high agreement. And to me,
L0156 [06:18] I've been in engineering meetings, that
L0157 [06:19] was a big surprise. So that was the
L0158 [06:21] first prize of the study uh that that
L0159 [06:23] people can actually agree on something.
L0160 [06:25] Now um right and and uh since
L0161 [06:32] we had this high agreement and it
L0162 [06:35] correlated also quite nicely with output
L0163 [06:37] when we backtrack we had in certain
L0164 [06:38] tickets we had the the time spent some
L0165 [06:41] companies have time logging. So from any
L0166 [06:43] way we looked at it it looked kind of
L0167 [06:45] okay. So we we thought okay now how do
L0168 [06:48] we run it at scale? So we built a model,
L0169 [06:51] we put it in a machine learning model
L0170 [06:53] and uh with that uh we were able to run
L0171 [06:57] it at scale. So basically what we intend
L0172 [06:59] to do and what we strive to do is we
L0173 [07:01] look at the output analysis through the
L0174 [07:04] machine learning model that tries to
L0175 [07:06] replicate the expert panel.
L0176 [07:11] All right. Now with with that context
L0177 [07:14] being said, I'll be presenting a few
L0178 [07:15] items and uh Rob will then take it back
L0179 [07:18] to the lower level to understand how
L0180 [07:20] things are are working. We I will show
L0181 [07:23] you a little bit on on how AI is
L0182 [07:26] impacting uh teams. So um this is a time
L0183 [07:31] chart. So we looked at 46 teams that use
L0184 [07:34] AI and we've been looking at them over
L0185 [07:37] quite a long period. Um at one point in
L0186 [07:41] the study um we kind of had to change
L0187 [07:43] the method methodology a little bit. So
L0188 [07:46] for us it was important that we that we
L0189 [07:49] find that we compare similar teams. So
L0190 [07:53] when we looked at the coariantss uh we
L0191 [07:55] were kind of going 4.25
L0192 [07:57] in in in terms of deviation. Um and uh
L0193 [08:03] we then measured them against teams that
L0194 [08:05] that didn't use AI. The problem that we
L0195 [08:08] encountered at one point here was um
L0196 [08:11] that um basically everyone started to
L0197 [08:14] look yeah and the control kind of
L0198 [08:17] control group went away. However, um so
L0199 [08:22] we had to adapt the the methodology in
L0200 [08:24] July, but overall what you can see, so
L0201 [08:27] there wasn't a big difference between
L0202 [08:29] teams that would be using AI and uh
L0203 [08:32] teams that that are using AI or even
L0204 [08:34] within teams that use AI. And now you
L0205 [08:36] can see over time that basically has has
L0206 [08:40] amplified. So over like a 5% different
```

## Section 3 -- Transcript segment 3 [L0207-L0309, 08:43-13:53]

```text
L0207 [08:43] difference in Q1 to Q3 in 2003, you can
L0208 [08:47] see like an up to 60%
L0209 [08:50] uh difference in in July 2026 just to
L0210 [08:53] give you some kind of understanding of
L0211 [08:56] how things are going.
L0212 [08:58] Yeah. Now if we look at this um on a on
L0213 [09:03] a team level you can see also that uh
L0214 [09:06] the discrepancy per team is is vastly
L0215 [09:11] different. So the the laggers there is
L0216 [09:14] no meaningful change in output. The the
L0217 [09:18] bottom uh the the the 25th 50th
L0218 [09:22] percentile is doing better. But when you
L0219 [09:24] look top uh to bottom it's a it's a very
L0220 [09:28] it's a very meaningful difference in
L0221 [09:30] terms of in terms of output and uh what
L0222 [09:33] they achieved. Now in in terms of uh
L0223 [09:40] looking now inside the teams and looking
L0224 [09:42] at the individuals we see that
L0225 [09:46] you know and I think everyone here in in
L0226 [09:49] this room encountered this uh to some
L0227 [09:51] level um you have individuals that you
L0228 [09:55] know may like it may not like it are
L0229 [09:57] really into it uh study invest time in
L0230 [10:00] it adopt it kind of lead it and uh there
L0231 [10:04] is
L0232 [10:06] really it's a significant difference.
L0233 [10:08] It's the biggest difference that we've
L0234 [10:10] ever seen. To be honest, when I started
L0235 [10:12] this study in in 2020, um that's when we
L0236 [10:16] conceptually, you know, thought about um
L0237 [10:20] how do we measure productivity? uh for
L0238 [10:22] me I I had worked in Silicon Valley and
L0239 [10:25] the 10 Xer was something that really
L0240 [10:27] annoyed me and to a certain extent I
L0241 [10:30] wanted to show that it doesn't exist and
L0242 [10:32] it it didn't exist then but over time
L0243 [10:36] we're starting to see it now. So people
L0244 [10:38] that know how to orchestrate agents,
L0245 [10:41] people that know how to work with AI,
L0246 [10:43] they achieve significantly
L0247 [10:46] better outcomes.
L0248 [10:49] Now um on top of that and I think this
L0249 [10:53] is a really interesting slide in terms
L0250 [10:55] of um how um performance is shifting. So
L0251 [11:01] what you see here is the the top um and
L0252 [11:05] the quartiles again and uh we
L0253 [11:11] saw a pretty high rank stability. The
L0254 [11:13] rank stability was uh 70. Yeah. and post
L0255 [11:18] AI it it dropped to 045.
L0256 [11:21] So we believe also like uh that the
L0257 [11:24] tactics that enabled you to be a top
L0258 [11:26] performer no longer enable you to be a
L0259 [11:29] top performer today. So what we believe
L0260 [11:33] is what happens and and to be honest um
L0261 [11:37] a lot of the people from the top bottom
L0262 [11:39] performers um they they moved to the to
L0263 [11:43] the top performers. One hypothesis is
L0264 [11:46] that like these were people that weren't
L0265 [11:49] coding. They were doing code reviews,
L0266 [11:50] maybe helping the teams. And now in
L0267 [11:52] terms of output, maybe some of that got
L0268 [11:54] automated, some of that got shifted
L0269 [11:56] away. Uh and now they became the top
L0270 [11:59] performers. So arguably that's the
L0271 [12:01] hypothesis, right? Like we don't fully
L0272 [12:03] understand why. We just observe that it
L0273 [12:05] happens. They were busy helping others
L0274 [12:08] uh deliver something, deliver good
L0275 [12:10] outcomes, but now they have time and and
L0276 [12:13] they're killing it. Yeah. But we also
L0277 [12:16] see that you know previously
L0278 [12:19] people performing in the top are are
L0279 [12:21] going uh down. Other than that from from
L0280 [12:24] from the Q2 you you see mostly
L0281 [12:29] um you know a downward movement. So
L0282 [12:33] that's what we observe in terms of um
L0283 [12:36] changing landscape.
L0284 [12:38] Yeah. Um now moving on to to something
L0285 [12:45] uh somewhat more technical. What we're
L0286 [12:48] doing is we started to look at how
L0287 [12:50] people
L0288 [12:52] orchestrate their agents and we looked
L0289 [12:56] at what um patterns we see in terms of
L0290 [13:00] or what artifacts we see in in the
L0291 [13:02] repository and and what the artifacts
L0292 [13:05] could possibly mean. So this is a
L0293 [13:07] preview from a paper we've submitted to
L0294 [13:09] ASE. It's uh it's part of the e
L0295 [13:13] automated software engineering uh
L0296 [13:15] conference and it'll happen in October.
L0297 [13:18] So we we don't have the paper out. The
L0298 [13:20] peer reviews are in uh the peer reviews
L0299 [13:23] are quite favorable. Um and um so we we
L0300 [13:28] look at the artifacts, we we look at the
L0301 [13:30] embeddings, we classify and we assign
L0302 [13:33] the levels and we correlate the levels
L0303 [13:36] with the output measurement that we have
L0304 [13:39] uh shown in in the beginning. So just
L0305 [13:43] when we look at uh okay why do we trust
L0306 [13:45] the four levels? So in terms of
L0307 [13:47] scientific uh validations uh the
L0308 [13:49] analysis comes back super strong and uh
L0309 [13:53] we we can see the impact on output is is
```

## Section 4 -- Transcript segment 4 [L0310-L0412, 13:56-17:52]

```text
L0310 [13:56] is quite clear. So in terms of uh
L0311 [13:59] looking at it and clustering it it is
L0312 [14:02] quite beautiful. Now what does that
L0313 [14:04] mean? Um
L0314 [14:08] when we look at it we see repos without
L0315 [14:11] AI config level one. So once you start
L0316 [14:13] the agents run on it and and you don't
L0317 [14:16] have any harnessing and tooling
L0318 [14:17] instruction skills or whatnot we see
L0319 [14:20] that in terms of um you know change
L0320 [14:24] after agent adoption it's it's just bad
L0321 [14:28] you know you see more cognitive
L0322 [14:30] complexity more static warnings code
L0323 [14:32] duplication the commit volume it's
L0324 [14:36] changing but it's just uh
L0325 [14:40] yeah it it's just it feels like the
L0326 [14:42] agents are limited So the tooling and
L0327 [14:44] instrumentation is essential to it. Now
L0328 [14:49] when we look at L2,
L0329 [14:51] you see a significant increase in PR
L0330 [14:54] throughput. You see uh um uh even a
L0331 [14:59] decrease in revert rate, code
L0332 [15:00] duplication goes down, code uh cognitive
L0333 [15:02] complexity goes down. So all metrics
L0334 [15:05] that we analyzed are actually now
L0335 [15:09] improving today with applying AI and and
L0336 [15:13] that wasn't always so like in the
L0337 [15:15] beginning a lot of the arguments of
L0338 [15:17] teams that didn't want to adopt AI is
L0339 [15:19] like hey rework will go up we'll just
L0340 [15:21] introduce defects uh the code quality
L0341 [15:23] will erode and we don't see that anymore
L0342 [15:27] in level two level three teams now I
L0343 [15:32] think with that I'm I'm handing it over
L0344 [15:35] to to Rob who will tell you a little bit
L0345 [15:37] how to optimize in the details of level
L0346 [15:41] three.
L0347 [15:42] Cool. So I hope Simon's convinced you
L0348 [15:45] that yeah structure in a codebase
L0349 [15:47] actually kind of matters for the things
L0350 [15:48] that we care about in terms of the
L0351 [15:50] quality of the codebase. So what I want
L0352 [15:51] to do now is to go into a little bit of
L0353 [15:53] a deep dive in terms of how you put that
L0354 [15:55] structure in place using skills kind of
L0355 [15:57] as the artifact to focus on there. This
L0356 [15:59] is the switch from that top down view to
L0357 [16:01] the bottoms up view. So on the left
L0358 [16:04] we've got kind of that macro view the
L0359 [16:06] finding to um that Simon was presenting
L0360 [16:08] kind of the observational over 150,000
L0361 [16:10] engineers and degrading kind of three
L0362 [16:12] times less once you've got that
L0363 [16:14] structured in context information while
L0364 [16:16] shipping at the same speed or faster. So
L0365 [16:19] next zooming in onto kind of a single
L0366 [16:21] agent, a single task, and the single
L0367 [16:24] artifact that we're going to use to
L0368 [16:25] influence how the agent does that task,
L0369 [16:27] which in this case is a skill. And a
L0370 [16:29] skill is that L3 artifact that he was
L0371 [16:32] just talking about. The thing that I
L0372 [16:34] want you to keep in mind is cool, the
L0373 [16:36] work is getting finished either way. You
L0374 [16:38] were seeing commits were still getting
L0375 [16:39] shipped at the same velocity. The task
L0376 [16:41] was still getting completed. So if we've
L0377 [16:43] got this idea of structure, what is that
L0378 [16:45] structure actually changing? What impact
L0379 [16:47] is that structure having? So the agent,
L0380 [16:51] as I was saying, finishes the task
L0381 [16:52] either way. But what changes is how the
L0382 [16:56] agent finishes the task. It's the
L0383 [16:57] instruction following bit there. I want
L0384 [16:59] to talk a little bit about what kind of
L0385 [17:01] tasks we have here. And what I mean by
L0386 [17:03] goal completion and instruction
L0387 [17:04] following. So the data set that we're
L0388 [17:06] running is we've got uh 500 skills.
L0389 [17:09] We've got 1,000 tasks. We got 19
L0390 [17:11] configs. The 19 configs are combinations
L0391 [17:14] of models and harnesses. So we've got 19
L0392 [17:16] permutations of different models,
L0393 [17:18] different harnesses because those have
L0394 [17:20] an impact on each other and also affect
L0395 [17:22] the performance. And then the tasks that
L0396 [17:24] we're using, those a thousand
L0397 [17:25] synthetically derived tasks are a
L0398 [17:27] synthetic, but b they are tasks that are
L0399 [17:29] grounded in the skill itself that are
L0400 [17:31] meant to be something that is reasonable
L0401 [17:32] that you would expect the skill to
L0402 [17:34] trigger for. So if you got a skill on
L0403 [17:36] say how to use how to put in place API
L0404 [17:38] security, the task that we're going to
L0405 [17:40] construct for that is add a new API
L0406 [17:42] route or change the authentication from
L0407 [17:44] password to some other mechanism um for
L0408 [17:47] that route or something else that's
L0409 [17:48] affecting the route that might not be
L0410 [17:49] security related but you would expect
L0411 [17:51] the agent to be picking up on the
L0412 [17:52] security implications of that. And so
```

## Section 5 -- Transcript segment 5 [L0413-L0515, 17:55-21:12]

```text
L0413 [17:55] goal completion we're intentionally not
L0414 [17:57] trying to do like super hard frontier
L0415 [17:59] pushing the boundary of the model here.
L0416 [18:00] Think of it as kind of like well scoped
L0417 [18:02] Jira tickets that you'd expect a
L0418 [18:04] mid-level engineer to be picking up on.
L0419 [18:06] Hence why we see kind of goal completion
L0420 [18:08] hitting a threshold of 90 93% regardless
L0421 [18:11] of whether the skill is in there or not.
L0422 [18:12] On the instruction following, this is
L0423 [18:14] the rubrics, the metrics that are
L0424 [18:16] grounded specifically in what the skill
L0425 [18:18] is telling the agent how to do. So if
L0426 [18:20] you have your own internal design
L0427 [18:21] patterns for how you want a certain
L0428 [18:22] library to be called or to make sure
L0429 [18:24] that you're updating to a certain
L0430 [18:25] version uh versus another, that's the
L0431 [18:27] information that would be encoded in the
L0432 [18:29] skill and then encoded in the
L0433 [18:30] instruction following improvement that
L0434 [18:32] we see there. One really interesting
L0435 [18:34] thing about that number specifically is
L0436 [18:36] that we see 55% following the
L0437 [18:38] instructions of the skill even when the
L0438 [18:40] skill is not present. That means the
L0439 [18:42] information that is encoded in the skill
L0440 [18:44] is actually part of the weights of the
L0441 [18:46] model already. And so when you're
L0442 [18:48] telling the model to do it, well, it was
L0443 [18:50] going to do it anyways. So is that
L0444 [18:51] tokens as actually valuable? Because now
L0445 [18:53] you're burning inference tokens and
L0446 [18:54] paying money to anthropic, open AAI or
L0447 [18:56] Google when the model was going to do it
L0448 [18:58] anyways without you telling it to do
L0449 [18:59] that. So the agent is still going to be
L0450 [19:01] finishing, but for the things that you
L0451 [19:04] as a company care about, it's this
L0452 [19:06] structure, these skills are changes how
L0453 [19:08] it does it, how well it does it. So test
L0454 [19:12] completion, this is basically rehash of
L0455 [19:14] what I just said. Touch completion
L0456 [19:16] unchanged. Uh the goal completion stays
L0457 [19:18] near the ceiling, but is it done
L0458 [19:21] correctly? It's that improvement jump.
L0459 [19:22] And here I wanted to dive into kind of
L0460 [19:24] three categories on what uh is changing
L0461 [19:27] specifically that we s see repeated.
L0462 [19:29] One, library and API choices. You might
L0463 [19:31] have an internal code style guidelines.
L0464 [19:33] You might have say hey we're allowed to
L0465 [19:35] use this set of libraries when we want
L0466 [19:36] to do ML and we're not allowed to use
L0467 [19:38] this other set or we have to make sure
L0468 [19:40] that we're not pulling in anything from
L0469 [19:41] npm that is what is it 7 days old now
L0470 [19:44] given all the recent issues with npm so
L0471 [19:46] those that information is stuff that the
L0472 [19:48] agent isn't going to know and so unless
L0473 [19:50] you encode it the agent is just going to
L0474 [19:52] do whatever is in the training data
L0475 [19:54] conventions required steps hey if you
L0476 [19:56] want to hit this um use this backend
L0477 [19:58] service you also then need to configure
L0478 [19:59] the API credentials in your environment
L0479 [20:01] this way you need to make sure you uh
L0480 [20:03] land this infrastructure as code and run
L0481 [20:04] tofu apply so that it actually gets
L0482 [20:06] deployed before you go spin this up or
L0483 [20:08] else you're going to have a bad time.
L0484 [20:09] That's information that's unique to your
L0485 [20:10] setup, your engineering environment that
L0486 [20:12] the agent is going to know. And then
L0487 [20:14] finally, prohibited or deprecated
L0488 [20:16] patterns. Maybe you really don't ever
L0489 [20:18] want an agent to write something that is
L0490 [20:19] exposed to the internet unless it goes
L0491 [20:21] through a reverse proxy that your
L0492 [20:22] security team manages. Agent isn't going
L0493 [20:24] to know that unless you tell it that. So
L0494 [20:27] again, what is that unique business IP,
L0495 [20:29] that unique flavor of how you as a
L0496 [20:31] company want your agents to be
L0497 [20:32] operating? So this is kind of a concrete
L0498 [20:35] example that we found that I found super
L0499 [20:37] interesting. So I use a lot of hugging
L0500 [20:39] face. Hugging face, as you might know,
L0501 [20:41] had an old CLI, hugging face- CLI, lots
L0502 [20:44] of words to write, and a new CLI, HF,
L0503 [20:46] many less words to write. However, the
L0504 [20:48] new hugging face CLI came out after
L0505 [20:51] model training data cutoffs for all the
L0506 [20:54] recent frontier models. So if you
L0507 [20:56] naively say, "Hey agent, go implement
L0508 [20:58] how to call this hugging face CLI or
L0509 [21:00] debug why my script using that isn't
L0510 [21:02] working," it's going to rewrite it on
L0511 [21:03] the left. And one of the patterns that
L0512 [21:05] the new CLI really anchors on is they
L0513 [21:08] want you to be passing um your
L0514 [21:09] credentials as envir not as part of
L0515 [21:12] login- token. And so agent's going to do
```

## Section 6 -- Transcript segment 6 [L0516-L0618, 21:14-24:16]

```text
L0516 [21:14] the old thing and we see this agent does
L0517 [21:16] the old thing. And if you're just
L0518 [21:18] looking at task completion because of
L0519 [21:19] backwards compatibility, hugging face
L0520 [21:21] hasn't deprecated this. say haven't
L0521 [21:23] killed the CLI because a lot of agents
L0522 [21:24] still use this and so this will pass a
L0523 [21:26] task completion metric but it means that
L0524 [21:27] you're going to be stuck at that point
L0525 [21:28] in time and you're not going to be able
L0526 [21:30] to roll forward you're not going to be
L0527 [21:32] able to tell your agent hey we need to
L0528 [21:33] use this new thing until it gets into
L0529 [21:35] the training data until it gets into
L0530 [21:37] kind of the past the metal cuto cut off
L0531 [21:38] date and then that's like 6 months in
L0532 [21:40] the future 9 months in the future some
L0533 [21:42] amount of time in the future and so this
L0534 [21:43] is how you then start to change that and
L0535 [21:45] to be providing that at inference time
L0536 [21:47] and so if we're just looking at
L0537 [21:48] throughput if we're just looking at
L0538 [21:50] output they're identical it's still
L0539 [21:51] going to do the same thing but it's held
L0540 [21:53] to a different standard and it's that
L0541 [21:55] standard is that encoding and that
L0542 [21:57] structure. There's a couple kind of key
L0543 [21:59] bits where we saw repeated instances of
L0544 [22:01] this happening. So numbers on the right
L0545 [22:03] are the lift that we see on the
L0546 [22:04] instruction following rubric. So that is
L0547 [22:06] the rubric that is grounded on what the
L0548 [22:08] skill is doing and this has come some
L0549 [22:10] clustering that we did just kind of
L0550 [22:11] standard K uh K nearest neighbor
L0551 [22:13] clustering um to figure out kind of
L0552 [22:15] different categories. The ones where we
L0553 [22:17] saw the biggest lift, the biggest
L0554 [22:18] improvement are the ones where you know
L0555 [22:21] there are opinions where you want to do
L0556 [22:23] something a little bit differently or
L0557 [22:24] where there isn't as much prior
L0558 [22:26] knowledge in the training data. So media
L0559 [22:28] and file processing, what are your
L0560 [22:29] internal conventions? How do you want to
L0561 [22:31] be handled that? There's content and
L0562 [22:33] docs. I hope everyone has a house style
L0563 [22:35] and isn't just relying on claude to
L0564 [22:37] write out whatever they want for their
L0565 [22:39] blogs. Security and compliance. Your
L0566 [22:41] security policy is going to be unique to
L0567 [22:43] your organization, your infrastructure,
L0568 [22:44] your setup, what your auditors require.
L0569 [22:46] It's not just going to be something you
L0570 [22:48] just want to copy and paste off the
L0571 [22:49] internet. So data processing, that one's
L0572 [22:51] a little bit more generic because
L0573 [22:52] there's only so many ways that you can
L0574 [22:54] kind of write a pandas transform or do
L0575 [22:57] kind of a basic data processing step.
L0576 [22:59] And then testing QA, this one was
L0577 [23:01] interesting for me, but kind of on
L0578 [23:02] reflection makes a lot of sense. Smalls
L0579 [23:04] are trained extensively to do
L0580 [23:05] test-driven development. They have seen
L0581 [23:08] lots and lots of tests. how different is
L0582 [23:10] your unique testing style or your unique
L0583 [23:12] testing structure compared to what uh
L0584 [23:15] kind of the other frontier labs are
L0585 [23:16] doing and if it's that different is it
L0586 [23:18] that much better. So this is kind of
L0587 [23:20] these kind of like ones where there
L0588 [23:22] isn't differentiation that you are able
L0589 [23:24] to apply as a business not sure how much
L0590 [23:26] value there is in terms of saying we
L0591 [23:28] want to force this context in. So
L0592 [23:30] investing in the structure where the
L0593 [23:32] conventions are local and important to
L0594 [23:34] your business that's where the value is.
L0595 [23:37] And then finally quickly just in terms
L0596 [23:39] of what you should be measuring and how
L0597 [23:41] you want to be measuring. I would make
L0598 [23:42] the claim that kind of just looking at
L0599 [23:44] the outcome that's just looking at
L0600 [23:45] measure three. That's just looking at
L0601 [23:46] the final box. And what you actually
L0602 [23:48] want to be doing is measuring across the
L0603 [23:50] spectrum. One, did the skill actually
L0604 [23:52] activate? We all know it's hard to get
L0605 [23:54] Claude to go activate skills,
L0606 [23:55] particularly when there's 20 or 30 or 40
L0607 [23:57] in the context window. Codex will
L0608 [23:59] actually shrink it down your
L0609 [24:00] descriptions if it says it takes up more
L0610 [24:01] than 2% of the budget by default. So you
L0611 [24:04] need to figure out a way to actually be
L0612 [24:05] assessing whether your skull is
L0613 [24:06] activating for the circumstances that
L0614 [24:08] it's doing and to optimize that
L0615 [24:10] description so that it can do that
L0616 [24:11] effectively. Second trajectory. So when
L0617 [24:14] it actually did the steps, when it
L0618 [24:16] actually did the thing, are you looking
```

## Section 7 -- Transcript segment 7 [L0619-L0721, 24:18-28:27]

```text
L0619 [24:18] at did the run follow the intended
L0620 [24:19] workflow? Did it actually do the steps
L0621 [24:21] in sequence as you wanted it to? And
L0622 [24:23] then third outcome, that's the standard
L0623 [24:25] one. That's like, hey, did it do the
L0624 [24:26] thing? Did it write the code? Did it
L0625 [24:28] pass the test? One really interesting
L0626 [24:30] finding from some different work um that
L0627 [24:32] we had is that if you change the harness
L0628 [24:34] around the model, you can actually move
L0629 [24:37] scores by up to 100%. You will have
L0630 [24:39] massive difference just by changing the
L0631 [24:41] way that the model is called because
L0632 [24:43] models are going to be trained
L0633 [24:44] extensively on a specific harness or
L0634 [24:46] not. So it's not just hey I'm testing
L0635 [24:48] Opus 48. It's I'm testing Opus48 in
L0636 [24:51] which specific version of clot code or
L0637 [24:54] in open hands or in open code or in any
L0638 [24:56] of the other kind of model harnesses out
L0639 [24:58] there including your own one. So you got
L0640 [25:00] to test the whole system al together.
L0641 [25:02] Measurement is how you do this shift to
L0642 [25:04] go from that L1 to L2 to L3 to L4. Going
L0643 [25:08] to pass it off to Simon to wrap it up
L0644 [25:09] with the spending index.
L0645 [25:11] >> Okay, cool. So maybe one thing worth
L0646 [25:14] mentioning the mod the level analysis is
L0647 [25:16] available as open source. uh it's
L0648 [25:18] available on our lab website. I'll be
L0649 [25:20] sharing that with you on the on on the
L0650 [25:23] last slide. So uh based on everything
L0651 [25:25] that we've seen like uh a dimension that
L0652 [25:27] we're lacking in in our research is a
L0653 [25:30] little bit the connection of you know
L0654 [25:32] the output and outcomes achieved uh in
L0655 [25:35] relation with um with token spend. I
L0656 [25:38] think there is also uh uh a lot of
L0657 [25:40] uncertainty on on what's an appropriate
L0658 [25:43] amount of token spend. So we decided to
L0659 [25:45] launch the Stanford AI spend index and
L0660 [25:49] basically we publish monthly AI spend
L0661 [25:50] per developer stats uh based on our
L0662 [25:53] participants. So what you can do is uh
L0663 [25:56] you can sign up and uh you can uh you
L0664 [25:59] can submit uh your own organization's
L0665 [26:02] data and in exchange you can unlock uh a
L0666 [26:04] little bit more granular data. So that
L0667 [26:06] will help us in the future to kind of
L0668 [26:08] like connect our research more uh in in
L0669 [26:11] terms of token spend. Uh naturally in
L0670 [26:14] terms of the the research organizations
L0671 [26:16] that like have their repositories
L0672 [26:19] integrated with our analysis platform,
L0673 [26:21] they're also connecting some of their um
L0674 [26:24] agents and and LLMs and we're also
L0675 [26:27] getting spend data from there. We're not
L0676 [26:29] able to to publish all of them, but in
L0677 [26:31] terms of modeling, we're working on
L0678 [26:33] really looking at like what's the best
L0679 [26:36] way to to use tokens and uh how to get
L0680 [26:39] the most out of them. Yeah. Um that's
L0681 [26:43] what I had or what we had. Yeah. Uh here
L0682 [26:46] is the the relevant websites on uh for
L0683 [26:51] our lab and and the AI spend index. And
L0684 [26:54] I think for Tesla, you all know where to
L0685 [26:55] go. You see the logo, you'll figure it
L0686 [26:57] out soon.
L0687 [26:59] >> All right.
L0688 [26:59] >> Uh, and I think we've got a couple
L0689 [27:01] minutes for questions as well at the
L0690 [27:02] end.
L0691 [27:03] >> First off, thank you very much, SIMON.
L0692 [27:12] >> We've got a question right there.
L0693 [27:14] >> Thanks, Prince.
L0694 [27:15] >> Oh, that was first. Thank you.
L0695 [27:17] Absolutely brilliant. Thank you so much,
L0696 [27:19] both of you. Um one question about that
L0697 [27:22] fascinating switch in the productivity
L0698 [27:24] of um engineers and in your own words
L0699 [27:28] who are now killing it. I know it may be
L0700 [27:31] a bit um tricky to collect that
L0701 [27:33] dimension of data. Yeah. By any chance
L0702 [27:36] did you include age in the groups?
L0703 [27:40] >> Uh we did not include age but we have um
L0704 [27:45] some level of HR data available. We have
L0705 [27:48] uh titling, we have um uh region. So so
L0706 [27:53] there is a bunch of data just not age
L0707 [27:55] specifically because under some
L0708 [27:58] regulation you know age data is
L0709 [28:00] controlled data and people get iffy
L0710 [28:02] about it.
L0711 [28:03] >> So we decided to not include that. But
L0712 [28:06] look, we we kind of infer that more or
L0713 [28:09] less uh by title that some correlation
L0714 [28:12] with that and uh some companies look we
L0715 [28:16] we analyze all their repositories and
L0716 [28:18] and some company some people are
L0717 [28:20] obviously around for 10 plus years and
L0718 [28:23] and we see that in
L0719 [28:25] >> so I'll I'll just say this at the end.
L0720 [28:27] Um
L0721 [28:27] >> I cannot tell you like if people
```

## Section 8 -- Transcript segment 8 [L0722-L0824, 28:29-32:27]

```text
L0722 [28:29] >> No, I know I know all I'm going to say
L0723 [28:31] is it's just and it may be interesting
L0724 [28:33] for the audience in the room as well. I
L0725 [28:34] I go to a lot of events and this is the
L0726 [28:37] first one where you have dev development
L0727 [28:40] developer in the title and in the focus
L0728 [28:42] and the age distribution is very
L0729 [28:44] interestingly skewed towards um more
L0730 [28:48] senior in experience let's call it that
L0731 [28:50] way ages um that's a very interesting um
L0732 [28:54] scenario which I don't see in other
L0733 [28:56] events so I I've been curious since the
L0734 [28:57] beginning are these the seniors coming
L0735 [29:00] back from you know just management into
L0736 [29:02] the trenches or is you know something
L0737 [29:04] else. But anyway, thank you.
L0738 [29:05] >> Um, if you I can tell you one thing with
L0739 [29:08] regards to the Q1 uh to top quartile
L0740 [29:13] movement. We see a lot of that happening
L0741 [29:15] on on staff engineer principal engineer
L0742 [29:17] level. So that's why we made formulated
L0743 [29:20] the hypothesis that maybe they were
L0744 [29:22] helping and didn't have time to code and
L0745 [29:24] and now you know when you have a code
L0746 [29:26] review agent or other ways to free up
L0747 [29:28] their time, they can do really well.
L0748 [29:37] Thank you. Um, on this slide as well,
L0749 [29:40] I've been reading quite a lot online
L0750 [29:41] about scenarios where people uh, sorry,
L0751 [29:43] where employees have been given bad
L0752 [29:45] performance ratings explicitly because
L0753 [29:47] they are not using AI. How does that
L0754 [29:50] factor into this stat? And could that
L0755 [29:52] bias at all? Like is it that people who
L0756 [29:54] don't want to use AI are just
L0757 [29:55] automatically being treated as not good
L0758 [29:57] performers anymore? No, because we look
L0759 [30:00] at all engineers whether or not they use
L0760 [30:02] AI or or not. Yeah. So, um it's it's we
L0761 [30:06] really just look at their output per the
L0762 [30:09] um model analysis that I showed you on
L0763 [30:11] the first slide. So, it's the expert
L0764 [30:14] panel algorithmic analysis that looks at
L0765 [30:16] your output. What have you contributed?
L0766 [30:18] And and based on that, we put you in a
L0767 [30:21] quartile. Yeah. So if you did all of
L0768 [30:24] that
L0769 [30:26] with AI or without doesn't matter. Yeah.
L0770 [30:29] But we don't look at the HR data. So
L0771 [30:31] this is really just based on the the uh
L0772 [30:34] Raider panel machine learning model.
L0773 [30:36] >> Thank you.
L0774 [30:39] >> We've got one back there and then one
L0775 [30:41] down here.
L0776 [30:44] >> You mentioned it matters um in what
L0777 [30:47] harness the model runs. Do you regularly
L0778 [30:50] publish those data as well?
L0779 [30:53] >> Um, maybe I wasn't precise in my
L0780 [30:56] language. It matters that you harness
L0781 [30:59] and that you have clear instructions.
L0782 [31:02] >> Or is that Oh, sorry.
L0783 [31:04] >> Yeah. Yeah. We we made the claim that uh
L0784 [31:05] it does matter what harness. Uh we are
L0785 [31:07] trying to get better about that. Um, so
L0786 [31:10] we've got a paper that just got
L0787 [31:11] submitted arcs that we're going to be
L0788 [31:13] sharing out publicly where we've done
L0789 [31:14] this 19 configs um to kind of look at
L0790 [31:16] the permutations of model and harness um
L0791 [31:19] and we're figuring out what we want to
L0792 [31:21] kind of be our benchmarking strategy
L0793 [31:22] moving forward to be sharing those
L0794 [31:24] numbers more widely. So I know it's a
L0795 [31:26] bit of a copout answer but also come
L0796 [31:28] talk to me afterwards down at the booth
L0797 [31:29] downstairs if you want more details on
L0798 [31:31] that
L0799 [31:31] >> and maybe maybe share them like on a
L0800 [31:33] regular basis y not just one paper would
L0801 [31:36] be great. We try to do we're going to
L0802 [31:37] try to do it every kind of model release
L0803 [31:38] as well just when you know there's a new
L0804 [31:40] model people want to understand how it
L0805 [31:42] performs.
L0806 [31:44] >> Great. Thank you. And I think we had
L0807 [31:45] another question down here. Oh, we've
L0808 [31:47] got another couple of questions down
L0809 [31:49] here. We're okay for a couple more.
L0810 [31:54] >> Yeah, thanks again. Um, this question is
L0811 [31:56] for Rob. I think you mentioned in one of
L0812 [31:58] your slides that uh there is a code
L0813 [32:02] structure or quality that you unlock or
L0814 [32:06] you've come to consensus or or or
L0815 [32:08] there's some some idea that the quality
L0816 [32:10] of the code matters or has an influence
L0817 [32:13] in the outcome. Do you do you have like
L0818 [32:15] an idea of what that quality is? What
L0819 [32:18] conventions
L0820 [32:20] uh it is? I mean it doesn't have to be a
L0821 [32:21] concrete answer but like you know
L0822 [32:24] following some of the engineering
L0823 [32:25] practices related qualities or you've
L0824 [32:27] come up across with some new ways of
```

## Section 9 -- Closing segment [L0825-L0928, 32:29-36:26]

```text
L0825 [32:29] doing this that'll help improve the the
L0826 [32:31] outcomes. So I think what we were
L0827 [32:34] looking at more specifically is just
L0828 [32:35] kind of following any instruction
L0829 [32:38] specifically, not the generation of
L0830 [32:40] those instructions, whether they're
L0831 [32:41] informed by cleaning code or any other
L0832 [32:43] kind of coding standards. Um because
L0833 [32:46] that kind of is very particular to an
L0834 [32:47] organization in terms of how they want
L0835 [32:49] to run their code style and to run how
L0836 [32:52] they kind of like manage that manage
L0837 [32:54] complexity across their codebase. So no,
L0838 [32:56] we did not look at that bit kind of
L0839 [32:58] within um our study. Were there any kind
L0840 [33:01] of findings from what you did though in
L0841 [33:02] terms of like how people structured kind
L0842 [33:05] of principles that they structured the
L0843 [33:06] code with um that had an impact in terms
L0844 [33:09] of performance?
L0845 [33:10] >> No, we we we don't look at this uh
L0846 [33:13] specifically. We're actually working on
L0847 [33:16] a paper that where we integrate with uh
L0848 [33:19] application performance management tools
L0849 [33:22] that would give us that dimension but we
L0850 [33:24] have nothing published about that yet.
L0851 [33:26] So, so there is some some some thought
L0852 [33:28] or inquisitivity on code quality might
L0853 [33:32] have an impact and you haven't
L0854 [33:34] investigated yet.
L0855 [33:35] >> So, we when I go back to the initial let
L0856 [33:38] me show you on the radar panel. So,
L0857 [33:40] there's questions on on uh quality and
L0858 [33:44] maintainability quality that's pretty
L0859 [33:46] subjective. Uh so and if you look at
L0860 [33:50] that paper you'll see there is this is
L0861 [33:53] the question with the lowest agreement.
L0862 [33:56] Um we have since uh then done separate
L0863 [33:59] uh panel analysis uh specifically on
L0864 [34:02] maintainability and in terms of how easy
L0865 [34:04] it is to maintain it. It there are
L0866 [34:07] significantly higher agreements. So
L0867 [34:09] that's what we use in our analysis when
L0868 [34:11] we talk about maintainability and
L0869 [34:13] whether that went up or down. That's
L0870 [34:15] what we would typically use.
L0871 [34:17] Thank you. Okay, I just take this across
L0872 [34:19] to Justin. There you go, Justin.
L0873 [34:22] >> I'm interested in the in the diagram
L0874 [34:23] we're looking at before with people's
L0875 [34:24] improvement. I mean, h how long is it
L0876 [34:26] taking people to get into these high
L0877 [34:28] performing states? And, you know, what
L0878 [34:31] what can you see what kind of triggers
L0879 [34:33] there are and what kind of things are,
L0880 [34:36] you know, are the high performers kind
L0881 [34:37] of getting there very quickly or or are
L0882 [34:39] people gradually still moving across
L0883 [34:42] into these things? because you your your
L0884 [34:44] first graph of the kind of exponential
L0885 [34:47] growth
L0886 [34:48] showed a very fast takeoff very
L0887 [34:50] recently, but I'm kind of interested in
L0888 [34:52] like how how are people getting there?
L0889 [34:54] Do do you understand what triggers them
L0890 [34:56] and is it is it is it something that can
L0891 [34:58] they can people are still hitting
L0892 [35:00] >> something super interesting to look at?
L0893 [35:01] We we just haven't done it.
L0894 [35:03] >> Yeah, we we take note that this is how
L0895 [35:07] it is. Um what we see is that
L0896 [35:12] so once you're classified as AI top
L0897 [35:16] performer, you tend to stay in that
L0898 [35:18] bucket.
L0899 [35:19] >> Um so it it seems to be a mindset switch
L0900 [35:23] um that takes place and we see teams
L0901 [35:26] that like when you have that are very
L0902 [35:29] strongly I pill like they just do super
L0903 [35:32] well. Yeah. I guess even if you're as an
L0904 [35:36] individual, you know, super into it, you
L0905 [35:38] know how to do it. If you have to drag
L0906 [35:41] your team along, then you won't be able
L0907 [35:43] to achieve as good as
L0908 [35:44] >> Yeah, I the team thing is a very
L0909 [35:46] interesting measure because I know
L0910 [35:47] people who have left because the rest of
L0911 [35:49] their team is not working in a way
L0912 [35:51] that's compatible with them and things
L0913 [35:52] like that. And so the the the team
L0914 [35:54] trying to understand the team dynamic
L0915 [35:56] changes would be interesting as well.
L0916 [35:58] >> Sure. Our some of our study participants
L0917 [36:00] asked us to do an analysis like what is
L0918 [36:02] the type of people that they're losing?
L0919 [36:05] Are they leaving losing their top
L0920 [36:06] performers? Um are are they hiring uh
L0921 [36:09] top performers? So they do all that like
L0922 [36:12] we we have and we offer them a panel and
L0923 [36:16] they could in principle look at it. It's
L0924 [36:18] just we haven't published anything about
L0925 [36:20] it.
L0926 [36:21] >> Okay, I'm afraid that's all we've got
L0927 [36:23] time for now. So, thank you again to
L0928 [36:26] Robin Simon.
```

