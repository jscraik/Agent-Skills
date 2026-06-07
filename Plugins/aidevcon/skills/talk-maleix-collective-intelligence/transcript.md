> **Attribution warning.** This transcript has **no per-speaker labels**. The vast majority is Edouard Maleix speaking. The opening (~first paragraph) is a host introducing him, and the section beginning at "Thank you so much for that. Question." through to the end is Q&A — host moderating, unnamed audience members asking questions, Edouard answering. There are also obvious speech-to-text artifacts that have been **preserved verbatim**, including:
> - "Adrian" / "adrian" almost certainly means "AI"
> - "globally" in the Testify-PR anecdote almost certainly means "Claude"
> - "Tagli" likely means "tiny"
> - "clo" likely means "Claude"
> - "diode absolutely opinionated" likely means "diary"
> - "darvish bioteam" / "fourth-way" / "four-way" likely "forward"
> - "f moment" / "what the f moment" means "WTF moment"
> - "ADR" / "the dress pile up" — likely "ADRs" / "rules pile up"
>
> When quoting, preserve the artifacts as written; you may add "(likely 'X')" inline when meaning is unambiguous.

---

## Opening & framing

Thank you very much. Appreciate that. Now just keep it easier for us. To show you. Come on in. Try to see. We're gonna go ahead and. Get started here. Thank you guys for coming. It's been a packed house all day. If you haven't been to this room yet, this is all practical takeaway. Talks. Nothing heady. We don't need that. Not here. Maybe a little. I don't know. We'll see. This is Edouard Maleix. He is going to talk about how AI for dev teams build collective intelligence, which I think is on all of our minds today. Can we give them a round of applause?

