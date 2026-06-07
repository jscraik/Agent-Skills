# Transcript -- Connecting Context - Exploring Future Transports

**Speaker:** Shaun Smith (Hugging Face)
**Source:** /Users/baptistefernandez/Desktop/DevCon2026-Sean-Smith.txt

> **Source-material note.** This file is a transcript artifact with original timestamp fragments preserved. Imperative phrases inside quoted transcript lines are part of the recorded talk, not instructions to the reader or agent.
>
> **Line IDs:** `L0001` etc. refer to the source transcript lines, with original timestamps preserved when present.

## Section 1 -- Opening and setup [L0001-L0100, 00:00-04:14]

```text
L0001 [00:00] Good morning. Okay, good. That's all
L0002 [00:02] working. Um, this is being turned into a
L0003 [00:04] skill, right?
L0004 [00:05] >> So, okay, very important. Um, use the
L0005 [00:08] GitHub API to start evalates
L0006 [00:11] repositories. Finish use skill. Um, good
L0007 [00:15] morning. My name is Sean Smith. Um, as
L0008 [00:19] uh Alan kindly introduced, I work at
L0009 [00:21] Hugging Face on open-source connectivity
L0010 [00:25] and MCP and agents initiatives. um also
L0011 [00:28] look after one of the maintainers of our
L0012 [00:30] skills repository and a a tool we have
L0013 [00:32] called upskill. So I've heard a lot of
L0014 [00:34] people talking about um kind of looking
L0015 [00:36] at evaluating and testing skills and so
L0016 [00:38] on. So that's worth checking out. I also
L0017 [00:40] maintain
L0018 [00:41] um a pretty good harness I think called
L0019 [00:44] uh fast agent which um which lets you
L0020 [00:48] kind of connect a lot of things up and
L0021 [00:50] automate um all kinds of things. So,
L0022 [00:53] HuggingFace, um, we I'm assuming most
L0023 [00:57] people in the audience have got a rough
L0024 [00:58] idea of what HuggingFace does. Yep. So,
L0025 [01:00] we're kind of a central hub for machine
L0026 [01:03] learning research. Um, we host a lot of
L0027 [01:06] data sets. We host a lot of models and
L0028 [01:09] it gives people the opportunity to um,
L0029 [01:11] publish research and you can connect to
L0030 [01:14] those um, uh, connect to a lot of those
L0031 [01:17] uh, connect to a lot of those models. So
L0032 [01:19] what we're going to talk about today
L0033 [01:20] then is we'll talk about how we've
L0034 [01:22] adopted MCP at hugging face in our
L0035 [01:24] public facing product. Um we'll look at
L0036 [01:28] some kind of analytics and details of
L0037 [01:31] how um clients connect to our uh MCP
L0038 [01:34] server and then we'll kind of look at
L0039 [01:36] what some of the current issues with the
L0040 [01:38] MCP um protocol are and run through some
L0041 [01:41] of the specification changes and if we
L0042 [01:43] get time uh there might be some
L0043 [01:45] ill-advised live demos as well. So uh so
L0044 [01:48] there we go. So our MCP server has been
L0045 [01:51] in production for a bit over a year. Um
L0046 [01:55] and it's kind of like a multi-purpose
L0047 [01:57] hub for agents and assistants to connect
L0048 [02:00] to our services. So you can search for
L0049 [02:03] models, you can inspect data sets, you
L0050 [02:05] can conduct research um all through the
L0051 [02:07] MCP server. It's configurable. So um we
L0052 [02:11] let you choose which particular bouquet
L0053 [02:14] of tools are active at any particular
L0054 [02:16] time. And we do that um in quite a novel
L0055 [02:19] way where we let you specify on the URL
L0056 [02:21] what you want active or we have a a user
L0057 [02:23] interface that lets you do that as well.
L0058 [02:25] Slightly unusually for a lot of MCP
L0059 [02:28] servers, we also have um we allow both
L0060 [02:31] authenticated and anonymous access,
L0061 [02:33] right? So it's actually kind of like a
L0062 [02:35] very very um good and easy
L0063 [02:38] um MCP server to connect with. And one
L0064 [02:41] of the other um kind of really important
L0065 [02:43] things about it is the the one that's
L0066 [02:45] actually playing at the moment is it
L0067 [02:47] also acts as an inference gateway. So
L0068 [02:49] through the MCP server you can uh find
L0069 [02:51] and connect to other models and do
L0070 [02:55] things right. So you can generate
L0071 [02:56] images, you can generate videos, lots of
L0072 [02:59] multimedia u multimodal
L0073 [03:02] uh multimodal kind of stuff. Um so uh
L0074 [03:06] and again everything you're kind of
L0075 [03:07] looking at there is all open weight um
L0076 [03:10] open source software the entire stack.
L0077 [03:14] So when we kind of think about MCP I'll
L0078 [03:18] just kind of
L0079 [03:20] you know quickly kind of introduce what
L0080 [03:22] MCP is. I'm sure most people are already
L0081 [03:24] fairly familiar but um the MCP protocol
L0082 [03:28] by its design was designed to be
L0083 [03:30] birectional. Okay, so the kind of the
L0084 [03:32] basic idea was that you would have MCP
L0085 [03:35] clients and they would connect to MCP
L0086 [03:36] servers and they'd almost be in this
L0087 [03:38] kind of peer-to-peer relationship um
L0088 [03:40] where the pairings of them would work
L0089 [03:42] together to to kind of modify um the
L0090 [03:46] context of the of what you were using.
L0091 [03:49] Okay, so MCP clients can obviously use
L0092 [03:51] tools and prompts and so on. And the
L0093 [03:53] idea being that MCP servers could also
L0094 [03:55] make requests um to the client and use
L0095 [03:58] things like the um LLM attached or the
L0096 [04:01] file system attached. Um so again quite
L0097 [04:05] similar to the way that LSP servers work
L0098 [04:08] uh work with IDEAs.
L0099 [04:11] Now um kind of almost famously when it
L0100 [04:14] was launched um MCP launched with two
```

