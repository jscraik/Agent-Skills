# Transcript — The Reinvention of the Dev Team

> **Attribution warning.** This transcript has **no per-speaker labels**. It is a single-speaker talk by **Hannah Foxwell**, preceded by an MC introduction and followed by post-talk announcements (tube strike, drinks, etc.) made by an event MC — not by Foxwell. Treat content between the MC intro and the closing "Thank you" as Foxwell's words. Do not attribute the post-talk announcements to her.
>
> **Transcription quality.** The source has many speech-to-text artifacts. Known/likely garbles include:
> - "reinfection of AI addiction" → *reinvention of the dev team* (the actual talk title)
> - "vulgar" → *velocity*
> - "robot" → *ratio*
> - "live coding" → *vibe coding*
> - "NBIM" → likely *n8n*
> - "Andrew new" → *Andrew Ng*
> - "Davos summit" → likely *AI Dev Summit* / *DevDay* (context unclear)
> - "tapas tea" → *tapas team*
> - "broken cone" → *broken comb*
> - "Hem" → likely a customer/conference name (unclear)
> - "Bib" → the product name as she states it; treat as given
>
> Preserve garbles verbatim when quoting; flag with `[likely: X]` if helpful.

---

## §1 — Introduction & framing

I think it's. One more big cheer for Hannah who is going to come onto the stage now, Foxwell. Is an. Independent advisor, writer and creator founder of AI for the Rest of Us. Creating accessible AI learning experiences for everyone regardless of their role or background. And we're going to be talking about the reinfection of AI addiction. Nowhere is the end of the day, it's all good.

Hi everyone, thank you for going towards the end of the day. I'm going to be talking about agentic software development, but I'm not going to be talking about the tools or technology. We'll be talking about what it means for our teams and how we organize ourselves with these new capabilities.

So ever since I started working in tech. This has been the fixation of every manager or engineering leader I have ever worked with. How do we get more velocity from the developers in our organization? We even call it vulgar today. We even track it in story points. And I feel like right now today. The velocity that we've been yearning for is here. It changes everything. And for a lot of teams, we don't quite know what to do with it yet. We don't know. We don't know.

I've been through these transformations that have impacted our velocity. I've been through cloud transformation. We plant, we didn't have to wait weeks for a survey to run our software. I've been through DevOps transformation, which means that we automated the path to production. We didn't go through week-long test cycles. And everyone knew organizational challenges, new patterns for success. And so what I'm very, very interested in right now is what agentic software development does. Now that we've unlocked that massive next step of velocity.

We view the words around it. Just a couple of years ago, you would have been on the stage and you would have been talking about developer experience, developer productivity. There are whole conferences organized around it. I think that dialogue has a kind of frightened now. It's like we've got the velocity that we've all been wanting. And now we have to figure out what to do. With it.

## §2 — The agentic maturity ladder

You may have already seen this slide because you must have had it in his deck. I stole it from him. But this is team behavior sort of like levels of agentic co-maturity. We like we start at the bottom with like a narrow IDE agent. So we get all the way down to level eight, which is like an agentic dream. So something like a gas town, something where like it's pure agentic development.

And we're all on a journey and I want to just reassure everyone that if you're still over here, but like level two or three. That's. Absolutely fine. And normal. Like I don't know many people who are operating at level eight and I certainly don't know anybody who can say creditably that they're doing this safely. So we are all on a journey. But I do think that it is we're keeping an eye on these things because this is what the future could look like for all of us.

Earlier this year, Cursor published their blog post talking about the third era of software developments. And this is when their platform on their coding platform, agentic task started to supersede the top completes and accept. And so whether your team is doing it or not, this is a clear signal that this is the way that software is being written. These are the metrics that show us the whole map platform, agentic software development is superseding type of things in other forms.

## §3 — Three anchors

And so let's talk about what it means for our teams. And so when I start to do thought experiments about and how to reason about this, I try to go back to basics. I try to think about like what things do I believe will be true no matter how good the agentic agents get. And so these are my three anchors that I use to navigate the change.

The first one, we need to build something worth building. The second, I believe speed requires safety. And the third one, and I hope there's no disagreement on this one. People matter.

