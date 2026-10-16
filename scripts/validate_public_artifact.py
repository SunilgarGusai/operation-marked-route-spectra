"""Public repository structural validation, independent of benchmark downloads."""
from pathlib import Path
import csv, json, re
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
required=['README.md','QUICKSTART.md','CITATION.cff','LICENSE','REPOSITORY_MANIFEST.csv','docs/GRAF_UPSTREAM_MIT_LICENSE.txt','docs/CLAIM_BOUNDARIES.md','docs/FROZEN_RESULTS.md','docs/SOURCE_SHA256.json','figures/seed_arc_lists.json','run_proofs.py','.github/workflows/repository-validation.yml']
assert all((R/x).is_file() for x in required)
paths=set(p.relative_to(R).as_posix() for p in R.rglob('*') if p.is_file() and not '__pycache__' in p.parts and 'outputs' not in p.parts and not '.git' in p.parts)
with (R/'REPOSITORY_MANIFEST.csv').open(newline='',encoding='utf8') as f:manifest={r['path'] for r in csv.DictReader(f)}
assert paths==manifest, f'manifest mismatch, absent={sorted(manifest-paths)}, missing={sorted(paths-manifest)}'
for path in paths:
 assert not (path.endswith('.tfrecord') or path.startswith('data/raw/') or path.startswith('data/holdout/')),path
 if path.endswith(('.py','.md','.txt','.yml','.csv','.json','.cff','.cmd')):
  s=(R/path).read_text(encoding='utf8')
  assert not re.search(r'[A-Za-z]:\\(?:Users|Research)\\',s),path
for svg in (R/'docs'/'assets').glob('*.svg'):
 root=ET.parse(svg).getroot()
 assert root.tag.endswith('svg'), f'invalid SVG: {svg}'
for name in ['docs/THEOREM_MAP.md','docs/GITHUB_ABOUT_METADATA.md','docs/VISUAL_GUIDE.md','docs/assets/spectral-mechanism.svg','docs/assets/evidence-layers.svg']:
 assert (R/name).is_file(), f'missing upgraded documentation: {name}'
assert (R/'LICENSE').read_text(encoding='utf8').startswith('MIT License'), 'Expected project-original MIT license'
print(f'PASS: public artifact manifest matches {len(paths)} files; no banned raw benchmark inputs')
