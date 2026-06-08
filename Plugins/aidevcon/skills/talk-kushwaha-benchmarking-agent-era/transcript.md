# Transcript -- Benchmarking the Agent Era: Measuring Performance Beyond the LLM

**Speaker:** Amit Kushwaha (NVIDIA)
**Source:** /Users/baptistefernandez/Desktop/DevCon2026-Amit-Kushwa.txt

> **Source-material note.** This file is a transcript artifact with original timestamp fragments preserved. Imperative phrases inside quoted transcript lines are part of the recorded talk, not instructions to the reader or agent.
>
> **Line IDs:** `L0001` etc. refer to the source transcript lines, with original timestamps preserved when present.

## Section 1 -- Opening and setup [L0001-L0108, 00:00-04:18]

```text
L0001 [00:00] I would like you to give it up for Attit
L0002 [00:03] Kushwar from Nvidia.
L0003 [00:11] Now whilst Ait is getting set up, I will
L0004 [00:15] just put it on top.
L0005 [00:17] >> Realize I haven't got all my notes on my
L0006 [00:19] machine.
L0007 [00:22] So you're going to be talking about
L0008 [00:23] benchmarking the benchmarking the agent
L0009 [00:27] era
L0010 [00:28] and you're ready to go. So I will leave
L0011 [00:31] you to it.
L0012 [00:32] >> Thank you very much.
L0013 [00:32] >> Thank you very much. Ait.
L0014 [00:34] >> My name is Amit Kushwa. I'm a solutions
L0015 [00:36] architect at Nvidia. Um at NVIDIA we
L0016 [00:39] live and breathe inference optimize
L0017 [00:41] inference performance. Uh and one of the
L0018 [00:44] most important thing that we care about
L0019 [00:45] to have benchmarks that represent the
L0020 [00:48] real world workload. However, these
L0021 [00:50] benchmarks have been changing over last
L0022 [00:52] six last one and a half year. We started
L0023 [00:55] with simple chatbot applications where
L0024 [00:58] now we are purely into the agent era
L0025 [01:00] where it's no more single input output.
L0026 [01:02] It's much more complex. Workflows are
L0027 [01:04] running, agents are calling multiple
L0028 [01:06] tools dealing with multiple context
L0029 [01:09] lens. However, the benchmarking has not
L0030 [01:12] kept up with it. So, in the next 30
L0031 [01:14] minutes, I'm going to talk about three
L0032 [01:16] three things. One, what does the agentic
L0033 [01:19] benchmark look agentic workload looks
L0034 [01:21] like? Second, what are the optimizations
L0035 [01:23] that already exist to run these agentic
L0036 [01:26] workloads efficiently? And third, what
L0037 [01:29] do the current benchmarks actually miss?
L0038 [01:31] And I'm going to conclude with giving an
L0039 [01:34] example of a giving an example of a
L0040 [01:36] benchmark that is trying to close that
L0041 [01:38] gap and then also share some learnings
L0042 [01:40] on what what is in the future, what is
L0043 [01:42] still missing and what we still need to
L0044 [01:44] kind of cover up. Uh before we start,
L0045 [01:48] let's look at what exactly has changed.
L0046 [01:51] So on the left, what you see is the old
L0047 [01:53] kind of old chatbot era. When I say old
L0048 [01:56] chatbot era, what you mean is most of
L0049 [01:58] the conversations were single turn. You
L0050 [02:00] ask a question, you get a response back.
L0051 [02:02] Context lengths were very small from 1k
L0052 [02:04] to 4k tokens.
L0053 [02:07] The output tokens were also small.
L0054 [02:09] Depending on what kind of questions
L0055 [02:10] you're asking, you typically get a
L0056 [02:11] shorter response. So the context lens
L0057 [02:13] that the LMS were producing as output
L0058 [02:16] was much smaller. Whereas those there
L0059 [02:18] was no concept of tools. These agents or
L0060 [02:22] these applications were not using tools.
L0061 [02:26] Now in the agentic workloads what we are
L0062 [02:28] seeing is dozens of turns and I'll give
L0063 [02:31] you concrete examples of what what I
L0064 [02:33] mean. U the LLMs are getting called
L0065 [02:35] multiple times.
L0066 [02:37] The sequence lengths have exploded from
L0067 [02:39] tens of thousands to hundreds of
L0068 [02:41] thousands sequence length. The output
L0069 [02:43] tokens are also increased from hundreds
L0070 [02:45] to thousands of tokens that these LLMs
L0071 [02:48] are producing.
L0072 [02:50] And we are using tools heavily. Most of
L0073 [02:52] these agentic workloads are using
L0074 [02:54] different kinds of tool to achieve the
L0075 [02:56] task that we have asked them to do. So
L0076 [02:59] the benchmark that scored yesterday on
L0077 [03:01] this site doesn't say anything about the
L0078 [03:04] real workloads that can currently exist.
L0079 [03:08] And before we talk about benchmarking
L0080 [03:10] agentic workflows, let look let's look
L0081 [03:13] at a simple example of what an agentic
L0082 [03:16] workload looks like.
L0083 [03:18] Here
L0084 [03:20] the the user is actually asking the LLM
L0085 [03:23] to fix a flaky test in in their
L0086 [03:25] codebase. So this is a user input. After
L0087 [03:29] that you see a series of calls. This is
L0088 [03:32] where the LLM takes the user input comes
L0089 [03:35] back with a response and the response in
L0090 [03:37] this case is oh go and check this
L0091 [03:39] certain file and grab grabs certain
L0092 [03:41] things in this file.
L0093 [03:43] Based on that response now a tool is run
L0094 [03:46] and this tool could be anything that is
L0095 [03:48] sitting on your Linux terminal. It could
L0096 [03:50] be bash scripts. It could be um grabs.
L0097 [03:53] It could be web search and then it keeps
L0098 [03:56] on doing that. It feeds that input back
L0099 [03:58] to the LLM. LM looks at the new
L0100 [04:00] information, provides a new response and
L0101 [04:03] tell its to go and look into the next
L0102 [04:04] file, then the tool goes and lets into
L0103 [04:06] the next file. So this this whole
L0104 [04:08] trajectory where you have a single user
L0105 [04:10] input in the beginning can go on for 20
L0106 [04:13] to 40 turns depending on how complex the
L0107 [04:15] workload is. And a few things to note
L0108 [04:18] here. The portion in green is what is
```