## §4 — Anchor 1: Build something worth building

So I'm going to start. I'm going to get straight into it because. I believe that we always, always must pursue the outcome and not the task. We always build something with them. We must be solving a problem. We need to be clear on the problem that we're solving. The code is how we solve. Our problem. It's not the what.

And so when you think about organizations, the typical organization today, what you have is you have a load of users and they have a problem. And then there's usually a person whose job it is to understand that problem and translate that into requirements. We then deliver it by developers using code. The solution to that problem is shipped as a product and it uses will benefit from that. And if you do a good job, you can do it this into your business.

And the way that things drug to themselves is that they're usually far, far, far too many user problems that anyone can solve them. So you filter them. You filter the noise. And the product manager filters that noise and tries to get the maximum value out of the product that they can. They make decisions about what to build and what not to do. And that doesn't change.

But what has changed is the pace at which we can solve problems. And so what I'm seeing is I'm seeing actually like the pace that we can address these problems in the development team creating what I call back pressure in product. The speed of decision making, the speed of analysis is actually not able to keep up with the pace of software development in a typical team.

And the right answer is not to just build more faster. But intrusification is a thing. If you say yes to every idea and to every user request or product will come bloated, your impact user experience. And eventually your product will actually suffer. And so. By seeing yes and building everything isn't the right answer either.

But one thing is true today and is new for us as an industry is that it is becoming increasingly cheap to test our ideas with real prototypes. And previously because life sat on both sides of the fence. I've been in product and I've been in engineering. And so I've been on both sides of the negotiation of like what do we build next? So as a product person it was really difficult to justify the investment in building a prototype where you had a freelier backlog. Like are we going to test this idea? Your code or am I going to try and figure out how to test my IDs and the way. But that is no longer true. We can prototype or we can do it quickly and deeply.

So what does this new robot like? We have to make sure that we make a good informed decision about how to deliver the maximum value through the software that we're creating. And so what I've seen is a few different manifestations of this.

The vibe coding product manager is for sure here. That product manager is building prototypes themselves and they're testing the ideas to make sure that the work that's funneling through to the dev team is am I getting away from a live coding product? Yes, yes. So yeah, so the work that flows through to the depth team is validated by a real working prototype and that's a very powerful pattern that I'm seeing.

If your product manager isn't comfortable prototyping and what you can do is you can move developers to be more front facing, to be more explorative and to partner with your product team on validating that you're building the right thing. Before it goes to the rest of the dev team that we're going to work on productionizing that feature, once it's proven to deliver value.

Another pattern that is becoming very, very widespread. Is the forward deployed engineer. Now a forward deployment isn't a sales engineer, they're not a speech architect. They're an empowered engineer that sits side by side with the users. And if they see a gap in the product, they are empowered to fix the product and deliver that value to that user. So you're actually really, really, really reducing that feedback move from user to product. By embedding an engineer side by side with your users. And it was only just a couple of weeks ago that there was announcement from Google, but they're building the capability of all deployed engineers to go and do this with their AI product. S.

Another thing that works particularly well for reducing that feedback loop between users and engineers is the idea of a product engineer. Are there some fantastic writing by Incident.io on the role of product engineer. But these are engineers that don't need to ask permission of a product manager go and improve the product. And this pattern works incredibly well if you're building products for software developers. Because you have that user empathy already. You're building for yourself. You are the user persona. And so teams like Incident, they're building products for software engineers. And so they have that in place. So they are empowered to go and improve the product.

So. When we talk about team design, like I work with a number of startups and one of the startups I work with, they hired your typical engineering team. So they've got some pretty funding. They hired like six engineers. And what became apparent very, very quickly is they just ran out of well qualified work to deliver. And I think we really need to challenge like what we considering normal development team. Because at the moment this normal development team of sort of 60 to 8 engineers in a single PM, it feels imbalanced. You end up with bottlenecks, especially around decision making.

And so what I've seen some folks do is experiment with different ratios. Two developers to every product manager. And one of the companies that I've seen experimented with this is called NBIM. So everyone who's experiment at the moment, that different ratio, the one that we're not used to, to see whether or not that can unlock more value, putting more product people per developer on the team.

