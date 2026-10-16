"""Independent exact verifier for VELE09 manuscript v0.2.

Checks the two-route seed, a general path-length blow-up law, the
second-moment criterion, and strict Perron spectral-radius ordering
for all positive *integer* uniform replication widths.
Uses no NAS accuracy labels. Python >=3.10, sympy, networkx, numpy.
"""
import json
import importlib.util
from pathlib import Path

import networkx as nx
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
z, x, y = sp.symbols('z x y')
ARCS = {
    'A': [(0,2),(0,3),(1,3),(0,6),(1,4),(2,5),(3,4)],
    'B': [(0,2),(1,3),(0,6),(1,4),(2,4),(2,5),(3,4)],
}
ALPHA = {(0,2),(3,4)}

def matrices(name, op):
    g=nx.Graph(); g.add_nodes_from(range(7));g.add_edges_from(ARCS[name])
    U=sp.zeros(7);B=sp.zeros(7)
    for i,j in ARCS[name]:
        U[i,j]=1
        if ((i,j) in ALPHA)==(op=='alpha'):B[i,j]=1
    ecc=[nx.eccentricity(g,i) for i in range(7)]
    E=sp.diag(*ecc)
    W=E*(B+B.T)+(B+B.T)*E
    Q=U*B+B*U
    F2=E*(Q+Q.T)+(Q+Q.T)*E
    L=W+z*F2
    C=B+B.T+z*(Q+Q.T)
    return {'U':U,'B':B,'E':E,'W':W,'F2':F2,'L':L,'C':C}

def general_lift_test():
    # Non-three-layer graph with directed route lengths up to 3.
    # Eccentricity must be >= 2 for every vertex to preserve labels under cloning.
    edges=[(0,1),(1,2),(2,3),(0,3),(3,4)]
    n=5
    graph=nx.Graph();graph.add_nodes_from(range(n));graph.add_edges_from(edges)
    ecc=[nx.eccentricity(graph,i) for i in range(n)]
    assert min(ecc)>=2
    U=sp.zeros(n);B=sp.zeros(n)
    for i,j in edges:
        U[i,j]=1
    for i,j in [(1,2),(3,4)]:
        B[i,j]=1
    ell=4 # route 0->1->2->3->4
    assert U**(ell+1)==sp.zeros(n)
    forms=[]
    for k in range(1,ell+1):
        M=sum((U**r*B*U**(k-1-r) for r in range(k)),sp.zeros(n))
        S=M+M.T
        forms.append(sp.diag(*ecc)*S+S*sp.diag(*ecc))
    for s in (2,3):
        J=sp.ones(s,s)
        Us=sp.kronecker_product(U,J)
        Bs=sp.kronecker_product(B,J)
        P=sp.eye(n*s)
        for k in range(1,ell+1):P+=Us**k
        R=P*Bs*P
        Cs=R+R.T
        Eg=sp.kronecker_product(sp.diag(*ecc),sp.eye(s))
        K=Eg*Cs+Cs*Eg
        reduced=sum((s**k*forms[k-1] for k in range(1,ell+1)),sp.zeros(n))
        assert K==sp.kronecker_product(reduced/s,J)
    return {'dag_nodes':n,'longest_route_length':ell,'clone_widths_checked':[2,3], 'status':'PASS'}