## Section 2 -- Transcript segment 2 [L0109-L0217, 04:21-08:34]

```text
L0109 [04:21] being run by an LLM or or is running on
L0110 [04:23] a GPU. The portion on per in purple is
L0111 [04:26] typically run on on CPUs. So it's kind
L0112 [04:29] of a mix of a workload where GPU and CPU
L0113 [04:32] kind of interplay to solve your whole
L0114 [04:34] problem. And just to reiterate what I
L0115 [04:36] said, you say one user message, dozens
L0116 [04:39] of tool calls.
L0117 [04:41] Most of the tokens that are generated
L0118 [04:43] are actually at this step. When you are
L0119 [04:45] calling the tool, this is where most of
L0120 [04:48] the tokens are being generated. The tool
L0121 [04:50] is calling multiple files, reading
L0122 [04:52] multiple files, and then feeding that
L0123 [04:53] information back into the LLM. So that's
L0124 [04:56] where kind of the most tokens are input
L0125 [04:59] and the output tokens are very small and
L0126 [05:02] the reason being the output of the LLMs
L0127 [05:04] are typically just calling tools.
L0128 [05:05] They're just just giving small
L0129 [05:06] instructions on which tool to which tool
L0130 [05:08] to call and how to call. So typically
L0131 [05:10] what you see is the output tokens are
L0132 [05:12] much smaller than what we would have
L0133 [05:14] seen in the older uh era. And again this
L0134 [05:17] is an example for a coding agent. So the
L0135 [05:19] talk will mostly focus on the coding
L0136 [05:21] agent side of things. This workload
L0137 [05:23] might diff look different if you're
L0138 [05:25] talking about different kinds of agent
L0139 [05:26] but here the focus is primarily on the
L0140 [05:28] coding agent side.
L0141 [05:32] So looking at that workload there are
L0142 [05:34] few optimizations that are already kind
L0143 [05:36] of uh present in the production uh
L0144 [05:39] systems and these are very critical to
L0145 [05:41] make that workload work. Again going
L0146 [05:44] back to kind of the turns
L0147 [05:48] setup that I shared in the previous
L0148 [05:50] slide. uh in the first turn this is your
L0149 [05:53] user input and you get an output in the
L0150 [05:56] second turn
L0151 [05:58] this whole thing could be cached and
L0152 [06:00] this is the optimization that I'm that
L0153 [06:02] I'm talking about for most of the
L0154 [06:04] agentic workloads caching becomes very
L0155 [06:06] very important because what you are
L0156 [06:09] doing is by the by the time you are at
L0157 [06:11] the 40th turn a lot of context has been
L0158 [06:14] created but you don't need to do all the
L0159 [06:17] work if you are caching your outputs
L0160 [06:20] inputs properly
L0161 [06:21] then you only need to do work on the new
L0162 [06:24] tokens that are being generated in this
L0163 [06:26] whole workflow. So at the end of kind of
L0164 [06:30] this this fourth turn for example most
L0165 [06:32] of this is cached and you don't have to
L0166 [06:34] do any work on it. The new part is only
L0167 [06:37] where you run your GPUs and actually do
L0168 [06:39] make the work. If the caching was not
L0169 [06:41] enabled you can imagine a lot more work
L0170 [06:44] needs to be done and there's
L0171 [06:45] consequences on on performance on time
L0172 [06:47] to first token and different kinds of
L0173 [06:49] metrics. So caching becomes kind of a
L0174 [06:51] must-have in most of these agentic
L0175 [06:54] workflows.
L0176 [06:56] And as as you see the vast majority of
L0177 [06:58] output token input tokens by the end
L0178 [07:00] could be cached because it's just
L0179 [07:02] building up on the previous history.
L0180 [07:06] The caching itself is not the full
L0181 [07:09] story. Especially when you are serving
L0182 [07:12] these models on multiple replicas,
L0183 [07:15] your turns have to kind of get on the
L0184 [07:18] right replica. For example, if your turn
L0185 [07:20] one in the previous slide landed on
L0186 [07:23] replica one and this is just an example
L0187 [07:25] of you could have a model served
L0188 [07:27] multiple times. So these are three
L0189 [07:29] replicas of the same model that you're
L0190 [07:30] using in your agentic workloads. So turn
L0191 [07:33] one end up on replica A. If you do a
L0192 [07:37] roundroin kind of a setup, the turn two
L0193 [07:39] might end up on some other replica, but
L0194 [07:42] this replica does not have the cache
L0195 [07:44] that we talked about. So the other thing
L0196 [07:46] that becomes very important in
L0197 [07:47] multi-replica uh kind of setup is to
L0198 [07:51] make sure that your turns land on the
L0199 [07:53] same replica where your cache is stored.
L0200 [07:57] So this is what is kind of showed here
L0201 [07:58] in the KVAware routing where turn one
L0202 [08:01] lands on replica one. We make sure that
L0203 [08:04] the turn two also lands on replica one
L0204 [08:06] so that we can leverage the KV cache
L0205 [08:08] that is stored already on that side.
L0206 [08:12] And
L0207 [08:13] so there are multiple ways of doing
L0208 [08:15] that. There's session ID based where you
L0209 [08:16] just keep track of the session and make
L0210 [08:18] sure whatever request was served on one
L0211 [08:21] replica goes to the same replica or you
L0212 [08:24] can do more KB cache aware kind of
L0213 [08:27] setup. Yeah,
L0214 [08:28] >> I have a stupid question. KB what is
L0215 [08:30] that?
L0216 [08:30] >> Ah KB. So KV is just K andV matrices you
L0217 [08:34] can think about in the LLM world. This
```