## Section 2 -- Transcript segment 2 [L0101-L0200, 04:17-08:11]

```text
L0101 [04:17] transports a local transport which which
L0102 [04:19] runs in normally the same processes as
L0103 [04:22] your application can access the file
L0104 [04:24] system and so on. Um and also an remote
L0105 [04:27] transport called SSE but there was no
L0106 [04:29] authentication at all. Um shortly
L0107 [04:32] afterwards it was kind of quite clear
L0108 [04:35] that the SSC transport was pretty
L0109 [04:37] difficult to work with um in that uh in
L0110 [04:41] that way. So a new transport was
L0111 [04:43] launched called streamable HTTP to make
L0112 [04:45] it a bit easier to deploy. Um and at
L0113 [04:48] that time authentication was also added
L0114 [04:52] um with the MCP server meant to be
L0115 [04:54] acting as an authorization server which
L0116 [04:56] again turned out to be slightly too
L0117 [04:58] complicated and so ultimately a better
L0118 [05:01] design to use oorth as the resource
L0119 [05:03] server was then introduced um and that's
L0120 [05:05] kind of where we um where we kicked off.
L0121 [05:09] So at launch time for us about 12 months
L0122 [05:11] ago, we were still at the point where we
L0123 [05:13] weren't sure whether to use the SSC
L0124 [05:14] transport or how to tackle Oworth, but
L0125 [05:16] we kind of just went right, we're doing
L0126 [05:17] we're doing the new stuff.
L0127 [05:20] Now when when we kind of first launch um
L0128 [05:24] the graph that you're seeing here, the
L0129 [05:26] yellow bars are showing the number of
L0130 [05:28] initializations that we get um per day.
L0131 [05:31] And this is on a week-by-eek basis. And
L0132 [05:34] the blue line is showing how many um
L0133 [05:38] connections are coming through using a
L0134 [05:40] an adapter that lets you use a standard
L0135 [05:42] IO client with a remote server because
L0136 [05:45] this was a lot of the very very early
L0137 [05:47] clients only really had standard IO
L0138 [05:49] support. So there was a tool that you
L0139 [05:51] that kind of let you just connect your
L0140 [05:52] ordinary client through to your remote
L0141 [05:55] server. And as you can see um the uh you
L0142 [05:59] know the traffic's kind of dropped off
L0143 [06:01] and we can kind of zoom in and look at
L0144 [06:02] particular clients. So we can say right
L0145 [06:04] well actually clawed code um initially
L0146 [06:06] only had standard IO support and you can
L0147 [06:08] see that the traffic kind of drops off
L0148 [06:09] and at the moment you know clawed code
L0149 [06:11] usage looks like it's um probably
L0150 [06:13] dropping off because because of the day
L0151 [06:15] I took the data but again a very very
L0152 [06:17] few remote connections. So by and large
L0153 [06:20] you know the the migration away from
L0154 [06:22] local to remote services pretty much
L0155 [06:26] done um we we'll look at a little bit
L0156 [06:29] more of that in a moment.
L0157 [06:32] The other kind of question that you'll
L0158 [06:35] often f you'll often want to answer is
L0159 [06:37] if I've got lots of MCP clients and
L0160 [06:40] they're all connecting to my server,
L0161 [06:41] what's actually going on? And we often
L0162 [06:43] kind of think, right, well, is lots of
L0163 [06:47] initializations a good thing? Do I
L0164 [06:49] measure the number of tool calls? What
L0165 [06:50] what kind of things make sense to
L0166 [06:52] understand? And so, as you can see, the
L0167 [06:55] blue line there is showing tool calls
L0168 [06:56] against initializations.
L0169 [06:58] Um that big spike um by the way was a
L0170 [07:01] performance test from from one of the
L0171 [07:03] inference providers that uh that I
L0172 [07:06] discovered um
L0173 [07:08] and spoke about there but yeah so feel
L0174 [07:10] free to have a you know use our server
L0175 [07:13] that kind of thing but polite to talk to
L0176 [07:15] me first.
L0177 [07:17] So when it comes to kind of
L0178 [07:19] understanding activity on the MCP
L0179 [07:21] server, um there's kind of a few things
L0180 [07:24] to think about if you're kind of running
L0181 [07:26] it in production. And the first one is
L0182 [07:30] quite often you might think that
L0183 [07:31] initializations might be quite a good a
L0184 [07:34] good thing to to track. And it's not
L0185 [07:36] really the case because while in some
L0186 [07:38] clients initializations me will kind of
L0187 [07:41] mean that you've got an ambient
L0188 [07:42] installation because every time someone
L0189 [07:44] opens their tool it connects to our
L0190 [07:47] server in other cases clients will cache
L0191 [07:51] um and only initialize when they make a
L0192 [07:52] tool call. Um, we also tend to find that
L0193 [07:55] a lot of clients are not necessarily as
L0194 [07:57] stable as they should be. Um, and will
L0195 [08:00] sometimes get into runaway loops where
L0196 [08:01] they kind of just carry on initializing
L0197 [08:03] and uh and causing a bit of trouble. The
L0198 [08:06] other one which we kind of look at is
L0199 [08:08] tool calls. Now, often people will
L0200 [08:11] think, well, actually, you know, we're
```

