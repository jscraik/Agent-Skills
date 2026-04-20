# Compound Engineering Anti-Patterns

Anti-patterns are common solutions to common problems that aren't really solutions at all. They are worst practices that cause more issues than they solve.

---

## Planning Anti-Patterns

### Death March
Continuing doomed projects without recognizing failure.

**Detection:**
- Team morale consistently low
- Estimates repeatedly missed by large margins
- No credible path to success
- Stakeholders asking "are we there yet?"

**Fix:**
- Route to `he-brainstorm` for honest assessment
- Consider project cancellation or major pivot
- Cut losses early

---

### Cart Before Horse
Working on B before A exists or works.

**Detection:**
- Dependencies not ready
- Integration tests fail due to missing upstream
- Work frequently blocked waiting for other components

**Fix:**
- Reorder implementation units
- Build dependency-first
- Use stub interfaces for parallel work

---

### Big Batch Syndrome
Large scope instead of small increments.

**Detection:**
- PRs with 50+ files
- Weeks of work without integration
- "Almost done" for extended periods
- Merge conflicts accumulating

**Fix:**
- Break into vertical slices
- Ship incrementally behind feature flags
- Integrate daily, not weekly

---

### Horizontal Slicing (TDD Anti-Pattern)
Writing all tests first, then all implementation.

**Detection:**
- Tests test imagined behavior not actual
- Tests break on refactor even when behavior correct
- Long time between running tests
- No working software until very end

**Fix:**
- Switch to vertical slices - one behavior at a time
- RED→GREEN→RED→GREEN cycle
- Run tests constantly

See: [[he-tdd]] for correct TDD workflow

---

### Vibe Coding for Production
Skipping specs for user-facing systems.

**Detection:**
- No plan or spec artifact
- Directly implementing from vague request
- "Just make it work" approach
- No acceptance criteria

**Fix:**
- STOP immediately
- Route to `he-plan` before continuing
- Production systems require specs

---

### Premature Optimization
Complex solutions for theoretical problems.

**Detection:**
- Caching before measuring
- Complex data structures for simple needs
- "What if we have millions of users?" (with 10 users)
- Optimizing code that's rarely executed

**Fix:**
- Measure first
- Optimize actual bottlenecks
- "Make it work, make it right, make it fast"

---

### Tool Trap
Assuming tools = culture transformation.

**Detection:**
- "We have Jenkins, we're doing DevOps"
- Tools purchased but workflows unchanged
- Automation without understanding

**Fix:**
- Tools enable culture, don't create it
- Focus on workflows and collaboration
- Measure outcomes, not tool adoption

---

## Execution Anti-Patterns

### Shotgun Debugging
Random changes hoping to fix without understanding root cause.

**Detection:**
- Multiple unrelated changes in single commit
- No hypothesis before changes
- "Let's try this and see"
- Copy-paste solutions from forums without understanding

**Fix:**
- Route to [[systematic-debugging]]
- Form hypothesis first
- Change one thing at a time
- Verify understanding before fix

---

### Doer as Checker
Same agent implements and validates without separation.

**Detection:**
- Bugs slip through review
- Blind spots in testing
- "It works on my machine"

**Fix:**
- Spawn separate reviewer agents
- Use [[he-review]] or [[he-technical-review]]
- Automated checks as independent oracle

---

### Permission Prompt Paralysis
Confirming every action slows execution to a crawl.

**Detection:**
- Flow constantly interrupted
- Waiting for user approval on trivial changes
- 10 prompts for simple task

**Fix:**
- Use `--dangerously-skip-permissions` in safe environments
- Git provides safety net (can revert)
- Trust the process, not individual actions

See: [[he-work]] for safe skip-permissions guidelines

---

### Copy-Paste Programming
Copying code without testing or understanding.

**Detection:**
- Code from StackOverflow pasted directly
- Similar logic duplicated across files
- "Borrowed" code not adapted to context

**Fix:**
- Understand before using
- Abstract into reusable functions
- Test borrowed code thoroughly

---

### No Rollback Plan
Forward-only execution with no recovery path.

**Detection:**
- "We can't go back now"
- Database migrations without rollback
- Deployments that can't be undone
- No feature flags for risky changes

**Fix:**
- Always plan rollback
- Test rollback procedures
- Use feature flags for gradual rollout

