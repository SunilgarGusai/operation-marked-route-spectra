"""New labelled two-operation infinite-family corollary of the Phase-7 witness.
Symbolic all-s identity, plus explicit cloned-DAG consistency tests.
No novelty or publishing priority is asserted by this executable certificate.
"""
import json,hashlib
from pathlib import Path
import numpy as np
import sympy as sp
from family_math import EDGES_A,EDGES_B,graph,sym

ROOT=Path(__file__).resolve().parents[1]
MARKED_ALPHA=(0,6)
MARKED_BETA=(1,2,3,4,5)

def operation_pencil(d,selected,s):
    U=d['U'];B=np.zeros_like(U)
    for idx in selected:
        i,j=d['edges'][idx];B[i,j]=1
    Aa=B+B.T
    P=U@B+B@U
    H=sym(Aa)+s*sym(P+P.T)
    E=sp.diag(*map(int,d['e']))
    W=E*H+H*E
    Aweighted=E*sym(Aa)+sym(Aa)*E
    return H,W,Aweighted,B

def run(max_direct=3):
    graphs=[graph(EDGES_A),graph(EDGES_B)]
    s,x=sp.symbols('s x')
    evidence={}
    for opname,marked in [('alpha',MARKED_ALPHA),('beta',MARKED_BETA)]:
        pair=[operation_pencil(g,marked,s) for g in graphs]
        ha,ka,ba,_=pair[0];hb,kb,bb,_=pair[1]
        polyA=sp.Poly(ha.charpoly(x).as_expr(),x)
        polyB=sp.Poly(hb.charpoly(x).as_expr(),x)
        assert sp.simplify(polyA.as_expr()-polyB.as_expr())==0
        assert sp.Poly(ba.charpoly(x).as_expr(),x)==sp.Poly(bb.charpoly(x).as_expr(),x)
        reduced_gap=sp.factor(sp.trace(ka*ka)-sp.trace(kb*kb))
        expected=(30*s*s if opname=='alpha' else 30*s*(s+2))
        assert sp.simplify(reduced_gap-expected)==0
        direct=[]
        for factor in range(1,max_direct+1):
            mats=[]
            for g in graphs:
                U=np.kron(g['U'],np.ones((factor,factor),dtype=np.int64))
                P=np.eye(len(U),dtype=np.int64)+U+U@U
                m=np.zeros((7,7),dtype=np.int64)
                for idx in marked:
                    u,v=g['edges'][idx];m[u,v]=1
                M=np.kron(m,np.ones((factor,factor),dtype=np.int64))
                marked_route=P@M@P
                C=marked_route+marked_route.T
                eps=np.repeat(g['e'],factor)
                K=C*(eps[:,None]+eps[None,:])
                predicted=np.kron(np.array(operation_pencil(g,marked,s)[0].subs(s,factor),dtype=np.int64),np.ones((factor,factor),dtype=np.int64))
                assert np.array_equal(C,predicted)
                mats.append((C,K))
            trace_gap=int(np.trace(mats[0][1]@mats[0][1])-np.trace(mats[1][1]@mats[1][1]))
            expected_full=(30*factor**4 if opname=='alpha' else 30*factor**3*(factor+2))
            assert trace_gap==expected_full
            assert np.allclose(np.linalg.eigvalsh(mats[0][0]),np.linalg.eigvalsh(mats[1][0]),atol=1e-9)
            direct.append({'s':factor,'vertices':7*factor,'second_moment_gap':trace_gap})
        evidence[opname]={'tagged_seed_edge_positions':list(marked),
                'common_ordinary_marked_charpoly':str(sp.factor(polyA.as_expr())),
                'weighted_adjacency_marked_common_charpoly':str(sp.factor(ba.charpoly(x).as_expr())),
                'reduced_weighted_tr2_gap':str(reduced_gap),
                'full_weighted_tr2_gap':str(sp.factor(s*s*reduced_gap)),
                'direct_tests':direct}
    out={'status':'PASS', 'theorem':'Two-operation infinite families: both ordinary operation-marked and operation-weighted adjacency spectra agree, both ecc-weighted marked-route spectra disagree',
         's_domain':'positive integers','edges_A':[list(x) for x in EDGES_A],
         'edges_B':[list(x) for x in EDGES_B],
         'operation_labels':{'alpha':list(MARKED_ALPHA),'beta':list(MARKED_BETA)},
         'operations':evidence,
         'limitations':['Blow-up is established and belongs to previously communicated VELE construction material.',
                        'Spectral cospectralities are separate, not the same as identical full jointly labelled graph.',
                        'Literature priority of operation-marked path weights has not been certified.',
                        'All tests are structural, not predictive NAS performance.']}
    p=ROOT/'outputs'/'TWO_OPERATION_INFINITE_FAMILY_CERTIFICATE.json'
    p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(out,indent=2),encoding='utf8')
    return out

if __name__=='__main__':
 print(json.dumps(run(),indent=2)[:4500])