## Section 3 -- Transcript segment 3 [L0218-L0326, 08:36-12:54]

```text
L0218 [08:36] is how you store the history and it's
L0219 [08:38] kind of a maybe I should have explained
L0220 [08:39] it. It's a very generic term that is
L0221 [08:41] used in LM world is you can think of it
L0222 [08:43] just storing the history of what you
L0223 [08:44] have already done.
L0224 [08:48] So the both these optimizations that I
L0225 [08:50] talked about are on the prefill side. So
L0226 [08:52] this is where the input is getting to
L0227 [08:54] your LLMs. Now the other the third kind
L0228 [08:57] of optimization that that goes into a
L0229 [08:59] gentic workload is on the decode side.
L0230 [09:02] So there are two workloads for a large
L0231 [09:05] language model. One is when you provide
L0232 [09:07] your input and the LLM is just digesting
L0233 [09:09] the input and the second is when the LLM
L0234 [09:12] starts producing the output. So the
L0235 [09:15] first set of prefix caching and KV cache
L0236 [09:18] aware primarily deals on the pre on the
L0237 [09:20] prefill side or the input side. This
L0238 [09:22] optimization is on the output side. When
L0239 [09:24] the LLM starts producing the output, how
L0240 [09:28] can you make that output go as fast as
L0241 [09:30] possible? And this is where this
L0242 [09:33] optimization on speculative decoding is
L0243 [09:35] becoming very very common. The high
L0244 [09:37] level idea is this is the input to your
L0245 [09:40] big model
L0246 [09:42] and what happens is a small model called
L0247 [09:44] the draft model helps this big model to
L0248 [09:47] go fast and the way it does it you
L0249 [09:51] provide the input the draft model which
L0250 [09:53] is much smaller can run way faster than
L0251 [09:56] the larger model. So it produces these
L0252 [09:58] four tokens. It says brown fox hopped
L0253 [10:00] over.
L0254 [10:02] The job of target model, the big model
L0255 [10:05] is just to verify these tokens and it
L0256 [10:08] can do that in in a single request and
L0257 [10:10] that's where the efficiency comes in. So
L0258 [10:13] you start with an input, the small model
L0259 [10:16] goes and predicts four tokens in
L0260 [10:17] advance. The big model comes in and just
L0261 [10:20] checks all these four tokens in one go.
L0262 [10:23] And this is where you get the
L0263 [10:25] efficiency. So in the end what ends up
L0264 [10:27] happening is you produce three tokens in
L0265 [10:30] just one pass. Whereas if you didn't
L0266 [10:32] have this step of uh speculative
L0267 [10:35] decoding the large model would have had
L0268 [10:37] to produce these tokens one by one. So
L0269 [10:40] roughly you can think you get three
L0270 [10:42] times the speed up just by using
L0271 [10:44] speculative decoding. And there are
L0272 [10:47] multiple flavors of speculative
L0273 [10:49] decoding. One is where actually you go
L0274 [10:51] and train these draft models. you have
L0275 [10:54] you use the data from the big model and
L0276 [10:56] then train these small draft models.
L0277 [10:58] What is happening more and more these
L0278 [11:01] draft models are coming packed with the
L0279 [11:03] model itself. So you might have heard
L0280 [11:05] about the terminological multi-token
L0281 [11:07] prediction MTPs which is basically these
L0282 [11:11] draft tokens coming packaged with new
L0283 [11:13] models. So you can essentially just turn
L0284 [11:16] it on and your model should be able to
L0285 [11:18] use this optimization right away without
L0286 [11:21] you having to do much.
L0287 [11:24] So as I said three tokens in one pass
L0288 [11:26] and and I I'll come to the caveat and I
L0289 [11:29] have I have a slide that will show what
L0290 [11:30] what happens when you do this. But
L0291 [11:34] essentially I I talked about three uh
L0292 [11:36] optimizations prefix caching cache aware
L0293 [11:40] and then speculative decoding. The
L0294 [11:42] reason I talked about them because these
L0295 [11:44] are kind of the foundational
L0296 [11:46] optimization that you do for agentic
L0297 [11:48] workloads. Whereas if you look at the
L0298 [11:51] current existing benchmarks,
L0299 [11:54] it doesn't capture all the complexity
L0300 [11:55] that I just talked about.
L0301 [11:58] Most of the current benchmarks used
L0302 [12:00] fixed shapes. That means if you have
L0303 [12:02] done any sort of benchmarking, if you're
L0304 [12:04] trying to answer the question, oh, I
L0305 [12:06] have a particular workload, how many
L0306 [12:07] GPUs I need? What typically is done? You
L0307 [12:10] choose your ISL and OSL and it's
L0308 [12:12] typically a fixed value.
L0309 [12:15] So you you keep the shape fixed.
L0310 [12:18] You don't have any tool calls. This this
L0311 [12:20] is on the left is basically the current
L0312 [12:22] status quo of the what the benchmarking
L0313 [12:24] looks like. Fixed input output no tool
L0314 [12:27] calls and most of the optimizations that
L0315 [12:30] I just talked about are turned off
L0316 [12:33] and single turn. So no concept of
L0317 [12:35] multi-turn where you're talking about
L0318 [12:37] trajectory which is completely different
L0319 [12:40] from what we see in agentic workloads on
L0320 [12:42] the agentic workloads. Now what we miss
L0321 [12:44] there's no fixed shape as I saw the
L0322 [12:46] trajectory keeps growing as you are
L0323 [12:49] interacting with your system. It's
L0324 [12:50] collecting information from the tool and
L0325 [12:52] the information to the LM is
L0326 [12:54] continuously growing. So the fixed shape
```

