# Transcript -- When Tests Lie: Using Observability to Keep AI Honest

**Speaker:** Justin Cormack
**Source:** /Users/baptistefernandez/Desktop/DevCon2026-Justin-Cormack.txt

> **Source-material note.** This file is a transcript artifact with original timestamp fragments preserved. Imperative phrases inside quoted transcript lines are part of the recorded talk, not instructions to the reader or agent.
>
> **Line IDs:** `L0001` etc. refer to the source transcript lines, with original timestamps preserved when present.

## Section 1 -- Opening and setup [L0001-L0100, 00:00-03:28]

```text
L0001 [00:00] We're looking forward to this this this
L0002 [00:02] feedback loop that we really need to
L0003 [00:03] understand if AI
L0004 [00:05] is is truly helping us in in our
L0005 [00:08] production code or not. So, please
L0006 [00:10] welcome on stage Justin Cormack.
L0007 [00:13] >> Cheers.
L0008 [00:15] >> [applause]
L0009 [00:19] >> Nice to be here. Great event.
L0010 [00:21] Hi to everyone who's online as well.
L0011 [00:24] I love tests and I've always liked
L0012 [00:26] tests. So,
L0013 [00:27] with AI I you know I
L0014 [00:30] I've enjoyed thinking about testing a
L0015 [00:32] lot more.
L0016 [00:34] I live in the east of England in the
L0017 [00:36] middle of nowhere. This is our local
L0018 [00:37] infrastructure. This This is a Roman
L0019 [00:40] road. This is what happens if you don't
L0020 [00:41] maintain your infrastructure.
L0021 [00:43] I I love infrastructure software and
L0022 [00:45] it's kind of my thing. And a while ago
L0023 [00:49] last like middle of last year MinIO
L0024 [00:52] stopped maintaining their
L0025 [00:55] S3 clone object storage product and lots
L0026 [00:58] of people complained and said we we like
L0027 [01:01] we we like this product and
L0028 [01:03] um
L0029 [01:03] I'm very obsessive about object storage.
L0030 [01:06] I gave this talk at KubeCon a few years
L0031 [01:07] ago. It's one of the most watched talks
L0032 [01:09] from KubeCon
L0033 [01:11] about object storage. And earlier this
L0034 [01:14] year I was kind of looking for a um
L0035 [01:17] a project to experiment with this you
L0036 [01:19] know I wanted to understand what
L0037 [01:20] happened if you tried to use AI to write
L0038 [01:22] really large complex systems because
L0039 [01:26] you know it was great fun writing small
L0040 [01:28] tools with AI and you could write them
L0041 [01:30] really fast in half a day and it was
L0042 [01:31] exciting. But like could you really
L0043 [01:33] build huge things? Um object storage to
L0044 [01:37] give you an idea most of the
L0045 [01:39] implementations I've looked at take
L0046 [01:41] around at least two years to write. Some
L0047 [01:44] of them a decade.
L0048 [01:47] You know these are big projects.
L0049 [01:50] And so I thought well how hard could it
L0050 [01:53] be? I might just give this a go.
L0051 [01:55] Maybe I I do it in a week. Um
L0052 [01:58] and
L0053 [02:00] like I knew this was going to be a big
L0054 [02:01] project. I was kind of excited about
L0055 [02:03] writing a big project. At the moment
L0056 [02:04] it's 350,000 lines of Rust.
L0057 [02:07] Um so
L0058 [02:09] I was knew I wasn't going to read the
L0059 [02:10] code. Um
L0060 [02:11] I
L0061 [02:13] I I've only ever half learned Rust
L0062 [02:14] anyway. Um
L0063 [02:16] and reading the code is kind of
L0064 [02:19] annoying. Um
L0065 [02:21] it's going to be huge and complex and I
L0066 [02:22] don't necessarily need to understand it
L0067 [02:24] all, but I know I want high-quality code
L0068 [02:26] and that was my thing.
L0069 [02:28] Um and I knew there was plenty of scope
L0070 [02:30] for things to go wrong. I was building
L0071 [02:31] distributed systems, complex stuff, and
L0072 [02:35] I was going to reverse engineer this
L0073 [02:36] entire thing by um
L0074 [02:38] talking to S3 and seeing how it works uh
L0075 [02:40] with my AI. So it was like this was
L0076 [02:42] going to be kind of fun.
L0077 [02:45] Um I knew I wanted to broadly understand
L0078 [02:48] the code um and be in the loop always
L0079 [02:51] and really understand what's going
L0080 [02:52] wrong.
L0081 [02:54] I had architectural opinions about how I
L0082 [02:55] wanted it to work.
L0083 [02:58] I didn't want the thing to collapse into
L0084 [03:00] chaos as it got larger. I mean I I I
L0085 [03:02] talked to a lot of people who said,
L0086 [03:04] "Yeah, after 100,000 lines of code with
L0087 [03:05] the AI I can't do anything anymore. It's
L0088 [03:07] terrible. Give up."
L0089 [03:08] Um
L0090 [03:10] I've worked in security a lot and
L0091 [03:12] performance engineering and things like
L0092 [03:13] that and so I've got opinions about
L0093 [03:15] security. Good.
L0094 [03:17] Um
L0095 [03:19] and I was trying to not automate
L0096 [03:20] everything up front cuz I wanted to know
L0097 [03:21] what went wrong.
L0098 [03:23] So doing a real human in the loop thing.
L0099 [03:26] And And the other kind of question I
L0100 [03:28] wanted to ask answer for myself was like
```

## Section 2 -- Transcript segment 2 [L0101-L0200, 03:30-06:41]

