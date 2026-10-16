"""One campaign, checkpointed: exact mathematical audit, exploratory grouped CV,
paired topology statistics, and validated single-file collection.
No reserved holdout labels are ever supplied to models.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('MKL_NUM_THREADS','2')
import argparse,datetime,gzip,hashlib,json,platform,sys,time,traceback,zipfile
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_absolute_error
from datasets import nb101,nb201,nb201_cache_candidates,sha
from math_extension import verify as verify_analytic
from verify_family_legacy import run as verify_family
from verify_operation_family import run as verify_operation_family

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs';CK=ROOT/'checkpoints';LOGS=ROOT/'logs'
for d in (OUT,CK,LOGS):d.mkdir(exist_ok=True,parents=True)
PROTOCOL='VELE09_INTEGRATED_V1_FROZEN_EXPLORATORY_20261015'
SEEDS=(11,23)
VARIANTS=('GRAF','GRAF_S2','GRAF_S2_WEIGHTED','GRAF_S2_PLACEBO')


def atom_json(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_name(path.name+'.new');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');os.replace(tmp,path)

def sha_string(s):return hashlib.sha256(s.encode('utf8')).hexdigest()

def environment():
 import sklearn,scipy,networkx,sympy
 import shutil
 return {'platform':platform.platform(),'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
         'scikit_learn':sklearn.__version__,'networkx':networkx.__version__,'sympy':sympy.__version__,
         'cpu_logical':os.cpu_count(),'free_GB':round(shutil.disk_usage(ROOT).free/1e9,3),
         'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}

def placebo(ids,width,seed=20261015):
 arr=np.empty((len(ids),width),dtype=np.float32)
 for i,k in enumerate(ids):
  for j in range(width):
   h=hashlib.sha256(f'{PROTOCOL}|placebo|{k}|{j}|{seed}'.encode()).digest()
   arr[i,j]=2*(int.from_bytes(h[:8],'big')/(2**64))-1
 return arr

def named_dataset(name,search_root=None):
 d=nb101(ROOT) if name=='nb101' else nb201(ROOT,search_root)
 d['X']['GRAF_S2_PLACEBO']=np.concatenate([d['X']['GRAF_S2'],placebo(d['ids'],d['X']['GRAF_S2_WEIGHTED'].shape[1]-d['X']['GRAF_S2'].shape[1])],axis=1)
 assert all(len(x)==len(d['ids']) for x in d['X'].values())
 return d

def model_signature(d):
 source_files=[ROOT/'src'/p for p in ['datasets.py','campaign.py','graf_nb101.py','nb201_features.py','verify_operation_family.py','math_extension.py']]
 return sha_string('|'.join([PROTOCOL,d['digest']]+[sha(f) for f in source_files]))

def group_folds(d,smoke=False):
 groups=d['groups'];idx=np.arange(len(groups));ug=sorted(set(groups))
 if smoke:
  # Not scientific results. Tests the end-to-end machine integration only.
  sel=idx[:min(180,len(idx))]; gg=groups[sel]
  folds=[]
  for tr,te in GroupKFold(n_splits=min(3,len(set(gg)))).split(sel,groups=gg):folds.append(('TEST_ONLY_FOLD_'+str(len(folds)),sel[tr],sel[te]))
  return folds[:1]
 if d['name']=='nb201':
  return [('TOPO_'+g,idx[groups!=g],idx[groups==g]) for g in ug]
 folds=[]
 for i,(tr,te) in enumerate(GroupKFold(n_splits=5).split(idx,groups=groups)):
  folds.append((f'GROUPK5_{i+1}',tr,te))
 return folds

def run_dataset(d,smoke=False):
 folds=group_folds(d,smoke)
 signature=model_signature(d);destination=CK/d['name'];destination.mkdir(exist_ok=True)
 expected=len(folds)*len(VARIANTS)*(1 if smoke else len(SEEDS))
 completed=0
 for label,tr,te in folds:
  if set(d['groups'][tr]) & set(d['groups'][te]):raise RuntimeError('Group leakage in fold '+label)
  ytrain=d['y'][tr]; ytest=d['y'][te]
  for feature in VARIANTS:
   for seed in SEEDS[:1] if smoke else SEEDS:
    key=f'{label}__{feature}__seed{seed}'
    ck=destination/(key+'.json')
    if ck.exists():
     r=json.loads(ck.read_text(encoding='utf8'))
     if r.get('signature')!=signature:raise RuntimeError('STALE CHECKPOINT; refuse mixing runs: '+str(ck))
     if r.get('n_test')!=len(te):raise RuntimeError('CHECKPOINT size mismatch')
    else:
     t0=time.monotonic()
     model=ExtraTreesRegressor(n_estimators=20 if smoke else 96,min_samples_leaf=3,max_features=0.9,n_jobs=2,random_state=seed)
     X=d['X'][feature];model.fit(X[tr],ytrain);pred=model.predict(X[te]);
     if not np.all(np.isfinite(pred)):raise RuntimeError('Nonfinite fitted predictions')
     errs=np.abs(pred-ytest)
     topo=d['groups'][te]
     macro=float(np.mean([errs[topo==g].mean() for g in set(topo)]))
     r={'signature':signature,'experiment':'ENGINEERING_TEST_ONLY' if smoke else 'EXPLORATORY_DEVELOPMENT_CV',
       'dataset':d['name'],'fold':label,'model':'ExtraTrees','variant':feature,'seed':seed,
       'n_train':len(tr),'n_test':len(te),'n_test_groups':len(set(topo)),
       'micro_mae_pp':float(errs.mean()),'macro_mae_pp':macro,'elapsed_s':round(time.monotonic()-t0,3),
       'test_ids':[d['ids'][i] for i in te],
       'topology':topo.tolist(),'target_pp':ytest.tolist(),'predicted_pp':pred.tolist(),
       'holdout_accessed':False}
     atom_json(ck,r)
    completed+=1
    if completed==1 or completed%5==0 or completed==expected:print(f'[{d["name"]}] {completed}/{expected} fold={label} variant={feature} seed={seed} MAE={r["micro_mae_pp"]:.4f}',flush=True)
    atom_json(LOGS/'PROGRESS.json',{'phase':'MODEL_CV','dataset':d['name'],'completed':completed,'expected':expected,'last_checkpoint':key,'status':'RUNNING'})
    if (ROOT/'PAUSE_REQUESTED.flag').exists():
     raise InterruptedError('Safe pause requested: remove PAUSE_REQUESTED.flag to resume')
 atom_json(LOGS/'PROGRESS.json',{'phase':'MODEL_CV','dataset':d['name'],'completed':expected,'expected':expected,'status':'COMPLETED'})
 return summarize(d,folds,smoke)

def summarize(d,folds,smoke):
 ckdir=CK/d['name'];signature=model_signature(d);records=[]
 for label,tr,te in folds:
  for feature in VARIANTS:
   for seed in SEEDS[:1] if smoke else SEEDS:
    p=ckdir/(f'{label}__{feature}__seed{seed}.json')
    r=json.loads(p.read_text(encoding='utf8'))
    if r['signature']!=signature:raise RuntimeError('Checkpoint protocol mismatch')
    records.append(r)
 group_results=defaultdict(lambda: defaultdict(list))
 for r in records:
  topo=r['topology'];truth=np.array(r['target_pp']);pred=np.array(r['predicted_pp']);errs=np.abs(pred-truth)
  for g in sorted(set(topo)):
   mask=np.array(topo)==g
   group_results[(r['variant'],r['seed'])][g].extend(errs[mask].tolist())
 aggregate=[]
 for feature in VARIANTS:
  for seed in SEEDS[:1] if smoke else SEEDS:
   allfold=[r for r in records if r['variant']==feature and r['seed']==seed]
   e=np.concatenate([np.abs(np.array(r['predicted_pp'])-np.array(r['target_pp'])) for r in allfold])
   per_g={g:float(np.mean(vals)) for g,vals in group_results[(feature,seed)].items()}
   aggregate.append({'variant':feature,'seed':seed,'micro_MAE_pp':float(np.mean(e)),
      'equal_topology_MAE_pp':float(np.mean(list(per_g.values()))),
      'n_predictions':len(e),'n_topology_groups':len(per_g),'topology_MAE_pp':per_g})
 comparisons=[]
 # Paired leave-group-out errors; independent unit is architecture topology, not arch row.
 for seed in SEEDS[:1] if smoke else SEEDS:
  for comparator in ('GRAF','GRAF_S2','GRAF_S2_PLACEBO'):
   a=group_results[(comparator,seed)];b=group_results[('GRAF_S2_WEIGHTED',seed)];common=sorted(set(a)&set(b))
   delta=np.array([float(np.mean(a[g])-np.mean(b[g])) for g in common])
   rng=np.random.default_rng(20261015+seed)
   draws=rng.integers(len(delta),size=(2000,len(delta)))
   bs=np.mean(delta[draws],axis=1)
   comparisons.append({'seed':seed,'baseline':comparator,'weighted':'GRAF_S2_WEIGHTED',
      'n_topology_groups':len(common),'equal_topology_improvement_pp':float(np.mean(delta)),
      'group_bootstrap_95_exploratory_pp':[float(x) for x in np.quantile(bs,[.025,.975])],
      'topology_level_improvements_pp':dict(zip(common,map(float,delta)))})
 target={'status':'ENGINEERING_ONLY' if smoke else 'EXPLORATORY_ONLY',
         'dataset':d['name'],'dataset_fingerprint':d['digest'],'n_architectures':len(d['ids']),
         'n_group_topologies':d['groups_n'],'unique_test_architectures_per_seed':len(d['ids']),
         'n_folds':len(folds),'n_model_evaluations':len(records),'variants':list(VARIANTS),
         'aggregate':aggregate,'paired_topology_comparisons':comparisons,
         'holdout_labels_used':0,'evaluation_warning':'Original holdout withheld; repeated development label reuse, not a confirmatory study'}
 atom_json(OUT/(f'{d["name"].upper()}_GROUP_CV'+('_SMOKE' if smoke else '')+'.json'),target)
 return target

def inspect(smoke=False):
 print('ENV',json.dumps(environment()),flush=True)
 out=verify_analytic(8 if smoke else 60)
 atom_json(OUT/'ANALYTIC_ROUTE_IDENTITY_AUDIT.json',out)
 fam=verify_family(2 if smoke else 4)
 assert fam['status']=='PASS'
 op=verify_operation_family(2 if smoke else 3)
 assert op['status']=='PASS'
 return {'route_derivative':out,'phase7_family':{'status':fam['status'],'exact_second_moment_gap':fam['squared_trace_gap_blowup']},
         'two_operation_family':{'status':op['status'], 'alpha_gap':op['operations']['alpha']['full_weighted_tr2_gap'], 'beta_gap':op['operations']['beta']['full_weighted_tr2_gap']}}

def collect():
 """One normalized POSIX ZIP namespace. Verify content outside the archive manifest."""
 out=OUT/'UPLOAD_ME_VELE09_INTEGRATED.zip';manifest=[]
 files=[]
 for dirname in ('outputs','logs','src','docs'):
  for f in sorted((ROOT/dirname).rglob('*')):
   if f.is_file() and f!=out and not f.name.endswith('.new'):
    if f.suffix in ('.zip','.pyc'):continue
    if '__pycache__' in f.parts:continue
    files.append(f)
 # Deliberately no compiled code, raw 15k-row features or 100s of checkpoint predictions in upload.
 # Include concise run manifests plus source fingerprints, model summaries & no holdout labels.
 for f in files:
  arc=f.relative_to(ROOT).as_posix();manifest.append({'path':arc,'sha256':sha(f),'bytes':f.stat().st_size})
 package={'schema':'VELE09_UPLOAD_MANIFEST_V1','protocol':PROTOCOL,'scope':'development only; no holdout labels','files':manifest}
 manifest_bytes=json.dumps(package,indent=2).encode('utf8')
 tmp=out.with_suffix('.zip.partial')
 with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in files:z.write(f,f.relative_to(ROOT).as_posix())
  z.writestr('MANIFEST.json',manifest_bytes)
 with zipfile.ZipFile(tmp) as z:
  assert len(set(z.namelist()))==len(z.namelist()),'duplicate filenames'
  assert z.testzip() is None
  m=json.loads(z.read('MANIFEST.json'))
  for it in m['files']:
   assert hashlib.sha256(z.read(it['path'])).hexdigest()==it['sha256'],it['path']
 os.replace(tmp,out);return str(out)

def run(mode,search_root=None):
 start=time.monotonic();state={'protocol':PROTOCOL,'mode':mode,'status':'RUNNING'}
 atom_json(LOGS/'RUN_STATUS.json',state)
 try:
  summary=inspect(smoke=mode=='smoke')
  # Verify both data streams up front before long modeling. In smoke, NB201 needs no real data.
  a=named_dataset('nb101')
  if mode=='full':
   b=named_dataset('nb201',search_root)
   if b['groups_n']!=31:raise RuntimeError(f'NB201 known-label pool must have 31 groups, got {b["groups_n"]}')
   summary['nb201']=run_dataset(b)
  summary['nb101']=run_dataset(a,smoke=mode=='smoke')
  state.update({'status':'ENGINEERING_SMOKE_PASSED' if mode=='smoke' else 'EXPLORATORY_CAMPAIGN_COMPLETED',
                'duration_s':round(time.monotonic()-start,1),'datasets':{k:summary[k]['status'] for k in summary if k.startswith('nb')}})
  atom_json(LOGS/'RUN_STATUS.json',state)
  path=collect();print('UPLOAD_FILE',path,flush=True);return 0
 except InterruptedError as e:
  state.update(status='PAUSED_AT_CHECKPOINT',error=str(e));atom_json(LOGS/'RUN_STATUS.json',state)
  print('PAUSED. Remove PAUSE_REQUESTED.flag and rerun main launcher.',flush=True)
  collect();return 75
 except Exception as e:
  state.update(status='FAILED',error=repr(e),traceback=traceback.format_exc());atom_json(LOGS/'RUN_STATUS.json',state)
  print(traceback.format_exc(),flush=True)
  collect();return 1

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['smoke','full','collect'],default='smoke');p.add_argument('--search-root',default=os.environ.get('VELE09_NB201_ROOT'));args=p.parse_args()
 sys.exit(0 if args.mode=='collect' and print(collect()) is None else run(args.mode,args.search_root))