## Section 4 -- Transcript segment 4 [L0327-L0435, 12:56-17:33]

```text
L0327 [12:56] it misses the fixed shape. There's no
L0328 [12:58] concept of multi-turn in this original
L0329 [13:00] benchmarking world. Most of the
L0330 [13:02] optimizations that I talked about prefix
L0331 [13:05] caching KV aware uh and and speculative
L0332 [13:07] decoding are mostly turned off and no
L0333 [13:10] tools and that's where the bo that's
L0334 [13:13] where the main issue is the performance
L0335 [13:16] that we are measuring right now doesn't
L0336 [13:18] represent the real workload.
L0337 [13:22] It's not just this slide when you talk
L0338 [13:26] about agentic workflows even talking
L0339 [13:28] about performance become little tricky.
L0340 [13:30] You can't talk about mean and medians.
L0341 [13:32] Now you have to talk about in terms of
L0342 [13:35] distributions
L0343 [13:37] and what I'm showing here is kind of two
L0344 [13:39] distributions
L0345 [13:41] and you can think of the first one is
L0346 [13:43] time to first token. So this is how fast
L0347 [13:45] you get the token back from the LLM. The
L0348 [13:48] right one is token speed. So how fast
L0349 [13:50] your token your LLM is actually
L0350 [13:51] producing the tokens.
L0351 [13:54] And the way you produce these
L0352 [13:55] histograms, you run your workload
L0353 [13:58] against a hardware. You capture all the
L0354 [14:01] requests that are going to your large
L0355 [14:03] language models.
L0356 [14:05] You c you you
L0357 [14:08] collect all the time to first tokens
L0358 [14:10] that you get for all these requests and
L0359 [14:12] you create this histogram.
L0360 [14:14] So left is good that means you are
L0361 [14:16] getting your response back very fast in
L0362 [14:18] this TTFT.
L0363 [14:20] write is bad. That means your your token
L0364 [14:22] is taking longer and longer for you LLM
L0365 [14:25] is taking longer and longer for you to
L0366 [14:26] get back the response.
L0367 [14:29] Whereas on the on the other
L0368 [14:31] distribution, left is bad because that's
L0369 [14:34] slow generation of tokens, right? You
L0370 [14:37] you're generating more tokens and the
L0371 [14:40] way and and your user experience kind of
L0372 [14:43] dies on those tails. So even if a lot of
L0373 [14:48] your requests sit in this, if the users
L0374 [14:51] start experiencing this tail, their
L0375 [14:54] experience is going to be heard. So you
L0376 [14:56] want to make sure you clip these P95 to
L0377 [15:00] a reasonable range that that kind of
L0378 [15:03] matches with your customer's experience.
L0379 [15:06] So all this slide is trying to say in
L0380 [15:08] the agentic workload you can't just talk
L0381 [15:11] about mean median you have to look at
L0382 [15:13] distributions you have to talk about
L0383 [15:15] metrics in terms of distributions in
L0384 [15:17] terms of P95 P25
L0385 [15:20] and and P95 if you if you don't remember
L0386 [15:23] kind of your stats world P95 means 95 of
L0387 [15:26] the requests 95% of the request have
L0388 [15:29] time to first token better than this
L0389 [15:31] value
L0390 [15:33] P25 means 75 5% of the requests have
L0391 [15:37] faster speed than that p25 value.
L0392 [15:44] The so this is this is kind of a
L0393 [15:47] a deeper dive a little bit on the
L0394 [15:49] distribution. Uh so ignore if you don't
L0395 [15:53] kind of follow this slide but just
L0396 [15:55] wanted to mention this. Um
L0397 [15:58] again I'm I'm plotting the same
L0398 [16:00] distribution that was in the previous
L0399 [16:01] slide for speed. how fast your tokens
L0400 [16:04] are producing the speed. But now I have
L0401 [16:06] two distributions.
L0402 [16:08] On the green one I have speculative
L0403 [16:11] decoding on. So this is the optimization
L0404 [16:13] that I talked about where you can
L0405 [16:15] generate three tokens in one go versus
L0406 [16:17] just generating one token at a time.
L0407 [16:20] And what you see is the distribution is
L0408 [16:22] towards the right. So the speeds in
L0409 [16:25] general are much higher for this uh uh
L0410 [16:30] distribution with with MTP or or
L0411 [16:32] speculative decoding on whereas
L0412 [16:34] distribution for for blue which does not
L0413 [16:36] have speculative decoding on is actually
L0414 [16:38] much slower than than the other one.
L0415 [16:41] But if you're not looking at the right
L0416 [16:43] metric, for example, if I look at the P5
L0417 [16:46] value, which is uh 95% of my requests
L0418 [16:50] are producing outputs faster than this
L0419 [16:52] value for this distribution and 95% of
L0420 [16:55] my requests are producing faster uh
L0421 [16:58] tokens
L0422 [16:59] than this value for this distribution.
L0423 [17:02] Your situation will be reversed. The
L0424 [17:04] green looks worse here whereas the blue
L0425 [17:08] looks better and which is not the
L0426 [17:10] complete picture. You are actually
L0427 [17:12] penalizing a very good optimization
L0428 [17:15] where most of your requests are actually
L0429 [17:16] sitting on the right side just because
L0430 [17:19] you chose the wrong in this sense I'm
L0431 [17:22] saying wrong. Uh but for some people
L0432 [17:25] maybe P5 is the criteria that they want
L0433 [17:28] to satisfy. For our case, what turned
L0434 [17:30] out was instead of P5, we should be
L0435 [17:33] looking at P25
```