Earlier this year, Andrew new was speaking at Davos summit. I'm proposed that actually the typical dev team might have even looked something like this. Two product people to a single developer. Because the speed of decision making is such that a single developer can keep on top of a backlog driven by two product managers. Who knows? Like, I don't know, I'm not up here advocating for any of these. I'm talking to you about what I'm seeing, people experiment with to unlock the velocity that agentic development gives them.

I also sat down with the CTO of consultancy because I thought that would be really interesting across a broad spectrum and lots of different development teams about how AI driven software development is impacting them. And what was really interesting is actually like they're not reducing team size, but they are expecting far more output. Only two or three have actually intentionally reduced team size because they feel like they have too many people. And, you know, this is one sample and we can look at the news and we can see in the news all of these various realms of layoffs that companies are doing and everyone is sort of challenging themselves. And I don't think it's necessarily about reducing headcount. It's just making sure you have people in the right places doing the right work. And I think the dynamics of our teams have absolutely fundamentally changed.

So I spent last year working with startups and this year I was. Like, I spent too much time helping them be successful. I want to have them coming myself. And so I started to build a product. It's called Bib. It is a base image management platform. So it's a platform that manages your container base images. And the hypothesis of this product is that zero CVE base images are becoming the new normal and that most organizations at some point in the near future will transition from the container based into these into day two a zero CVE version. So while you do that, why not have a platform to automate it for you?

So we are a two person team, a ratio of one developer to one product first. And I'm wearing the product hat. And I felt the new pain of this extra velocity in a very, very real way. So we gave ourselves two weeks to build these sort of MVP, the first iteration of this product. And on day one. We decided what we were going to build that week. And on day one, we finished by lunchtime. And so it was like, how brilliant.

On day two, I was actually, I was catching a train to London, so I was chatting to steal and we were like deciding what we should build. And I was on the train platform and I got a text saying done 11 a.m. And 11 a.m. and I love to think about that. And oh my gosh, what could have looked like? If work just existed between 9am and 11am and then I got the rest of my day free. Wouldn't that be fantastic?

But I think it's a common theme that I've heard across a few of the talks here is that actually there's this unlocking of this velocity. It makes us more ambitious and we have to be more ambitious. And so we had to relearn, like I had to completely throw out a lot of my product toolkit about ruthless prioritization, about slicing up features. I had to think way, way, way ahead about what the end goal of this product was and how I wanted it all to work. Like instead of focusing on one thing, I must think bigger.

So that's what we did. We gave ourselves two weeks to test an idea. We tested our idea at Hem, the idea seemed to be very well received. And so we were able then to make an informed decision about actually we're going to invest more time in this product idea. And so from my own like kind of real lived experience, I feel so excited about this new era of software development because you can test every idea. You can make more informed decisions. Like I haven't had to go and knock on the door of a VC and say please give me money because I've got a good idea. I've actually been able to build a plane and test that it's a good idea.

And so when I think about team design and I think about how we make sure that no matter how fast we get, we always build something we're building. We always build something that has an impact.

**Here are the things that I'm keeping. Here are things that I'm trashing and here are things I'm trying.**

So I'm keeping empowered product teams. No one should have to ask permission to help their users. Absolutely fast feedback with real users is your superpower. You have to really understand the problem that you're solving. And I think when everybody is empowered to build and everyone is empowered to build quickly. User experience and usability are going to be your different changes. So don't forget about those.

I'm absolutely trashing the two pizza team. And my six month roadmap. I was at a conference earlier this year and someone suggested that we start calling it a tapas team, which I really like the teeny tiny tapas tea, the small plates. I like that a lot.

And I'm trying the forward deployed engineer model, the empowered engineer that sits side by side with the customer. Love that. Product engineers. And I think that's a very powerful one if you're building dev tools. Prototyping and testing your ideas quickly fail fast if it's a bad idea and then smaller teams for sure. Really thinking about the right ratio of developers to product people to keep that flow of ideas and value moving smoothly through your organization.

## §5 — Anchor 2: Speed requires safety