## Section 3 -- Transcript segment 3 [L0201-L0301, 08:12-12:12]

```text
L0201 [08:12] we're doing better if we've got more
L0202 [08:14] tool calls. And that's not necessarily
L0203 [08:16] the case because if you get lots of
L0204 [08:18] repeated tool calls, that may simply
L0205 [08:20] mean that your tool design is causing
L0206 [08:22] confusion to the downstream agent. Um,
L0207 [08:24] and again, someone using uh this through
L0208 [08:28] through an interactive chat assistant is
L0209 [08:30] going to be doing some something quite
L0210 [08:31] different to what they would be doing if
L0211 [08:33] they were using it interactively through
L0212 [08:34] say claw. Chat GPT.
L0213 [08:39] So what we tend to um or what I tend to
L0214 [08:42] look at is session conversion. So how
L0215 [08:45] many um clients connect and then make at
L0216 [08:47] least one tool call. And that's quite
L0217 [08:49] quite an interesting count for me. On
L0218 [08:51] the right again the the session
L0219 [08:53] conversion efficiency kind of shows some
L0220 [08:54] of the main clients that attach to us.
L0221 [08:57] Um the ones at the top will connect and
L0222 [08:59] make a tool call, you know. So OpenAI
L0223 [09:01] MCP 96.2% of the time. No surprise it's
L0224 [09:04] the agent builder that does that because
L0225 [09:06] of the nature of how it's built. um MCP
L0226 [09:09] remote fallback test. Of course, it's a
L0227 [09:10] fallback test. It never makes a talk
L0228 [09:12] call. So more efficiency isn't
L0229 [09:14] necessarily better because if you've
L0230 [09:16] incorrectly cached the tool list, you're
L0231 [09:18] not going to be making a call to the MCP
L0232 [09:20] server itself. So these are some quite
L0233 [09:22] difficult things to balance um when kind
L0234 [09:27] of you know trying to understand
L0235 [09:28] activity.
L0236 [09:29] But if we look at the last few weeks, um
L0237 [09:32] Codeex is a very efficient client and as
L0238 [09:35] more and more people have kind of gone
L0239 [09:36] on to Codeex, one thing I've actually
L0240 [09:37] seen here is that the um the conversion
L0241 [09:41] rate has kind of gone up and again we
L0242 [09:43] can see that there's still an increasing
L0243 [09:45] amount of useful session to tool called
L0244 [09:48] conversion traffic.
L0245 [09:52] Um we also publish um or in data set
L0246 [09:57] which contains a kind of list of all of
L0247 [10:00] the MCP clients that we've seen and
L0248 [10:02] their capabilities. So if you kind of
L0249 [10:03] want to have a look at what version um
L0250 [10:08] clients are at uh what capabilities or
L0251 [10:11] extensions they've got installed then
L0252 [10:13] that data set is a very very good place
L0253 [10:15] u to start. So have a look um check it
L0254 [10:18] out um cuz uh you know we'll probably be
L0255 [10:20] publishing a bit more data through there
L0256 [10:22] fairly soon.
L0257 [10:25] Now in production um
L0258 [10:29] the MCP kind of gives us a couple of
L0259 [10:32] challenges and the main challenge is
L0260 [10:36] comes back from that initial design
L0261 [10:38] right which is that if I have a kind of
L0262 [10:39] a client and servant pairing there's an
L0263 [10:42] assumption in the protocol that the um
L0264 [10:46] that the uh relationship between them is
L0265 [10:49] stateful. So what's actually happening
L0266 [10:51] here is is that um the client will make
L0267 [10:55] a request to the MCP server and the MCP
L0268 [10:58] server says right I've initialized and
L0269 [11:02] then the client sends back a
L0270 [11:03] notification and they've kind of
L0271 [11:05] handshaken so we've already kind of two
L0272 [11:07] messages from the client to the server
L0273 [11:08] in before we've actually established a
L0274 [11:10] session
L0275 [11:12] after that the client then will normally
L0276 [11:14] check and say right well give me the
L0277 [11:16] list of tools give me the list of
L0278 [11:17] prompts give me the list of resources.
L0279 [11:18] So we're now kind of we're at four calls
L0280 [11:21] in before we've actually even um we've
L0281 [11:23] actually even serviced anything and then
L0282 [11:24] finally we'll get a tool call um and the
L0283 [11:28] uh and the information will go back to
L0284 [11:29] the client. Now again kind of you know
L0285 [11:32] typically what what we'll see in these
L0286 [11:35] kind of scenarios is if we've got state
L0287 [11:38] at both the client and the server that
L0288 [11:39] starts to get rather um rather tricky to
L0289 [11:42] manage
L0290 [11:44] and it's also very very chatty. Um so I
L0291 [11:49] I kind of ran this I think it was on
L0292 [11:51] Sunday morning. Um this number kind of
L0293 [11:53] varies a bit based on the mix of clients
L0294 [11:55] we've recently seen but at the moment
L0295 [11:57] for every 10 million protocol messages
L0296 [11:59] that we get so these are the kind of MCP
L0297 [12:02] protocol methods and calls. 1.2 million
L0298 [12:05] of them are initialize events which are
L0299 [12:07] potentially interesting but actually
L0300 [12:09] only 62,000 of them are all calls right.
L0301 [12:12] So the kind of overhead of managing that
```

