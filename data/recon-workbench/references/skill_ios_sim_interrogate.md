---
name: ios_sim_interrogate
description: iOS Simulator interrogation: simctl screenshots/video, Web Inspector for web content, Instruments for native behaviors.
---

Inputs:
- Simulator context (booted simulator), and either app bundle id or URL for web content.
- Goal + scenario.

Important:
- Safari Web Inspector inspects web content and WKWebView, not native Swift call stacks.
- Use Xcode/Instruments for native Swift/ObjC behavior.

Output:
- Annotate which evidence comes from media captures vs inspector exports vs Instruments traces.