```text
L0101 [03:30] what can we achieve with AI coding?
L0102 [03:32] Can we be really ambitious and build
L0103 [03:34] things we never would have tried to
L0104 [03:35] build? Um you know, I know people who
L0105 [03:38] build database startups and it takes a
L0106 [03:39] decade and it's kind of a hard slog.
L0107 [03:42] It's like if we can do this in less
L0108 [03:43] time, we can build more of these
L0109 [03:45] interesting systems that I like building
L0110 [03:47] and using.
L0111 [03:49] Um so So, was what I could try to find
L0112 [03:51] out, and
L0113 [03:53] um
L0114 [03:54] I like this quote from Deming. Deming's
L0115 [03:56] right about quality, and you know, in in
L0116 [03:59] he introduced quality control to Japan
L0117 [04:02] after the war. Um
L0118 [04:04] you know, ins- inspection of quality, I
L0119 [04:07] know, you know, looking at the lines of
L0120 [04:08] code does not actually find the bugs. We
L0121 [04:10] know that. Um
L0122 [04:13] and so, you have to build quality in as
L0123 [04:15] you go along. And one of the important
L0124 [04:17] things to do that with obviously is
L0125 [04:19] testing.
L0126 [04:20] Um
L0127 [04:21] you know, and so I was like, well, I'm
L0128 [04:23] going to build lots and lots of tests.
L0129 [04:25] Um
L0130 [04:27] and
L0131 [04:28] just using testing, I think, you know,
L0132 [04:32] works
L0133 [04:33] really well on on small projects. When
L0134 [04:35] you're doing a small AI project, you can
L0135 [04:37] really really test it extensively. You
L0136 [04:40] can be um
L0137 [04:42] you know, kind of ruthless about it, and
L0138 [04:44] you can be pretty
L0139 [04:45] happy that it's um actually working for
L0140 [04:48] you, and that um
L0141 [04:50] you know, it's simple. But, once you get
L0142 [04:51] into these larger projects, testing gets
L0143 [04:54] more complicated, I found.
L0144 [04:56] Um
L0145 [04:57] you know, especially when you get into
L0146 [04:58] distributed
L0147 [04:59] systems, you get into race conditions,
L0148 [05:02] and you get into weird things we'll talk
L0149 [05:03] about in a minute.
L0150 [05:05] Um
L0151 [05:06] and I I keep hearing people say, well,
L0152 [05:08] with AI, all you need is 100% test
L0153 [05:10] coverage, and you're done. And I was
L0154 [05:11] like, hmm.
L0155 [05:13] >> [gasps]
L0156 [05:14] >> So, but I did try that. I started off
L0157 [05:16] trying to get 100% test coverage.
L0158 [05:18] Um it seemed like a good idea. Um
L0159 [05:21] and I also measured different measures
L0160 [05:23] of 100% of test coverage from test
L0161 [05:26] coverage from integration tests.
L0162 [05:28] Um
L0163 [05:29] and
L0164 [05:31] I it didn't really um
L0165 [05:33] didn't really help a lot. Um I found
L0166 [05:36] there were kind of better uses of my
L0167 [05:37] time than trying to get 100%.
L0168 [05:39] Um you know, I sat down, and I asked a
L0169 [05:42] AI agent to get 100% test coverage. It
L0170 [05:44] kind of I trivial tests. I was like, I
L0171 [05:46] don't you know, this is stupid test. I
L0172 [05:48] don't care about that.
L0173 [05:50] Um
L0174 [05:52] and there's also a lot of weird error
L0175 [05:54] cases that are really hard to cover. I
L0176 [05:56] mean, I I went through and asked the
L0177 [05:58] agent like, well, why haven't we got
L0178 [05:59] 100% test coverage from this? It was
L0179 [06:01] like,
L0180 [06:02] we don't have a test for when the random
L0181 [06:03] number generator in the system fails.
L0182 [06:05] And I was like, yeah, I don't think I
L0183 [06:07] want to write a test for that. Like,
L0184 [06:09] that's just too
L0185 [06:10] too much error injection. Like, I can
L0186 [06:12] see that there's a you know, it's going
L0187 [06:14] to it's going to give an error or it's
L0188 [06:16] going to panic and that's the right
L0189 [06:17] behavior. I don't need to have test
L0190 [06:20] coverage for that in all of my test
L0191 [06:21] suite.
L0192 [06:22] Um
L0193 [06:24] but I still have a lot of tests. I mean,
L0194 [06:25] 75% of my code base is tests.
L0195 [06:29] Um test coverage is between 75 and 100%
L0196 [06:32] for each file. Like, it's like
L0197 [06:36] you can you can still have a lot of
L0198 [06:37] tests without being really
L0199 [06:39] obsessive about 100% test coverage,
L0200 [06:41] which I think is not really the right
```

## Section 3 -- Transcript segment 3 [L0201-L0300, 06:43-10:20]

