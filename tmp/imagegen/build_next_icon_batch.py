import json
import re
from pathlib import Path

ROOT = Path('/Users/jamiecraik/dev/agent-skills')
TMP = ROOT / 'tmp/imagegen'
PROMPT_MD = ROOT / 'artifacts/icon-prompts/chatgpt-skill-plugin-icon-prompts.md'

existing = sorted(TMP.glob('batch*.jsonl'))
max_idx = 0
for p in existing:
    m = re.fullmatch(r'batch(\d+)\.jsonl', p.name)
    if m:
        max_idx = max(max_idx, int(m.group(1)))
next_idx = max_idx + 1

batch_jsonl = TMP / f'batch{next_idx}.jsonl'
batch_map = TMP / f'batch{next_idx}-mapping.json'
out_dir = Path(f'tmp/imagegen/batch{next_idx}-out')

text = PROMPT_MD.read_text()
lines = text.splitlines()

entries = []
i = 0
while i < len(lines):
    m = re.match(r'^###\s+.+\(`([^`]+)`\)$', lines[i])
    if not m:
        i += 1
        continue
    slug = m.group(1)

    targets = None
    prompt = None
    j = i + 1
    while j < len(lines):
        l = lines[j]
        if l.startswith('### '):
            break
        if l.startswith('- Targets: '):
            parts = re.findall(r'`([^`]+)`', l)
            targets = parts if parts else None
        if l.strip() == '```text':
            k = j + 1
            buf = []
            while k < len(lines) and lines[k].strip() != '```':
                buf.append(lines[k])
                k += 1
            prompt = '\n'.join(buf).strip()
            j = k
        j += 1

    if targets and prompt:
        kind = 'plugin' if targets[0].startswith('plugins/') else 'skill'
        entries.append({'slug': slug, 'kind': kind, 'targets': targets, 'prompt': prompt})

    i = j

DONE = set()
for rp in sorted(TMP.glob('batch*-copy-report.json')):
    try:
        arr = json.loads(rp.read_text())
    except Exception:
        continue
    for row in arr:
        if row.get('status') in {'copied', 'copied_with_suffix'}:
            k = row.get('kind'); n = row.get('name'); v = row.get('variant')
            if k and n and v:
                DONE.add((k, n, v))

selected_skills = []
selected_plugins = []
for e in entries:
    slug = e['slug']
    targets = e['targets']
    kind = e['kind']

    if kind == 'skill':
        small = next((t for t in targets if 'icon-small' in t), None)
        large = next((t for t in targets if 'icon-large' in t or t.endswith('/imagegen.png')), None)
        if large and large.endswith('/imagegen.png'):
            large = large.replace('/imagegen.png', '/icon-large.png')
        if not small or not large:
            continue
        if (kind, slug, 'small') in DONE and (kind, slug, 'large') in DONE:
            continue
        selected_skills.append((e, small, large))
    else:
        icon = next((t for t in targets if t.endswith('/icon.png')), None)
        logo = next((t for t in targets if t.endswith('/logo.png')), None)
        if not icon or not logo:
            continue
        if (kind, slug, 'icon') in DONE and (kind, slug, 'logo') in DONE:
            continue
        selected_plugins.append((e, icon, logo))

selected_skills = selected_skills[:10]
selected_plugins = selected_plugins[:1]

jobs = []
mapping = {'jobs': []}

def sanitize(name: str) -> str:
    return re.sub(r'[^a-z0-9-]+', '-', name.lower()).strip('-')

for e, small_t, large_t in selected_skills:
    slug = e['slug']
    base_prompt = e['prompt']
    safe = sanitize(slug)

    small_prompt = base_prompt + '\n\nVariant instruction: generate the SMALL icon version with strong silhouette clarity and minimal micro-detail for tiny UI rendering.'
    large_prompt = base_prompt + '\n\nVariant instruction: generate the LARGE icon version with richer internal detail while preserving the same symbol and style family.'

    small_out = f'skill-{safe}-small.png'
    large_out = f'skill-{safe}-large.png'

    jobs.append({'prompt': small_prompt, 'out': small_out, 'background': 'transparent', 'output_format': 'png'})
    mapping['jobs'].append({'kind': 'skill', 'name': slug, 'variant': 'small', 'generated': str(out_dir / small_out), 'target': small_t, 'prompt': small_prompt})

    jobs.append({'prompt': large_prompt, 'out': large_out, 'background': 'transparent', 'output_format': 'png'})
    mapping['jobs'].append({'kind': 'skill', 'name': slug, 'variant': 'large', 'generated': str(out_dir / large_out), 'target': large_t, 'prompt': large_prompt})

for e, icon_t, logo_t in selected_plugins:
    slug = e['slug']
    base_prompt = e['prompt']
    safe = sanitize(slug)

    icon_prompt = base_prompt + '\n\nVariant instruction: produce the plugin ICON optimized for compact UI surfaces and high recognizability at small size.'
    logo_prompt = base_prompt + '\n\nVariant instruction: produce the plugin LOGO optimized for larger card/header contexts with slightly richer detail.'

    icon_out = f'plugin-{safe}-icon.png'
    logo_out = f'plugin-{safe}-logo.png'

    jobs.append({'prompt': icon_prompt, 'out': icon_out, 'background': 'transparent', 'output_format': 'png'})
    mapping['jobs'].append({'kind': 'plugin', 'name': slug, 'variant': 'icon', 'generated': str(out_dir / icon_out), 'target': icon_t, 'prompt': icon_prompt})

    jobs.append({'prompt': logo_prompt, 'out': logo_out, 'background': 'transparent', 'output_format': 'png'})
    mapping['jobs'].append({'kind': 'plugin', 'name': slug, 'variant': 'logo', 'generated': str(out_dir / logo_out), 'target': logo_t, 'prompt': logo_prompt})

TMP.mkdir(parents=True, exist_ok=True)
with batch_jsonl.open('w') as f:
    for job in jobs:
        f.write(json.dumps(job, ensure_ascii=False) + '\n')
batch_map.write_text(json.dumps(mapping, indent=2) + '\n')

print(f'batch={next_idx} jobs={len(jobs)} skills={len(selected_skills)} plugins={len(selected_plugins)}')
print(f'jsonl={batch_jsonl}')
print(f'mapping={batch_map}')
if selected_skills:
    print('skill_slugs=' + ','.join([x[0]['slug'] for x in selected_skills]))
if selected_plugins:
    print('plugin_slugs=' + ','.join([x[0]['slug'] for x in selected_plugins]))