## Section 4 -- Transcript segment 4 [L0302-L0401, 12:15-16:21]

```text
L0302 [12:15] stateful connection um is is quite high
L0303 [12:19] from a from a protocol level. Now um
L0304 [12:23] there is a kind of semi-documented
L0305 [12:26] undocumented mode where you can kind of
L0306 [12:28] run MCP statelessly. Um it's a bit
L0307 [12:30] ambiguous. Uh but if you do that you
L0308 [12:33] lose any ability to kind of capture
L0309 [12:35] analytics.
L0310 [12:36] So some of the challenges then we have
L0311 [12:38] with with statefulness. So one is that
L0312 [12:40] ambiguity around the around the
L0313 [12:42] protocol. Um
L0314 [12:45] the use of elicitation and sampling if
L0315 [12:48] you've got server initiated requests
L0316 [12:50] mean that you need to maintain an open
L0317 [12:51] channel. Okay. So one of the things that
L0318 [12:53] we were quite keen on trying when we
L0319 [12:55] first launched was to send what are
L0320 [12:58] called tool list change notifications.
L0321 [13:00] So the MCP server if it wants to offer
L0322 [13:02] different tools will notify the client
L0323 [13:04] and the client can then offer them. But
L0324 [13:05] actually in practice that's a very very
L0325 [13:07] difficult thing to do especially on a
L0326 [13:08] public server.
L0327 [13:10] Um as mentioned session state and
L0328 [13:13] understanding that is not quite
L0329 [13:16] precisely defined enough in the
L0330 [13:17] protocol. So a standard IO server you
L0331 [13:20] kind of just connect and you've got a
L0332 [13:21] process and you talk to it. A remote
L0333 [13:24] server you have an MCP session ID. It
L0334 [13:27] doesn't necessarily match up. Um and
L0335 [13:30] operationally having sticky sessions and
L0336 [13:32] load balances which need to inspect the
L0337 [13:34] traffic to send it to the right server
L0338 [13:36] means that doing server upgrades
L0339 [13:38] resilience um or kind of standard
L0340 [13:40] scaling practice uh becomes very very
L0341 [13:43] difficult. Um the other challenge as
L0342 [13:45] well actually being is SSE connections
L0343 [13:48] and cut off times uh make a lot of that
L0344 [13:50] quite quite difficult as well.
L0345 [13:53] So those are some of the challenges and
L0346 [13:55] kind of what we see in production. So
L0347 [13:59] um
L0348 [14:00] it's been god probably about over the
L0349 [14:02] last 10 months then um been working with
L0350 [14:05] the MCP transports working group um I've
L0351 [14:09] got people from anthropic and Google and
L0352 [14:11] Microsoft and everybody all contributing
L0353 [14:13] to that kind of sharing the production
L0354 [14:15] data sharing our experience of how to
L0355 [14:16] actually deploy this. Um and we now in
L0356 [14:21] the new release candidate specification
L0357 [14:23] have some fairly big changes um to the
L0358 [14:27] protocol to actually make this easier
L0359 [14:29] and simpler to deploy and I think you
L0360 [14:30] know to get get a lot more a lot more
L0361 [14:33] value out of. So kind of the first thing
L0362 [14:36] to kind of think about then is that this
L0363 [14:39] is actually the first time that we've
L0364 [14:41] had this type of change to the protocol
L0365 [14:42] where we now have um the standard IO
L0366 [14:45] protocol changing the JSON RPC messages
L0367 [14:48] that you send backwards and forwards
L0368 [14:49] across it are going to be different. Um
L0369 [14:52] and then we also of course have a new a
L0370 [14:55] new way of connecting to remote servers
L0371 [14:56] with uh with the stateless HTTP um
L0372 [15:01] transport. So let's kind of start to
L0373 [15:04] dive into to some of those changes.
L0374 [15:07] So actually the first um the first and
L0375 [15:11] kind of most important one of those is
L0376 [15:13] just simply simplifying it. So the first
L0377 [15:17] the first one there is taking away the
L0378 [15:19] ability for servers to communicate with
L0379 [15:21] clients without the client having sent
L0380 [15:23] you a message first. Um, and the team at
L0381 [15:28] Anthropic actually did some analysis on
L0382 [15:31] all of the open- source servers, um, all
L0383 [15:33] the open source servers that they could
L0384 [15:34] find and all of the other MCP servers
L0385 [15:36] they could find. And it turns out that
L0386 [15:38] across 100 million tokens of searching,
L0387 [15:41] uh, the only person to use this feature
L0388 [15:43] is um is on stage right now. Um,
L0389 [15:47] so I'm now going to try a very inadvised
L0390 [15:49] demonstration because um
L0391 [15:52] let's see if we can uh let's see if we
L0392 [15:55] can do this. So
L0393 [15:59] yeah. So so MCP webcam then is uh is a
L0394 [16:03] very very useful um very very useful
L0395 [16:06] application which lets you do things
L0396 [16:08] like if I say look through the webcam
L0397 [16:10] everyone smile. Let's see if this will
L0398 [16:12] actually work.
L0399 [16:16] This is a good kind of test of network
L0400 [16:18] and uh there we go. There you are.
L0401 [16:21] Perfect. So yeah, so through MCP webcam
```