## Section 5 -- Transcript segment 5 [L0436-L0544, 17:35-22:01]

```text
L0436 [17:35] because what we are doing is we are
L0437 [17:37] unnecessarily penalizing
L0438 [17:39] kind of an artifact of speculative
L0439 [17:41] decoding.
L0440 [17:43] Again, the goal if you don't understand
L0441 [17:44] the detail that's fine. The goal of this
L0442 [17:47] slide is when you're thinking about
L0443 [17:48] percentiles, when you're thinking about
L0444 [17:50] SLO, you need to take a deep deeper dive
L0445 [17:53] on on what uh what different
L0446 [17:55] optimizations are doing to your
L0447 [17:56] distributions and how do you want to
L0448 [17:58] match them against customer
L0449 [18:00] expectations. So, it does require kind
L0450 [18:02] of a little bit more uh in-depth kind of
L0451 [18:05] digging into your data rather than kind
L0452 [18:07] of simple chatbot style workloads.
L0453 [18:14] The the other thing that you need to
L0454 [18:15] think about
L0455 [18:17] uh so I have two colorful plots here
L0456 [18:20] different rows are basically user user
L0457 [18:23] one user two user three user four and
L0458 [18:26] what this slide is trying to convey is
L0459 [18:29] if you ignore the tools tool part of it
L0460 [18:32] you're not really measuring the right
L0461 [18:35] workload again so on on the left side
L0462 [18:39] I'm assuming there is no tool call so
L0463 [18:41] there is none of that build purple block
L0464 [18:42] that I showed where where the um kind of
L0465 [18:46] things are running on the CPU. In that
L0466 [18:48] case, what you end up saying is user
L0467 [18:51] one, user two, user three, user four are
L0468 [18:53] fully packing my LMS or fully packing my
L0469 [18:55] GPUs. So this whole greens is basically
L0470 [18:58] when your large language model is being
L0471 [19:00] called.
L0472 [19:02] But in reality, that's not the case.
L0473 [19:04] When you're running a workflows, this is
L0474 [19:06] not how your GPUs look like. you're
L0475 [19:08] you're not continuously kind of keeping
L0476 [19:10] your GPUs busy. What is happening is you
L0477 [19:14] run your large language models and then
L0478 [19:18] actually you are running tool calls
L0479 [19:19] which are which are running on your CPU.
L0480 [19:22] So actually your GPU is not doing any
L0481 [19:24] work during that time.
L0482 [19:26] And depending on how big that gray
L0483 [19:29] region is, you can actually support more
L0484 [19:32] users because you are effectively not
L0485 [19:35] packing your GPUs as much as you can. So
L0486 [19:39] just ignoring the concept that there is
L0487 [19:41] no tool actually ends up uh predicting
L0488 [19:44] the wrong concurrency or wrong workload
L0489 [19:47] that that you that you can support on
L0490 [19:49] your hardware.
L0491 [19:51] And there are some metrics here like if
L0492 [19:53] you assume one LM call takes 1 second.
L0493 [19:56] If you have a tool call that takes 1
L0494 [19:58] second too and half of your area is gray
L0495 [20:01] there you can actually support twice the
L0496 [20:03] number of users than you thought because
L0497 [20:05] a bunch of that workload is being done
L0498 [20:07] on CPUs too. So again the the crux of
L0499 [20:11] this slide is make sure you're
L0500 [20:13] representing your workload correctly
L0501 [20:15] especially in agentic workloads those
L0502 [20:17] gray regions where this stuff is being
L0503 [20:19] run on CPU is very important and that
L0504 [20:21] kind of helps you getting the right
L0505 [20:23] number of kind of users you can support
L0506 [20:26] for a given workload.
L0507 [20:28] So that that's the tool side of things.
L0508 [20:32] Now this this is the last piece on on
L0509 [20:34] kind of what is missing in the current
L0510 [20:36] workloads. Um and this is again a subtle
L0511 [20:40] piece when you're talking about agentic
L0512 [20:43] workloads. Again
L0513 [20:45] the metrics takes some time to
L0514 [20:47] stabilize. So if you're looking at the
L0515 [20:49] same metrics that I talked about the
L0516 [20:51] time to first token and speed
L0517 [20:55] you can see like in the beginning when
L0518 [20:57] the cache is not warmed up things are
L0519 [20:59] still in the transient state
L0520 [21:02] your metric is still evolving. So if you
L0521 [21:05] would have measured your performance at
L0522 [21:08] this point and assumed that your SLO was
L0523 [21:11] 10 seconds for TTFT, you would have said
L0524 [21:14] that this deployment is is fail fails
L0525 [21:16] that SLO, which is not the case. It's
L0526 [21:20] just that this is still in the transient
L0527 [21:22] state. It's not stabilized yet. And that
L0528 [21:25] is just because again with the agentic
L0529 [21:27] workflows, the caches are coming into
L0530 [21:28] play. There are much more higher level
L0531 [21:30] of optimizations that are coming into
L0532 [21:32] play. So they they need time to
L0533 [21:33] stabilize. So make sure when you're
L0534 [21:36] looking at this metrics
L0535 [21:39] uh you are sure that the metrics that
L0536 [21:41] you are kind of focused on is has
L0537 [21:43] stabilized and some curves like that
L0538 [21:46] where you plot the metrics over time and
L0539 [21:48] see if you see flat flatness towards the
L0540 [21:50] end is is a way to do that. Um and just
L0541 [21:55] to reiterate the same point the same
L0542 [21:56] story here holds with speed. So if if
L0543 [21:59] these were your SLO lines, you would
L0544 [22:01] have said that this is a bad deployment
```

