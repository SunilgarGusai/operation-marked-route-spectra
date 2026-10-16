"""NAS-Bench-201 operation-edge DAG features and source-aligned GRAF feature port.

The GRAF family follows config nb201.json and features/{base,nasbench201}.py
at https://github.com/gabikadlecova/GRAF (consulted 2026-10-15).
This is an independent adaptation, not original package execution.
"""
import re
import hashlib
from itertools import combinations
import numpy as np

OPS = ('none','skip_connect','nor_conv_1x1','nor_conv_3x3','avg_pool_3x3')
GRAF_ORDER = ('skip_connect','none','nor_conv_3x3','nor_conv_1x1','avg_pool_3x3')
EDGES = ((0,1),(0,2),(1,2),(0,3),(1,3),(2,3))
OP_GROUPS = tuple(s for k in range(1,6) for s in combinations(GRAF_ORDER,k))
assert len(OP_GROUPS)==31

def parse_arch(arch):
    chunks=arch.strip().split('+')
    if len(chunks)!=3:raise ValueError('Expected three NASBench201 input groups')
    labels={}
    for dst,chunk in enumerate(chunks,1):
        pairs=re.findall(r'([^|~]+)~([0-9]+)',chunk)
        if len(pairs)!=dst:raise ValueError('Invalid source count in group '+repr(chunk))
        for opname,src in pairs:
            src=int(src)
            if src>=dst or opname not in OPS or (src,dst) in labels:raise ValueError('Invalid operation-edge pair')
            labels[(src,dst)]=opname
    if set(labels)!=set(EDGES):raise ValueError('Missing or repeated edges')
    return tuple(labels[e] for e in EDGES)

def format_arch(ops):
    labels=dict(zip(EDGES,ops))
    return '+'.join('|'+'|'.join(f'{labels[(i,j)]}~{i}' for i in range(j))+'|' for j in (1,2,3))

def _path_stats(edge_ops, subset, active_only=False):
    # GRAF restricted edge subsets: preserves all 6 operation-labelled edges,
    # including 'none' if specified by its published operation-subset config.
    adj=np.zeros((4,4),dtype=int)
    for (u,v),op in zip(EDGES,edge_ops):
        if op in subset and (not active_only or op!='none'): adj[u,v]=1
    # shortest, longest counts in edge-length. If no path, source NB201 returns
    # n_edges=6 for minimum and 0 for max (base.py).
    short=[float('inf')]*4;long=[-1]*4;short[0]=0;long[0]=0
    for u in range(4):
        for v in range(u+1,4):
            if adj[u,v] and short[u]!=float('inf'):
                short[v]=min(short[v],short[u]+1)
                long[v]=max(long[v],long[u]+1)
    return (int(short[3]) if short[3]!=float('inf') else 6,
            max(0,long[3]),adj)

def graf_source(edge_ops):
    out={f'graf_count_{op}':float(edge_ops.count(op)) for op in GRAF_ORDER}
    for i,ops in enumerate(OP_GROUPS):
        short,long,adj=_path_stats(edge_ops,set(ops))
        # GRAF nasbench201.py has `start=1,end=4`; its in/out dicts in base.py
        # use edge[0] to populate 'in' and edge[1] to populate 'out'.
        out[f'graf_min_path_{i:02d}']=float(short)
        out[f'graf_max_op_{i:02d}']=float(long)
        out[f'graf_in_degree_{i:02d}']=float(adj[0,:].sum())
        out[f'graf_out_degree_{i:02d}']=float(adj[:,3].sum())
        out[f'graf_avg_in_{i:02d}']=float(adj.sum()/4)
        out[f'graf_avg_out_{i:02d}']=float(adj.sum()/4)
    assert len(out)==191,len(out)
    return out

def active_graph(edge_ops):
    A=np.zeros((4,4),dtype=int)
    for (u,v),op in zip(EDGES,edge_ops):
        if op!='none':A[u,v]=1
    return A

def eccentricities(A):
    # For disconnected cell support, eccentricity is component-wise;
    # and disconnected flag enters the model. No fabricated infinite distances.
    und=((A+A.T)>0).astype(int)
    eps=[]
    comps=[]
    unseen=set(range(4))
    while unseen:
        start=min(unseen);seen={start};front={start}
        while front:
            new={w for v in front for w in np.flatnonzero(und[v]) if w not in seen}
            seen.update(new);front=new
        unseen-=seen;comps.append(seen)
    for v in range(4):
        dist={v:0};q=[v]
        while q:
            u=q.pop(0)
            for w in np.flatnonzero(und[u]):
                if w not in dist:dist[w]=dist[u]+1;q.append(int(w))
        eps.append(max(dist.values()))
    return np.array(eps,dtype=float),len(comps)

def route_paths(A):
    T=A.copy()
    X=A.copy()
    for k in range(2,4):
        X=X@A;T=T+X
    return T

def op_route(A,edge_ops,which):
    # M_op[u,v] counts every u-v directed path with multiplicity of edges
    # of type `which` on that path. This is NOT GRAF's restricted-path feature.
    d=np.zeros_like(A)
    for (u,v),op in zip(EDGES,edge_ops):
        if op==which and op!='none':d[u,v]=1
    T=route_paths(A)
    # Including identity prefixes/suffixes: sum_{prefix,marked edge,suffix}
    P=np.eye(4,dtype=int)+T
    return P@d@P

def path_features(edge_ops):
    A=active_graph(edge_ops);T=route_paths(A)
    eps,components=eccentricities(A)
    C=T+T.T;K=(eps[:,None]+eps[None,:])*C
    eig=np.linalg.eigvalsh(C);keig=np.linalg.eigvalsh(K)
    r={'cell_active_edges':float(A.sum()),'cell_components':float(components),
       'cell_connected_support':float(components==1),
       'cell_has_route':float(T[0,3]>0),'cell_route_inputout':float(T[0,3]),
       'cell_route_total':float(T.sum()),'cell_ecc_mean':float(eps.mean()),
       'cell_ecc_max':float(eps.max()),'cell_route_rho':float(max(abs(eig))),
       'cell_ecc_route_rho':float(max(abs(keig))),
       'cell_route_tr2':float(np.trace(C@C)),
       'cell_ecc_route_tr2':float(np.trace(K@K))}
    for op in OPS[1:]:
        R=op_route(A,edge_ops,op)
        U=R+R.T;W=(eps[:,None]+eps[None,:])*U
        z=np.linalg.eigvalsh(U);w=np.linalg.eigvalsh(W)
        nm=op.replace('nor_conv_','c').replace('avg_pool_','p').replace('skip_connect','skip')
        r[f'op_{nm}_route_total']=float(R.sum())
        r[f'op_{nm}_rho']=float(max(abs(z)))
        r[f'op_{nm}_tr2']=float(np.trace(U@U))
        r[f'weighted_op_{nm}_rho']=float(max(abs(w)))
        r[f'weighted_op_{nm}_tr2']=float(np.trace(W@W))
    return r

def group_key(edge_ops):
    return ''.join('1' if x!='none' else '0' for x in edge_ops)

def split(edge_ops):
    # no target dependence. Frozen group assignment.
    h=hashlib.sha256(('VELE09_P9C_NB201_V1|'+group_key(edge_ops)).encode()).hexdigest()
    q=int(h[:16],16)/float(2**64)
    if q<.70:return 'train'
    if q<.85:return 'development'
    return 'reserved_holdout'


def all_features(edge_ops):
    return {**graf_source(edge_ops),**path_features(edge_ops)}