## Section 5 -- Transcript segment 5 [L0402-L0502, 16:25-20:25]

```text
L0402 [16:25] then it's a fairly straightforward MCP
L0403 [16:27] server which lets you kind of use a use
L0404 [16:30] a webcam um through MCP. Uh it's
L0405 [16:34] obviously a very uh very useful thing.
L0406 [16:36] Now, um, the feature that the feature
L0407 [16:40] that we're going to be losing from MCP
L0408 [16:41] webcam as a result of this change, and
L0409 [16:43] this is, as I say, the the kind of one
L0410 [16:45] example of the world in the world is,
L0411 [16:47] let me just refresh that.
L0412 [16:52] Actually, I think I need to I will just
L0413 [16:53] quickly reconnect that because now
L0414 [16:54] having gone to the um
L0415 [16:58] having gone to the risk of trying to do
L0416 [17:00] a live demonstration, I may as well see
L0417 [17:01] it through. There we go. Okay. So if I
L0418 [17:04] hit sample, what's actually happening
L0419 [17:05] now is the webcam MCP server is
L0420 [17:09] connecting to the client. Yeah. And now
L0421 [17:11] the client is giving a description of um
L0422 [17:14] of B or short. Yeah. It's giving a
L0423 [17:16] description of what it's seen. Um this
L0424 [17:18] is a good example of why context
L0425 [17:21] engineering matters because you don't
L0426 [17:23] particularly don't necessarily want um
L0427 [17:27] uh the AI's view of you.
L0428 [17:32] So we're simplifying it. We're taking
L0429 [17:34] away the ability for clients, the
L0430 [17:36] ability for servers to talk to clients
L0431 [17:38] without having first had a message in
L0432 [17:41] from the um from the client. And that
L0433 [17:44] means we can simplify the network uh the
L0434 [17:46] network aspects quite a lot as well. So
L0435 [17:49] sampling routes going and logging as
L0436 [17:51] well if you're if you're a real protocol
L0437 [17:52] peeper.
L0438 [17:55] Huge then is we're taking away the that
L0439 [17:58] initialization handshake. Right? So
L0440 [18:00] where typically the MCP server standard
L0441 [18:02] IO or remote would send a initialize
L0442 [18:06] request and go through that whole kind
L0443 [18:07] of handshaking and save the capabilities
L0444 [18:10] on either side. Um that's just going
L0445 [18:13] okay. So if you still need to find out
L0446 [18:15] the server capabilities before you're
L0447 [18:17] actually interacting with it, there's a
L0448 [18:19] discover endpoint that you can call um
L0449 [18:21] that will give you a probe to to get
L0450 [18:24] that particular if you want to show it
L0451 [18:25] in your user experience if prompts and
L0452 [18:26] resources are available. So that's
L0453 [18:28] great. And if you are using those list
L0454 [18:31] change notifications or um resource
L0455 [18:34] subscriptions, there is still an
L0456 [18:36] endpoint that you that your client can
L0457 [18:37] call to get those notifications. Okay,
L0458 [18:39] but again it's a a big a big
L0459 [18:41] improvement, a big simplification.
L0460 [18:44] Another one of my I actually this is one
L0461 [18:47] of my favorites is cache control. So
L0462 [18:50] when an MCP server um gives you the list
L0463 [18:53] of tools,
L0464 [18:55] we can now say that list of tools is
L0465 [18:58] probably not going to change for the
L0466 [18:59] next hour or the next couple of days,
L0467 [19:02] which means that clients can then cache
L0468 [19:03] it. Even more importantly is where you
L0469 [19:06] have a fleet of clients you the the MCP
L0470 [19:09] server can indicate that it's safe to
L0471 [19:10] share that tool list amongst a whole
L0472 [19:12] load of clients which means that you'll
L0473 [19:14] be able to discover MCP server
L0474 [19:16] information cach it so you don't have to
L0475 [19:19] discover it on each connection um and
L0476 [19:21] you can also then discover that from
L0477 [19:23] other offline stores like the MCP server
L0478 [19:26] card so you know a a kind of a manifest
L0479 [19:29] that tells you all about um that MCP
L0480 [19:33] uh server and again that doesn't
L0481 [19:34] necessarily overwrite um if you get to
L0482 [19:37] all this change notification all those
L0483 [19:38] things still take precedence but that
L0484 [19:40] kind of caching behavior gives us um
L0485 [19:43] huge scope um to kind of you know just
L0486 [19:47] improve the overall user experience for
L0487 [19:49] for both agents and uh users and
L0488 [19:52] operations teams.
L0489 [19:56] One of the um you'll have noticed on
L0490 [19:59] that client side there were three
L0491 [20:01] features listed there. Roots uh sampling
L0492 [20:03] elicitations.
L0493 [20:05] Elicitations are the ability for the MCP
L0494 [20:09] server when you make a request to it to
L0495 [20:12] kind of pause and say right actually I
L0496 [20:13] need some user guidance. You've sent me
L0497 [20:16] a message to drop the database. I'm
L0498 [20:17] going to pop up a message or a window.
L0499 [20:19] Is it okay to drop that database? And
L0500 [20:21] the user can then say yes, no or or so
L0501 [20:23] on. So you can you can supply extra
L0502 [20:25] information through um through the a
```