My next anchor. Is that speed requires safety. So we can go very, very quickly and we can break things. But your users aren't going to thank you for that. And so I think the second pillar is about how we move quickly and do it safely.

The path to production is so, so important. And I think the evolution of how we engineer our pipelines and our past production and the platforms that support them are going to be differentiating. And if you have these capabilities already, you're going to be able to unlock a lot of value from agentic software development.

But what I've seen happen in a few places is that actually what was a kind of smooth process from idea into production becomes a little bit of a car crash. So where after the code is written and before that code delivers value to users. And so if there's any manual steps on that path of production for yourself where you're going to end up with a pilot, whether that be code reviews, whether that be your testing suite, you're going to end up with a bottleneck somewhere else.

And so investing in your path to production, your pipelines for automation is so important to actually leverage AI for software development. It's a forever truth that like high confidence requires testing. And if you want high confidence quickly, you absolutely have to automate that.

One of the blog posts that I particularly like, and this was actually from last year. So things may have changed was from AWS about how they had to completely rethink their path to production, to be able to get the extra velocity and to get the volume of code that the software developers were delivering safely into production. And I think if your organization hasn't started to think about that, started to map up how to reduction, look for those bottlenecks, think about investing time in optimizing it, then this is my sort of advice to you. I think that problem might not be manifesting today, but I feel like it will eventually.

So getting your pipelines in order is super important. There's really good news here. And that is that AI is fantastic at writing tests. So if you have manual testing or slow testing on your path to production, then this is a really fantastic use case. We're using AI to improve your software development capability. And there's a red case study from JP Morgan that talks about how they are using AI to do continuous component testing. Making it safer to deliver a larger number of changes into production because you have that enhanced test coverage.

So again, when we talk about like, we talk about your team of developers today, you might not need all of them working on features right now today. What you might want to do is split that team and have some folks focused on pipeline. Some folks focused on test coverage. Something that makes it safe to move quickly.

I don't need to read that back quote. So yeah, like in my experience, the cost of day two is always greater than day one to scale and maintain an application that has real users is going to cost you a lot more in the long run than just getting version one of that application into the hands of users. We don't talk about it enough really.

Users also care about this stuff. Like you're never going to get a feature request that comes in and says like don't be shipping any vulnerabilities, but they expect it. Like they expect it from you. And reliability issues will make the news, especially if you're on popular platform. And so investing in reliability is super important.

We must always, always balance velocity with reliability. Because our users may not care about us shipping a hundred features every month. What they care about is you actually doing the thing that you said you were going to do and doing it reliably and safely. Again. Very few customers will come knocking on your door and say make sure you're secure. They expect it of you. And so good security tends to be invisible. It's an absence of problems. And what I have found is that like good security is invisible bad security is an absolute reputation killer.

So these are areas where we actually want to be investing time. And like in the past. Having to negotiate the time on the backlog to do that important work was always a trade-off. Do we build this feature? The users are asking for do we do this important invisible work? Now we don't necessarily have to make those robots. We can do it all. We should at least be trying to do it all.

Practices like progressive delivery that make it safe to deliver a large amount of change into the hands of your youth is are super important. So I'm talking about things like feature flags. So that you decouple feature delivery from the actual deployment of the software. I'm talking about blue green deployments where you can actually have a new release being used by a subset of your users. Progressive delivery will make it much, much more safe for you to move quickly and deliver a lot more change to your users. So if you haven't got those capabilities in your platform at the moment now might be the client to try it out.

I said that we always need to balance velocity and stability and luckily we already have a language to reason about this. So I will advocate for site reliability engineering forever. Having SLIs, serious level indicators that tell you whether your product is doing the right thing for its users, objectives about how often it has to work to be your user's needs and error budgets, the amount of kind of forgivable failure in the system. By getting these things in place, by measuring them continuously, you can have a better dialogue about whether or not you need to intentionally slow down the amount of change that's going to shift to your users so that you can make sure that you're always meeting their expectations on reliability.

And so when I think about the future of organizational design, I'm seeing a future where actually platform engineering SRE are even more important than they were because they unlock the velocity of the development teams who are serving users and the development teams who are building features. So platform teams who make it safe to move quickly using automation. And SRE teams that can act as internal consultants helping teams invest in reliability so that you can deliver with this velocity, but you don't do it at the expense of your availability and your performance of the product.

