"""NB101 source-aligned GRAF feature port (NOT official end-to-end GRAF experiment).
Source correspondence: gabikadlecova/GRAF main:
 graf_nas/configs/nb101.json, graf_nas/features/nasbench101.py,
 graf_nas/features/base.py, graf_nas/search_space/nasbench101.py.
No NASLib, Torch, zero-cost proxies, or author-provided predictor training included.
The official max_op_on_path_opnodes subtracts 2 twice; the ``source`` mode
preserves this unusual behavior. ``semantic`` mode instead reports number
of allowed interior vertices in a longest allowed input-output path.
"""
from itertools import combinations
from collections import deque
import numpy as np

OPS=['maxpool3x3','conv1x1-bn-relu','conv3x3-bn-relu']
ALL=['input','output']+OPS
SUBSETS=[tuple(combo) for z in range(1,4) for combo in combinations(OPS,z)]

def path_dist(A, allowed, ops):
    n=len(ops); reach=[v in allowed or v in ('input','output') for v in ops]
    edges=[[j for j in range(i+1,n) if A[i][j] and reach[i] and reach[j]] for i in range(n)]
    lo=[10**9]*n;hi=[-10**9]*n;lo[0]=0;hi[0]=0
    for i in range(n):
        for j in edges[i]:
            if lo[i]!=10**9:lo[j]=min(lo[j],lo[i]+1)
            if hi[i]!=-10**9:hi[j]=max(hi[j],hi[i]+1)
    return (int(lo[-1]) if lo[-1]!=10**9 else n,
            (int(hi[-1]-1) if hi[-1]!=-10**9 else None))

def source_features(row,mode='source'):
    A=row['adjacency'];ops=row['operations'];n=len(ops)
    assert n>=2 and ops[0]=='input' and ops[-1]=='output'
    assert all(A[i][j]==0 for i in range(n) for j in range(i+1))
    if mode not in ('source','semantic'):raise ValueError(mode)
    res={f'graf_op_count_{op}':float(ops.count(op)) for op in ALL}
    for subset in SUBSETS:
        name='_'.join('mp' if x=='maxpool3x3' else 'c1' if x.startswith('conv1') else 'c3' for x in subset)
        allowed=set(subset)
        shortest,max_interior=path_dist(A,allowed,ops)
        res[f'graf_{mode}_min_path_{name}']=float(shortest)
        # Original code: longest path vertices - 2 - 2; disconnected=0-2-2 = -4
        res[f'graf_{mode}_max_op_{name}']=float((max_interior-2) if max_interior is not None else -4) if mode=='source' else float(max_interior if max_interior is not None else 0)
        # NB101 node_degree: get_in_out_edges_opnodes; endpoints included in denominators.
        in_count=[0]*n;out_count=[0]*n
        for i in range(n):
            for j in range(i+1,n):
                if A[i][j]:
                    if ops[i] in allowed:in_count[j]+=1
                    if ops[j] in allowed:out_count[i]+=1
        res[f'graf_{mode}_in_degree_{name}']=float(in_count[-1])
        res[f'graf_{mode}_out_degree_{name}']=float(out_count[0])
        res[f'graf_{mode}_avg_in_{name}']=float(sum(in_count)/n)
        res[f'graf_{mode}_avg_out_{name}']=float(sum(out_count)/n)
    assert len(res)==47,len(res)
    return res