def verify():
    A={o:matrices('A',o) for o in ('alpha','beta')}
    B={o:matrices('B',o) for o in ('alpha','beta')}
    result={'status':'PASS','width_domain':'positive integers','operations':{},'general_depth_test':general_lift_test()}
    for op in ('alpha','beta'):
        a,b=A[op],B[op]
        assert sp.expand(a['C'].charpoly(x).as_expr()-b['C'].charpoly(x).as_expr())==0
        assert sp.expand(a['W'].charpoly(x).as_expr()-b['W'].charpoly(x).as_expr())==0
        d1=sp.trace(a['W']*a['F2'])-sp.trace(b['W']*b['F2'])
        d2=sp.trace(a['F2']**2)-sp.trace(b['F2']**2)
        gap=sp.factor(z*z*(sp.trace(a['L']**2)-sp.trace(b['L']**2)))
        assert sp.expand(gap-z**3*(2*d1+z*d2))==0
        wanted=30*z**4 if op=='alpha' else 30*z**3*(z+2)
        assert sp.expand(gap-wanted)==0
        result['operations'][op]={'cross_moment_gap':str(sp.expand(d1)), 'two_hop_square_gap':str(sp.expand(d2)), 'full_trace_gap':str(gap)}
    # Alpha: one positive off-diagonal entry suffices for all widths.
    T=A['alpha']['L']-B['alpha']['L']
    ea,eb=sp.zeros(7,1),sp.zeros(7,1);ea[1]=1;eb[4]=1
    assert T==z*(ea*eb.T+eb*ea.T)
    g=nx.Graph();g.add_nodes_from(range(7));Lb=B['alpha']['L']
    g.add_edges_from((i,j) for i in range(7) for j in range(i+1,7) if Lb[i,j]!=0)
    assert {0,1,2,3,4,5} in list(map(set,nx.connected_components(g)))
    result['alpha_perron_proof']='PASS: nonnegative irreducible component, rank-two entrywise positive difference'
    # Beta: bipartite 3 x 4 blocks, cubic Gram characteristic polynomials.
    ma=A['beta']['L'].extract([0,1,2],[3,4,5,6]);mb=B['beta']['L'].extract([0,1,2],[3,4,5,6])
    assert A['beta']['L'].extract([0,1,2],[0,1,2])==sp.zeros(3)
    assert B['beta']['L'].extract([3,4,5,6],[3,4,5,6])==sp.zeros(4)
    pa=sp.Poly((ma*ma.T).charpoly(y).as_expr(),y);pb=sp.Poly((mb*mb.T).charpoly(y).as_expr(),y)
    ca,cb=pa.all_coeffs(),pb.all_coeffs()
    da=sp.factor(cb[1]-ca[1]);db=sp.factor(ca[2]-cb[2]);dc=sp.factor(cb[3]-ca[3])
    assert sp.expand(da-(15*z*z+30*z))==0
    assert sp.expand(db-(540*z**4+1080*z**3+574*z*z+2060*z))==0
    assert sp.expand(dc-(18571*z*z+28910*z))==0
    bound=sp.expand(da*(72*z*z+49)-db)
    assert sp.expand(bound-z*(540*z**3+1080*z**2+161*z-590))==0
    # For integer s>=1: s^3,s^2,s >=1, so this polynomial factor >=1191.
    assert 540+1080+161-590==1191
    assert (mb*mb.T)[0,0]==72*z*z+49
    result['beta_perron_proof']={
        'delta_a':str(da),'delta_b':str(db),'delta_c':str(dc),
        'difference_delta_a_times_lower_bound_minus_delta_b':str(sp.factor(bound)),
        'status':'PASS: cubic sign at Perron Gram eigenvalue, for integers z>=1'}
    # Representative direct full matrices check for both operation channels.
    for s in (1,2,3):
        for op in ('alpha','beta'):
            ka=np.array(A[op]['L'].subs(z,s)).astype(float)
            kb=np.array(B[op]['L'].subs(z,s)).astype(float)
            assert float(np.linalg.eigvalsh(ka)[-1])>float(np.linalg.eigvalsh(kb)[-1])
    result['representative_widths']=[1,2,3]
    return result

if __name__=='__main__':
    r=verify()
    path=HERE/'V02_EXACT_MATHEMATICAL_CERTIFICATE.json'
    path.write_text(json.dumps(r,indent=2),encoding='utf8')
    print('PASS: general depth law, both co-moment gaps, and all-width spectral-radius proof checks')
    print(path)