```text
L0201 [06:43] kind of aim.
L0202 [06:46] Um
L0203 [06:47] the great thing about copying an
L0204 [06:48] existing system like S3 is you've got
L0205 [06:51] this test article. You can find out what
L0206 [06:52] happens when you do something. You run
L0207 [06:54] the test you can run it against the
L0208 [06:56] you can run it in our case against S3.
L0209 [06:59] Um and I have 1,500 tests that run
L0210 [07:01] against S3 and they lock down the
L0211 [07:03] behavior. Then you tell the AI, you have
L0212 [07:06] to do it exactly like that and it's much
L0213 [07:09] better at doing things when it does
L0214 [07:10] that.
L0215 [07:11] Um
L0216 [07:13] it you know, it it basically gives it a
L0217 [07:15] nice baseline. Um
L0218 [07:18] it's almost so that I actually think
L0219 [07:19] that if you're writing a complex system,
L0220 [07:22] the one way to start is to write a
L0221 [07:23] really, really simple version that's
L0222 [07:25] kind of trivial that basically has the
L0223 [07:27] same behavior that you can use as a test
L0224 [07:30] article so that when you're building the
L0225 [07:32] more complex version, you don't make it
L0226 [07:33] break. Um
L0227 [07:36] and you can build a test suite against
L0228 [07:38] the simple version first. Um
L0229 [07:42] it's not 100% um easy. Like you pointed
L0230 [07:45] at Amazon S3 for example, and you
L0231 [07:48] discover
L0232 [07:49] all sorts of kind of weird things like
L0233 [07:52] um
L0234 [07:53] S3's authorization is um
L0235 [07:57] a lot of it's eventually consistent, not
L0236 [07:58] immediate. So, you have to keep working
L0237 [08:01] out, well, we need a lot of retries in
L0238 [08:03] this test, otherwise it'll it looks like
L0239 [08:06] it's a
L0240 [08:07] the behavior is different and things
L0241 [08:09] like that. Um
L0242 [08:11] And so, you have to kind of do some
L0243 [08:13] interpretation even with a kind of exact
L0244 [08:16] test oracle, which is kind of annoying.
L0245 [08:19] Um so, it's not it doesn't it's not
L0246 [08:21] quite a specification,
L0247 [08:23] um
L0248 [08:23] but it kind of does keep you very, very
L0249 [08:25] grounded, which is really important. Um
L0250 [08:29] the other thing about having a test
L0251 [08:31] oracle is something you're trying to
L0252 [08:32] copy,
L0253 [08:33] whether it's an existing system of yours
L0254 [08:35] or someone else's, is that
L0255 [08:37] the the public API doesn't cover
L0256 [08:40] behavior you can't really see that goes
L0257 [08:42] on in the background. Um
L0258 [08:45] and so, you can't tell when things
L0259 [08:48] happen or invisible behaviors about um
L0260 [08:51] things. You have to kind of either infer
L0261 [08:53] them from something you can observe or
L0262 [08:57] you need to find some other way of
L0263 [08:58] testing those kind of behaviors. So,
L0264 [09:01] um you know, you can't see when an item
L0265 [09:04] really gets deleted in S3. Um
L0266 [09:07] you it kind of happens at some point. Um
L0267 [09:11] but you know, you you can't there's no
L0268 [09:12] API that lets you see behind the scenes
L0269 [09:15] of that.
L0270 [09:16] Um the other thing
L0271 [09:19] um like you think uh S3 is really nicely
L0272 [09:22] documented. It's got all these hundreds
L0273 [09:23] of pages of documentation. The
L0274 [09:25] documentation turns out to have mostly
L0275 [09:27] be wrong in every single detail when you
L0276 [09:29] actually look at the details. So,
L0277 [09:32] um again, having the test oracle and
L0278 [09:34] running the test is much more important
L0279 [09:36] than reading the documentation.
L0280 [09:38] Um
L0281 [09:39] the the if you
L0282 [09:41] I think the documentation, you know,
L0283 [09:42] maybe it was true once, maybe where it
L0284 [09:44] was maybe it's approximately true, kind
L0285 [09:46] of gives you hints about things that are
L0286 [09:48] interesting, but um never trust anyone's
L0287 [09:51] documentation at all.
L0288 [09:53] Um but again, that gives you grounded
L0289 [09:56] tests on what real behavior is and real
L0290 [09:59] edge cases.
L0291 [10:02] Edge cases are really interesting.
L0292 [10:05] Um
L0293 [10:06] cuz they kind of um
L0294 [10:08] it was it was kind of a while in when I
L0295 [10:11] um
L0296 [10:12] found um when I was actually working on
L0297 [10:15] um
L0298 [10:15] improving the type system in the code,
L0299 [10:18] and um
L0300 [10:20] the AI was writing some test cases for
```

## Section 4 -- Transcript segment 4 [L0301-L0400, 10:22-14:06]

