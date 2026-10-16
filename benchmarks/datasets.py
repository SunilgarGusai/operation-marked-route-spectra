"""Read-only, label-leakage-guarded development data.

NAS-Bench-101: the same frozen Phase 8/9B architecture records, development labels and
partitions; NAS-Bench-201: the REAL official Phase 9C local frozen cache only. Nothing
in this module loads holdout accuracy. All cross-validations are exploratory and
never replace the original holdout test.
"""
import ast,csv,gzip,hashlib,json
from collections import Counter
from pathlib import Path
import numpy as np
from graf_nb101 import source_features

NB101_HASH='1c7235f462405fd75a2db1290282bd4a78f2dcf6d5931e9d7a75a37f18cd7790'
EXPECTED_NB201={'train':7808,'development':4736,'reserved_holdout':2496}
NB201_OFFICIAL_CACHE_SHA='7323dec8cc1213ddec819550bbe349b518b5f0d1013d3ac7016361ee27fae193'
NB201_SOURCE_SHA='c82e70b5ffb0dba0f09d88ecc8df5a6d3ce8da8a99ad223285104f4537314033'

BASE=['n','m','op_c1','op_c3','op_mp','log_params']
PATH=['total_paths','input_output_paths','longest_path','longest_input_output_path']+[f'pathlen_{i}' for i in range(1,7)]+['ecc_mean','ecc_max','ecc_classes']
TERMS=['rho','rho_fro','energy','tr2','tr3']
ORDINARY=[f'{s}_{term}' for s in ['adj','route','op_path_c1','op_path_c3','op_path_mp'] for term in TERMS]
WEIGHTED_BASIC=[f'{s}_{term}' for s in ['adj_ecc','route_ecc'] for term in TERMS]
WEIGHTED_OP=[f'ecc_op_path_{t}_{m}' for t in ['c1','c3','mp'] for m in TERMS]
OP_OCC=['interior_'+x+'_path_occurrences' for x in ('c1','c3','mp')]
S2=BASE+PATH+ORDINARY+OP_OCC+WEIGHTED_BASIC

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for ch in iter(lambda:f.read(1024*1024),b''):h.update(ch)
 return h.hexdigest()

def nb101(root):
 data=Path(root)/'data'; features=data/'PHASE8_FROZEN_OFFICIAL_FEATURES.jsonl.gz'
 if sha(features)!=NB101_HASH:raise RuntimeError('NB101 SOURCE FROZEN FEATURES SHA MISMATCH')
 with open(data/'FROZEN_PARTITIONS.csv',newline='',encoding='utf8') as f:
  part={r['id']:r for r in csv.DictReader(f)}
 with open(data/'DEVELOPMENT_LABELS.csv',newline='',encoding='utf8') as f:
  lab={r['id']:r for r in csv.DictReader(f)}
 if len(lab)!=3359 or Counter(v['partition'] for v in part.values())!={'train':2742,'development':617,'reserved_holdout':617}:
  raise RuntimeError('NB101 partition/label cardinalities changed')
 if set(lab)!=set(k for k,v in part.items() if v['partition']!='reserved_holdout'):
  raise RuntimeError('NB101 development label set contains missing or holdout IDs')
 rows=[];ids=set()
 with gzip.open(features,'rt',encoding='utf8') as f:
  for line in f:
   r=json.loads(line);hid=r['id'];p=part[hid]
   if p['partition']=='reserved_holdout':continue
   if lab[hid]['partition']!=p['partition']:raise RuntimeError('NB101 label split mismatch')
   raw=r['features'];a=ast.literal_eval(r['adjacency']) if isinstance(r['adjacency'],str) else r['adjacency'];ops=ast.literal_eval(r['operations']) if isinstance(r['operations'],str) else r['operations']
   d={}
   for x in BASE+PATH+ORDINARY+WEIGHTED_BASIC+WEIGHTED_OP+OP_OCC:
    if x=='log_params':d[x]=np.log1p(float(lab[hid]['trainable_parameters']))
    elif x in ('op_c1','op_c3','op_mp'):
     name={'op_c1':'conv1x1-bn-relu','op_c3':'conv3x3-bn-relu','op_mp':'maxpool3x3'}[x]
     d[x]=float(raw['operation_counts'][name])
    elif x.startswith('pathlen_'):
     z=int(x[8:])-1;d[x]=float(raw['path_length_counts'][z]) if z<len(raw['path_length_counts']) else 0.
    else:d[x]=float(raw[x])
   g=source_features({'adjacency':a,'operations':ops},mode='source')
   d.update(g);rows.append((hid,p['topology_key'],float(lab[hid]['validation_accuracy_mean'])*100,d))
   ids.add(hid)
 if len(rows)!=3359 or len(ids)!=3359:raise RuntimeError('NB101 full frozen pool not loaded')
 graf=sorted(next(iter(rows))[3].keys() & set(g.keys()))
 variants={'GRAF':graf,'GRAF_S2':graf+S2,'GRAF_S2_WEIGHTED':graf+S2+WEIGHTED_OP,'GRAF_S2_PLACEBO':graf+S2}
 return assemble(rows,variants,'nb101',hashlib.sha256((sha(features)+sha(data/'DEVELOPMENT_LABELS.csv')).encode()).hexdigest())

