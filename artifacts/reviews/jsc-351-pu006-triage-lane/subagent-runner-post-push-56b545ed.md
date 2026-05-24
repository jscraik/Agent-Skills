# PR #196 Governed Triage Report

## Summary

- status: blocked
- repository: jscraik/Agent-Skills
- expected worktree: /private/tmp/agent-skills-jsc351-pu006
- expected head: 56b545ed3996aeeb12d1265fdcfea9b7217845b2
- checked at: 2026-05-24T01:48:55.315098Z
- can progress under governed workflow: no

## Worktree Identity

- pwd: /private/tmp/agent-skills-jsc351-pu006
- branch: codex/jsc-351-skills-sdk-service-boundary
- local head: 56b545ed3996aeeb12d1265fdcfea9b7217845b2

## PR State

- PR head: 56b545ed3996aeeb12d1265fdcfea9b7217845b2
- PR state: OPEN
- draft: True
- mergeable: MERGEABLE
- review decision: 
- submitted GitHub reviews: 0
- inline review comments: 0

## Blockers

- independent_review_missing: submitted GitHub reviews returned []

## Safe Next Action

Do not start the next implementation slice. Resolve the blockers above or record an explicit governance waiver that names the waived controls and residual risk.

## Command Evidence

### pwd

- command: pwd
- exit: 0

stdout:

    /private/tmp/agent-skills-jsc351-pu006

stderr:

    (empty)

### branch

- command: git branch --show-current
- exit: 0

stdout:

    codex/jsc-351-skills-sdk-service-boundary

stderr:

    (empty)

### local_head

- command: git rev-parse HEAD
- exit: 0

stdout:

    56b545ed3996aeeb12d1265fdcfea9b7217845b2

stderr:

    (empty)

### status

- command: git status --short --branch
- exit: 0

stdout:

    ## codex/jsc-351-skills-sdk-service-boundary...origin/codex/jsc-351-skills-sdk-service-boundary
     M Skills/agent-ops/goal-governor/SKILL.md
    ?? Skills/agent-ops/goal-governor/scripts/write_pr_triage_report.py
    ?? Skills/agent-ops/goal-governor/tests/test_write_pr_triage_report.py
    ?? artifacts/reviews/jsc-351-pu006-triage-lane/subagent-post-push-56b545ed.md

stderr:

    (empty)

### pr_view

- command: gh pr view 196 --repo jscraik/Agent-Skills --json number,state,isDraft,mergeable,reviewDecision,headRefOid,headRefName,url,title
- exit: 0

stdout:

    {"headRefName":"codex/jsc-351-skills-sdk-service-boundary","headRefOid":"56b545ed3996aeeb12d1265fdcfea9b7217845b2","isDraft":true,"mergeable":"MERGEABLE","number":196,"reviewDecision":"","state":"OPEN","title":"refactor(jsc-351): extract skills sdk service boundaries","url":"https://github.com/jscraik/Agent-Skills/pull/196"}

stderr:

    (empty)

### checks

- command: gh pr checks 196 --repo jscraik/Agent-Skills --watch=false
- exit: 0

stdout:

    Analyze (javascript)	pass	1m26s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639610/job/77562868214	
    Analyze (python)	pass	2m29s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639610/job/77562868219	
    Artifact secrets pre-check	pass	19s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639613/job/77562868207	
    CodeQL	pass	2s	https://github.com/jscraik/Agent-Skills/runs/77562927408	
    CodeRabbit	pass	0		Review completed
    Gitleaks (secrets scan)	pass	15s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639613/job/77562868218	
    Scan	pass	36s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639627/job/77562868184	
    Semgrep (SAST)	pass	1m8s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639613/job/77562868210	
    Semgrep OSS	pass	2s	https://github.com/jscraik/Agent-Skills/runs/77562915891	
    Socket Security: Project Report	pass	6s	https://socket.dev/dashboard/org/jamiescottscraik/sbom/5864a049-c4ca-4541-83c3-7e03791acad0	
    Socket Security: Pull Request Alerts	pass	3s	https://socket.dev	
    Trivy	pass	1s	https://github.com/jscraik/Agent-Skills/runs/77562893039	
    Trivy (dependency CVE scan)	pass	37s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639613/job/77562868213	
    actions-pinning	pass	16s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562901666	
    audit	pass	21s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562901654	
    check	pass	43s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562901677	
    ci/circleci: pr-pipeline	pass	0	https://circleci.com/gh/jscraik/Agent-Skills/995	Your tests passed on CircleCI!
    consistency-drift-advisory	pass	15s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562901669	
    consistency-drift-health	pass	13s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562901658	
    dependency-review	pass	16s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562901660	
    docs-lint	pass	19s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639614/job/77562868242	
    docs-test	pass	13s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639618/job/77562868246	
    gate	pass	19s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639611/job/77562868216	
    license/snyk (jscraik)	pass	0	https://app.snyk.io/org/jscraik/pr-checks/4a02bdc8-6560-4ae2-81a6-c3b69d2137b9/license	No license issues in 4 tests
    linear-gate	pass	13s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562874701	
    lint	pass	14s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562901661	
    memory	pass	12s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562901673	
    pr-pipeline	pass	56s	https://app.circleci.com/pipelines/gh/jscraik/Agent-Skills/994/workflows/06210ce3-2eb0-4742-bc62-d8aa542c132a?utm_campaign=vcs-integration-link&utm_medium=referral&utm_source=github-checks-link&utm_content=bottom	
    pr-template	pass	5s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562868211	
    risk-policy-gate	pass	15s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562887629	
    security-scan	pass	1m0s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639602/job/77562868199	
    security/snyk (jscraik)	pass	0	https://app.snyk.io/org/jscraik/pr-checks/4a02bdc8-6560-4ae2-81a6-c3b69d2137b9	No manifest changes detected in 4 projects
    semgrep	pass	1s	https://github.com/jscraik/Agent-Skills/runs/77562891294	
    skill-diagnostics	pass	23s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639618/job/77562868241	
    test	pass	28s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562901676	
    typecheck	pass	13s	https://github.com/jscraik/Agent-Skills/actions/runs/26348639612/job/77562901651

stderr:

    (empty)

### reviews

- command: gh api repos/jscraik/Agent-Skills/pulls/196/reviews
- exit: 0

stdout:

    []

stderr:

    (empty)

### comments

- command: gh api repos/jscraik/Agent-Skills/pulls/196/comments
- exit: 0

stdout:

    []

stderr:

    (empty)

WROTE: artifacts/reviews/jsc-351-pu006-triage-lane/subagent-runner-post-push-56b545ed.md
