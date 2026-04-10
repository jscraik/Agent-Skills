# Daily Skill Health

- Generated at: `2026-04-10T06:50:25Z`
- Window: `2026-04-04..2026-04-10`
- Baseline source: `bootstrap pending`
- Baseline window: `n/a`
- Runs total: `32`
- Decision: `HOLD`
- Critical non-regression compliance: `37.5%`
- Terminal non-regression compliance: `100.0%`
- Non-regression recovered: `62.5%` (intermediate failures recovered)
- Budget compliance: `100.0%`
- Capture coverage: `100.0%` (32/32)
- Confidence buckets: `high=0` `medium=12` `low=20` `unknown=0`
- Injection usage: `25.0%` (8/32)
- Injection suppressed by controls: `0`
- Uplift promotion decisions: `pass=0` `hold=0` `insufficient_data=32`
- Uplift auto-apply decisions: `pass=0` `hold=0` `insufficient_data=32`
- Event envelope errors: `16`
- Event envelope errors total: `24`
- Event envelope errors waived: `8`
- Event envelope errors unresolved: `16`

- Event envelope waiver file: `artifacts/skill-graphs/pilot/artifact-parity-waivers.json`

## Event envelope errors (unresolved)

- run_20260409T064532056345Z_cbb8d4_919c4e9: missing events.jsonl
- run_20260409T064532169749Z_5b4309_91cfa81: missing events.jsonl
- run_20260409T064532279715Z_04dd5b_91ed06e: missing events.jsonl
- run_20260409T064532394104Z_1c1272_921ad51: missing events.jsonl
- run_20260409T064532504568Z_50ef7d_923f024: missing events.jsonl
- run_20260409T064532619060Z_c6442d_92682bd: missing events.jsonl
- run_20260409T064532730733Z_f93d59_9291174: missing events.jsonl
- run_20260409T064531946744Z_4270e1_91780eb: missing events.jsonl
- run_20260408T064527014926Z_50ef7d_946f024: missing events.jsonl
- run_20260408T064527137168Z_c6442d_94982bd: missing events.jsonl
- run_20260408T064527254102Z_f93d59_94b1174: missing events.jsonl
- run_20260408T064526421324Z_4270e1_93980eb: missing events.jsonl
- run_20260408T064526538395Z_cbb8d4_93bc4e9: missing events.jsonl
- run_20260408T064526656356Z_5b4309_93efa81: missing events.jsonl
- run_20260408T064526774193Z_04dd5b_940d06e: missing events.jsonl
- run_20260408T064526894446Z_1c1272_943ad51: missing events.jsonl

## Event envelope waivers applied

- run_20260407T064405056266Z_04dd5b_8e4d06e (run_20260407T064405056266Z_04dd5b_8e4d06e): waiver_id=`event-envelope-missing-8e4d06e` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260407T064405159287Z_1c1272_8e7ad51 (run_20260407T064405159287Z_1c1272_8e7ad51): waiver_id=`event-envelope-missing-8e7ad51` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260407T064405259532Z_50ef7d_8e9f024 (run_20260407T064405259532Z_50ef7d_8e9f024): waiver_id=`event-envelope-missing-8e9f024` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260407T064405363942Z_c6442d_8ec82bd (run_20260407T064405363942Z_c6442d_8ec82bd): waiver_id=`event-envelope-missing-8ec82bd` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260407T064405465228Z_f93d59_8ee1174 (run_20260407T064405465228Z_f93d59_8ee1174): waiver_id=`event-envelope-missing-8ee1174` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260407T064404758172Z_4270e1_8dc80eb (run_20260407T064404758172Z_4270e1_8dc80eb): waiver_id=`event-envelope-missing-8dc80eb` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260407T064404855416Z_cbb8d4_8dec4e9 (run_20260407T064404855416Z_cbb8d4_8dec4e9): waiver_id=`event-envelope-missing-8dec4e9` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260407T064404953569Z_5b4309_8e1fa81 (run_20260407T064404953569Z_5b4309_8e1fa81): waiver_id=`event-envelope-missing-8e1fa81` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