So I'm going to talk another little bit about being my experience of my two person team building my first product. So like I said, we have the first version of the product ready in two weeks. So what do we do after that? I can honestly tell you it looks hell of a lot like platform engineering, reliability engineering. Like there was not a lot of feature development. It was about scalability, security and doing it right. So whilst it was cheap to actually build like a functioning application, what then took the time was making sure that application was ready to scale and that it was safe to do so. So this is my kind of like my own experience of where the time went. It wasn't in feature delivery at all. It was in making sure that that platform was robust enough to be used by real enterprise customers.

And so when we talk about our organization design and the humans, like I can see a world where actually at the moment I find platform teams, SRE team, security teams, they are massively outnumbered by the number of developers who are focused on features. I can see that balance shifting. I can see an increased importance for the platform and the SRE capabilities because they are the people who unlock the value of those feature aligned teams.

**So what are we keeping? What am I trashing and what do I try**

are definitely keeping SRE practices, progressive delivery and internal platforms. These are things that they can save.

I am trashing anything manual on my path to production. That doesn't mean we can't do manual testing. It just can't be on the critical path.

I use things like feature flags to make sure there is safe to ship something buggy and that reusers won't notice. And I'm absolutely going to be addressing tech debt using AI. I'm going to be trying to improve my test coverage, make it really easy to spot issues. I'm using AI to accelerate my migrations, my refractors. And I'm definitely looking at bringing back the SRE team as internal consultants that can help teams invest in reliability.

## §6 — Anchor 3: People matter

Now as I wrap up, my third anchor is actually probably the most important and it's the people matter.

And so as we. Reinvent our teams for this new age of agentic software development, it has to be done with people in mind. We have to create jobs that are worth doing. And the first thing that I'm going to controversially say is that fluid code that was written by thousands of lines of it. It's not fun. It is not a very fun job.

And so I've got a very keen eye on the organizations that are trying new things. Like instead of having a massive pilot of code reviews, what are they doing instead? There's a couple, there's a couple of organizations that have publicly said they're not doing mandatory code reviews. That doesn't mean that they don't do cope reviews. It just means that they're not doing them in mandatory way on every single change.

Some of these organizations are actually shifting left on the peer review. So previously a code review would actually, you know, go to a senior engineer who would spot issues with it. We're now shifting left to maybe at the point where you write the spec for the agent. You're shifting left that decision making and that oversight and that peer review to make sure that you're building the right thing.

I really like this quote by Joseph Ruscio. *"The mistake would be to treat unread code as a failure of discipline rather than a signal that the discipline itself must change."*

And again, I don't have answers here. I just know that asking engineers to review thousands and thousands of lines of AI authored code is going to create a lot of very unhappy engineers. And so we have to figure out another way that we can build quality assurance into our process without creating unsustainable work.

Another thing that I know for sure. People are not going to want to do is to support a fragile service. An agent cannot hold the page in. And so this is one of like the infungible sort of things that I believe like engineering teams need to navigate. And it's who is owning the service in production.

Because on call is still a thing. But you have to have a sustainable on-call rotor. You can't have a single engineer being on call all of the time. That's not fair. That's not right. That's not sustainable. And so when I think about how small we might be able to make our teams, this is the thing that I keep coming back to. It's like what is the most, the smallest team that you can have a sustainable encore road. And I think it's four people. Four people capable of supporting them that product in production because you always have a primary and who is on the secondary and you can't be on call more than 50% of the time. I know a lot of people who wouldn't even want to be on call 50% of the time. So like the minimum viable human like is going to be dictated by some of these roles.

I think I said at the beginning, like when we were building Bib, we absolutely like we ran out of work on day one. We ran out of work on day two. I think the thing that I would urge folks to challenge is a lot of these ceremony that we surround our development teams with. Might not be adding value or it might not be adding value anymore. And some taters it might be slowing us down. The sprint flying that only happens every two weeks. Is that the right pace of decision making that we need?