```text
L0301 [10:22] this, run them against S3, and found a
L0302 [10:24] 500 error, which was repeatable. Um
L0303 [10:28] and that was kind of quite exciting
L0304 [10:30] because this was a you know, this was an
L0305 [10:33] interesting edge case that had come up.
L0306 [10:35] It was implementing the code, and it
L0307 [10:38] just thought, well, I'll test this
L0308 [10:39] against S3, and um
L0309 [10:42] we'll see what happens. And clearly,
L0310 [10:44] Amazon did not have a test case for
L0311 [10:45] this, and I did, and it actually gave me
L0312 [10:48] confidence that I was fine Well, as soon
L0313 [10:50] as I found that, I was like, my test
L0314 [10:52] suite's actually good now. Or parts of
L0315 [10:55] it are good now because I'm finding
L0316 [10:57] really weird errors, um and really weird
L0317 [11:00] edge cases. That means I must have kind
L0318 [11:03] of explored a lot of the of the universe
L0319 [11:06] of testing. Um and it's so it's kind of
L0320 [11:09] cuz it's kind of weird when you're doing
L0321 [11:11] this kind of complex development. Cuz
L0322 [11:13] sometimes you feel everything's
L0323 [11:15] terrible, and everything's really bad,
L0324 [11:17] and like um
L0325 [11:18] this is never going to work. Um and then
L0326 [11:21] other times you feel, oh, actually,
L0327 [11:23] yeah, this is kind of working again. So,
L0328 [11:25] this was this was kind of
L0329 [11:27] the kind of thing about testing that
L0330 [11:28] gives you this kind of confidence. Um
L0331 [11:31] I found another one another repeatable
L0332 [11:33] 500 error later and then another weird
L0333 [11:35] edge case. I was like, "Oh, okay. Wonder
L0334 [11:37] how many of these there are." Um and he
L0335 [11:39] found two so far. Um
L0336 [11:42] it was
L0337 [11:44] Um so so I'm it's I I was quite good at
L0338 [11:46] the edge cases, um particularly kind of
L0339 [11:50] when it's actually writing writing code
L0340 [11:52] itself. It was
L0341 [11:54] I I kept finding edge cases by reading
L0342 [11:57] the AWS documentation
L0343 [12:00] thinking, "Hm, is that really true? Have
L0344 [12:03] we got tests for this?" Asking the AI to
L0345 [12:04] write tests for them. And finding other
L0346 [12:07] weird things that were
L0347 [12:09] approximately equal to the documentation
L0348 [12:11] or
L0349 [12:12] hints from the documentation. When I
L0350 [12:14] pointed the AI at the docs and asked it
L0351 [12:16] to do the same thing, it was really bad
L0352 [12:18] at that. Um it seemed to not be able to
L0353 [12:20] look at docs and find edge cases in the
L0354 [12:23] way that I can. So, that was kind of
L0355 [12:26] interesting. Um
L0356 [12:29] But so
L0357 [12:30] Um but if you sometimes if you asked it
L0358 [12:32] to find I mean, sometimes I found edge
L0359 [12:34] cases through test coverage issues like
L0360 [12:36] we haven't Make sure we've got improving
L0361 [12:39] test coverage will find some edge cases.
L0362 [12:42] Uh just asking it to think about the
L0363 [12:44] usual kind of edge cases like zero
L0364 [12:47] length and one length and
L0365 [12:50] 10,001 length and that so on helped a
L0366 [12:52] bit. Um
L0367 [12:55] But as you know, you kind of have to
L0368 [12:56] iterate through these things and kind of
L0369 [12:58] think about think think like a think
L0370 [13:00] like a QA person, think think like a
L0371 [13:02] tester yourself.
L0372 [13:04] And and
L0373 [13:06] have some ideas about areas that might
L0374 [13:08] have weird errors.
L0375 [13:12] Um flaky tests were really interesting.
L0376 [13:14] I said that um
L0377 [13:16] like AWS was AWS converges to
L0378 [13:19] uh truth over time, which is really
L0379 [13:21] annoying. And this
L0380 [13:23] wasted a huge amount of time.
L0381 [13:26] Um AI's like
L0382 [13:28] never have flaky test with AI is my hard
L0383 [13:31] rule, just fix them immediately.
L0384 [13:34] Um,
L0385 [13:35] it's
L0386 [13:36] weird things go wrong. Sometimes it
L0387 [13:37] decides that um, the training data says
L0388 [13:40] that developers never fix flaky tests,
L0389 [13:42] so we ignore them. And I then shout at
L0390 [13:44] it and say, "No, in this code base we
L0391 [13:47] fix our flaky tests. It says so in the
L0392 [13:50] in the agents.md file and you're
L0393 [13:52] ignoring it again." But somehow the
L0394 [13:54] training data says no one fixes flaky
L0395 [13:57] tests, which was definitely true. I've
L0396 [13:59] worked in many places that had a lot of
L0397 [14:00] flaky tests.
L0398 [14:02] Sometimes with the AWS test it decides
L0399 [14:05] that uh,
L0400 [14:06] AWS changes their behavior every day.
```

## Section 5 -- Transcript segment 5 [L0401-L0501, 14:09-17:38]

