import json
import sys
from pathlib import Path
import shutil

if len(sys.argv) != 2:
    print('usage: copy_icon_batch.py <batch-number>')
    sys.exit(2)

batch = sys.argv[1]
root = Path('/Users/jamiecraik/dev/agent-skills')
mapping_path = root / f'tmp/imagegen/batch{batch}-mapping.json'
report_path = root / f'tmp/imagegen/batch{batch}-copy-report.json'

if not mapping_path.exists():
    print(f'mapping not found: {mapping_path}')
    sys.exit(1)

mapping = json.loads(mapping_path.read_text())
jobs = mapping.get('jobs', [])
report = []

for job in jobs:
    src = root / job['generated']
    dst_rel = Path(job['target'])
    dst = root / dst_rel
    dst.parent.mkdir(parents=True, exist_ok=True)

    final_dst = dst
    action = 'copied'
    if final_dst.exists():
        base = final_dst.stem
        suf = final_dst.suffix
        i = 1
        while True:
            candidate = final_dst.with_name(f'{base}.gen{i}{suf}')
            if not candidate.exists():
                final_dst = candidate
                action = 'copied_with_suffix'
                break
            i += 1

    if not src.exists():
        report.append({
            'status': 'missing_source',
            'kind': job.get('kind'),
            'name': job.get('name'),
            'variant': job.get('variant'),
            'source': str(src.relative_to(root)),
            'target': str(dst_rel),
        })
        continue

    shutil.copy2(src, final_dst)
    report.append({
        'status': action,
        'kind': job.get('kind'),
        'name': job.get('name'),
        'variant': job.get('variant'),
        'source': str(src.relative_to(root)),
        'target_requested': str(dst_rel),
        'target_written': str(final_dst.relative_to(root)),
    })

report_path.write_text(json.dumps(report, indent=2) + '\n')

copied = sum(1 for r in report if r['status'] in {'copied', 'copied_with_suffix'})
with_suffix = sum(1 for r in report if r['status'] == 'copied_with_suffix')
missing = sum(1 for r in report if r['status'] == 'missing_source')

print(f'batch={batch} jobs={len(jobs)} copied={copied} suffixed={with_suffix} missing={missing}')
print(f'report={report_path}')
