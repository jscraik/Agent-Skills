# Transcript — When Our PM Started Writing Code: What Merge Rate Taught Us About AI Adoption

> **⚠️ Source warning.** This transcript has **no per-speaker labels**. The vast majority is Tammuz Dubnov delivering the talk; the host speaks at the very start and during wrap-up, and audience members ask questions during the ~5-minute Q&A near the end. The source also contains substantial speech-to-text artifacts — notably:
> - "**animated**" almost always means "**AI-native**"
> - "**Tanya is a 204**" likely means "**Autonomy AI**" (Tammuz's company)
> - "**clamorous college**" / "**climate astrology**" / "**Calamarous Coding**" all refer to the same internal methodology Tammuz names but defers explaining
> - "**OS unco**" near the end is unclear — possibly "OS / agent" or "an OS / unco[upled]"
> - "**Tammuz I bought**" in the Q&A appears to mean the Autonomy bot author identity ("Tammuz / our bot")
> - "**Grana lamps**" at the very end is likely "Granola" (an audience member self-introducing)
>
> Do not silently "correct" these — preserve verbatim. When attributing, prefer "Tammuz said" for the main talk and "an audience member asked" / "Tammuz responded" for Q&A. Do not invent named attributions for questioners.

---

## §1 — Intro & framing questions

Good morning. Everyone. How's everyone feeling? To be honest, there's a tube strike. It's raining. I get it. I get it. But it's going to be a great day, I think. Starting with this session, which is going to be really interesting. This is Tammuz Dubnov. He's the founder and CTO of Autonomy AI. Doing some really cool stuff over there. And we're going to hear a bit about it. Anyone horror movie fan in the room? No, kind of unlucky because this is about when PMs start writing code. Over to you, Tammuz.

Y. Pleasure to be here. And that was the first time I got introduced to the horror story, so that was nice. A little refreshing. All right. We will be talking about PM's writing vote, but that's not the true essence of this, the essence of this is. Organizations want to become animated [AI-native]. How is this a part of it? And sisterly, how can you start measuring it as you try and push your organization to be more AI native and make those adoptions that are needed?

So before we start, the problems that hopefully. Hopefully not, but likely we all have anybody here have had proper conversation with the CFO, CEO of AI spendings. Wow. Okay, I have those. Like bi-weekly, like every other day would ask the same question. Okay. Good for you guys in that case. Right? Anybody here have PMs and designers opening the arts [PRs]? Solid. Actually, it's a great history. And next question. Anybody here know the merger [merge rate] on those PRs? You guys know I start opening our meaningful or crap for lack of better word. Okay, so that's going to be a part of the focus.

## §2 — What "AI-native" actually means

There. Everybody wants to be any [AI] native. If you don't want to be aggregated [AI-native]. I'm not sure why you're in this room. If you don't know, again, Just open up basically any news channel. But when I ask people, okay, what does a need to mean to you? Nobody can define it. It's not to me. Do you guys know what animator [AI-native] means? No, do you guys have an artist [AI-native?] means those are the big buzzwords. When I ask, nobody knows. Everybody wants to have harness. Everybody wants to be a native. When I ask them, what does that mean? They can't really answer. But the answer or the second answer I do get is, well, being an animated means that rpms are designers in our QAs, more people who've been pull requests. And that's somewhat true. But in my side, that is the symptom. That's somewhat being really easy.

So I'll give you my definition. For me, being AI native. Means that the person that cares, the person has the authority to make the decision. It's also the person who can do the work. That basically AI collapses the gap. Collapses the handover. You as a person who cares about eats an organization has the authority to decide about each organization actually do the work. By having ages execute.

## §3 — Why handover is the real bottleneck

Why that is really impactful and why that actually speeds up an organization is because the bottleneck for a while now has not been how fast can I write cod. E? The bottleneck is doing that they hand off. Then hey, as a PM, I have an idea design and please make a figma. Okay, let's talk about it a week after. Let's see if we're lying. Hey, I have this spectrum [spec]. I'm happy with. Your developer, let's factor into your sprint, get to this spring [sprint], next sprint, whenever we can work it in. Now that idea has waited. A spring [sprint] or two. And now I get to actually see it. And now I need to do the review and we're going to do pixel perfect iterations and we're going to notice you got this wrong in the ticket. I got this wrong to take it. We're going to start iterating and doing those really long handover processes. That slow down. The velocity choke it.

So even if people can write code really quickly. It doesn't mean that the features go out to users faster. And what you get when you do move towards AI native is the people who care. And execute with agents almost immediately. Can do those iterations on the spot. And then when they are happy with it, they can send off to a developer to review. And you basically have coupled in this aggregate, you've coupled in product review all before the developer even hears a word about the features supposedly. And that's what it means. It means graphs and stuff can be days or weeks to 13 minutes.

And what that means is an individual level is that everybody gets an upgrade. We have VMs [PMs] that don't really care about stacks. They care about the features. Well now they can actually implement and experience the features and tune them themselves. We get engineers that maybe don't care about the UI, UX, at least a lot of the engineers I know. They care much more about the system, the factoring how the components are built, how the dependencies are mapped out. Now they can start working on those. And we have the senior engineers that frankly want to work in architecture and solve bigger and harder problems. And selling. With AI native organizations, everybody can go and focus on the stuff where they really matter. And frankly, that's the stuff that they really care about.

And you can see that the data is moving that way as well. People are not hiring more workers to do more work. They're hiring more people to make decisions. And you can see that the rate of hiring project managers going up. Much faster than developers that are not going out. Because as organizations become more AI native, as they move faster. The bounding is the decision makers. And you want the people, repeated PMs, the designers, like to make that decision that will impact the user.

## §4 — Wrong ways to go AI-native — Uber & Microsoft cautionary tales

Now in the rush to become any, there's some people are doing it wrong. And you can be really, really expensive. Everybody heard of Uber when we're going on there? Okay, so this came out just to three or four days ago. Uber has increased the area [AI] spend since 2024. By 6x. Now that 6x growth was completely used within four months, they are out of AI budget for the rest of the year. And we asked them what the impact is. I've trained over 40 and made up everybody to get all the tokens we want. That's like the upward CFO conversations that you guys have managed to be on. You will get an answer saying, hey, costs are getting part of justified. People are more and more tokens. But me as a business leader, I'm not seeing how there's a link to actually moving faster. On features. And that's it. The really, really big gap. They're just throwing more llm compute that's not fixed organization. They actually move to be alienated [AI-native] and give the people can decide the ability to execute.

Microsoft. Kind of similar phenomena, they get really cloud code [Claude Code]. And now they're taking it away. Because just giving hot code [Claude Code] to more and more people in your organization is a wonderful way to earn money. It is not the right way to speed up the order.

## §5 — Where the tokens actually go

And now if we actually want to see like what is all these token budget, where it's going to be standard be done by analyzing over 2,400 companies and how they use AI. And you can see from. $100 that you spend on the only $18 actually goes to meaningful code that actually gets shipped to users. A lot of it goes to stuff that gets reward [rewritten]. Bugs are generated and you get this wonderful loop. I've spent more and more money in LLMs because of their own matters and basically how the model is traine. D.

## §6 — Right way — Shopify as positive example

Now, it's not a sad story. Some people are doing it virtual. Shopify is doing a great job in becoming more animated [AI-native], but the focus is not necessarily on developers. It's not about giving them. Higher than ex on cloud code. It's about empowering the rest of the organization. And again, the people that can decide their domain, the ability to execute their domain. So you'll see here when all in thousands of cursor licenses and when they actually measure the stuff that gets shipped from those non-technical individuals. How much of it is valuable, how much of it needs to be written, they said that 50% just gets accepted. It means that the quality is so high. That the work getting done by those non-engineers can actually emerge as is and doesn't go to the public that has to go and patch it and listen. And you see even the VTF [VP of?] engineering very clearly says the faster grain roots. Are not engineers. Everybody else that deeply cares about the organization and now connection.

## §7 — Wrong-vs-right patterns enumerated

So if we try and break down the wrong ways and the right ways, I'll give you what I say, that's the wrong place.

If you just. Give bigger limits and more spendings to the same developers on the same task, you will get a bigger budget. But you will get developers that aren't really interested in the tasks that you've given them because the same as before. And in my experience, developers to work on tasks that they're not interested in the agentic era. They'll just hand it off to an agent. And they will let the agent check itself and notice there's an issue and affix itself. I notice there's another issue and do effectively. Huge token consumption in a single session. For a bucket engineer. How they care would have probably seen me like, oh no, no, no, we went the wrong direction. Go this way. But the disinterested engineers will just hand it off and that the agent will endlessly because they don't really feel into consent.

You will give another way to understand. Is you will get pms and designers prototyping tools so they can prototype faster and they can create potentially thickness [Figmas?] faster. But that doesn't solve the big bottleneck of cup but handover. It just gets them to create a signal faster. And wait for the next for longer. It's like they argue saying the US hurry up and wait. Which can hurt. To wait.

And lastly, we've seen a lot of organizations give cloud code [Claude Code] to everybody. Now plot code [Claude Code] in the name is the word code. People that don't know how to really look at code, don't really know what to do with calculate. And getting into PMs and designers is a great way. For them to go to your desks every other day to say, hey, help me set up the environment. So growth. Hopefully then build the PRs that are thousands of lands and total nonsense. And basically ways for them to increase the PR fatigue that your death [dev] team is already feed. Ing.

And now that the right way is to do all this is actually take the tools that are tuned for that type of user. So cloud cover [Claude Code] is a wonderful tool for developers. There are tools for PMs and science [designers]. We specifically focus on as well. Tanya is a 204 [Autonomy AI]. It's not technical individuals. You move the person that cares to be the person that does the work. So pixel perfect work that you put on a developer that doesn't really care about how it looks except it's going to eat your token budget needlessly because they don't really care.

And lastly, you do not let go of your guards. We talk to organizations that have made a big jump to the AI native. And then we go top down. So we talk to the executives, leaders and organizations. And then on calls, they will find out new features. In front of clients that don't match the product. Not physically, not functionality. But everybody moves so fast and tries to be animated and runs forward and all of your guards, stuff that engineering principles have put in place over the years of experience is. Something you disappear. So it is really important to keep those in place. That's your quality assurance. That's the way to make sure that AI doesn't run forward and break your product and take in a totally different direction. And what you intended.

I'm not going to talk about it in this talk because there's not enough time. But personally, I adopted methodology and our organization is what we call clamorous college [Calamarous Coding], how you can keep those guards in while also moving quickly. I'm trying to put velocity without getting conflict. But the key here is. Same tools. Differently. The focus is on getting the people who care, the tools to execute.

## §8 — Harness engineering

And all of that confidence enabling those non-technical individuals to touch code base that can be brownfield can be extremely complicated, extremely legacy. That confidence comes from the harness. So again for the harness buzzword that not everybody knows, the world has defined it is basically harness. Means that you saw the agent make mistake and you make it unfeasible for the agent to make the same sticky game [mistake again]. You put in some sort of wall. To see that the next time that happened, the agent gets automatic feedback. Hey, you did this wrong. Correct. It.

And the important thing here. Is that the harness needs to adapt. The mistake is made. Mistake is realized. The harness needs to adapt to prevent that mistake from happening again. So it's not something that's supposed to be handheld. It's something you're supposed to grow and evolve organically. With more usage over time.

And so I'll tell you some of our principles as we do a lot of harness engineering training for our jewel [tool]. And everybody here works in an organization with the code base of massive code base. So you need the harness, you need the agents to actually know what the code is. You have to understand it, they need to onboard themselves. They do not need to abandon what to do. They need to be able to communicate with the user. You can't depend on the user to incur and say in this file and dispense of lines, let's work on it. You need to understand the product level language and what that actually translates into code. And they can manage really long sessions and keep them expressed. They need to be able to check their own work. To get automatic feedback loops at higher quality. With that, you also can know what good means and of course they need to prove. That's a key part of the harness.

So we personally put a lot of emphasis on all this, but in particular, I'm working with non-technical individuals. You need somebody to own the code and read the code. That's on the agent. You don't. Want to transit all those code constraints to the product. Every single time you talk to them. They want to even just know that inherently and factor it in. And you want the agent to check itself constantly. There's nothing worse than an overconfident agent. And finally, you want to learn not just from an individual session, but from all of your users in parallel so that the growth is actually exponential. And truly accumulated.

And the question I can get is that sounds amazing. But I just know that my code is really difficult setting it up. It's not actually going to work. And the answer is frankly, we've never knocked any of it anywhere. Everything is feasible. You just have to go about it the right way. Since we're talking about non-technical individuals, they care much more about the user facing. So maybe if you're super complicated, microcystin [microservice] architecture back in, it's not feasible to set up for them every time. Customer in front. If we can run setups that are crazy monorepo, nx, multi-rego [multi-repo] with like sibling libraries compiled so the agent may actually see it. And we've done with everything from security for like secrets to access private repositories and our factories [artifact registries] that contain like the core libraries that you need to actually run. So everything is feasible for anti-agents [AI agents] can manage everything now. We've not seen a case that's not tangible.

## §9 — Authority boundaries — the failed PR example

But it is really important to say the people that care can't do work. That they're not really authorized to do. And so there is very much client. Lyman [client / line management] sent his engineers most definitely have replaced me making the judgment calls on the actual engineering decisions architecture decisions that it be the back end. And having them focus again on stuff that they care about more. Whereas the non-technical individuals can focus on the user facing changes. Whether that's hanging stuff like copy to layout to new features to get a new x-ray [UX-ray? new UX]. And what that actually more or less boils down to is they can do the user facing the US [UX] work and you get your engineers to focus on what really matters all the IP.

Now this line sounds really nice. And potentially obvious. It is not so easy. It is more than expected that you will fail. The merge it rebuilding for is not 100. And knowing the line between a task that involves stacking and doesn't fall back in. Is not all that clear especially for somebody non technical that really wants to make any map.

So I'll give you an example from us. We had this VR [PR] and we close it the designer. Did a lot of work in the PR domain a little bit thousand lines. A new feature they want to have like an images through very specific part of the site. So somebody jumps through the versions. They can see visually what the other versions were. And the agent succeeded. And when they did the product review, it worked beautifully exactly like they wanted it. And as soon as it went into the developer, the developer said, oh, we're not going to merge this. And that was because then the agent made everything server side and stored the images there and basically the user came back the next day and just would be gone. Whereas the developer said, oh, we can't store this until we have an internal discussion, decide how we want to store them. It's going to be in the db or bang [bucket] in the bucket. I don't even know the answer to this. So there's no way we're going to go with what the agent decided for the.

And again, that's something for us that just meant this conversation got sped up. The developers talked about it the next day. The feature was. In, I think the meat [week] after and what the developer did is they took. This branch, took all the friends and all the us [UX] back. So not a sack tail [setback]. But the expectations shouldn't be, hey, 100%. If a pm opens a PRO be mad as a developers for not merchants, you want them to be that part.

## §10 — How to measure AI-native adoption

And so now the thing that really matters. From your data center is how do you measure it? I'll tell you how we do it across the hundreds of orbs [orgs] and thousands of PRs to get opened with us. And we can make the basis.

So the first thing to track is printing account [the count] of the pull request. How many are open by non-tax [non-technical] for individuals? And which individual? So you know that everybody is actually getting. Enabled and impactful. We have seen places where. Some non-technicals and a piano [PMs?] more confident they are some are more hesitant. You want everybody to actually feel comfortable. You can track that just by the count.

But beyond that, you want to make sure that you're not adding PRCT [PR count?] by opening nuts and steels. And that's where the nurture [merge rate] comes in. From our numbers, just so you're familiar, an average non-technical contributor in our organization in order. 50 hours, they're merging is about **74%** Which means that one out of four, they accidentally overstepped. And that's okay. That's not PR fatigue. That's totally fine. That's a level where we still have a lot of trust between the PRS they open and dev team the review. Set.

And lastly, you also want to measure how much extra work you're adding not just in terms of PR reviews. Sometimes developers will need to be followed work. The agent doesn't know. Future roadmap plans and refactors that are intended or whatnot. And there, how we do it is we measure from PRs that are open and merge. How many get merged without any dev interfering without them pushing more commits to fix change adjust. And again for us that is **84%**. So 84% of the PR submerged generated by non-technical individuals simply get merged. Which is a way to make sure that you are not. Increasing the burden on the dev team, not just from PR fatigue, but from tax perspective.

## §11 — Closing — democratising authorship

The moral of the story. The point of being handed [AI-native] is actually democratizing authorship so that the person that is accountable, person that has the authority is a person who can do the work. Without independent on a bunch of other individuals in the org and hoping that they do the work or waiting for them to do the work. And again, that's where the velocity, the disconnect between spending more and AI, but not feeling a faster feature of shipment. And that's where the gap is from.

And frankly, all you need is an OS unco is to make this possible. We're having, but you do want something that is absolutely coupled in your code base to enable all those non-technical individuals without getting the technical nature or plot code [Claude Code] and lots of proof. Okay. And that's it. Thank you.

Thank you so much. We will have about five minutes for questions. Anyone likes to ask and start over here.

## §12 — Q&A — measurement tooling

**[Audience question]** The metrics. Do you create your own tool to get those metrics? Because you know you have the last one, which is number of PRs that have zero death [dev] touches. Right. If your credit wants to be ours. How do you actually know which ones are. Being touched by engineering? You automated that you use an off the shelf tool. Out of you look at it ourselves.

**[Tammuz]** Our system looks at every part of the author is. Frankly the author shows up as the Tammuz I bought [Autonomy bot]. But there's a trace of the user that authored it. And then we look at the commitment [commit] stream for merch [merge]. So you know the last question made by the and then you see it for people actually push stuff to it that changed the code not just like emerging. And so that's how you can track it pretty easily.

## §13 — Q&A — do engineers move into UI/PM space?

**[Audience question]** Yeah, I was wondering if you also see this stuff moving the other way as well. So like moving the PMs more to the right. Do you have the engineers moving more into the PM UI feature space as well?

**[Tammuz]** So a few things. It's interesting that those kind of movement in both directions. One is. I'll talk a little bit about what our process with climate astrology [Calamarous Coding]. Yes. Developers want to move fast. As such, they don't want to wait for product decision, UX decisions. They want to be able to pay and build this feature in vendor [in here / inherent] works. These from my perspective. Let me get them in. And the way we're seeing or we work and we see some organizations work as well. It's basically that they let the developer make those decisions. We depend pretty heavily on feature types [feature flags]. So you say developer, go for it, make all your product decisions. Everything is feature flag. Why? Because we need to be able to merge it quickly. Otherwise it makes conflicts at a really rapid rate just because of it velocity. And then we let the people of German UX [the people who do design / UX] and nuances in the future in QA. They come and follow pull requests and to clean it up. So yes, we must definitely push our developers to make the decision and just get the feature out. And we feel very comfortable with opening follow up requests. So like a feature maybe like three or four puller bus [pull requests] and that's totally fine.

## §14 — Q&A — rollback / safety mechanisms

**[Audience question]** Do you have any rollback mechanisms for these features built in the system or registered outside. If something emerged, it blows up production. Do you have any alternative voice?

**[Tammuz]** We do dependent organizations like CI to some extent. Good and the bad is the agent's model or coefficient between all your coding standards and the components library and how you set up the environment. And we will write the same way that you write. So that means we saw organizations that wrote feature types [feature flags]. The agents automatically output feature flags. Organizations don't have that practice. We will not introduce that practice. On a more troubling note organization that don't have a lot of tests. We see the agents don't really add tests because I don't know practice. We're going to add like. A toggle up to force.

**[Audience follow-up]** You're not opinionated. You just follow the right.

**[Tammuz]** No, the harness is super lean to adapt your practices. That's what we saw with the organization prefer. Ence.

## §15 — Q&A — proving PR-fatigue cost to leadership

**[Audience question]** You mentioned a few times trying to avoid like a pig [PR? big PR?] on the side of engineering. Have you found any good ways that you can use to visualize or communicate the amount of time developers are spending on those things? Because we find definitely as product starts to write more features and put them all the hours in the dev teams end up slowing down because they're spending all the time reviewing things. That's quite hard for us to prove.

**[Tammuz]** I have the same challenges internally in my r dance [R&D / org] as well. And so a few things. One, when we develop this system, we optimize the agent to output his streamlines [streamlined] code. Data necessary [Add only necessary?] optimizing reads and we have a bunch of ways that he can model the co-release [codebase] and MC [MCP?] to actually find the components and reuse it properly. So we saw that that helps the smaller PRs. The less PR fatigue.

The issue with PR is if you just go to the pool passage, you say all of the same. And so what we did internally is we now have an agent in every token. It labels the risk level and the size. So you as an operating nine [opening a PR] polar questioning to you. You will see that three of those are low risk small. You will see that one is like extra large. And you basically have an easier way to manage it yourself. And it doesn't become as overwhelming as only about an nine PR. So, no, I have like three super small ones, two medium, one extra large. I'm going to put a lot of effort there. They also factor in the risk level and how much attention effort they put into it. So we started that one easier way for them to gauge. And two, for the teammates, they affected that. So when a nuclear [PR] is open, they see the amount of load on each developer. I get the size and risk and make sure that they transparently at the brain.

## §16 — Wrap-up & off-mic fragments

**[Host]** That is unfortunately all the time we have for questions. But somebody's empty [Autonomy] are here. They have a booth in the exhibition area. So highly recommend you grab them for a chat at some point today. Let's give to Tammuz out of the block [round of applause]. A couple of the sessions have moved rooms. Please double check what you're doing next. And yeah, make sure you're in the right place. Thanks guys.

**[Off-mic, post-talk fragments — speakers unclear]**

She should be coming. Just let her know you're finished. Thank you. Sweater. Like even soft. Ware [software] lines. So. Even for us, we can truly do that. And we're. Dramatically. Small stuff for the low risk stuff. Thank you. Thank you. Thank you.

I'll give them like a green field. I work at Grana lamps [Granola]. I believe we must also be so confined. But. I'm on a green scale [greenfield?]. Project. And I've been like a solo dev for. Like almost a year on this thing. I want to bring it. So I've been learning with agent review basically.
