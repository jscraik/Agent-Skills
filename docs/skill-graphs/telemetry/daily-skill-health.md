# Daily Skill Health

- Generated at: `2026-04-12T06:44:20Z`
- Window: `2026-04-06..2026-04-12`
- Baseline source: `frozen_snapshot`
- Baseline window: `2026-04-05..2026-04-11`
- Runs total: `48`
- Decision: `HOLD`
- Critical non-regression compliance: `37.5%`
- Terminal non-regression compliance: `100.0%`
- Non-regression recovered: `62.5%` (intermediate failures recovered)
- Budget compliance: `100.0%`
- Capture coverage: `100.0%` (48/48)
- Confidence buckets: `high=0` `medium=18` `low=30` `unknown=0`
- Injection usage: `25.0%` (12/48)
- Injection suppressed by controls: `0`
- Uplift promotion decisions: `pass=0` `hold=0` `insufficient_data=48`
- Uplift auto-apply decisions: `pass=0` `hold=0` `insufficient_data=48`
- Event envelope errors: `32`
- Event envelope errors total: `40`
- Event envelope errors waived: `8`
- Event envelope errors unresolved: `32`

- Event envelope waiver file: `artifacts/skill-graphs/pilot/artifact-parity-waivers.json`

## Event envelope errors (unresolved)

- run_20260411T063348089335Z_1c1272_91ead51: missing events.jsonl
- run_20260411T063348205332Z_50ef7d_920f024: missing events.jsonl
- run_20260411T063348323211Z_c6442d_92382bd: missing events.jsonl
- run_20260411T063348436763Z_f93d59_9251174: missing events.jsonl
- run_20260411T063347630118Z_4270e1_91480eb: missing events.jsonl
- run_20260411T063347744899Z_cbb8d4_916c4e9: missing events.jsonl
- run_20260411T063347860332Z_5b4309_919fa81: missing events.jsonl
- run_20260411T063347973328Z_04dd5b_91bd06e: missing events.jsonl
- run_20260410T065025010349Z_5b4309_916fa81: missing events.jsonl
- run_20260410T065025126723Z_04dd5b_918d06e: missing events.jsonl
- run_20260410T065025246860Z_1c1272_91bad51: missing events.jsonl
- run_20260410T065025360237Z_50ef7d_91df024: missing events.jsonl
- run_20260410T065025474543Z_c6442d_92082bd: missing events.jsonl
- run_20260410T065025587352Z_f93d59_9221174: missing events.jsonl
- run_20260410T065024768042Z_4270e1_91180eb: missing events.jsonl
- run_20260410T065024889084Z_cbb8d4_913c4e9: missing events.jsonl
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