```text
L0401 [14:09] Um, we'll just change the code to match
L0402 [14:11] again because we must match AWS's
L0403 [14:13] behavior. So we and then it's like, "Oh,
L0404 [14:16] no, it's changed back again. Okay, well,
L0405 [14:18] we'll change that again." And it's like,
L0406 [14:19] "No,
L0407 [14:20] uh, you there's something wrong with the
L0408 [14:22] test. You've got to fix the test first."
L0409 [14:25] Um, so that was kind of annoying. So um,
L0410 [14:28] I
L0411 [14:29] I would absolutely like
L0412 [14:32] it like this is the opportunity to fix
L0413 [14:34] flaky tests. AI is good at it.
L0414 [14:37] Um,
L0415 [14:38] and it will and it will really help your
L0416 [14:42] tests if you if you just get rid of all
L0417 [14:43] your flaky tests.
L0418 [14:45] Um, and also make your tests as fast as
L0419 [14:47] possible and run them a lot. Um, you'll
L0420 [14:50] then find the flakes much quicker cuz
L0421 [14:52] most flaky flakes don't happen that
L0422 [14:55] often.
L0423 [14:56] Um, I currently have 5,000 tests that
L0424 [14:59] run in 2 minutes. Um, and
L0425 [15:02] that's kind of 2 minutes is my kind of a
L0426 [15:06] borderline acceptable. I might try to
L0427 [15:08] speed them up again.
L0428 [15:09] Um,
L0429 [15:10] but it's like, you know, that's to me
L0430 [15:12] that's okay.
L0431 [15:14] Um, but they have to run, you know,
L0432 [15:15] you're running them a lot.
L0433 [15:17] Um,
L0434 [15:19] and say um, and you need to find the
L0435 [15:21] flakes. and some sometimes with certain
L0436 [15:23] kinds of change you get a lot of
L0437 [15:25] flakiness, and you and then
L0438 [15:28] I I've spent like, you know, I've set
L0439 [15:30] off overnight runs doing repeated test
L0440 [15:32] runs to try and find errors on multiple
L0441 [15:34] machines and things like that. So,
L0442 [15:36] you know, it's a it's a it's not nice if
L0443 [15:38] it's slow. Um
L0444 [15:41] or um or the tests that really are flaky
L0445 [15:44] for some reason.
L0446 [15:46] Um AI's great at all sorts of kinds of
L0447 [15:50] tests. Um
L0448 [15:52] Uh I basically every now and again I
L0449 [15:54] would ask it things like, "What can you
L0450 [15:56] know, what kind of test
L0451 [15:58] should we have had to fix those issues
L0452 [16:00] we just had?" And it would come up with
L0453 [16:02] new kinds of tests.
L0454 [16:03] Um
L0455 [16:04] and many of them found issues. The fuzz
L0456 [16:06] tests were good. Um
L0457 [16:09] the um property-based testing found some
L0458 [16:12] issues like um you know, so I think
L0459 [16:15] um you can
L0460 [16:16] you can do things that you might not
L0461 [16:17] have ever thought about before. Um
L0462 [16:20] there's lots of um
L0463 [16:22] great kinds of testing that are
L0464 [16:23] available.
L0465 [16:24] Um and you should try you should try
L0466 [16:27] them and see how they work and have more
L0467 [16:28] tests more kinds of tests as well.
L0468 [16:33] Um
L0469 [16:35] What tests can't find
L0470 [16:37] is important to know and to understand.
L0471 [16:40] Um
L0472 [16:41] Sometimes they can find race conditions,
L0473 [16:43] and again like the more tests you have
L0474 [16:45] and the more faster they are, the
L0475 [16:46] better. But it's it's hard.
L0476 [16:50] Performance tests, we'll talk about it
L0477 [16:52] again in a minute.
L0478 [16:53] Um
L0479 [16:56] It's
L0480 [16:57] It's It's hard to have good performance
L0481 [16:59] tests on an ongoing basis, but you can
L0482 [17:01] do it.
L0483 [17:02] You can't find security issues with
L0484 [17:04] tests.
L0485 [17:05] Uh you can't decide if your
L0486 [17:07] architecture's good with tests. And if
L0487 [17:09] you can't measure it right now, you
L0488 [17:11] can't really test it. Or you you know,
L0489 [17:13] if you do
L0490 [17:14] So, there's There's of things that you
L0491 [17:15] have to kind of think, uh,
L0492 [17:18] outside your tests and try and work out
L0493 [17:19] how to get them inside and that's that's
L0494 [17:23] you know, you've got to you've got to be
L0495 [17:24] thinking about these issues that your
L0496 [17:26] tests are not finding. And again, that's
L0497 [17:28] why just focusing on test coverage means
L0498 [17:31] you're not thinking about security
L0499 [17:32] enough.
L0500 [17:35] Um, to make things more testable,
L0501 [17:38] um,
```

## Section 6 -- Transcript segment 6 [L0502-L0601, 17:39-20:58]

```text
L0502 [17:39] you know, you've got to think about
L0503 [17:41] things that, you know, any kind of
L0504 [17:42] signal you can get out of the black box.
L0505 [17:44] Basically, you know, if there's a
L0506 [17:46] meowing noise, then you it's giving you
L0507 [17:48] information that you need to know.
L0508 [17:51] Um,
L0509 [17:53] increase the scope of what you can test.
L0510 [17:56] Like build more testable interfaces. Uh,
L0511 [17:59] one thing I kind of regret doing is not
L0512 [18:00] really building them out the management
L0513 [18:02] and reporting and back end interfaces
L0514 [18:04] because I could have run the tests on on
L0515 [18:06] those to understand what's going on
L0516 [18:08] better.
L0517 [18:09] Um, I was really focusing on the public
L0518 [18:11] API because that's the thing I was felt
L0519 [18:13] I was trying to replicate and not
L0520 [18:15] the internals. I have unit tests on
L0521 [18:17] them, but it's the APIs are kind of
L0522 [18:19] internal and structured and
L0523 [18:22] I don't necessarily know how much I
L0524 [18:24] trust them.
L0525 [18:25] Um,
L0526 [18:27] cuz I can't see them. I can only see
L0527 [18:29] them come through your testing and I
L0528 [18:30] can't like sit there and play with them.
L0529 [18:32] So, I kind of
L0530 [18:34] like the more you build out the better.
L0531 [18:37] Um, tracing and, um,
L0532 [18:40] and classic, you know, observability
L0533 [18:42] pieces,
L0534 [18:43] um,
L0535 [18:44] I just go with the like even a just
L0536 [18:47] getting the AI to build a
L0537 [18:49] a hand-built, hand-maintained
L0538 [18:51] tracing framework was incredibly useful.
L0539 [18:53] You don't need to
L0540 [18:55] tie it into production system or
L0541 [18:56] something, but anything that can give it
L0542 [18:58] traces that it can look at to debug is
L0543 [19:00] amazingly useful.
L0544 [19:02] Um,
L0545 [19:03] it
L0546 [19:05] In this [clears throat] case, it had a
L0547 [19:06] bunch of overheads, so when I used it
L0548 [19:08] for performance testing,
L0549 [19:11] it was a little bit misleading, but it
L0550 [19:13] told it you know, basically gave where
L0551 [19:15] the the big um
L0552 [19:17] the big performance gaps were.
L0553 [19:20] Um
L0554 [19:21] and it was incredibly useful for
L0555 [19:22] debugging because I could give it
L0556 [19:25] um I you know, I could run the test I
L0557 [19:28] could have my test suites running
L0558 [19:29] looking for race conditions or errors,
L0559 [19:31] give it trace and say
L0560 [19:34] this happened overnight in my overnight
L0561 [19:36] run. Uh we need to fix this and it would
L0562 [19:39] get it would lay it actually down on
L0563 [19:41] what the real problem was rather than
L0564 [19:43] trying to guess because if you
L0565 [19:45] if you give an AI a bug, but you don't
L0566 [19:49] know how to repro it and it's a very
L0567 [19:52] it's a rare condition
L0568 [19:54] it can waste a lot of time either try I
L0569 [19:56] mean it can either fail to reproduce it
L0570 [19:58] itself or it can guess what the solution
L0571 [20:00] might be and get it wrong or something.
L0572 [20:02] And if you can give it a
L0573 [20:03] >> [snorts]
L0574 [20:03] >> a trace um
L0575 [20:05] and some trace tooling and just get it
L0576 [20:08] to sit there and
L0577 [20:09] try and reproduce it and um itself and
L0578 [20:12] see if it's the same thing then it
L0579 [20:13] usually can and that works really well.
L0580 [20:16] So you don't need to necessarily all
L0581 [20:18] hook it up to a production environment.
L0582 [20:20] You can really do this
L0583 [20:22] just by build by getting the AI to build
L0584 [20:24] some tracing tools for you.
L0585 [20:27] Um
L0586 [20:28] performance testing I found the AI is
L0587 [20:29] very much like
L0588 [20:31] human people doing performance test
L0589 [20:33] performance uh improvements like
L0590 [20:36] you build something it wouldn't improve
L0591 [20:38] the performance or it'd make it worse
L0592 [20:39] cuz they would think this must be the
L0593 [20:41] way to fix this and it's not.
L0594 [20:44] Um and that's just the way of
L0595 [20:45] performance engineering to be honest and
L0596 [20:48] kind of lean into that. Um
L0597 [20:51] just remember this is cheap low cost
L0598 [20:53] work and you just throw it away if it
L0599 [20:54] doesn't work. Don't do it just cuz it
L0600 [20:56] seemed a good idea and keep it. It's
L0601 [20:58] like generally just
```

