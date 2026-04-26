# Context Preservation

1. Reproduce and stabilize the failing behavior before proposing changes.
2. Trace backward from the symptom to the point where valid state first became invalid.
3. Test one hypothesis at a time, and for uncertain links require a prediction that can confirm or falsify the chain.
4. Present the root cause, proposed fix scope, and test recommendations before remediation when the request is diagnosis-first or confidence is still settling.
5. When remediation is in scope, check workspace safety, prefer failing-test-first validation, apply the minimal fix, and verify no regressions.
