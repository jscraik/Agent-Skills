# Deepening Workflow

## From Plausible To Professional

Replace summary claims with source evidence; "should refactor" with patch vs
interface; "tests pass" with caller-visible verifier; "cleaner pattern" with
variation, caller simplification, liability, and regression proof.

## Evidence Search Pattern

~~~bash
rg -n "<target symbol|file stem|public name>" <target-parent> tests Docs Infrastructure
rg -n "from .*<module>|import .*<module>|<public_name>" .
rg -n "<command handle|schema key|config key|package metadata>" .
~~~

Use repo wrappers before ad hoc commands. If no verifier exists, recommend a tracer.

## One-Question Rule

Ask one question only for missing owner/source, migration permission,
compatibility, authoritative consumer, or proof-vs-blocked.
