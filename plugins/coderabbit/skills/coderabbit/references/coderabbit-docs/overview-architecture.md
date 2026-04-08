---
source: https://docs.coderabbit.ai/overview/architecture
---

# The System Behind Every Review Comment

CodeRabbit Architecture | How CodeRabbit works internally

While other tools just scan your changed code, CodeRabbit **orchestrates an entire system** for every single review. This isn't a simple "review this changeset" prompt to an LLM. It's a **production-grade AI infrastructure** designed for one purpose: understanding your code at the deepest level possible.

![CodeRabbit Architecture](https://mintcdn.com/coderabbit/JDF48eE9RUTOwhLY/images/assets/images/architecture.png?fit=max&auto=format&n=JDF48eE9RUTOwhLY&q=85&s=b962fbb736c591ed9f7ba3adfe2cdcb9)

Behind each comment lies:

- **Sandboxed cloud execution** with your full repository cloned for isolated analysis
- **Multi-dimensional code analysis** combining 40+ static analyzers, linters and SAST tools
- **Agentic exploration** that autonomously investigates your codebase for context
- **Specialized AI agents** working in parallel: Review, Verification, Chat, Pre-Merge Checks, and Finishing Touches
- **Living memory** that learns from your feedback, PRs, issues, and coding guidelines
- **Enterprise integrations** connecting your entire development workflow

**That's why CodeRabbit doesn't just review code, it understands it.**
