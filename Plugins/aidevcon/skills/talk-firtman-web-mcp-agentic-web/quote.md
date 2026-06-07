# Notable verbatim quotes

> Line ranges below refer to `transcript.md` sections (§N).

### On the agentic-web framing
- *"agents want to build for the web"* — §2
- *"the web wants to run agents"* — §2
- *"users want to browse the web using agents agentic browsers"* — §2

### On the cost of today's techniques
- *"it is time, tokens, and context"* — §3
- *"agents are burning Belgians [billions]. When the browser is just a... guessing game."* — §3
- *"It's observing screenshots... I need to click there. I need to click on the date picker. Then I need to take another screenshot... So this is consuming a lot of the game. Tokens. And Context."* — §3

### On what Web MCP changes
- *"WebMCP will let the front end expose capabilities and not just fix it [pixels]."* — §4
- *"now we are passing from inference to a contract that we as web developer define. That's WebMCP."* — §4
- *"As a user with the UI, we have a contract. We are exposed to an interface to the agent."* — §4

### MCP vs Web MCP
- *"MCP is kind of connect an agent directly to the back. Servers, APIs, data, workflows."* — §5
- *"That's what we have Web MCP. That is kind of the way that we have to talk to the front end."* — §5
- *"it's not one or the other. It's actually both."* — §5
- *"The Web MCP... has access to the front end, and that means the current page... the whole user session. And every client API."* — §5

### Spec lineage
- *"Web MCP is to MCP as [X] is to Java."* — §6 (attributed to an unnamed Twitter post)
- *"it's a proposed standard API... from the W3C"* — §6

### Tool definition
- *"what's a tool... it's just can be a new function. It can be any form that you have in your website."* — §7
- *"The description should be... for Asians [agents]. So we need to understand that our customer is an AI agent. Not the user."* — §8

### Status
- *"tomorrow we will have Chrome 149, it's going to be an origin trial, meaning that you can start using it with real users."* — §7
- *"agents will fall back to any other technique if the tools are not provided by the website."* — §7
- *"Web MCP needs your work. So you need... It's not going to appear automagically."* — §7

### Design guidance
- *"use only one purpose per tool. So don't create tools that are overlapping."* — §13
- *"be state aware and register only when useful."* — §13
- *"Your consumer is not the user. It's the AI agent. So you can actually respond with technical errors... then the agent can iterate and solve those issues without any human intervention."* — §13
- *"try to return a small output exactly what has been requested."* — §13

### Doom demo
- *"So I did [a port of] Doom... and I added Web MCP to it... Play Doom. As a maniac. One minute... So... he is playing... use it while I'm sleeping."* — §11

### Adoption recipe
- *"you can pick just one high value page state that you have in your web app, and expose a read only diagnostic tool from that... Then you evaluate that with calls and arguments... Then you automate that using [Chrome Dev]Tools MCP or Puppeteer."* — §14

### Closing summary
- *"It will expose tools to the agent from the front end, not the back end. That's the diff with MCP. It will use the full browser context and you can use it right now with origin trial in Chrome for end users, or using Chrome DevTools MCP or Puppeteer."* — §15
