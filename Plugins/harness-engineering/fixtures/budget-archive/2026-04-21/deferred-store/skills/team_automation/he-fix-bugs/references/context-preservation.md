# Context Preservation

2. Reproduce and stabilize the failing behavior before proposing changes.
3. Trace backward from the symptom to the point where valid state first became invalid.
4. Test one hypothesis at a time, and for uncertain links require a prediction that can confirm or falsify the chain.
5. Present the root cause, proposed fix scope, and test recommendations before remediation when the request is diagnosis-first or confidence is still settling.
6. When remediation is in scope, check workspace safety, prefer failing-test-first validation, apply the minimal fix, and verify no regressions.