## Section 7 -- Transcript segment 7 [L0602-L0701, 21:00-24:23]

```text
L0602 [21:00] just say no throw that one away and
L0603 [21:02] start try something else.
L0604 [21:04] Um
L0605 [21:05] comparing performance against other
L0606 [21:07] systems was quite fun. I did
L0607 [21:09] I did some performance testing against
L0608 [21:12] one of the other S3 implementations
L0609 [21:15] and got the read performance to be the
L0610 [21:17] same and that was nice. And then it was
L0611 [21:19] like, why is our write performance
L0612 [21:20] really slow? And I spent a bunch of time
L0613 [21:22] thinking and said eventually said,
L0614 [21:25] they've got a comment in the code saying
L0615 [21:26] we haven't done we don't have sync when
L0616 [21:28] we actually write. And I was like, okay,
L0617 [21:30] well, if you don't have sync when you
L0618 [21:31] write, then of course it's going to be
L0619 [21:32] faster.
L0620 [21:33] So, I stopped wasting my time trying to
L0621 [21:35] actually make performance the same as
L0622 [21:37] something that's doing something we
L0623 [21:38] don't want to do. So,
L0624 [21:40] um
L0625 [21:42] um but
L0626 [21:44] um it's it's a good it's good to over
L0627 [21:46] that.
L0628 [21:48] um
L0629 [21:49] Other things, um I had a lot of issues
L0630 [21:52] early on with with how permission
L0631 [21:54] checking worked and um
L0632 [21:56] time of check time of use um
L0633 [21:59] testing permissions twice in different
L0634 [22:01] places.
L0635 [22:03] I tried tracing these um and you know,
L0636 [22:06] that fixing some issues, but ended up
L0637 [22:07] just telling it to fix it in the type
L0638 [22:10] system instead of actually trying to use
L0639 [22:12] tracing or anything to do this like
L0640 [22:14] have an authorized request type that
L0641 [22:16] can't be reauthorized. Um
L0642 [22:19] make make sure that all the things going
L0643 [22:21] into you know, at at this gate are all
L0644 [22:23] authorized. All these types of functions
L0645 [22:25] take authorized requests and then just
L0646 [22:28] force force everything through types and
L0647 [22:31] um
L0648 [22:32] that saves a lot of effort and you know,
L0649 [22:35] once you've once you've constructed it
L0650 [22:37] so you can't re you don't have to have a
L0651 [22:39] test for this anymore because you know
L0652 [22:40] that the the types
L0653 [22:43] are enforcing it for you and I spend a
L0654 [22:44] lot of time
L0655 [22:46] like looking at the interface types
L0656 [22:47] between modules and just seeing if they
L0657 [22:49] look sane.
L0658 [22:52] Security reviews, I used I I like code X
L0659 [22:56] security. I found a lot of issues. I
L0660 [22:59] what I do with them is I
L0661 [23:01] uh check the findings into the repo and
L0662 [23:03] ask the AI to review them. Um
L0663 [23:07] uh
L0664 [23:09] 3/4 [clears throat] of them are valid.
L0665 [23:10] Um they're not necessarily 100% security
L0666 [23:13] findings. Um
L0667 [23:15] and then I would every now and again
L0668 [23:17] I'll do review sessions for like how
L0669 [23:18] could we have avoided these? What tests
L0670 [23:20] should we have that would fix these? Um
L0671 [23:23] I found it really valuable cuz although
L0672 [23:25] I do a lot of AI code review at the time
L0673 [23:28] um and find a lot of issues and do a lot
L0674 [23:30] of review iteration, it still found
L0675 [23:32] things that had been missed that were
L0676 [23:34] actually important and really quite um
L0677 [23:37] you know, kind of kind of major things.
L0678 [23:39] So
L0679 [23:41] I've
L0680 [23:42] um
L0681 [23:43] I I I very I and so I've done more kinds
L0682 [23:46] of AI security review as well. I mean
L0683 [23:49] code security reviews pull requests,
L0684 [23:51] which is fine.
L0685 [23:52] Um
L0686 [23:54] but you also want to sit down and just
L0687 [23:56] review the state of the code as it is as
L0688 [23:58] a whole and look for issues and so on.
L0689 [24:01] >> [snorts]
L0690 [24:01] >> Um
L0691 [24:03] I found that you know, I found that has
L0692 [24:05] been very valuable. Um
L0693 [24:08] as I said, human in the loop
L0694 [24:10] I
L0695 [24:11] I view myself as part of the feedback
L0696 [24:13] loop. I have opinions and I'm here to
L0697 [24:16] find out what's going wrong.
L0698 [24:17] And um
L0699 [24:20] and
L0700 [24:21] you know, so I've been
L0701 [24:23] not trying to automate things too much
```