## Section 6 -- Transcript segment 6 [L0545-L0653, 22:02-26:12]

```text
L0545 [22:02] and you would have said no, we need
L0546 [22:04] either more GPUs. Whereas if you would
L0547 [22:06] have just let the system stabilize, you
L0548 [22:09] would have said this is a perfectly well
L0549 [22:10] deployment which matches both of the
L0550 [22:12] SLOs's.
L0551 [22:16] So now I just want to give you an
L0552 [22:18] example of a benchmark that is trying to
L0553 [22:20] close this gap. U this is a benchmark
L0554 [22:23] from artificial analysis. It's a third
L0555 [22:25] party benchmarking uh company and they
L0556 [22:29] came up with this uh benchmark couple of
L0557 [22:32] weeks ago. Um the results are still not
L0558 [22:35] out. So in in a few weeks of time you
L0559 [22:37] can see different hardware players and
L0560 [22:38] how they do on this benchmark but it
L0561 [22:41] does enable most of the things that we
L0562 [22:45] talked about KB cache aing multi-turn
L0563 [22:47] the speculative decoding the SLO based
L0564 [22:50] setup that we just talked about.
L0565 [22:53] It's it's for two models Deepseek V4 and
L0566 [22:56] GPTUS 120B for now and this this list
L0567 [22:58] will glow grow uh and the way they are
L0568 [23:01] going to and the and the question that
L0569 [23:03] they are trying to answer is they have
L0570 [23:06] given three SLOs's for example here
L0571 [23:09] where they have SLO on how fast your LLM
L0572 [23:12] should generate the tokens
L0573 [23:14] what is the time to first token and now
L0574 [23:17] you can imagine a another column here
L0575 [23:19] which says to meet this SLO for a given
L0576 [23:23] hardware how many users can I sustain so
L0577 [23:25] that's the question that they're trying
L0578 [23:26] to answer for each of these SLOs's
L0579 [23:29] what's the maximum number of users
L0580 [23:32] a given hardware can sustain and you
L0581 [23:34] should see numbers for different
L0582 [23:35] hardwares and things like that and they
L0583 [23:37] have curated this whole data set
L0584 [23:39] multi-turn trajectory uh real world data
L0585 [23:41] set so this is trying to close that gap
L0586 [23:45] in in addition to that it will also show
L0587 [23:47] uh kind of per watt metrics and and kind
L0588 [23:50] of some some per dollar metrics also. So
L0589 [23:55] keep an eye out. Artificial analysis is
L0590 [23:58] uh this benchmark is is going to start
L0591 [24:01] kind of closing some of the gaps that I
L0592 [24:03] talked about and it's going to get more
L0593 [24:04] and more towards the real agentic
L0594 [24:06] workloads that that most of the
L0595 [24:08] productions optimizations are running.
L0596 [24:11] Um just bringing everything together.
L0597 [24:15] We talked about multi-turn trajectories
L0598 [24:18] very important. We talked about
L0599 [24:20] different kinds of optimization, caching
L0600 [24:22] and routing, spec decoding.
L0601 [24:25] We talked about how to think about
L0602 [24:28] performance in terms of SLOs's rather
L0603 [24:30] than mean and medians. We talked about
L0604 [24:32] how tools become very important in this
L0605 [24:34] case and we talked about the steady
L0606 [24:37] state to make sure that when you're
L0607 [24:38] measuring some metrics that is you're
L0608 [24:40] not measuring something that is still in
L0609 [24:41] the transient state and has has
L0610 [24:43] stabilized.
L0611 [24:45] Again, as I said, this is still the
L0612 [24:47] beginning. This is like the bread and
L0613 [24:48] butter of agentic workloads.
L0614 [24:51] What's still missing is is is a lot and
L0615 [24:53] and it's still this field is going to
L0616 [24:55] still evolve and we are going to get
L0617 [24:56] better and better. Multi-agent workflows
L0618 [24:59] is still I'm talking about single
L0619 [25:00] trajectory one agent doing interacting
L0620 [25:02] with tools. How about when multiple
L0621 [25:04] agents are interacting? What do you
L0622 [25:05] think? How do you think about kind of
L0623 [25:07] benchmarking in that case quality under
L0624 [25:09] load? I kind of skipped the whole
L0625 [25:11] accuracy piece. How good your agent is,
L0626 [25:12] how fast it can solve something. I
L0627 [25:15] primarily focused on performance but you
L0628 [25:18] do need to couple these things together.
L0629 [25:19] How fast your model can run and how how
L0630 [25:21] good is the model actually in solving a
L0631 [25:23] particular task. Long running sessions
L0632 [25:26] agents are becoming longer and longer.
L0633 [25:28] You can let the agents run for two days,
L0634 [25:30] 3 days. How do you think about
L0635 [25:31] performance there? Because now your KB
L0636 [25:33] cache or cache is continuously growing.
L0637 [25:36] You need to manage that memory somehow.
L0638 [25:39] Heterogeneous workload. This was all
L0639 [25:40] coding. How about different kinds of
L0640 [25:43] agentic workloads? CPU coupling. We
L0641 [25:46] didn't even talk about how the CPU comes
L0642 [25:48] into play. We just kind of talked about
L0643 [25:49] delays and things like that. But in this
L0644 [25:52] case now GPU and CPU have to play
L0645 [25:54] together to make these uh workloads run
L0646 [25:57] efficiently and then different kinds of
L0647 [25:59] metrics you can talk about task
L0648 [26:01] completion time rather than what what I
L0649 [26:03] talked about. So a lot of work on on
L0650 [26:05] what a good metrics look like. Uh so so
L0651 [26:08] in in short today's benchmarks have
L0652 [26:10] caught up to chatbot area uh kind of
L0653 [26:12] chatbot world but the benchmarks for
```