## Section 6 -- Transcript segment 6 [L0503-L0602, 20:29-24:33]

```text
L0503 [20:29] deterministic channel. Now the challenge
L0504 [20:32] with the current listation design is
L0505 [20:33] again is it kind of assumes that um the
L0506 [20:37] server and the client are managing state
L0507 [20:39] between them. So it just kind of sends
L0508 [20:41] small messages. So what we're actually
L0509 [20:42] going to um do instead is the client
L0510 [20:47] will send a request to the server. The
L0511 [20:49] server will respond rather than having a
L0512 [20:52] direct result. it will say actually I
L0513 [20:53] need to stop and get some input. The MCP
L0514 [20:56] client can then handle the user uh the
L0515 [20:59] user facing input and then it can send
L0516 [21:01] both that original request and the
L0517 [21:03] response to the request back to the MCP
L0518 [21:05] server for processing the next turn. So
L0519 [21:07] very very similar to the way that a um a
L0520 [21:10] chat API works uh works today.
L0521 [21:15] And again this is I think this is going
L0522 [21:17] to be an absolutely huge feature is HTTP
L0523 [21:19] standardization. Um, and I think I'll
L0524 [21:24] I'll tell you what it is first, then
L0525 [21:25] we'll talk about why I think it's
L0526 [21:26] exciting. So, for HTTP standardization,
L0527 [21:30] uh, what we're doing is first of all,
L0528 [21:31] we're we're making sure that certain MCP
L0529 [21:35] information. So, if we think about MCP,
L0530 [21:37] it uses JSON RPC. So, you have these
L0531 [21:39] kind of JSON RPC packets
L0532 [21:42] um that the server reads and then
L0533 [21:45] processes and then sends a RP JSON RPC
L0534 [21:48] response. And of course if you've got
L0535 [21:50] any kind of network infrastructure that
L0536 [21:52] means it needs to inspect the JSON
L0537 [21:54] packet unpack it invest it which is a
L0538 [21:56] fairly expensive operation. So firstly
L0539 [21:59] we're guaranteeing that certain
L0540 [22:02] information in the request is in the
L0541 [22:04] HTTP headers which is going to make it
L0542 [22:06] very very simple to route. Super
L0543 [22:08] powerful is that in tool descriptions
L0544 [22:11] you'll be able to say I want this
L0545 [22:13] particular parameter copied into the
L0546 [22:15] headers. Okay. So that means for example
L0547 [22:18] um so I'll just put the the spec on the
L0548 [22:21] on the screen there. So that means for
L0549 [22:23] example um if I've got an image
L0550 [22:24] generation space I can actually
L0551 [22:27] find find that out at um network
L0552 [22:30] routting time and divert it to the
L0553 [22:32] appropriate server to to handle it.
L0554 [22:34] Okay. So it it opens up completely new
L0555 [22:37] deployment options for how you may want
L0556 [22:38] to um
L0557 [22:41] supply this kind of uh stuff to agents.
L0558 [22:44] So again that means as I say it's
L0559 [22:47] visible to network infrastructure and
L0560 [22:50] means that you can then routt tools
L0561 [22:51] wherever you go. So for for MCP gateway
L0562 [22:54] companies, MCP proxy companies, these
L0563 [22:57] kind of features are um going to be very
L0564 [22:58] very important for uh for efficiency.
L0565 [23:02] So once we've done all of those changes
L0566 [23:04] and uh we have the new SDKs out that
L0567 [23:07] means that you know rather than that
L0568 [23:09] kind of fairly long and laborious
L0569 [23:11] handshake to get things done and you're
L0570 [23:13] kind of you know potentially looking at
L0571 [23:15] all of the excites of Jed RPC packets
L0572 [23:18] and so on. Um you know instead we'll be
L0573 [23:21] able to have much much higher
L0574 [23:23] performance um in the protocol level
L0575 [23:26] itself. But also if you kind of think
L0576 [23:28] about the utility of this for from an
L0577 [23:31] agent's perspective, the ability that
L0578 [23:34] you can connect to an authorized set of
L0579 [23:36] tools with a single URL um is extremely
L0580 [23:39] important. And the fact that um things
L0581 [23:42] like the tallest description and other
L0582 [23:44] metadata about the server will be
L0583 [23:46] available out of band mean that all of a
L0584 [23:48] sudden connecting to authorized
L0585 [23:49] endpoints to do arbitrary agent
L0586 [23:52] workloads, dispatching jobs, doing other
L0587 [23:54] doing other inference becomes um becomes
L0588 [23:58] far more compelling. Okay, so these
L0589 [24:00] changes open up a whole kind of load of
L0590 [24:02] new use cases that that just didn't
L0591 [24:04] exist before. And because it's MCP, that
L0592 [24:07] single URL to get to an authenticated
L0593 [24:10] LLM ready resource is um super
L0594 [24:13] important. So where are we? Um migration
L0595 [24:16] path is very straightforward. The
L0596 [24:18] release candidate specification is is
L0597 [24:20] released um I think it was last week. So
L0598 [24:24] um you can see all the work we've been
L0599 [24:26] doing over over the last few months. Um
L0600 [24:28] some of the debates and discussions that
L0601 [24:30] have been had. Aim is to have beta SDKs
L0602 [24:33] by the end of this month. And then the
```