---

## Review Anti-Patterns

### Style Over Substance
Reviewing formatting when logic is broken.

**Detection:**
- Comments on indentation while tests fail
- Nitpicks on naming when algorithm is wrong
- "Missing period in comment" while function returns wrong value

**Fix:**
- Contract acceptance first (does it work?)
- Then style and polish
- Separate automated formatting from review

---

### Silent Drift
Code becomes source of truth while spec stays stale.

**Detection:**
- Implementation differs from plan
- "The spec is out of date"
- Decisions captured only in code comments
- Multiple sources of truth

**Fix:**
- STOP immediately
- Update governing artifact
- Spec and code must match

---

### Missing Verification Matrix
No explicit criteria for acceptance.

**Detection:**
- "Looks good to me" without testing
- No documented acceptance criteria
- Subjective "feels right" review

**Fix:**
- Define verification matrix in plan/spec
- Automated gates before human review
- Explicit pass/fail criteria

---

## Knowledge Management Anti-Patterns

### Skipping the Compound Step
Plan→Work→Review but not capturing learnings.

**Detection:**
- Same problems solved repeatedly
- Team asks "how did we fix this before?"
- Solutions in chat history, not docs
- Knowledge walks out the door with people

**Fix:**
- Always use [[he-compound]] for learning capture
- Document in `docs/solutions/` or `.harness/`
- Knowledge compounds when captured

---

### Lava Flow
Accumulated dead code nobody dares remove.

**Detection:**
- Commented-out code blocks
- Unused imports and variables
- "Just in case" code
- "Someone might need this"

**Fix:**
- Route to [[he-compound-refresh]] for cleanup
- Version control preserves history
- Delete with confidence (can restore)

---

### Documentation Decay
Docs become outdated and untrusted.

**Detection:**
- "Don't trust the docs, ask Sarah"
- Docs say X, code does Y
- Last updated 2 years ago
- README steps don't work

**Fix:**
- Update docs with code changes
- Treat doc drift as bug
- Automate doc verification where possible

---

## Workflow Anti-Patterns

### Manual CI/CD Gates
Too many manual approvals slowing delivery.

**Detection:**
- Waiting for approval to deploy to staging
- Manual test execution
- Human-gated quality checks
- Deployment queues

**Fix:**
- Automate everything possible
- Policy-as-code for approvals
- Progressive delivery (canary, feature flags)
- Trust tests over humans for routine checks

---

### Brooks' Law Misapplication
Adding people to late projects making them later.

**Detection:**
- New team members struggling to contribute
- Communication overhead increasing
- Velocity decreasing with more people
- "Too many cooks"

**Fix:**
- Add teams, not individuals
- Parallelize independent work
- Don't split established teams

---

### Death by Meeting
Planning replaced with synchronous discussion.

**Detection:**
- 50% of time in meetings
- Decisions made in rooms, not documented
- "I thought we agreed..." conflicts
- No written record

**Fix:**
- Document decisions in specs
- Async first, sync for complex discussions only
- Plans are the source of truth

---

## Quick Reference Table

| Anti-Pattern | Detected By | Fixed By |
|-------------|-------------|----------|
| Death March | Missed estimates, low morale | he-brainstorm for assessment |
| Cart Before Horse | Blocked work, failed integration | Reorder dependencies |
| Big Batch | Large PRs, conflicts | Vertical slices, daily integration |
| Horizontal Slicing | Brittle tests, no early feedback | he-tdd vertical slices |
| Vibe Coding | No specs, vague requests | STOP, route to he-plan |
| Shotgun Debugging | Random changes, no hypothesis | Route to [[systematic-debugging]] for root-cause analysis |
| Doer as Checker | Bugs slip through | Separate review agents |
| Style Over Substance | Nits while tests fail | Contract acceptance first |
| Silent Drift | Code != spec | Update governing artifact |
| Skipping Compound | Repeated problems | Always use he-compound |
| Lava Flow | Dead code accumulation | he-compound-refresh |

---

## See Also

- [[he-tdd]] - Correct TDD workflow
- [[systematic-debugging]] - Proper debugging approach
- [[he-compound]] - Knowledge capture
- [[he-compound-refresh]] - Cleanup and refresh