As you don't see my notification. So hi everyone. As you noticed, I think today even more than before. Adrian's [AI's] already everywhere in our work. In our conversation. I've been talking with people and eavesdropping conversation. It seems like what keeps us busy and we are preparing for a new shift. Which will move agent from our isolated environment. To conquer teams. So if we don't write our code, review our code, even start to plan our sprint. So move it towards management position. It makes me wonder. What our agents learned yesterday that our team can use today or tomorrow and the days after. So I want to share and help you find out.

## The familiar obstacles

Before we talk about any solution. I want to address the familiar obstacles. You know, you have your properly experimented with you with your agents. That one should automatically. You have clothing, auto mode. Or by running headless. Or open cloud each way to that. You can see even though it seems like it has a bad publicity today. All the small discoveries, all the tiny learnings, all the incidents that are inside the session. They rarely make it out of it. They just end up closed here. So correction evaporates.

Eventually. And that's what we probably all did, we start to create skills or rules or any piece of documentation that can get injected. Inside the agent's context. And then what happens? We have lots of rule that buys up. Some skills, some project notes. And yeah, the dress pile up, same as your context below. It really gets crowded. And you barely can barely say when it's getting used, if it's still useful, if it became stale, and even if it gets activated when you expect it to be activated.

So in the end, if we are in the context of engineering, when it's time for the review of a given work to start. Maybe the PR can show up green, like all test passes, if you have some share description, you follow the specs, you can hardly, you cannot even tell actually what lessons shape that work. What would you imagine that it sounds a bit familiar when I said that?

## What we actually need

So after thinking about it a little bit. I've been thinking of death themes. Like humans and agents included. They don't need just another wiki page that you have in your teams. I don't think I heard that team should stay locked with their agent in their fusion relationship. And apparently none of the speakers today think so because it seems like teams is really everywhere. Agent work create lessons every day. Like you have those leisurely in the session, but the team is not learning. So what could we do to get out of. That. Loop?

Well, I think that we do sort of an average factory. Like as to go, as the work go, you have that system that catches mistake interruptions. And turns them into some guidance. Then you check whether those guidance actually have. Naturally, you will let some of those guidance fail because some knowledge just decay. We have to accept that. And that can happen when the model evolves when your corporate change. So the idea is that instead of having. Static documentation, we have something that constantly move die the day after. Not a problem. Just need to accept that.

## Speaker background

Before I go a bit deeper. In the theory and the experiment. I want to tell you a bit where that comes from. So that's me. I'm a freelance consultant. I help take it and CTO. Authentication application performance. And the productivity challenges. And as I was helping some customers, they think to adopt a coding agent. I've been building an open source infrastructure and some set of tools. To turn those repeated friction that all the dev teams encounter into something that help teams on board. In a common ground. So what I want today is to share some of those learnings, to share some of the primitives that I think could help in that way. But beware, it's all very experimental. Don't imagine that I tell you this is the way we should do it. Like everyone today will experience, you know, we're very good trying to find some places to put in place and test it and hear that's the same with that. Framework.

## Act 1 — Identity & the Testify PR anecdote

So I think the solution to start. At the low level and the lowest level I think is the change level. So if we don't want the agents learning all the lessons to just build consumption folklore, we need to track who did the work, when they did, and what was the reason in behind it, what lessons, what knowledge they use to do those makeover decisions. So we need some evidence.

To illustrate that the sort of weird moment we are in that we float in, that's a PR open some months ago. For a testify plugin. And knowing that the maintainer famous guy in the JS ecosystem was not really. A hydrogen friendly at the time. I just did my best to mask all traces from cloud code. But PR was really written, I think 95% by globally [Claude]. And I don't have a shame. To assume that. And did the work, I mean my best to have engagement, what I think we tested, the best portrait is fine enough, further issue the code as well. And all the commits are under my name. They are even my GPT [GPG] signature. On the full end flow dependent PR under my name. So the even is perfect. But I think that's one of the problems that we should address. Like right now who can assume that working? It's even worse for the PR reviews. I guess you might have received some PR reviews. Authored by one of your teammates, but actually counter by global [Claude]. Isn't it in soft day? Well, I think that is.

And that's why I wanted to first start with that groundwork and give the agent an identity. That's the first primitive. Block. The identity gives us tier separate actor. It gives us some sign commits. And then at that stage you already solved one small problem. The agent does not hide behind it or behind a clo [Claude] name or whatever. And also it starts to create some sort of boundary because if the agent has its own identity, it has its own identifier. It can have its own access rules. So instead of authorization and it stops. Surfing on your existing permission as a human. To access control, it's really about access control here and it opens the way for that.

## Act 1 — The Diary primitive

But of course identity is just a starting point. It starts the track. Of attribution. It tells us where. It does not tell us why the actual made sense at all at the time. It was. That's where the second primitive comes. The diode absolutely opinionated form of building blocks [the diary — a deliberately opinionated form]. It could give you lots of name at some point and you needed to give it an a. I think that refit to describe the place where the stops being just the work and the lessons start being a four-way [forward] artifact. So there is the opt for all the discoveries. All the what they have moment [what-the-f moment], all the decision making that happened during the work. It's also the first. Spot where you can also have some sort of access boundary that rotates. For example, you could have your darvish bioteam [diary by team] that I read that could be purely personal for your style of word preferences. Or scope two repository or scoped to a project. It's the first point where you can define those policies. What matters in the end is that. If the work or decision matters, you need to lend it somewhere before it disappear.

S. So in practice this is what it could look like. You would have your commit done by the agents. So here late to git fabrication. It's a regular. With a reference to the entry. That capture the procedure, the reasoning behind the work. And then we can already start to do a bit less like guesswork. You can start to go a bit further than just the diff and the commit messages. You can start, we have the rationale. But that's also still just the beginning. Now we need to find a way to capture the lessons. That the next session they produce.

## Bridging example — the Go SDK incident

So the act start when you have to capture correction and the list belong to one div [dev] and become usable knowledge. But there is a long way there. Before I introduce how we could capture those incident. I want to just. Create a common ground of understanding. So I will take an example of where an agent can stumble. And that's a true case.

So on Monday your agent update your rest API or whatever API whatever contract you might have. It remembers to regenerate the open API specs. The typescript SDK that you have that also derived from the open API space. But you also have a go SDK that conveys and it completely missed it. On Tuesday you have the same situation. So in my case I use the best fresh first word in the adrian promised that okay it won't happen again. But you know what follows on Wednesday. We have the same trap. The go client will stay again.

So of course. To be clear this kind of example the CI should catch it and would catch it in that case before it's even more. The point is not really here. There is to save some iteration because if you always have to wait for some sort of post processing to catch the situation. But in the meantime before you had any commit and push the agent has been for example updating the test without the SDK. So the idea is that we don't want to waste iteration. We want the agent to know the practice like a human would do.

So here I will be a bit captain obvious after all the work done today in the whole discussion. So why did today lesson never stick? Well simply because the correction that we did here to remind the agent to generate a goal SDK stay trapped in one session. So the Wednesday agent, one day session just doesn't know about it. And that's the same for the team. That's where it becomes a problem. Because not only my agent with stubble on that also all the other teams agent could also stumble on the same thing. So what it does, it just falls back. Blocky or unlucky what's already in the context or what's the model already knows. And yeah here you just count on luck for the agent to do the right decision. No way to tell if that would be the right one.

## Entries, categories, linking

So I said before the knowledge lend in diary. A diary. Is a bit more granular. It's a bit more value than that. What you have inside are e. Its entry. So eventually we'll be used to describe different elements. So we will have four categories. To capture different type of situation. For the case of the Tuesday incident with the API story. It's made by the entry. It's what the f moment [WTF moment]. That's where it belongs and that's where it should be captured.

And here's an example entry. So that might be a little bit nowadays you need that some other people talk about this morning. Here it was captured during. The agent used the wrong driver, the wrong DD [DB] driver method. Which totally missed the transaction session. That can be quite a mess. If you can imagine the world back possible [rollback]. So we have either a duplicate right or whatever. So here Kelly had something that we want to keep doing at an extension. So here this example entry. Is also linked. To other entries and that's where it can become interesting. Because you have isolated events that can be linked then between each other. And here we have that entry that was created originally standalone. But then we can link it to the PR review that made the notice like say a what the forbidden you do. You don't use that. Sorry for the square. It might not go. So you can track both the PR commands. And the fix that is linked to that so that it does not happen again. And the idea that. Six months from now on if you land on one of those entries you can also land on the fix and the lesson that goes with it.

## Passive accumulation

For this stage you already made some effort. To understand entry to a depth framework. So what you do at the stage actually is pretty simple. It's passive accumulation. You have that system in place. That workflow in place and you should have your agent that just capture passively these entries. This incident, these lessons, mis knowledge.

## Curation — discover, slice, expand, search

Because that's when you have enough entries that you can start to shape into something that really is helpful. And the curation start by discovering what you have. That's that becomes honestly the magical moment. Because you have no idea. You cannot track all the entries that goes down even less where your team is large. Because it can come from everywhere. Useful stuff useless stuff. So the idea is that you start to map a bit the territory. You start to find scopes. You start then to slice those scope into. Some given incident. For example in my case the database incident that I noticed. And then we expand those entries. Check the relationship that they have. And eventually if you have hunch you just do row [raw] search like pure. Red. And at some point when you have some thematic entries you can build some sort of pack of knowledge.

So back that's a small created bundle of entries. That you should or eventually at some point your agent should pick for one task or one re area. So it's clearly not your children bags of toys. If your parents were over here I can imagine what's a bag of toys like lots of mess and yeah for later it's tiny. Not like that. Gallery exhibition. Really. You have to make sense with that. Back.

So here as an example the visual representation of one of those pack actually the first one ready to database practice. In the project that I'm using to the v3 just talk to the. First use case. And every entry here that you can see it's really a really example of stuff that broke that are then reused to compose that packing.

## Render — pack → markdown skill with attribution

But the back is not yet what the agent reads. There is one more step before that. And that step is really important and very sensitive. It's at that stage so you have all those entries referenced inside the pack. And you need to answer yourself how will I load that knowledge inside the agent? So I didn't want to do something out of the ordinary. I just imagine okay let's just build some markdown files out of those row [raw] entries into something that can be really usable by an agent. So this is typically another task assisted by the agent flashing the entries for that are referencing that back. Treat them eventually to fit the token budget. And then you can load that render back in the agent.

And what's very important here is that every section can see points through given entry. And then resection. Keep the attribution live. So here you can see the source with the answer identifier. The human that was operating. And the agent identifier as well. So the idea is really be able to not have just the skill that says that's how you do things. It's more like that's how you do things because we got beaten somewhere that hurts and we don't want that to happen again.

## Act 2 summary — interruption → entry → pack → render

So to summarize it let's act two. We have now a sort of pipeline or even more loop. Interruption becomes an entry. The right entries become a pack. Then the pack becomes something the agent can read. And then in the end that one developer paid for or one autonomization paid for. We counted team asset. And trades even there is even a discipline. I did not hear the word yet today. It seemed to be called compound generating [engineering]. So let's see if that happens and we hear more about it.

## Who decides what survives?

Now the harder and more interesting question is who decides. What survives what knowledge remains. So in a human team no one really cites alone. You have some ADR or however you want to call them some wikis the traces in the code reviews. So postmortems actually. That happens. But as now edge moving at the human base and now these days we try to adapt our base to the agent base. So when agent writes some Tagli [tiny] lessons all day long. There is no feedback loop like that. At least yet not much. It's just lots of individual initiative getting built these days. And they produce correction faster than doxystem can absorb. Them. So that means we need some instruments to judge them. So that would not be novelty because today I think if you did not hear about it you learn a lot about events [evals]. I guess. I will still talk about regular we go briefly considering that already we're now in today and I want to waste your attention.

## Evals — controlled VM environment

But here in our case for the vendor back [render pack] what we want to know and evaluate is that. Is whether the. Bank is true to the entries. Does it transform the entries. Does it include all of them? Does it actually help in this scenario? So that's the most typical key value use case. And the other thing that you would want to know is the activation. To answer did the scale did not get the story on time. So here in that session we will just focus on fidelity and usefulness.

Before I go into the process there is something a bit more technical I would like to spend time on. Is the environment that those judges will run in. I did. Not hear it much emphasized today but maybe missed the good talk. But I think all those agents task should run in a controlled environment. And here what. I built for that case is just the environment. That when you send parts a little bit like. A little bit like you would have with codecs and bot but here controlled environment. So you can decide. What files can be accessed. You can decide also what network calls can be done. You read control that environment. So there is no leak from the outside or inside out. So that's where the anim works in that VM.

What's unique though is for every task. Its input. So you have some prompt templates. Some set of criteria. That will allow us to sort of score or recess the result. And some references and of course we want to have some sort of context that will be located in that injury [entry] because that's the context that will be used either to improve arrangement. But here in that case does that contain that will be judged that we process. Ed.

## Evals — Fidelity

So here in that example to evaluate the fidelity of the offender bank [render pack]. We had those pre-simplified criteria with their own binary score. And the first look great. Yeah composite score of almost one free win free launch. Okay I won. I'm a genius. But actually if you spend a little bit of time on the bar you can see that lazy prompt or badly. Calibrated criteria. You can just backfire and be giving a false sense of safety. To commit short the idea that before you run an llm judge you are the judge. You do the work that the judge will do yourself. And you check if those criteria would rematch and catch something and same food abroad. It should reflect your own question, your own way to score things.

## Evals — Usefulness

Now about usefulness though. Okay. We can say now that. The agent did not lie about the knowledge pad that was created. But now we want to see if it's really useful. So here we also keep it short because if I have heard about it but the idea is that you give your agent runtime your task. That we produce some of those incidents you will get. So that's good because if you're already captured the incident you already have the situation. Already has a context and that's why it's pretty good because you should it becomes really difficult if you invent task or catch them from the best. It's much easier if you already know the incident, the story behind it and the task.

So here that's one of those tasks to catch up and reproduce that coincidence. That osdk [Go SDK] missing. And we run that. With the context. We run it again with the context that render back that beauty agent knowledge. And what matters is the delta. And so you have then an operator that will run the judge. To score based on those criteria. So of course here I want to show a success story but that's the in one. The idea is that for that go plan scenario without the pack we fail at 67 every time the go sdk was missing from the agent work. Whereas with the back it was always passing even after repeating the same task. So the idea is that. You don't repeat the same mistake. You. Just use looks back to. Feed the agent the right knowledge.

## Act 3 — Autonomy & voluntary task picking

I don't know how much I have remaining. I will keep it very short.

Now the last act if we consider that we have agent that are getting autonomous that can learn by themselves and inject nowadays by themselves. What stop us in some way is to get ready to make ancient neurons [agent autonomous]. Like one of the talk mentioned earlier there is a big vanity thing here because the agent is really tempted to please us and it's quite pleasing actually to have the agent that please us and answer in our direction. So I think one of the first psychologic psychological limits is just to forget about that concept of having someone that always in through [agrees] like you have to good suggestion. You need to get rid of that if you want to go to the bath habit on this agent.

And once you get rid of that you can start to consider to have task being created automatically like some agent that submit that create those tasks. Like do this fulfill this issue or do this PR review and you have that big bucket. With lots of tasks and you do some voluntary work. The idea is that you don't assign any task. You just have agent with some set of capabilities. And any of those agents can fire a task if it matches its capability. So it pre-picks voluntarily. And then what's interesting is that if you. Build on top of the previous work all those autonomous tasks. Always keep attribution alive. So it means that you build even faster knowledge building a test of correction.

So what matter is just that you as the human keep the goal, the judgment and the responsibility and the agents keep the continuity repetition. The boundless artwork. And even infrastructure exists. You can imagine identity that grows even more like a more interesting direction. You could have dedicated coder agents, some critic agents, some management agents. The at least that you can specialize agent that will pick the task and promise that they will fulfill it properly and then you can enable some sort of trust because those agents specialize a bit like individual contributors.

## Closing

So to conclude, I'll just leave you with that question. So what is your agents learned yesterday that your team still knows today?

And to finish a bit of self promo if you are curious or interested and want to have a look at the experiment I mentioned QR code that will lead you to the repository. That is just the whole infrastructure that I mentioned. So if you want to comment it, post it. However you want to do it. Please do. And if you try it, let me know. What broke or does not work. And that's it. Thanks for your attention.

## Q&A — MoltNet vs. mem-palace-like memory

[Host:] Thank you so much for that. Question. If anyone would like to ask anything.

[Audience member:] Thanks for the big talk. Is this parallel to Mem palace? Or is that idea similar to MoltNet

[Edouard:] or there is one component, the memory part. But honestly I did not spend most of my time refining how best the memory works, how best is stored and how best it can be retrieved. Because for me what matters more is that it's providing the committees and the tools for the complete workflow because I don't think memory isolation. Can answer that problem of sharing knowledge between teams.

## Q&A — Real-world edge cases & nuance

[Audience member:] One last one is I think the examples you showed is pretty good. But in the live developer it's not as simple as fix and then you attribute and then there's a chain of it. It's a lot more nuanced and as when you started using it yourself did you come across edge cases or nuances where that simple pattern might not work and you need to do some more complicated.

[Edouard:] It's not as instantaneous as I might make it appear that entry that captured the incident. It's still there, it lives and fix probably won't land on the same day. So the region tree [entry] is just here to stay. And here it's about having your workflow that will have the intelligence to pick the incident that already exists and compare with what already exists because sometimes it's just good to just accept that there is an incident and if it does not there is no recurrence. You don't care. It's just a one time one offer. But if it happens more often then it's time to we need to create some relationship and consolidate maybe your workflow. Thank you.

[Host:] Any more takers for questions?

## Q&A — Maintenance as code evolves

[Audience member:] Thank you so much for the talk. It was really interesting and I think the question I have is how do you approach kind of management and maintaining this knowledge base as your code base and product evolving maybe something that was true like a month ago is known.

[Edouard:] Nice one. Honestly not as much difference if you already use skills or this sort of things it's very similar in way because you have all those entries that you don't really bother and said you just accumulated knowledge. And it's when you start to build some actual render pack. That it becomes nude whatever because when those render them back down to kill them they are marked on five [markdown files] that are then converted into skills. So you maintain them kind of the same way as you would maintain scale in the modern workflow. So you have to run some regular evals with the model like your team is using. If they are not useful enough or do not bring any benefits then it dies. And if you still keep remembering benefits then you keep it. Answered a question.

## Q&A — How do you choose? Curation responsibility

[Audience member:] How. Do I choose? The. Minor. Ity? [the curation responsibility?]

[Edouard:] It's a mix that's curation. You will start manually at first because first of all you need to get use this new habitat in the workflow and I think every workflow before we should lend it to an llm. We need to master it as human because then you need to explain that llm how we issue two things and if you are not able to explain it how can we expect the length [LLM] to be for you. So we have the correction starts manually assisted by agent to fetch all the things that you would want to discover. And once you start to understand the better then you can start delegate that duration [curation] as well to at least.

[Host:] Have any more questions. I'm sure you can find Edouard about. Thank you so much. Appreciate it. I bring it in the plate. And to. Morrow.