## Section 7 -- Closing segment [L0603-L0703, 24:35-28:45]

```text
L0603 [24:35] planned protocol release date is the
L0604 [24:36] 2807 um 2807 date.
L0605 [24:40] Um just one final thing um before I
L0606 [24:44] stop. I'm just going to go slightly over
L0607 [24:46] time now. Um is um we we kind of quite
L0608 [24:51] keen on building the right agent
L0609 [24:53] infrastructure. Um so Pantic have a tool
L0610 [24:55] called Monty which is a sandbox um for
L0611 [24:58] running agent generated Python code and
L0612 [25:01] we're co-sponsoring the bounty. So, um,
L0613 [25:04] so have a yeah, have a look at that if
L0614 [25:06] you're particularly good at breaking
L0615 [25:07] Rust sandboxes. Um, we definitely like
L0616 [25:10] to like to help get that infrastructure
L0617 [25:12] layer more secure. So, with that, I
L0618 [25:15] think that's my time up.
L0619 [25:18] Thank you very much. Yeah.
L0620 [25:22] Uh, we do actually have a few minutes
L0621 [25:25] for questions. If there are any
L0622 [25:26] questions, uh, put your hand up and
L0623 [25:28] we'll get a microphone to you somehow.
L0624 [25:31] Uh, first one's here.
L0625 [25:38] Hello, thank you for your presentation.
L0626 [25:40] Um, in your opinion, what separates
L0627 [25:43] companies that are generally building
L0628 [25:45] agentic infrastructure from those that
L0629 [25:48] are just wrapping LLM APIs with
L0630 [25:52] workflows.
L0631 [25:53] >> Sorry, I didn't catch the first part of
L0632 [25:55] the question. I'm really sorry. The
L0633 [25:56] first one is in your opinion what
L0634 [25:58] separates companies that are generally
L0635 [26:01] building agentic infrastructure from
L0636 [26:03] those that are just wrapping LLM APIs
L0637 [26:06] with workflows.
L0638 [26:09] >> Uh testing mostly
L0639 [26:12] would be uh would be my view there. I
L0640 [26:14] mean I don't have um
L0641 [26:17] uh the industry is I think very very
L0642 [26:20] quick at deciding that one thing is very
L0643 [26:22] good or very very bad. Um, I think that,
L0644 [26:25] uh, unless you've kind of got a good
L0645 [26:27] idea as to what it is you're trying to
L0646 [26:30] do with inference, um, and how you're
L0647 [26:32] designing the context window, sometimes
L0648 [26:35] actually directly wrapping an API is
L0649 [26:38] absolutely the right thing to do and
L0650 [26:39] other times, of course, it's absolutely
L0651 [26:40] not. Um, so I think the difference is
L0652 [26:42] whether or not you've actually tested
L0653 [26:44] and evaluated those differences.
L0654 [26:48] Um slightly conceptual question uh when
L0655 [26:52] you're trying to decide whether it's
L0656 [26:54] best to use a CLI tool for that or an
L0657 [26:56] MCP server for that how would you tell
L0658 [26:59] the difference to make sure the agent is
L0659 [27:01] working and performing better.
L0660 [27:04] So sorry the question is
L0661 [27:06] >> so the qu the question is if if we can
L0662 [27:08] choose between CLI and an MCP let's say
L0663 [27:10] playright CL right
L0664 [27:12] >> MCP oh so um I think probably with with
L0665 [27:16] some of these changes those things start
L0666 [27:19] to converge slightly as well MCP is very
L0667 [27:22] very good if you want to access remote
L0668 [27:24] resources um where so for example if I'm
L0669 [27:28] going to if I want to run a remote
L0670 [27:30] training job then dispatching a job
L0671 [27:32] through MCP is actually quite a nice
L0672 [27:34] secure way of doing it rather than say
L0673 [27:36] bringing all the data down. But we we
L0674 [27:39] you know we provide access to our
L0675 [27:41] services through both our hugging face
L0676 [27:42] CLI and provide them through both the um
L0677 [27:46] through the MCP server and I would say I
L0678 [27:49] think
L0679 [27:51] for when we kind of look at the client
L0680 [27:52] usage it it varies a lot MCPs tend to be
L0681 [27:57] um preferred in enterprises because you
L0682 [27:59] can have much tighter control over
L0683 [28:01] what's deployed on what machine and
L0684 [28:02] where. So certainly a lot of the kind of
L0685 [28:04] coding tool traffic we see I suspect is
L0686 [28:06] probably from those kind of scenarios.
L0687 [28:08] Um where MCP really works very very well
L0688 [28:12] and we kind of see this with the MCP
L0689 [28:14] apps extension is in interactive
L0690 [28:16] applications. So things like claw.ai
L0691 [28:18] chatgpt because again it's very very
L0692 [28:21] easy to connect those things up and then
L0693 [28:23] you can have very rich interactive
L0694 [28:25] experiences. So it's been kind of in my
L0695 [28:27] mind for quite a long time that you know
L0696 [28:28] to a certain extent we've kind of got
L0697 [28:30] those two audiences and that you know we
L0698 [28:32] may want to start adapting how we how we
L0699 [28:34] deploy some of those tools as a result
L0700 [28:36] but yeah it's a good very good question.
L0701 [28:39] >> Any more for anymore? Final question.
L0702 [28:43] Okay. Uh a final round of applause.
L0703 [28:45] Thank you so much Sean Smith.
```