## Section 8 -- Transcript segment 8 [L0702-L0801, 24:25-28:06]

```text
L0702 [24:25] because I want to actually understand
L0703 [24:26] what's going wrong in order that I can
L0704 [24:29] because I've I'm I'm responsible for the
L0705 [24:31] quality and I care about the code and I
L0706 [24:34] want to know it's good.
L0707 [24:36] Um cuz that's the my kind of aim with
L0708 [24:39] this. So
L0709 [24:40] I I kind of view myself as part of that.
L0710 [24:44] Um
L0711 [24:46] So what do we learn? So a test article
L0712 [24:48] or model is really useful. Um
L0713 [24:51] and copying things that exist is
L0714 [24:53] actually
L0715 [24:54] a nice activity. Um that's long history
L0716 [24:58] of open source projects
L0717 [25:00] doing that. Um, the GNU project was
L0718 [25:02] there to replicate Unix and so on.
L0719 [25:05] Um, and you know, it's it's a great
L0720 [25:08] activity to do um, and it's it's kind of
L0721 [25:11] good fun and it works quite well.
L0722 [25:13] Um,
L0723 [25:14] this is my GitHub commit
L0724 [25:17] graph. As you can see,
L0725 [25:19] refactoring. Like
L0726 [25:21] you have to do a enormous amount of
L0727 [25:22] refactoring. The the ridiculous amount
L0728 [25:24] of week in the middle where I uh was
L0729 [25:27] 120,000 lines plus and 75,000 lines
L0730 [25:30] minus.
L0731 [25:31] Part of that was uh that was just a I
L0732 [25:33] had I basically had these refactoring
L0733 [25:35] weeks where there's another one near the
L0734 [25:36] beginning and I would just refactor
L0735 [25:38] stuff. There [snorts] was one 43,000
L0736 [25:40] line
L0737 [25:41] uh single file that had to be refactored
L0738 [25:44] at that point as well, which is kind of
L0739 [25:46] the ends got there, but like refactoring
L0740 [25:49] is part of the feedback loop. Um,
L0741 [25:52] don't I don't you don't feel you have to
L0742 [25:53] one shot things. Like you're converging
L0743 [25:56] on a better answer
L0744 [25:58] and [snorts] you're a better program and
L0745 [25:59] you've got, you know, time to do that
L0746 [26:01] and you need to sit there and think,
L0747 [26:04] "Well, yeah, we made some progress. We
L0748 [26:06] got some features done.
L0749 [26:08] Uh, but what you know, what could be
L0750 [26:10] better still?" And that feedback loop
L0751 [26:13] is, you know, it's the kind of outer
L0752 [26:15] harness of of your work and um,
L0753 [26:19] and you mustn't ignore that.
L0754 [26:23] Tests are really a discovery tools.
L0755 [26:25] They're not like it's not that there's
L0756 [26:26] an answer and that if you had the right
L0757 [26:28] set of tests, it's there.
L0758 [26:31] You kind of
L0759 [26:32] you need to expand the tests if you're
L0760 [26:34] uncertain and
L0761 [26:36] where you think where you're suspicious
L0762 [26:38] and you think there might be more
L0763 [26:39] errors, um, work out new things you can
L0764 [26:42] add tests to.
L0765 [26:44] Um,
L0766 [26:45] and you know, just kind of
L0767 [26:47] it's part of your kind of quality
L0768 [26:49] control thoughts about, you know, what's
L0769 [26:52] going on and like am I
L0770 [26:54] am I happy about this? Do I think this
L0771 [26:56] code is looking good?
L0772 [26:59] Um or do I am I worried? And if it's
L0773 [27:01] worried, you probably want to add more
L0774 [27:03] tests and
L0775 [27:05] um you know, kind of
L0776 [27:07] spend more time trying to trying to
L0777 [27:08] break things. Um because your role is to
L0778 [27:11] is to be there and break things and um
L0779 [27:13] get them fixed.
L0780 [27:15] Um
L0781 [27:17] I'm going to open source this code in a
L0782 [27:18] week or so when I've just finished the
L0783 [27:20] distributed systems bit. Again, when I'm
L0784 [27:22] happy with it. So, if you want to
L0785 [27:25] uh have a look, uh sign up and I'll send
L0786 [27:27] you a a mail when it's ready.
L0787 [27:29] Um
L0788 [27:30] and we got
L0789 [27:32] a couple of minutes for questions.
L0790 [27:35] >> [applause]
L0791 [27:41] >> Thank you, Justin. Any questions in the
L0792 [27:43] room, please put your hands up and I'll
L0793 [27:45] run over to you with the mic. Oh,
L0794 [27:46] there's a gentleman there as well. Any
L0795 [27:48] questions?
L0796 [27:53] One in the middle there.
L0797 [27:56] With the tables, it's a little bit
L0798 [27:57] trickier, huh?
L0799 [28:02] >> Hi. Um did you did you experiment with
L0800 [28:04] any uh
L0801 [28:06] formal verification or or testing tools
```

