# Daily Skill Health

- Generated at: `2026-04-15T08:02:08Z`
- Window: `2026-04-09..2026-04-15`
- Baseline source: `rolling_window`
- Baseline window: `2026-04-07..2026-04-09`
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
- Event envelope errors: `24`
- Event envelope errors total: `40`
- Event envelope errors waived: `16`
- Event envelope errors unresolved: `24`

- Event envelope waiver file: `artifacts/skill-graphs/pilot/artifact-parity-waivers.json`

## Event envelope errors (unresolved)

- run_20260414T080113088052Z_4270e1_91280eb: missing events.jsonl
- run_20260414T080113215773Z_cbb8d4_914c4e9: missing events.jsonl
- run_20260414T080113334093Z_5b4309_917fa81: missing events.jsonl
- run_20260414T080113449366Z_04dd5b_91ad06e: missing events.jsonl
- run_20260414T080113568206Z_1c1272_91dad51: missing events.jsonl
- run_20260414T080113687304Z_50ef7d_91ff024: missing events.jsonl
- run_20260414T080113805620Z_c6442d_92282bd: missing events.jsonl
- run_20260414T080113923109Z_f93d59_9241174: missing events.jsonl
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

## Event envelope waivers applied

- run_20260413T081921163303Z_c6442d_91e82bd (run_20260413T081921163303Z_c6442d_91e82bd): waiver_id=`event-envelope-missing-91e82bd` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260413T081921414441Z_f93d59_9201174 (run_20260413T081921414441Z_f93d59_9201174): waiver_id=`event-envelope-missing-9201174` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260413T081920417414Z_4270e1_90f80eb (run_20260413T081920417414Z_4270e1_90f80eb): waiver_id=`event-envelope-missing-90f80eb` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260413T081920519358Z_cbb8d4_911c4e9 (run_20260413T081920519358Z_cbb8d4_911c4e9): waiver_id=`event-envelope-missing-911c4e9` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260413T081920625530Z_5b4309_914fa81 (run_20260413T081920625530Z_5b4309_914fa81): waiver_id=`event-envelope-missing-914fa81` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260413T081920731856Z_04dd5b_916d06e (run_20260413T081920731856Z_04dd5b_916d06e): waiver_id=`event-envelope-missing-916d06e` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260413T081920845569Z_1c1272_919ad51 (run_20260413T081920845569Z_1c1272_919ad51): waiver_id=`event-envelope-missing-919ad51` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260413T081920967414Z_50ef7d_91bf024 (run_20260413T081920967414Z_50ef7d_91bf024): waiver_id=`event-envelope-missing-91bf024` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260412T064420106973Z_50ef7d_925f024 (run_20260412T064420106973Z_50ef7d_925f024): waiver_id=`event-envelope-missing-925f024` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260412T064420226688Z_c6442d_92882bd (run_20260412T064420226688Z_c6442d_92882bd): waiver_id=`event-envelope-missing-92882bd` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260412T064420341042Z_f93d59_92a1174 (run_20260412T064420341042Z_f93d59_92a1174): waiver_id=`event-envelope-missing-92a1174` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260412T064419504123Z_4270e1_91980eb (run_20260412T064419504123Z_4270e1_91980eb): waiver_id=`event-envelope-missing-91980eb` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260412T064419624036Z_cbb8d4_91bc4e9 (run_20260412T064419624036Z_cbb8d4_91bc4e9): waiver_id=`event-envelope-missing-91bc4e9` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260412T064419747082Z_5b4309_91efa81 (run_20260412T064419747082Z_5b4309_91efa81): waiver_id=`event-envelope-missing-91efa81` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260412T064419865434Z_04dd5b_920d06e (run_20260412T064419865434Z_04dd5b_920d06e): waiver_id=`event-envelope-missing-920d06e` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
- run_20260412T064419988886Z_1c1272_923ad51 (run_20260412T064419988886Z_1c1272_923ad51): waiver_id=`event-envelope-missing-923ad51` reason=`Historical run is missing events.jsonl while base artifacts remain available; waived pending replay/backfill.`