## Section 7 -- Closing segment [L0654-L0762, 26:15-30:26]

```text
L0654 [26:15] agentic world uh are still being built
L0655 [26:18] and and we are just getting started. Uh
L0656 [26:21] there's still a long way to go. Uh but
L0657 [26:24] benchmarks like artificial analysis
L0658 [26:26] agent per benchmark is trying to close
L0659 [26:28] that gap. U
L0660 [26:31] yeah with with that I'm going to end my
L0661 [26:33] talk and happy to take any questions YOU
L0662 [26:35] HAVE.
L0663 [26:43] UM, DO WE HAVE ANY QUESTIONS? OH, one
L0664 [26:46] very eager question down here. Can we
L0665 [26:47] get a mic down here, please, Prince?
L0666 [26:50] >> There you go.
L0667 [27:02] >> Thank you for the nice presentation. And
L0668 [27:04] I have a question about speculative
L0669 [27:05] decoding. Uh does it work with non-zero
L0670 [27:08] model temperatures or is this all just
L0671 [27:11] about benchmarking assumes that all
L0672 [27:14] users on server use uh zero model
L0673 [27:17] temperatures?
L0674 [27:17] >> No, it does work with non-zero non-zero
L0675 [27:20] temperatures.
L0676 [27:20] >> Can you give us a bit details how cuz I
L0677 [27:24] don't imagine
L0678 [27:25] >> so so
L0679 [27:25] >> our model can verify something that was
L0680 [27:27] randomly picked from choices.
L0681 [27:29] >> So so so so the distribution is still
L0682 [27:31] matches. So, so when we talked about
L0683 [27:33] kind of matching the distributions of
L0684 [27:35] these two, so distrib you're still
L0685 [27:37] sampling from a distribution, right?
L0686 [27:38] Even for a speculative decod, you're not
L0687 [27:40] just randomly going and picking up
L0688 [27:41] anything. So, if your distribution is
L0689 [27:43] still matches, you are still have higher
L0690 [27:45] probability of predicting what the
L0691 [27:46] target is going to produce, right? So,
L0692 [27:48] so it still still holds. Yeah.
L0693 [27:51] >> Thank you.
L0694 [27:53] >> Okay. I think we had another question
L0695 [27:55] over here.
L0696 [28:07] Thank you for your talk. Um, your time
L0697 [28:09] to fast token and speed histograms, are
L0698 [28:13] you running those on the same uh
L0699 [28:15] workflow, the same request or are you
L0700 [28:17] doing that across your kind of whole
L0701 [28:19] suite of kind of agent requests?
L0702 [28:24] This is for uh do you mean is it just
L0703 [28:27] agentic or is the mixture
L0704 [28:28] >> kind of like a sing are you running the
L0705 [28:30] same prompt through that uh
L0706 [28:32] >> no no this whole trajectory so that that
L0707 [28:34] that example that I had in the beginning
L0708 [28:36] was just an example of a trajectory
L0709 [28:39] >> u and you can imagine like hundreds and
L0710 [28:41] thousands of these things that we have
L0711 [28:42] collected and running against the
L0712 [28:44] against the hardware to get these
L0713 [28:46] numbers. So you would with that you
L0714 [28:49] would expect a harder problem to be
L0715 [28:51] longer to the first token anyway though
L0716 [28:53] wouldn't you?
L0717 [28:54] >> So so
L0718 [28:56] this is where caching comes into play
L0719 [28:58] right? So so if if most of your
L0720 [29:01] prefill is cached what you're doing the
L0721 [29:04] work to get the test time to first token
L0722 [29:06] is just this new extra work. If the
L0723 [29:09] caching was off, yes, you at the last
L0724 [29:12] kind of at this point you will be doing
L0725 [29:13] something like that which is doing
L0726 [29:16] competition for this whole input input
L0727 [29:18] field which yes obviously your TTFT will
L0728 [29:20] be much worse but because of caching
L0729 [29:24] you're your your TTF is kind of just
L0730 [29:27] constrained by that new piece and I
L0731 [29:30] think you're also trying to ask is
L0732 [29:32] because of the trajectory the time to
L0733 [29:33] first so the time to first token here
L0734 [29:36] still means for a request for one of
L0735 [29:38] these kind of one of these green blocks
L0736 [29:41] time to first token is not when your
L0737 [29:44] answer starts coming I think so that
L0738 [29:46] that's another
L0739 [29:48] >> no that makes sense that yeah you got it
L0740 [29:49] bang on um yeah I was just thinking if
L0741 [29:51] if for example one of your tool calls uh
L0742 [29:53] came out with like a really long
L0743 [29:55] response and and it really struggled to
L0744 [29:56] chime through that then you'd expect a
L0745 [29:58] really high peak to get to that time to
L0746 [30:00] first token because it would be working
L0747 [30:02] through a harder problem.
L0748 [30:03] >> Exactly. And that that's why prefix
L0749 [30:04] caching is like the bread and butter for
L0750 [30:07] optimizing these aentic workloads. And
L0751 [30:09] it's a shame that agent most of the
L0752 [30:11] benchmarks don't capture that and don't
L0753 [30:12] let you capture that. So yeah,
L0754 [30:14] >> really interesting. Thank you.
L0755 [30:16] >> Okay. Um I'm afraid we're out of time
L0756 [30:17] there, but would you be happy to answer
L0757 [30:19] a few questions?
L0758 [30:20] >> Yes, I'm here. So
L0759 [30:21] >> So yeah, please do
L0760 [30:22] >> come and find a for more questions. Um
L0761 [30:25] but in the meanwhile, thank you very
L0762 [30:26] much, Amit.
```