## Section 9 -- Closing segment [L0802-L0902, 28:09-31:52]

```text
L0802 [28:09] for the distributed system part?
L0803 [28:11] >> Um not yet because I'm quite I'm still
L0804 [28:14] working through it. I'm
L0805 [28:16] uh
L0806 [28:17] I want to next. I'm
L0807 [28:19] looking at basically I mean I um
L0808 [28:23] Yeah, I'm basically going to look at
L0809 [28:24] verification tools as soon as it's kind
L0810 [28:26] of fully implemented. I'm I'm like uh
L0811 [28:30] I have a sort of huge transition plan
L0812 [28:33] from the single host to the multi host
L0813 [28:35] and like all the bits of it being worked
L0814 [28:36] through and I'm hoping like next week
L0815 [28:39] it'll be runnable as fully distributed
L0816 [28:41] and um
L0817 [28:43] and so yeah, then I um yeah, I'm
L0818 [28:46] um yeah, I'm really interested in what I
L0819 [28:48] can do there because I think there's
L0820 [28:50] probably going to be some bugs.
L0821 [28:52] >> [laughter]
L0822 [28:53] >> Um, and I'm, you know, I've been kind of
L0823 [28:55] I've been looking at those tools um
L0824 [28:57] for quite a while and I'm I'm really
L0825 [28:58] interested in that space and um what you
L0826 [29:00] can what you can verify and what you can
L0827 [29:03] formally verify. I'm
L0828 [29:05] Formal verification is like something
L0829 [29:06] that um I'd love to do more of and it's
L0830 [29:09] kind of something that
L0831 [29:10] um
L0832 [29:11] there's mixed reports about how good AI
L0833 [29:14] is at it as well and I'm really
L0834 [29:16] fascinated in that area. So, yes.
L0835 [29:21] >> There's one at right at the back. I know
L0836 [29:22] one that yep.
L0837 [29:25] >> Hi. Um, thanks for that. Absolutely
L0838 [29:27] brilliant.
L0839 [29:28] Um
L0840 [29:29] quite you know, it's it's uncanny how
L0841 [29:32] similar to
L0842 [29:34] what I'm doing and
L0843 [29:37] I don't know how you will um
L0844 [29:38] you know, just think about this question
L0845 [29:39] but
L0846 [29:40] the challenge I had and I think you you
L0847 [29:44] are bound to have it with a test oracle
L0848 [29:47] um is
L0849 [29:48] as you know, the AI loves telling you
L0850 [29:51] that oh, that would be a tautology
L0851 [29:53] because um when you're building a system
L0852 [29:55] and you have a test oracle um the test
L0853 [29:57] oracle has to work on an entirely
L0854 [30:00] different way of doing the exact same
L0855 [30:02] thing with the system you're testing so
L0856 [30:04] that you're not just running
L0857 [30:06] the logic twice which would naturally
L0858 [30:10] produce the same output. So,
L0859 [30:13] the the the the the big difficulty I had
L0860 [30:15] was um implementing the system using the
L0861 [30:18] AI and then implementing the test oracle
L0862 [30:22] to follow an entirely different way of
L0863 [30:25] achieving the same outcome um so that
L0864 [30:28] you know, these two keep each other in
L0865 [30:31] check.
L0866 [30:32] So, this may be a you know, just maybe
L0867 [30:35] we're doing entirely different things
L0868 [30:36] but does that sound familiar? Did you
L0869 [30:39] think or did you have to fight that?
L0870 [30:42] >> Um but yeah, I mean I think it was
L0871 [30:45] slightly easier cuz S3 was so was so
L0872 [30:47] external and like just there and like
L0873 [30:51] I had some similar issues though with
L0874 [30:54] um
L0875 [30:55] with some of the model testing it set up
L0876 [30:57] where it was like what am I actually
L0877 [31:00] testing anything that's different from
L0878 [31:01] the code and I think that
L0879 [31:04] um
L0880 [31:05] Yeah, and I think that I said that I'd
L0881 [31:08] still build an article even if I was
L0882 [31:10] building a complex software, but I think
L0883 [31:11] I'd probably build it maybe outside the
L0884 [31:14] repo or something as a fixed like very
L0885 [31:17] dumb model of it that was um
L0886 [31:20] Uh um yeah, cuz I think you you can end
L0887 [31:22] up in the situation where you turn out
L0888 [31:24] you're not really testing anything at
L0889 [31:26] all that's not the same as the thing
L0890 [31:27] you're testing and you need to you need
L0891 [31:29] to have that sort of fixed guarantee
L0892 [31:32] that it's what you want
L0893 [31:35] um
L0894 [31:36] and um
L0895 [31:38] and yeah, it's it's it's definitely
L0896 [31:40] easier when you've got a external system
L0897 [31:42] you're copying or something that you can
L0898 [31:43] really nail down that that's true.
L0899 [31:49] >> Awesome, that's all the time we have for
L0900 [31:50] questions, but please give it up for
L0901 [31:51] Justin.
L0902 [31:52] >> [applause and music]
```