def nb201_cache_candidates(root,search_root=None):
 root=Path(root).resolve()
 if search_root: roots=[Path(search_root)]
 else:roots=[root.parent,root]
 got=[]
 for base in roots:
  if not base.exists():continue
  try:
   for f in base.glob('**/NB201_FROZEN_FEATURES.jsonl.gz'):
    report=f.parent/'NB201_PREPARE_REPORT.json'
    if report.exists():got.append((f,report))
  except (OSError,PermissionError):pass
 return sorted(set(got),key=lambda pair:str(pair[0]))

def nb201(root,search_root=None):
 import gzip
 from collections import defaultdict
 from nb201_features import GRAF_ORDER
 valid=[];failed=[]
 for f,r in nb201_cache_candidates(root,search_root):
  try:
   report=json.loads(r.read_text(encoding='utf8'))
   if report.get('source_rows')!=15625 or report.get('rows')!=15040:raise ValueError('not full official 15040 records')
   if report.get('sha256_cache')!=NB201_OFFICIAL_CACHE_SHA or report.get('sha256_source')!=NB201_SOURCE_SHA:raise ValueError('not the original verified user Phase9C source/cache release')
   if report.get('split_counts')!=EXPECTED_NB201:raise ValueError('unexpected frozen split')
   if sha(f)!=report['sha256_cache']:raise ValueError('cache digest differs from report')
   valid.append((f,report))
  except Exception as e:failed.append((str(f),str(e)))
 if not valid:
  raise FileNotFoundError('Official NB201 15040-record Phase 9C cache not found. Synthetic/preparation caches REJECTED. Search root: '+str(search_root or Path(root).parent)+'; candidate errors: '+str(failed[:5]))
 if len(valid)>1 and len({x[1]['sha256_cache'] for x in valid})>1:raise RuntimeError('Multiple conflicting FULL NB201 frozen caches; set VELE09_NB201_ROOT')
 path,report=valid[0]
 rows=[];count=Counter(); ids=set();schema=None
 with gzip.open(path,'rt',encoding='utf8') as f:
  for line in f:
   r=json.loads(line);s=r['split'];count[s]+=1
   if s=='reserved_holdout':
    if 'validation_accuracy' in r:raise RuntimeError('Reserved NB201 holdout labels appeared in frozen cache')
    continue
   if 'validation_accuracy' not in r:raise RuntimeError('NB201 development label missing')
   if schema is None:schema=list(r['features'])
   if list(r['features'])!=schema:raise RuntimeError('NB201 schema differs within frozen cache')
   rid=str(r['file_id']);ids.add(rid)
   rows.append((rid,r['topology_key'],float(r['validation_accuracy']),r['features']))
 if count!=EXPECTED_NB201 or len(rows)!=12544 or len(ids)!=12544:raise RuntimeError('NB201 cardinality mismatch; refuse analysis')
 graf=[x for x in schema if x.startswith('graf_')]
 ordinary=[x for x in schema if (x.startswith('cell_') and 'ecc' not in x) or x.startswith('op_')]
 basic=[x for x in schema if x in ('cell_ecc_mean','cell_ecc_max')]
 weighted=[x for x in schema if x.startswith('weighted_op_') or x in ('cell_ecc_route_rho','cell_ecc_route_tr2')]
 if len(graf)!=191 or len(weighted)!=10:raise RuntimeError('NB201 feature definitions unexpected')
 s2=sorted(set(graf+ordinary+basic));variants={'GRAF':graf,'GRAF_S2':s2,'GRAF_S2_WEIGHTED':sorted(set(s2+weighted)),'GRAF_S2_PLACEBO':s2}
 return assemble(rows,variants,'nb201',report['sha256_cache'])

def assemble(rows,variants,name,digest):
 ids=[r[0] for r in rows]; groups=np.array([r[1] for r in rows]);y=np.array([r[2] for r in rows],float)
 if not np.all(np.isfinite(y)):raise RuntimeError('nonfinite development targets')
 out={}
 for k,cols in variants.items():
  arr=np.array([[r[3][c] for c in cols] for r in rows],dtype=np.float32)
  if not np.all(np.isfinite(arr)):raise RuntimeError(f'Nonfinite {name} features {k}')
  out[k]=arr
 return {'name':name,'ids':ids,'groups':groups,'y':y,'X':out,'digest':digest,
         'groups_n':len(set(groups)), 'variants':{x:list(variants[x]) for x in variants}}