Do we have any and do we have any managers in the room? Yes, managers. It's a tough time to be a manager of software engineering teams. Because we don't really know what the role of software engineering is evolving into. But one thing that I'm going to urge you all to do is to go and watch a talk by Sophie Weston from Kukon last year where she talked about the broken cone. Instead of the T shaped folks, develop people who have a broad understanding and a few various areas of depth. And when you're doing career coaching with folks, think about the skills. That they may need that were that will help them. Think about what I've talked about. It's like, do you have engineers who are going to lean more towards product or are you going to have engineers who are going to lean more towards platform? And can you help people develop those skills that we really need right now?

I am almost out of time, but I think one of the things that I like to do, I like to imagine the team that I would build in the future. And the one thing that is absolutely critical for me right now is user empathy. If you hire someone like and they can't sit down with a user understand their problem and design a solution that solves that problem, then that person is going to become a bottleneck. They're going to be spoon-fed requirements and that has become normal in our industry. And I think that's a practice that needs to end.

And so you'll be very relieved to hear this is my final slide. People matter, like I want to make sure that every engineer has a sustainable encore router. I want to make sure that we have a language to discuss like our error budgets and our availability targets and invest appropriately. And I want to do realistic career planning from the skills that we need today, not the skills that we needed yesterday.

I'm trashing heavy planning processes, two weeks sprints are absolutely too long right now. And mandatory cope reviews feels like an unsustainable practice that's going to need to be replaced with some other ways of assuring quality.

I'm definitely shifting left on peer review. Using spec driven development and I'm going to encourage all of you in this room and especially the managers to think about how we create people who are less T-shaped and more of a broken code. People with a diverse areas of depth because those are the sort of people who are going to thrive in this new age.

## §7 — Close

We are all on a journey and we do not know where we're heading and I find it exciting but it can also be daunting. And so as you leave here, hopefully I've given you some ideas. To experiment with or to help you address some of the new challenges. I would just urge all of you to experiment with empathy because it is not an easy thing. To change your discipline so fundamentally and at such speed. So yes, we do need to try new things. We need to share our learning. But do it with people. Don't do it too.

Here are the things that I'm keeping no matter what, no matter how good agents become, I'm always going to build an organization that focuses on the user, build something worth building, solve a real problem. I'm going to be investing in ways that we can move safely with speed. And I'm going to always, always focus on the people because people matter and we need to create teams that are joyful. To work in and careers that are worth pursuing.

So that's me. I'm Hannah. Come and find me for questions over a beer. I will release you now. Thank you.

## §8 — Post-talk announcements (event MC — NOT Foxwell)

> The following is the event MC making housekeeping announcements after Foxwell's talk. Do **not** attribute any of this to Hannah Foxwell.

How will. The outside. Beers? I. Am the bearer of bad news. I'm afraid that tomorrow the troop strike is going ahead. So I'm making sure you all know about this. The circle of pink dilligans will be shut down and part of the metropolitan line in Samantha be suspended. Other lines are expected to run unplanned, but they will be reduced service. So just be aware of that. Check out how you're going to get here tomorrow if you need to. But it's worth coming in because we've got over £3,000 worth of giveaway at the closing section.

Other things you need to know. Recordings of all the sessions of all the other tracks will be made available soon for today and tomorrow. The workshops are probably booked. There is a waiting list. You can get on it. QR on the waiting list. People aren't closer to people on the waiting list. We don't know how many. And if you are going to the workshops and you've got to make sure you get in there early if you get who you want to be there. And if there's a demand for a specific workshop, they will try and rerun it for three in the Tess.

There is a quality now outside the front door. You will not be able to get away from it. You will have to walk through it. There is wine, beer, cocktails and soft drinks. And because of that tomorrow starts at 10 a.m thank you very much. I mean, maybe I'll see you tomorrow.

About the range. Thank you so much. I'm here tomorrow for most of the day. So you'll get to have your friend. I know what fancy competition is now. In the Bib area. You see, they didn't tell me that. Yeah, just like your own place. Yeah, so I'll be there. Yeah. I've come down from Manchester, so. Manchester, actually in the midlands, I'm from north. Anyway, thanks very much for today. You too, Dan.
