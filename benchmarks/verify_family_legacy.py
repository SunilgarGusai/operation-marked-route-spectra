"""Independent exact Phase 7 theorem check and small direct blowup verification.
Run from any directory. Writes machine-readable certificates to ../outputs.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
import networkx as nx
import sympy as sp
from family_math import *

ROOT=Path(__file__).resolve().parents[1]

def run(max_explicit=4):
    A=graph(EDGES_A); B=graph(EDGES_B)
    assert tuple(A['e'])==EXPECTED_EA and tuple(B['e'])==EXPECTED_EB
    assert nx.is_isomorphic(A['G'],B['G'])
    dg1=nx.DiGraph(EDGES_A);dg2=nx.DiGraph(EDGES_B)
    assert not nx.is_isomorphic(dg1,dg2)
    s,x=sp.symbols('s x')
    H1=base_pencil(A,s);H2=base_pencil(B,s)
    poly1=sp.Poly(H1.charpoly(x).as_expr(),x);poly2=sp.Poly(H2.charpoly(x).as_expr(),x)
    assert sp.expand(poly1.as_expr()-poly2.as_expr())==0
    expected=sp.Poly(x**7-(3*s*s+2*s+7)*x**5-(6*s+2)*x**4+
        (s*s+3)*(s*s+2*s+4)*x**3+2*(2*s+1)*(s*s+s+3)*x**2+
        (3*s*s+2*s-4)*x-2*(s+1),x)
    assert sp.expand(poly1.as_expr()-expected.as_expr())==0
    F1=weighted_pencil(A,s);F2=weighted_pencil(B,s)
    t1=sp.factor(sp.trace(F1*F1));t2=sp.factor(sp.trace(F2*F2))
    assert sp.expand(t1-(272*s*s+256*s+572))==0
    assert sp.expand(t2-(242*s*s+196*s+572))==0
    assert sp.expand(t1-t2-30*s*(s+2))==0
    assert pc(A['B'])==pc(B['B'])
    assert pc(H1.subs(s,1))==pc(H2.subs(s,1))
    assert pc(F1.subs(s,1))!=pc(F2.subs(s,1))
    def rad(block):
        v=(block@block.T)
        roots=sp.solve(v.charpoly().as_expr(),dict=False)
        return sp.sqrt(max(roots,key=lambda z:float(z)))
    def extractF(d):
        ee=sp.diag(*map(int,d['e']))
        P=sym(d['P'])
        return ee*P+P*ee
    FA=extractF(A);FB=extractF(B)
    qa=FA[:2,4:7];qb=FB[:2,4:7]
    assert qa==sp.Matrix([[6,6,0],[8,0,0]])
    assert qb==sp.Matrix([[6,6,0],[7,0,0]])
    asymA=rad(qa);asymB=rad(qb)
    assert sp.simplify(asymA-sp.sqrt(68+4*sp.sqrt(145)))==0
    assert sp.simplify(asymB-sp.sqrt((121+sp.sqrt(7585))/2))==0
    assert float(asymA)>float(asymB)
    direct=[]
    for n in range(1,max_explicit+1):
        ra=numeric_blown(A,n);rb=numeric_blown(B,n)
        assert np.array_equal(ra['C'],np.kron(np.array(H1.subs(s,n),dtype=np.int64),np.ones((n,n),dtype=np.int64)))
        assert np.array_equal(ra['K'],np.kron(np.array(F1.subs(s,n),dtype=np.int64),np.ones((n,n),dtype=np.int64)))
        assert np.array_equal(rb['K'],np.kron(np.array(F2.subs(s,n),dtype=np.int64),np.ones((n,n),dtype=np.int64)))
        assert int(ra['U'].sum())==int(rb['U'].sum())==7*n*n
        assert int(ra['T'].sum())==int(rb['T'].sum())==7*n*n+3*n*n*n
        assert int((ra['K']@ra['K']).trace()-(rb['K']@rb['K']).trace())==30*n**3*(n+2)
        assert np.allclose(np.linalg.eigvalsh(ra['C']),np.linalg.eigvalsh(rb['C']),atol=1e-8)
        assert np.allclose(np.linalg.eigvalsh(ra['B']),np.linalg.eigvalsh(rb['B']),atol=1e-8)
        g1=nx.from_numpy_array(ra['A']);g2=nx.from_numpy_array(rb['A'])
        assert nx.is_isomorphic(g1,g2)
        assert np.array_equal(np.array([nx.eccentricity(g1,v) for v in range(7*n)]),ra['e'])
        assert np.array_equal(np.array([nx.eccentricity(g2,v) for v in range(7*n)]),rb['e'])
        direct.append({'replication_factor':n,'vertices':7*n,'edges':7*n*n,
                       'positive_length_paths':7*n*n+3*n**3,
                       'endpoint_paths':2*n*n+3*n**3,
                       'exact_K_second_moment_gap':30*n**3*(n+2),
                       'rho_K_A':float(np.linalg.eigvalsh(ra['K'])[-1]),
                       'rho_K_B':float(np.linalg.eigvalsh(rb['K'])[-1])})
        print(f'PASS direct s={n}: N={7*n}, exact trace gap={30*n**3*(n+2)}',flush=True)
    out={
      'status':'PASS', 'scope':'Exact symbolic theorem for every integer s>=1; finite direct checks are supplementary',
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'base_graphs':{'A':list(map(list,EDGES_A)),'B':list(map(list,EDGES_B))},
      'symbolic_common_charpoly_H':str(sp.expand(expected.as_expr())),
      'symbolic_common_charpoly_coefficients':[str(sp.factor(v)) for v in expected.all_coeffs()],
      'adjacency_eccentricity_common_polynomial':pc(A['B']),
      'squared_trace_base_A':str(sp.expand(t1)),'squared_trace_base_B':str(sp.expand(t2)),
      'squared_trace_gap_reduced':'30*s*(s+2)',
      'squared_trace_gap_blowup':'30*s**3*(s+2)',
      'asymptotic_rho_scaled_A':str(asymA),'asymptotic_rho_scaled_B':str(asymB),
      'asymptotic_rho_scaled_A_decimal':float(asymA),'asymptotic_rho_scaled_B_decimal':float(asymB),
      'direct_tests':direct,
      'limitations':['Existing blow-up operation is NOT claimed as new; Paper B owns general VELE blow-up theory.',
                     'Ordinary spectra and B spectra match separately; matrices with labels jointly determine K.',
                     'Noncospectral weighted K for all s is proved; rho ordering for all s is not asserted.',
                     'No NAS accuracy labels or model-training results were used.']}
    path=ROOT/'outputs'/'PHASE7_EXACT_CERTIFICATES.json';path.parent.mkdir(exist_ok=True,parents=True)
    path.write_text(json.dumps(out,indent=2),encoding='utf-8')
    print('PASS: symbolic all-s theorem, B spectra, exact trace gap, asymptotic constants.',flush=True)
    return out

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--max-direct',type=int,default=4)
    opts=a.parse_args();run(opts.max_direct)
