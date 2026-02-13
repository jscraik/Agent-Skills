# ChatGPT Apps production checklist template

## 1) Context and scope
- Product goal:
- Primary user journey:
- Launch timeline:
- Platforms/modes (inline/PiP/fullscreen/mobile):

## 2) Priority mapping
### P0 (must-have)
- [ ] Lesson:
  - Task:
  - Test:
  - Widget change:
  - Tool-output change:
  - Owner:

### P1 (release readiness)
- [ ] Lesson:
  - Task:
  - Test:
  - Widget change:
  - Tool-output change:
  - Owner:

### P2 (iteration speed)
- [ ] Lesson:
  - Task:
  - Test:
  - Widget change:
  - Tool-output change:
  - Owner:

## 3) Flow map
- Widget -> Tool server:
- Tool server -> Widget render payload:
- Widget -> Model follow-up:
- Widget -> Model-context update:

## 4) Tool-result envelope
- schema_version:
- kind:
- entities:
- uiHints:
- nextActions:
- _meta usage boundaries:

## 5) Validation gates
- [ ] P0 tests green
- [ ] CSP/domain checks green
- [ ] Publishability flags validated
- [ ] Mobile smoke passed
- [ ] Risks documented with mitigations
