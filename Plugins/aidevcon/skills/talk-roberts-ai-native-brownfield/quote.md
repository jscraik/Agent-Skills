# Notable Quotes — Katie Roberts

All quotes verbatim from `transcript.md`. Section names refer to the corresponding section in the transcript.

## On 100% test coverage being the wrong goal

> "I keep hearing people say, well with AI, all you need is 100% test coverage and you're done... I sat down and I asked AI agent to get 100% test coverage. It kind of wrote trivial tests that are like, I don't, you know, this is stupid test. I don't care about that."
— *Quality via testing; against 100% coverage*

> "we don't have a test for when the random number generator in the system fails. And I was like, yeah, I don't think I want to write a test for that."
— *Quality via testing; against 100% coverage*

> "75% of my code base is tests. Test coverage is between 75 and 100% for each file... You can still have a lot of tests without being really obsessive about 100% test coverage, which I think is not really the right kind of aim."
— *Quality via testing; against 100% coverage*

## On the test oracle pattern

> "I have 1500 tests that run against S3 and they lock down the behavior. Then you tell the AI, you have to do it exactly like that. And it's much better at doing things when it does that."
— *Test oracle pattern*

> "if you're writing a complex system, the one way to start is to write it really, really simple version that's kind of trivial that basically has the same behavior that you can use as a test oracle so that when you're building the more complex version, you don't make it break."
— *Test oracle pattern*

## On documentation

> "you think S3 is really nicely documented, it's got all these hundreds of pages of documentation. The documentation turns out to mostly be wrong. And every single detail, when you actually look at the details."
— *Test oracle pattern*

> "never trust anyone's documentation at all."
— *Test oracle pattern*

## On edge cases

> "writing some test cases for this, run them against s3 and found a 500 error. Which was repeated... clearly Amazon did not have a test case for this. And I did. And it actually gave me confidence that I was fine."
— *Edge cases*

> "When I put the AI at the docks and asked her to do the same thing, it was really bad at that. It seemed to not be able to look at docs and find edge cases in the way that I can."
— *Edge cases*

## On flaky tests

> "never have flaky tests with AI as my hard rule. Just fix them immediately."
— *Flaky tests with AI — the hard rule*

> "Sometimes it decides that the training data says that developers never fix flaky tests, so we ignore them."
— *Flaky tests with AI — the hard rule*

> "with the AWS test, it decides that I do this, changes their behavior every day. We'll just change the code to match again because we must match AWS's behavior."
— *Flaky tests with AI — the hard rule*

> "I currently have 5,000 tests that run in two minutes. And that's kind of two minutes is my kind of borderline acceptable."
— *Flaky tests with AI — the hard rule*

## On what tests can't find

> "You can't decide if your architecture is good with tests. And if you can't measure it right now, you can't really test it."
— *What tests can't find*

> "if there's a meowing noise, then it's giving you information that you need to know."
— *What tests can't find*

## On AI-built tracing

> "even just getting the AI to build. A hand-built hand maintained tracing framework was incredibly useful. You don't need to tie it into production system or something, but anything that can give it traces that it can look at to debug is amazingly useful."
— *AI-built tracing as a debugging tool*

## On AI performance engineering

> "I started wasting my time trying to actually make performance the same as something that's doing something we don't want to do."
— *AI performance engineering* (re: another S3 impl skipping fsync)

> "this is cheap low cost work and you just throw it away if it doesn't work. Don't do it just because it seemed a good idea and keep it."
— *AI performance engineering*

## On types over tests

> "ended up just telling you to fix it in the type system instead of actually trying to use tracing or anything to do this like having authorized request type that can't be reauthorized... once you've constructed it so you can't have to have a test for this anymore because you know that the types are enforcing it for you"
— *Type system over tests for invariants*

## On human in the loop

> "I view myself as part of the feedback loop. I have opinions and I'm here to find out what's going wrong... I've been not trying to automate things too much because I want to actually understand what's going wrong in order that I can because I'm responsible for quality and I care about the code and I want to know it's good."
— *Human in the loop*

## On refactoring

> "refactoring is part of the feedback loop. You don't feel you have to one shot things like you're converging on a better answer."
— *Lessons / closing*

> "your role is to is to be there and break things and get them fixed."
— *Lessons / closing*

## On the test-oracle tautology risk (Q&A)

> "you can end up in a situation where you turn out you're not really testing anything at all. That's not the same as the thing they're testing. And you need to have that sort of fixed guarantee that it's what you want."
— *Q&A — the test-oracle "tautology" risk*
